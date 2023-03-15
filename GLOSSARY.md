# Glossary

**Backend.**
A class which translates between the table structure we present to the user (the ehrQL tables) and the table structure in an EHR provider's database (the database tables).

Each Backend is specific to an EHR provider and a Query Engine, which tells Data Builder how to talk to the kind of database used by the EHR provider. For instance the TPP backend uses the MSSQLQueryEngine which knows how to connect to Microsoft SQL Server and speak Transact-SQL to it.

A Backend is not required in order to connect to a database. If the structure of the database tables exactly matches the structure of the ehrQL tables then there is no translation to be done. In that case, we can query the database just be specifying the appropriate Query Engine.

**Contract.**
A specification for a collection of EHR data.
A Contract is fulfilled by a Table.

**Dataset Definition.**
Describes, using ehrQL, the EHR data to extract from a Backend.

**Domain-Specific Language (DSL).**
A programming language designed for a specific application domain.
For example, ehrQL is a DSL;
it is a programming language designed for the specific application domain of EHR data.

**Dummy Data.**
Randomly-generated data used as a substitute for the EHR data when generating a dataset from a dataset definition.

**ehrQL.**
The Electronic Health Records Query Language, pronounced  err-kul (or *Hercule* as in Poirot, if you're feeling continental).
A Domain-Specific Language (DSL) for EHR data.
It consists of the classes, methods, and functions that are used in Dataset Definitions.

**Electronic Health Records (EHR) data.**
Data about the health of the patients in a population, stored electronically (i.e. digitally).

**Measure.**
A quotient (a numerator divided by a denominator) for a given time interval and period (e.g. each month for a year).

**Query Engine.**
Takes a query (a graph of connected Query Model objects), connects to a database and returns the corresponding data. Usually this will be a relational database speaking some dialect of SQL. But it doesn't have to be.

**Query Language.**
A programming language designed for querying a data store.
For example, ehrQL.

**Query Model.**
The core data structure by which Data Builder represents a query. It is responsible for defining the semantics of all the operations we support on the data, and for ensuring that only semantically valid queries can be constructed. When a user writes ehrQL this constructs a graph of Query Model objects which are then passed to a Query Engine for execution. This provides a clear boundary between the syntactic surface of ehrQL (where expressiveness and user convenience are paramount) and the underlying semantics.

**ehrQL table**
Describes the structure and types of some EHR data. User's can write queries against this data using ehrQL.

**Database table**
Table in the SQL sense as stored in the database of an EHR provider. These are not directly exposed to users. Users interact with ehrQL tables and their queries are translated into queries against database tables by a Backend.

**`variable_definitions`.**
Found throughout the Data Builder codebase, the Query Model equivalent of an ehrQL dataset definition. Specifically, a dictionary that maps column names to Query Model objects (plus a `population` key which defines the population).
