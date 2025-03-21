import collections
from itertools import islice

import sqlalchemy
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql.elements import (
    AsBoolean,
    BinaryExpression,
    BooleanClauseList,
    UnaryExpression,
    operators,
)
from sqlalchemy.sql.expression import ClauseElement, Executable


def clause_as_str(clause, dialect):
    """
    Return a SQL clause as a string in the supplied SQL dialect with any included
    parameters interpolated in
    """
    compiled = clause.compile(
        dialect=dialect,
        compile_kwargs={"literal_binds": True},
    )
    return str(compiled).strip()


def is_predicate(clause):
    """
    Some boolean expressions are guaranteed to be boolean-typed by virtue of their
    syntax, e.g.

      a == b

    Others happen to be boolean-typed by virtue of the columns they use, but you can't
    tell just by looking at them, e.g.

      some_table.some_boolean_column

    We call the former class "predicates".

    While some databases treat both classes of boolean expression as equivalent, others
    have rules about which syntactic contexts accept predicates and which accept boolean
    expressions. As the two are semantically equivalent we can always convert from one
    to other, but we need to know which is which so we can apply the appropriate
    conversion rules.
    """
    if isinstance(clause, BooleanClauseList | AsBoolean):
        return True
    if isinstance(clause, BinaryExpression):
        return clause._is_implicitly_boolean
    # We have to identify `NOT ...` expressions by the operator they use
    if isinstance(clause, UnaryExpression) and clause.operator is operators.inv:
        return True
    return False


class GeneratedTable(sqlalchemy.Table):
    """
    This wraps a standard SQLAlchemy Table and adds a pair of extra attributes
    which are a sequence of queries needed to create and populate this table and a
    sequence (possibly empty) of queries needed to clean it up.

    This provides a generic mechanism for constructing "multi-step" queries i.e. queries
    that require creating intermediate objects before fetching their results. These
    intermediate objects could be temporary tables, persistent tables, materialized
    views, or anything else so long as it functions syntactically as a table.

    NOTE: At present, the `add_setup_and_cleanup_queries` code assumes that once a
    GeneratedTable is created it no longer cares whether any of the tables it was
    created from continue to exist. This is true for all the types of generated table we
    currently have but it may not be true forever (non-materialized views, for instance,
    would not have this property). If we do start using such types then we will get loud
    and immediate failures from the database. We will then need to add an extra
    attribute to GeneratedTable indicating whether the table requires its parents to
    stick around, and the code in `add_setup_and_cleanup_queries` will need to be
    modified to respect this.
    """

    setup_queries = ()
    cleanup_queries = ()

    @classmethod
    def from_query(cls, name, query, metadata=None, **kwargs):
        """
        Create a GeneratedTable whose column structure matches that of the supplied query
        """
        if metadata is None:
            metadata = sqlalchemy.MetaData()
        columns = [
            sqlalchemy.Column(c.name, c.type, key=c.key) for c in query.selected_columns
        ]
        return cls(name, metadata, *columns, **kwargs)


def add_setup_and_cleanup_queries(queries):
    """
    Given a list of SQLAlchemy queries, find all GeneratedTables embedded in them and
    return a list which includes the original queries plus all the necessary setup and
    cleanup queries from those GeneratedTables in an appropriate order for execution.

    The "appropriate" order here obviously means respecting the dependencies as we need
    to ensure that tables are created before we try to run queries which reference those
    tables. But we also want to respect another constraint which is minimising the
    lifetime of tables. That is: we want to create tables at the last possible moment
    before we need them, and we want to clean them up as soon as they are no longer
    needed. This allows us to run long series of queries without creating undue pressure
    on temporary table storage space.

    The toplogical order we get "for free" with `graphlib.TopologicalSorter` can't
    deliver this because it wants to put all the dependency-less queries ahead of any
    queries which have dependencies, and we want to defer them to the last possible
    moment. This means we need to to do the ordering ourselves.

    NOTE: If you are here because you are trying to debug why some temporary objects are
    being cleaned up too early then see the note in the GeneratedTable docstring.
    """
    # We have a tree whose nodes consist of queries and the GeneratedTables on which
    # they depend, and any GeneratedTable on which _those_ depend and so on recursively.
    # We represent this using the two dicts below:
    #
    # Map nodes to a list of their immediate parents
    parents = {}
    # Map nodes to a list of all their ancestors
    ancestors = {}
    # Populate the dicts
    for query in queries:
        build_relations(parents, ancestors, query)

    # Count how many direct children each node has (i.e. how many times it appears as a
    # parent) so we can track when they are no longer needed
    child_count = collections.Counter()
    for parent_nodes in parents.values():
        child_count.update(parent_nodes)

    # We use a dictionary as a poor man's ordered set type which ensures we only add a
    # node once even if it's an ancestor of multiple other nodes
    ordered_nodes = {}
    # Add the queries to be run in order ...
    for query in queries:
        # ... first including any ancestors, in reverse order so most distant ancestors
        # come earliest
        for ancestor in reversed(ancestors.get(query, ())):
            ordered_nodes.setdefault(ancestor)
        ordered_nodes.setdefault(query)

    # Now walk over the nodes, adding their queries to the final list and cleaning up
    # any tables as soon as they are no longer needed
    all_queries = []
    for node in ordered_nodes:
        all_queries.extend(get_node_queries(node))
        # Decrement the child count of each of this node's parents. If any of these now
        # have zero children then they are no longer needed and they can be cleaned up
        for parent in parents.get(node, ()):
            child_count[parent] -= 1
            if child_count[parent] == 0:
                all_queries.extend(parent.cleanup_queries)

    return all_queries


