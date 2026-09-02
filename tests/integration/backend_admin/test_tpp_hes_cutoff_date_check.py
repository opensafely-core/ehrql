import pytest

from ehrql.backends.tpp import TPPBackend
from tests.backend_schemas.tpp.schema import APCS, EC, OPA


@pytest.mark.parametrize(
    "expected,table_data",
    [
        (
            # True when all tables contain at least one instance of target month
            "true",
            {
                "APCS": ["202301", "202304", "202305"],
                "EC": ["202301", "202304", "202305"],
                "OPA": ["202301", "202304", "202305"],
            },
        ),
        (
            # False if a single table does not contain the target month
            "false",
            {
                "APCS": ["202301", "202304", "202305"],
                "EC": ["202301", "202304", "202305"],
                "OPA": ["202301", "202305"],
            },
        ),
        (
            # False if no tables contain the target month
            "false",
            {
                "APCS": ["202301"],
                "EC": ["202301"],
                "OPA": ["202301"],
            },
        ),
    ],
)
def test_hes_cutoff_date_check(mssql_database, capsys, expected, table_data):
    apcs = [
        APCS(
            Patient_ID=i,
            APCS_Ident=i,
            Der_Activity_Month=month,
        )
        for i, month in enumerate(table_data["APCS"])
    ]
    ec = [
        EC(
            Patient_ID=i,
            EC_Ident=i,
            Der_Activity_Month=month,
        )
        for i, month in enumerate(table_data["EC"])
    ]
    opa = [
        OPA(
            Patient_ID=i,
            OPA_Ident=i,
            Der_Activity_Month=month,
        )
        for i, month in enumerate(table_data["OPA"])
    ]

    mssql_database.setup(*apcs, *ec, *opa)

    args = [
        "hes_cutoff_date_check",
        "--dsn",
        mssql_database.host_url(),
        "--expected-activity-month",
        "202304",
    ]
    TPPBackend().run_admin_command(args, environ={}, user_args=[])

    assert capsys.readouterr().out.strip() == expected


@pytest.mark.parametrize("month", ["20261", "2026-01", "Feb2026"])
def test_hes_cutoff_date_check_month_validation(mssql_database, capsys, month):
    args = [
        "hes_cutoff_date_check",
        "--dsn",
        mssql_database.host_url(),
        "--expected-activity-month",
        month,
    ]
    with pytest.raises(SystemExit):
        TPPBackend().run_admin_command(args, environ={}, user_args=[])
    assert f"Month ({month}) not valid" in capsys.readouterr().err.strip()
