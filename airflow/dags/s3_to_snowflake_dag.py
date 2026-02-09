from __future__ import annotations

from datetime import datetime

from airflow import DAG
from airflow.models import Variable
from airflow.providers.snowflake.operators.snowflake import SnowflakeOperator
from airflow.providers.snowflake.transfers.s3_to_snowflake import S3ToSnowflakeOperator


def _get_variable(name: str, fallback: str) -> str:
    value = Variable.get(name, default_var=fallback)
    return value


with DAG(
    dag_id="s3_to_snowflake_demo",
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
    default_args={"owner": "airflow"},
    tags=["demo", "snowflake", "s3"],
) as dag:
    database = _get_variable("SNOWFLAKE_DATABASE", "DEMO_DB")
    schema = _get_variable("SNOWFLAKE_SCHEMA", "RAW")
    stage = _get_variable("SNOWFLAKE_STAGE", "DEMO_STAGE")
    table = _get_variable("SNOWFLAKE_TABLE", "EVENTS_RAW")
    s3_bucket = _get_variable("S3_BUCKET", "my-demo-bucket")
    s3_key = _get_variable("S3_KEY", "landing/events.csv")

    create_table = SnowflakeOperator(
        task_id="create_raw_table",
        snowflake_conn_id="snowflake_default",
        sql=f"""
        create table if not exists {database}.{schema}.{table} (
            event_id string,
            event_type string,
            event_timestamp timestamp_ntz,
            user_id string
        );
        """,
    )

    load_from_s3 = S3ToSnowflakeOperator(
        task_id="load_s3_to_snowflake",
        snowflake_conn_id="snowflake_default",
        s3_keys=[s3_key],
        s3_bucket=s3_bucket,
        table=table,
        stage=stage,
        schema=schema,
        database=database,
        file_format="(type = csv field_delimiter = ',' skip_header = 1)",
        copy_options=["ON_ERROR=CONTINUE"],
    )

    create_table >> load_from_s3
