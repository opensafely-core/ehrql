Note: all the below commands work by writing `just test` in place of `pytest`.  I personally prefer to go direct to pytest as I don't want the extra output that the Just wrapper generates, but feel free to use whatever your most comfortable with.

In any case, it is definitely worth getting to grips with pytest and not relying solely on the pre-baked handful of test runs available in the Justfile.

## Running only some of the tests

Running the full test suite is still a little slow.
Below are some ways of mitigating this by running only some of the tests.

At the most basic level you can run a specific directory of tests (e.g. all the "spec" tests):
```sh
pytest tests/spec
```

Or just a specific test file:
```sh
pytest tests/spec/series_ops/test_equality.py
```

Or just a specific test within a file:
```sh
pytest tests/spec/series_ops/test_equality.py::test_is_null
```

You can specify more than one of these test arguments together; e.g. this will run one spec test and all the unit tests:
```
pytest tests/spec/series_ops/test_equality.py::test_is_null tests/unit
```

One of the many nice features of pytest is that it will display the name of failed tests in a format which can be directly copied to the command line to run just that test e.g.
<pre><code>======================================== short test summary info ========================================
FAILED <strong>tests/unit/test_codes.py::test_codelist_from_csv_missing_column</strong>
 - AssertionError: Regex pattern did not match.
====================================== 1 failed, 4 passed in 0.03s ======================================
</code></pre>

This means you can copy and paste failing test names from the Github Actions output and run just those tests again locally.

It's also possible to run all the tests but skip those that run against MSSQL by using a [keyword expression](https://docs.pytest.org/en/6.2.x/usage.html#specifying-tests-selecting-tests):
```
pytest -k 'not mssql'
```

As this will still run the SQLite tests, and as most of the SQL generating machinery is common between the different query engines, this gives a fairly good balance between comprehensiveness and speed. Of course if you've been specifically working on the SQL generation then this test run will be inadequate. But for quick feedback on other sorts of change it can be quite helpful. And ultimately, CI has your back here.

It's also possible to combine the `-k` expression with all the other test selection mechanisms above. So for instance, to run the spec tests just on SQLite you can use:
```
pytest tests/spec -k sqlite
```