def build_relations(parents, ancestors, node):
    # Avoid re-recursing into nodes we've already seen: on some of our larger and more
    # nested query graphs this can get very expensive
    if node in parents:
        return

    parents[node] = []
    ancestors[node] = []
    for parent in get_parents(node):
        parents[node].append(parent)
        build_relations(parents, ancestors, parent)
        ancestors[node].append(parent)
        ancestors[node].extend(ancestors[parent])


def get_parents(node):
    for query in get_node_queries(node):
        for table in get_generated_tables(query):
            # An oddity of the GeneratedTable class is that instances generally hold a
            # reference to themselves: one of the setup queries for table X will often
            # be "create a table with the structure given by X". We ignore this apparent
            # (though not actual) circularity.
            if table is not node:
                yield table


def get_node_queries(node):
    if isinstance(node, GeneratedTable):
        return node.setup_queries
    else:
        return [node]


def get_generated_tables(clause):
    """
    Return any GeneratedTable objects directly referenced by a SQLAlchemy ClauseElement
    """
    return [elem for elem in iterate_unique(clause) if isinstance(elem, GeneratedTable)]


def iterate_unique(clause):
    """
    Iterate over all unique query elements referenced by `clause`

    This is almost a verbatim copy of `sqlalchemy.sql.visitors.iterate()` with the
    difference that this keeps track of which elements have already been seen and avoids
    recursing into them again. For certain query structures this can make a huge
    difference to how long it takes to retrieve all the elements.

    Original code from:
    https://github.com/sqlalchemy/sqlalchemy/blob/rel_2_0_0/lib/sqlalchemy/sql/visitors.py#L829-L867

    Copyright (C) 2005-2023 the SQLAlchemy authors and contributors

    This function is part of SQLAlchemy and is released under the MIT License:
    https://www.opensource.org/licenses/mit-license.php
    """
    yield clause
    children = clause.get_children()

    if not children:
        return

    stack = collections.deque([children])
    seen = set()
    while stack:
        t_iterator = stack.popleft()
        for t in t_iterator:
            # Some SQLAlchemy objects overload equality so they aren't safe to use
            # directly in sets but we can track them by ID
            key = id(t)
            if key not in seen:
                seen.add(key)
                yield t
                stack.append(t.get_children())


class InsertMany:
    """
    Wraps up the query "insert this iterator of rows into this table" so that we can
    execute it in the most efficient way possible, without the caller having to worry
    about what that might be.

    Acts enough like a SQLAlchemy ClauseElement for our purposes.
    """

    # The batch_size here doesn't make a huge difference as SQLAlchemy does its own
    # internal batching optimisied for the specific database dialect. It just needs to
    # be big enough that it gives SQLAlchemy's batching enough to work with, but not so
    # big that we need to worry about memory consumption.
    def __init__(self, table, rows, batch_size=10000):
        self.table = table
        self.rows = rows
        self.batch_size = batch_size

    def get_children(self):
        return [self.table]

    # Called when the clause is executed
    def _execute_on_connection(self, connection, distilled_params, execution_options):
        assert not distilled_params, "Cannot supply parameters to InsertMany clause"
        insert_statement = self.table.insert()
        keys = self.table.columns.keys()
        # SQLAlchemy's insert-multiple-rows interface wants rows supplied as dicts
        # rather than tuples
        params = map(lambda values: dict(zip(keys, values)), self.rows)
        while params_batch := list(islice(params, self.batch_size)):
            connection.execute(
                insert_statement,
                params_batch,
                execution_options=execution_options,
            )

    def compile(self, *args, **kwargs):  # NOQA: A003
        insert_statement = self.table.insert()
        # If we're not trying to render a statement with literal values instead of
        # parameters then we just pass directly through to the default `compile()`
        # method
        if not (
            "compile_kwargs" in kwargs and kwargs["compile_kwargs"].get("literal_binds")
        ):
            return insert_statement.compile(*args, **kwargs)
        # If we *are* trying to render with literal values then things are bit more
        # tricky because there's no direct parallel to multi-row inserts in plain
        # SQL-as-text. So instead we compile a multi-statement string which does the
        # same thing.
        sql = []
        for row in self.rows:
            bound_insert = insert_statement.values(row)
            compiled = bound_insert.compile(*args, **kwargs)
            sql.append(str(compiled).strip())
        # Note, we're returning a string here, rather than a CompiledSQL object. This
        # works fine for our purposes. We can consider doing something more complicated
        # if the need arises.
        return ";\n".join(sql)


class CreateTableAs(Executable, ClauseElement):
    inherit_cache = True

    def __init__(self, table, selectable):
        self.table = table
        self.selectable = selectable

    def get_children(self):
        return (self.table, self.selectable)


@compiles(CreateTableAs)
def visit_create_table_as(element, compiler, **kw):
    return "CREATE TABLE {} AS {}".format(
        compiler.process(element.table, asfrom=True, **kw),
        compiler.process(element.selectable, asfrom=True, **kw),
    )
