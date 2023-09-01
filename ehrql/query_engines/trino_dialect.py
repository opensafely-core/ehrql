from trino.sqlalchemy.compiler import TrinoDDLCompiler as BaseTrinoDDLCompiler
from trino.sqlalchemy.dialect import TrinoDialect as BaseTrinoDialect


class TrinoDDLCompiler(BaseTrinoDDLCompiler):
    def get_column_specification(self, column, **kwargs):
        """
        Prevent SQLAlchemy from trying to create NOT NULL column constraints, which
        some Trino connectors don't support (particularly the memory connector,
        which is used for tests).

        This is only required by the SQLAlchemy ORM layer and therefore only
        used in test.
        """
        colspec = super().get_column_specification(column, **kwargs)
        colspec = colspec.replace(" NOT NULL", "")
        return colspec

    def visit_primary_key_constraint(self, constraint, **kw):
        """
        Prevent SQLAlchemy from trying to create PRIMARY KEY constraints, which
        some Trino connectors don't support (particularly the memory connector,
        which is used for tests).

        This is only required by the SQLAlchemy ORM layer and therefore only
        used in test.
        """
        return ""


class TrinoDialect(BaseTrinoDialect):
    supports_statement_cache = True
    ddl_compiler = TrinoDDLCompiler

    # Tell SQLAlchemy it can used batched insert options for faster test setup
    supports_multivalues_insert = True
    use_insertmanyvalues = True
    use_insertmanyvalues_wo_returning = True
