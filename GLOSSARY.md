# Glossary

**Backend.**
A class that translates between the table structure we present to the user (the ehrQL Tables) and the table structure in an EHR provider's database (the Database Tables).

Each Backend is specific to an EHR provider and a Query Engine.
For example, the TPP backend is specific to TPP (an EHR provider) and the MSSQLQueryEngine.

A Backend is not required in order to connect to an EHR provider's database.
If the structure of the Database Tables exactly matches the structure of the ehrQL Tables, then no translation is required.
In this case, we query the EHR provider's database by specifying the appropriate Query Engine.

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
Takes a Query, connects to an EHR provider's database, and returns the corresponding data.
Usually, the database will be relational and will speak SQL.

**Query Language.**
A programming language designed for querying a data store.
For example, ehrQL.

**Query Model.**
The core data structure by which Data Builder represents a Query.
It is responsible for defining the semantics of all the operations we support on the data, and for ensuring that only semantically valid queries can be constructed.
When a user writes ehrQL this constructs a Query that is then passed to a Query Engine for execution.
This provides a clear boundary between the syntactic surface of ehrQL (where expressiveness and user convenience are paramount) and the underlying semantics.

**ehrQL Table**
The table structure we present to the user.
User's can write queries against this table structure using ehrQL.

**Database Table**
The table structure in an EHR provider's database.
We do not present this table structure to the user.
Instead, the user interacts with ehrQL Tables; their queries are translated into queries against this table structure by a Backend.

**`variable_definitions`.**
Found throughout the Data Builder codebase, the Query Model equivalent of a Dataset Definition.
Specifically, a dictionary that maps column names to Query Model objects (plus a `population` key that defines the population).
