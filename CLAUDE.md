# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

ehrQL uses `just` (a command runner) for all development tasks. Run `just list` to see all available commands.

### Development Environment
- `just devenv` - Set up virtual environment and install dependencies
- `just virtualenv` - Create virtual environment only

### Testing
- `just test-all` - Run full test suite with coverage (as in CI)
- `just test-unit` - Run unit tests only
- `just test-spec` - Run spec tests (generated from ehrQL specification)
- `just test-integration` - Run integration tests (require database)
- `just test-functional` - Run end-to-end CLI tests
- `just test-acceptance` - Run tests against real study examples
- `just test-generative` - Run Hypothesis-based generative tests with higher example count
- `just test-docker` - Run Docker image tests
- `just test-docs-examples` - Run documentation example tests
- `just test [ARGS]` - Run specific pytest commands/files

### Code Quality
- `just check` - Run linting and formatting checks (non-modifying)
- `just fix` - Auto-fix linting and formatting issues
- Linting: Uses `ruff` for code formatting and linting
- No static type checking (previously used mypy but removed)

### Documentation
- `just docs-serve` - Start MkDocs development server
- `just docs-build` - Build documentation
- `just generate-docs` - Generate auto-generated documentation files
- `just docs-check-generated-docs-are-current` - Verify docs are up-to-date

### Database Operations
- `just create-tpp-test-db` - Create MSSQL test database with TPP schema
- `just connect-to-mssql` - Open interactive SQL Server shell
- `just connect-to-trino` - Open interactive Trino shell
- `just remove-database-containers` - Clean up test database containers

### Build/Docker
- `just build-ehrql [image_name]` - Build ehrQL Docker image
- `just build-ehrql-for-os-cli` - Build image tagged for OpenSAFELY CLI use

## Architecture Overview

ehrQL is a domain-specific query language for electronic health records with a layered architecture:

### Core Components

1. **Query Language Layer** (`query_language.py`)
   - User-facing Pythonic API with `Dataset`, `PatientSeries`, `EventSeries`
   - Type-specific series: `DateSeries`, `BoolSeries`, `IntSeries`, etc.
   - Operations: `where()`, `sort_by()`, aggregations, case expressions

2. **Query Model Layer** (`query_model/`)
   - Internal AST representation using immutable dataclasses
   - `nodes.py` - Core operation nodes (Filter, Sort, AggregateByPatient)
   - `transforms.py` - Query optimization and rewriting
   - Forms a directed acyclic graph of operations

3. **Table Schema Layer** (`tables/`)
   - `core.py` - Standard tables (patients, medications, clinical_events)
   - Backend-specific: `tpp.py`, `emis.py`, `ted.py`
   - Uses `@table` decorator for typed column definitions

4. **Backend Layer** (`backends/`)
   - Adapts queries for different EHR systems (TPP, EMIS, TED)
   - Handles schema mapping and backend-specific query modifications

5. **Query Engine Layer** (`query_engines/`)
   - Translates query model to SQL and executes queries
   - `mssql.py`, `sqlite.py`, `trino.py`, `local_file.py`
   - `base_sql.py` provides common SQL generation logic

6. **File Formats** (`file_formats/`)
   - Handles CSV, Arrow, and other output formats

### Query Processing Flow
```
Python Query → Query Language → Query Model → SQL → Database → Results
```

### Key Patterns
- **Type Safety**: Strong typing with compile-time validation
- **Immutable Queries**: Query model uses immutable dataclasses
- **Multi-Backend**: Single query runs on different EHR systems
- **Dummy Data**: Built-in synthetic data generation for testing

## Development Notes

### Testing Strategy
- **Acceptance tests**: Real study examples (keep minimal for maintenance)
- **Spec tests**: Cover all ehrQL features, run against all query engines
- **Unit tests**: Complex logic not covered by spec tests
- **Integration tests**: Database-dependent functionality
- **Generative tests**: Hypothesis-based testing with query generation

### Test Database Setup
Integration tests use persistent Docker containers for databases. Tests clean schema between runs but leave containers running for speed.

### Security Considerations
ehrQL enforces security boundaries in OpenSAFELY:
1. **User code isolation**: Runs in restricted subprocess via `loaders.py`
2. **Query restrictions**: `Backend.modify_dataset()` hook adds access controls
3. **No patient data in logs**: Careful logging to avoid data leakage

### Documentation
- Lives in `docs/` directory, built with MkDocs
- Some files auto-generated in `docs/includes/generated_docs/`
- Examples in Markdown fences with `ehrql` syntax are tested
- Python files in `docs/` are treated as working ehrQL definitions

### Code Conventions
- 100% test coverage required (liberal use of `no cover` pragmas allowed)
- Uses `ruff` for formatting/linting (line length 88)
- No static type checking, but annotations used for clarity in `query_model`
- Dataclasses retain type annotations
- **IMPORTANT**: Always run `just fix` after making any code changes to ensure proper formatting and linting

### ehrQL CLI Entry Point
Main CLI is `ehrql` command (via `ehrql.__main__:entrypoint`):
- `ehrql generate-dataset` - Core dataset generation
- `ehrql dump-dataset-sql` - Show generated SQL
- `ehrql create-dummy-tables` - Generate test data
- `ehrql --help` for full command reference

Log SQL queries by setting `LOG_SQL=1` environment variable.
