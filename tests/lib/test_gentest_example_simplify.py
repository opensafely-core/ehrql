import textwrap

from tests.lib.gentest_example_simplify import simplify


# Basic smoketest as a crude guard against breakage
def test_gentest_example_simplify():
    example = textwrap.dedent(
        """\
        # As copied directly from Hypothesis output
          population=AggregateByPatient.Exists(
              SelectPatientTable("p0", TableSchema(i1=Column(int)))
          ),
          variable=Negate(
              SelectColumn(
                  SelectPatientTable("p0", TableSchema(i1=Column(int))), "i1"
              )
          )
          data=[
              {"type": data_setup.P0, "patient_id": 1},
          ],
        """
    )
    result = simplify(example)
    assert "variable = Function.Negate(p0_i1)" in result
