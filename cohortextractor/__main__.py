"""
Shim module to avoid rename churn in studies

See __init__.py for a full explanation.
"""
from cohortextractor2.__main__ import main

if __name__ == "__main__":
    main()
