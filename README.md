# OpenSAFELY ehrQL

ehrQL is a Python-based query language for electronic health record (EHR) data.
It has been designed for use with the OpenSAFELY platform.

Documentation is at the [OpenSAFELY documentation site](https://docs.opensafely.org/ehrql).

# For developers

See [DEVELOPERS.md](DEVELOPERS.md).

There is also [a glossary](GLOSSARY.md) of terms used in the codebase.

# About the OpenSAFELY framework

The OpenSAFELY framework is a Trusted Research Environment (TRE) for electronic
health records research in the NHS, with a focus on public accountability and
research quality.

Read more at [OpenSAFELY.org](https://opensafely.org).



## Identify files we do need

❯ find ehrql/ -name "*.py" | sort  > files.txt
❯ .venv/bin/coverage run -m ehrql generate-dataset dd.py --output dd.csv
❯ .venv/bin/coverage report --no-skip-covered | awk '{print $1}' | grep ehrql | sort > covered.txt
❯ diff -y --suppress-common-lines files.txt covered.txt   | awk '{print $1}' | grep -v docs
ehrql/backends/emis.py
ehrql/backends/tpp.py
ehrql/file_formats/validation.py
ehrql/query_engines/mssql_dialect.py
ehrql/query_engines/mssql.py
ehrql/query_engines/trino_dialect.py
ehrql/query_engines/trino.py
ehrql/tables/beta/core.py
ehrql/tables/beta/__init__.py
ehrql/tables/beta/raw/core.py
ehrql/tables/beta/raw/__init__.py
ehrql/tables/beta/raw/tpp.py
ehrql/tables/beta/smoketest.py
ehrql/tables/beta/tpp.py
ehrql/tables/examples/__init__.py
ehrql/tables/examples/tutorial.py
ehrql/utils/mssql_log_utils.py
ehrql/utils/sqlalchemy_exec_utils.py

## combine into portable executable

Get cosmopolitan https://cosmo.zip/
wget https://cosmo.zip/pub/cosmos/bin/python

# make wheels for all the requirements
pip wheel -r requirements.txt -w ./dependency_wheels

Pure python version of sqlalchemy:

export DISABLE_SQLALCHEMY_CEXT=1; .venv/bin/pip wheel --no-binary :all: sqlalchemy==2.0.23

ls ../../dependency_wheels/*.whl | xargs --replace=F -n 1 unzip F -d Lib/
zip -r python.com Lib
