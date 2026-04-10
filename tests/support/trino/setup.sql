-- In production each user has a writable schema named with their username in which to
-- create temporary tables; we want to mirror that set up here so we create a "trino"
-- schema (named after the default user") in the default "trino" catalog.
CREATE SCHEMA trino.trino;
