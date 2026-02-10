# Snowflake + S3 + Airflow + dbt Demo

This repo provides a local development setup to orchestrate loading data from S3 into Snowflake using Apache Airflow, then model it with dbt.

## Prerequisites

- Docker + Docker Compose
- AWS account with an S3 bucket
- Snowflake account (trial is fine)
- (Optional) dbt CLI locally if you want to run dbt outside Airflow

## Quick start

1. **Clone the repo**
   ```bash
   git clone <YOUR_GIT_URL>
   cd Snowflake-S3-Airflow-Dbt-Demo
   ```

2. **Create your environment file**
   ```bash
   cp .env.example .env
   ```
   Update `.env` with your values.

3. **Start Airflow**
   ```bash
   docker compose up airflow-init
   docker compose up
   ```

4. **Open Airflow UI**
   - Default URL: `http://localhost:8081`
   - If you prefer 8080, set `AIRFLOW_HOST_PORT=8080` in `.env` and open `http://localhost:8080`
   - You can confirm the mapped port with:
     ```bash
     docker compose port airflow-webserver 8080
     ```
   - Default user/pass: `airflow` / `airflow`

5. **Configure Airflow connections**
   Create these connections in the Airflow UI or via environment variables:
   - `aws_default` (type: Amazon Web Services)
   - `snowflake_default` (type: Snowflake)

   Example environment variables (set in `.env`):
   ```bash
   AIRFLOW_CONN_AWS_DEFAULT=aws://<AWS_ACCESS_KEY_ID>:<AWS_SECRET_ACCESS_KEY>@/?region_name=<AWS_REGION>
   AIRFLOW_CONN_SNOWFLAKE_DEFAULT=snowflake://<USER>:<PASSWORD>@<ACCOUNT>/<DATABASE>/<SCHEMA>?warehouse=<WAREHOUSE>&role=<ROLE>
   ```

6. **Run the DAG**
   - Enable and trigger `s3_to_snowflake_demo` in Airflow.
   - Ensure `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` are set in `.env` (used to create the Snowflake external stage).

## Snowflake setup

Run the SQL in `scripts/snowflake_setup.sql` to create the database, schema, warehouse, and a landing table.

```bash
snowsql -a <ACCOUNT> -u <USER> -f scripts/snowflake_setup.sql
```

## AWS S3 setup

1. Create a bucket (e.g., `snowflake-dbt-airflow`)
2. Upload sample data (CSV) to `s3://snowflake-dbt-airflow/sample_events.csv`

Sample CSV headers expected by the demo (see `data/sample_events.csv`):
```
event_id,event_type,event_timestamp,user_id
```

## dbt setup (optional local run)

1. Install dbt Snowflake adapter:
   ```bash
   pip install dbt-snowflake
   ```

2. Create a dbt profile:
   ```bash
   mkdir -p ~/.dbt
   cp dbt/profiles.yml.example ~/.dbt/profiles.yml
   ```

3. Run dbt:
   ```bash
   cd dbt
   dbt debug
   dbt run
   ```

## Project layout

```
airflow/                 # Airflow Docker image + DAGs
dbt/                     # dbt project
scripts/                 # Snowflake setup SQL
docker-compose.yml       # Local Airflow stack
```

## Next steps

Once you have Snowflake and AWS set up, update `.env`, set your Airflow connections, and trigger the DAG. If you want me to tailor the setup to your specific Snowflake account or AWS bucket conventions, share those details and I can refine the configs.


## Troubleshooting

- If browser cannot open Airflow UI, run `docker compose ps` and check the `PORTS` column for `airflow-webserver` (for example `0.0.0.0:8081->8080/tcp` (or another host port)).
- The warning `the attribute `version` is obsolete` comes from Docker Compose V2 when a `version` field is present. This repo omits `version` to avoid that warning.
- Long lists of `SyntaxWarning` messages from provider libraries during startup are non-fatal if webserver later shows `Listening at: http://0.0.0.0:8080`.
