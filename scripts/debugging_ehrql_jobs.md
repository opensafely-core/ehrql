# Debugging ehrQL jobs

The script at `scripts/run-debug.sh` allows you to run ehrQL using the production Docker container with a local
ehrQL checkout.

## Running the script

Inside the backend, as your user, in a local checkout of ehrql:

1) Check out the branch you want to run

1) Create a file at `scripts/environ.env` with any required environment variables. This **MUST** use your personal
   DB credentials. See documentation in the script for the minimum required variables.

1) Clone and `cd` to the study repo you want to run

1) Run the script with the usual ehrQL arguments, e.g.
   ```
   ../ehrql/scripts/run-debug.sh generate-dataset analysis/dataset_definition.py --output test.arrow'
   ```

By default, the script runs the container in the background and tails the logs.


## Persisting log files

Once the job is done, persist the log file with:

```
docker logs --timestamps <constainer id> >& logs.log
```

(If you want to [send the logs to honeycomb](#sending-log-data-to-honeycomb), do this as the opensafely user so the file has the correct permissions.)


## Sending log data to honeycomb

We can parse the log file and send it up to honeycomb using job-runner's [ehrql_log_telemetry](https://github.com/opensafely-core/job-runner/blob/main/agent/cli/ehrql_log_telemetry.py) command.

Note: the log file needs to exist at a location that is [mounted into the job-runner container](https://github.com/opensafely-core/backend-server/blob/main/services/jobrunner/docker-compose.yaml#L29), e.g. `/srv/high_privacy`.

As the opensafely user:

```
just jobrunner/cli ehrql_log_telemetry \
    <temp honeycomb dataset> \  # a named dataset for these debug traces (doesn't have to exist already)
    <path/to/log/file>  \  # the path inside the docker container (/srv/high_privacy is mounted to the same path inside the container)
    <ehrql operation>  \  # generate-dataset or generate-measures
    --workspace  \  # optional name of workspace
    --commit  \  # optional commit
    --action  \  # optional name of action
    --attrs a=b c=d ... # optional; any additional attributes you want to trace, in k=v pairs
```

This command parses the log file using the script at `scripts/parse_logs.py` and then traces the queries from the log. The root span is named
using the ehrql operation passed to the command. In honeycomb, query by `name = ehrql.<operation>` to find the top-level span that encompasses
all the queries for this job.
