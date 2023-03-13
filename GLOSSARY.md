# Glossary

**Backend.**
The logical representation of a collection of EHR data.
A Backend is associated with a provider of EHR data, a data store, and a Query Language.
For example, the TPP Backend is associated with TPP, Microsoft SQL Server, and Transact-SQL.

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
Randomly-generated data used as a substitute for the EHR data to extract from a Backend.

**ehrQL.**
The Electronic Health Records Query Language, pronounced *Hercule*.
A Domain-Specific Language (DSL) for EHR data.
It consists of the classes, methods, and functions that are used in Dataset Definitions.

**Electronic Health Records (EHR) data.**
Data about the health of the patients in a population, stored electronically (i.e. digitally).

**Measure.**
A quotient (a numerator divided by a denominator) for a given time interval and period (e.g. each month for a year).

**Query Engine.**
Translates the Query Model into the Query Language associated with a Backend.
For example, a Query Engine translates the Query Model into Transact-SQL, which is associated with the TPP Backend.

**Query Language.**
A programming language designed for querying a data store.
For example, ehrQL.

**Query Model.**
It consists of the objects that are created by ehrQL and passed to the Query Engines.

**Table.**
The conceptual representation of a collection of EHR data.
A Table fulfils a Contract.

**`variable_definitions`.**
Found throughout the Data Builder codebase, a variable that maps names to Query Model objects.
