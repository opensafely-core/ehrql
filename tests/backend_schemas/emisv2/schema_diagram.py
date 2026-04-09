"""
To run this script:
    # Install the graphviz system binary (this is different from the graphviz python package)
    sudo apt install graphviz

    python3 tests/backend_schemas/emisv2/schema_diagram.py "excel_schema_file.xlsx"
"""

import argparse
from pathlib import Path

import pydot
from script import get_schema_from_csv


def rename_schema_table(table_name_from_foreign_key_field):
    """
    Some table names are labelled incorrectly in the foreign key fields. This is known behaviour for two tables:
    1. mapping_dmdpreparation.dmd_product_code_id in the 'medication_drug_record' table
    2. mkb_mapping_attribute.code_id in the 'patient' table
    """

    if table_name_from_foreign_key_field == "mapping_dmdpreparation":
        return "mkb_mapping_dmdpreparation"
    elif table_name_from_foreign_key_field == "mkb_mapping_attribute":
        return "mkb_mapping_attributes"


def main(input_file):
    emis_schema = get_schema_from_csv(input_file)

    graph = pydot.Dot("my_graph")
    graph.set_type("digraph")

    # List which holds the foreign key links between tables in tuples
    edges = []

    for table_name, table_content in emis_schema.items():
        """
        Example schema
        schema = {
                "patient": [
                    {
                        "Column": "patient_id",
                        "Type": "VARBINARY(16)",
                        "Primary Key": "Yes",
                        "Foreign Key": "",
                    },
                    {
                        "Column": "date_of_birth",
                        "Type": "timestamp(6)",
                        "Primary Key": "",
                        "Foreign Key": "",
                    },
                ],
                "medication": [
                    ...
                ],
            }

        """

        label = [table_name]

        for row in table_content:
            if row["Foreign Key"]:
                column_name = row["Column"]

                foreign_key = row["Foreign Key"].split(",")

                for key in foreign_key:
                    table, primary_key = key.split(".")

                    # Check that accurate table names were referenced in the foreign key fields.
                    if table.strip() not in emis_schema:
                        table = rename_schema_table(table.strip())

                    edges.append(
                        (
                            f"{table_name.strip()}:{column_name}",
                            f"{table.strip()}:{primary_key.strip()}",
                        )
                    )

            column_name = row["Column"]
            label.append(f"<{column_name}> {column_name}")

        # Organises the columns from top to bottom in a stacked structure: "{A | B | C | D}"
        full_label = "{" + "|".join(label) + "}"

        my_node = pydot.Node(table_name.strip(), label=full_label, shape="record")
        graph.add_node(my_node)

    # Add edges - foreign key links
    for from_table, to_table in edges:
        my_edge = pydot.Edge(from_table, to_table)
        graph.add_edge(my_edge)

    path = Path(__file__).parent / "schema_relationship_diagram.svg"
    graph.write_svg(path)


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "input_file", type=str, help="Raw file as received from EMIS for v2 backend"
    )
    args = parser.parse_args()

    main(args.input_file)


if __name__ == "__main__":
    run()