For further details on what the `-k` invocation is actually doing, see the [Parameterisation](#Parameterisation) section below.


## Coverage

Coverage issues can be the most frustrating part of the development process. Often you don't find out about them until you think you're done, having got things green locally and opened a PR. Fundamentally, it's only possible to get an accurate coverage report by running all the tests and, as discussed, that's annoyingly slow. However, it's possible to get faster feedback on whether specific tests provide coverage of specific bits of production code.

The magic incantation is:
<pre><code>pytest  --cov-report=html --cov=<strong>ehrql.some.module</strong> [... <em>rest of pytest arguments as usual</em> ...]
</code></pre>

Note that the argument to `--cov` is a dotted Python import path, not a file path. You can specify `--cov` multiple times if you want to check the coverage of multiple modules.

This will generate an HTML formatted report, which can be much easier to work with than the console output, at `htmlcov/index.html`. You should be able to open this directly in a browser using:
```
open htmlcov/index.html
```

(The URLs in the report are stable so once you've got the relevant page open you just have to refresh it to see updated reports; there's no need to go via the index again.)

Sometimes, when a PR fails through incomplete coverage, you know which tests you would expect to cover the code in question so you can use this approach to check coverage while running just those tests for much faster feedback.

Note that other parts of the module under test might be covered by parts of the test suite which you aren't running, so you're not aiming for 100% coverage of the module here: just concentrate on covering the parts of the code which weren't covered before.


## Parameterisation

You'll notice some test names appear with square brackets on the end:
```
tests/unit/test_file_formats.py::test_get_file_extension[None-.csv]
tests/unit/test_file_formats.py::test_get_file_extension[filename1-.txt]
tests/unit/test_file_formats.py::test_get_file_extension[filename2-.foo]
tests/unit/test_file_formats.py::test_get_file_extension[filename3-.txt.gz]
tests/unit/test_file_formats.py::test_get_file_extension[filename4-]
```

These indicate [parameterised](https://docs.pytest.org/en/6.2.x/parametrize.html) tests (or `parametrize`, as they insist on spelling it), which means that a single test function is called multiple times with different arguments.

Including the square brackets on the test name will run the specified test, with just the specified set of parameters:
```
pytest tests/unit/test_file_formats.py::test_get_file_extension[filename1-.txt]
```
(Don't spend any time trying to work out exactly how the text in the square brackets relates to the parameters in question. Pytest tries to do something vaguely sensible here, but in general you should just be copy/pasting from pytest output, not trying to craft `[filename4-]` by hand.)

In cases like the one above, the parameters only apply to one specific test and are defined right next to the test function, [like so](https://github.com/opensafely-core/databuilder/blob/6c73f9d55bdb8afdce9899411decb56e28347159/tests/unit/test_file_formats.py#L34-L45):
```py
@pytest.mark.parametrize(
    "filename,extension",
    [
        (None, ".csv"),
        (Path("a/b.c/file.txt"), ".txt"),
        (Path("a/b.c/file.txt.foo"), ".foo"),
        (Path("a/b.c/file.txt.gz"), ".txt.gz"),
        (Path("a/b.c/file"), ""),
    ],
)
def test_get_file_extension(filename, extension):
    assert get_file_extension(filename) == extension
```

But it's also possible to parameterise a fixture, meaning that any test which uses that fixture gets automatically parameterised over all the fixtures parameters. A good example of this is the ["engine" fixture](https://github.com/opensafely-core/databuilder/blob/6c73f9d55bdb8afdce9899411decb56e28347159/tests/conftest.py#L89-L117):
```py
QUERY_ENGINE_NAMES = ("in_memory", "sqlite", "mssql", "spark")

...

@pytest.fixture(params=QUERY_ENGINE_NAMES)
def engine(request):
    return engine_factory(request, request.param)
```
This fixture configures a query engine and an instance of the right type of database for that query engine to talk to. Because it is parameterised over all available query engines, any test which uses the `engine` fixture is automatically run against all the query engines.

For example, this test [here](https://github.com/opensafely-core/databuilder/blob/6c73f9d55bdb8afdce9899411decb56e28347159/tests/integration/test_query_engines.py#L6-L14) doesn't have any explicitly specified parameters:
```py
def test_handles_degenerate_population(engine):
    # Specifying a population of "False" is obviously silly, but it's more work to
    # identify and reject just this kind of silliness than it is to handle it gracefully
    engine.setup(metadata=sqlalchemy.MetaData())
    variables = dict(
        population=Value(False),
        v=Value(1),
    )
    assert engine.extract_qm(variables) == []
```

But when we run it we see it results in four tests, not one:
```console
$ pytest tests/integration/test_query_engines.py -v

========================================== test session starts ==========================================
tests/integration/test_query_engines.py::test_handles_degenerate_population[in_memory] PASSED      [ 25%]
tests/integration/test_query_engines.py::test_handles_degenerate_population[sqlite] PASSED         [ 50%]
tests/integration/test_query_engines.py::test_handles_degenerate_population[mssql] PASSED          [ 75%]
tests/integration/test_query_engines.py::test_handles_degenerate_population[spark] PASSED          [100%]

=========================================== 4 passed in 0.56s ===========================================
```

This approach is used most heavily in the spec tests to ensure that every test case is run against every query engine.

You'll notice that name of the engine (`in_memory`, `sqlite`, `mssql`) etc appears as the parameter name in square brackets. Using the `-k` argument to supply a [keyword expression](https://docs.pytest.org/en/6.2.x/usage.html#specifying-tests-selecting-tests) we can select just some of the query engines to run against e.g. to run the spec tests against just SQLite we can use:
```
pytest tests/spec -k sqlite
```
This works because the expression we supply is matched against the whole test name which includes the engine parameter.

You can build up more complex boolean expressions using standard Python syntax. For instance, this expression includes all tests _except_ those which use the sqlite or MSSQL engines:
```
pytest -k 'not sqlite and not mssql'
```
