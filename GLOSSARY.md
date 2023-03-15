# Glossary

**Backend.**
A class that translates between the table structure we present to the user (the ehrQL Tables) and the table structure in an EHR provider's database (the Database Tables).

Each Backend is specific to an EHR provider and a Query Engine, which tells Data Builder how to talk to the kind of database used by the EHR provider.
For instance, the TPP backend uses the MSSQLQueryEngine, which knows how to connect to Microsoft SQL Server and speak Transact-SQL to it.

A Backend is not required in order to connect to a database.
If the structure of the database tables exactly matches the structure of the ehrQL tables, then there is no translation to be done.
In that case, we can query the database just be specifying the appropriate Query Engine.

**Dataset Definition.**
Describes, using ehrQL, the EHR data to extract from a Backend.

**Domain-Specific Language (DSL).**
A programming language designed for a specific application domain.
For example, ehrQL is a DSL;
it is a programming language designed for the specific application domain of EHR data.

**Dummy Data.**
Randomly-generated data used as a substitute for the EHR data when generating a dataset from a Dataset Definition.

**ehrQL.**
The Electronic Health Records Query Language, pronounced  err-kul (or *Hercule* as in Poirot, if you're feeling continental).
A Domain-Specific Language (DSL) for EHR data.
It consists of the classes, methods, and functions that are used in Dataset Definitions.

**Electronic Health Records (EHR) data.**
Data about the health of the patients in a population, stored electronically (i.e. digitally).

**Measure.**
A quotient (a numerator divided by a denominator) for a given time interval and period (e.g. each month for a year).

**Query**
A graph of connected Query Model objects.

**Query Engine.**
Takes a Query, connects to a database, and returns the corresponding data.
Usually this will be a relational database speaking some dialect of SQL.
But it doesn't have to be.

**Query Language.**
A programming language designed for querying a data store.
For example, ehrQL.

**Query Model.**
The core data structure by which Data Builder represents a Query.
It is responsible for defining the semantics of all the operations we support on the data, and for ensuring that only semantically valid queries can be constructed.
When a user writes ehrQL this constructs a Query that is then passed to a Query Engine for execution.
This provides a clear boundary between the syntactic surface of ehrQL (where expressiveness and user convenience are paramount) and the underlying semantics.

**ehrQL Table**
Describes the structure and types of some EHR data.
User's can write queries against this data using ehrQL.

**Database Table**
Table in the SQL sense as stored in the database of an EHR provider.
These are not directly exposed to users.
Users interact with ehrQL Tables and their queries are translated into queries against Database Tables by a Backend.

**`variable_definitions`.**
Found throughout the Data Builder codebase, the Query Model equivalent of a Dataset Definition.
Specifically, a dictionary that maps column names to Query Model objects (plus a `population` key that defines the population).
