from __future__ import annotations

from datetime import datetime

from airflow import DAG
from airflow.models import Variable
import os

from airflow.providers.snowflake.operators.snowflake import SnowflakeOperator


def _get_variable(name: str, fallback: str) -> str:
    value = Variable.get(name, default_var=os.getenv(name, fallback))
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
    s3_bucket = _get_variable("S3_BUCKET", "snowflake-dbt-airflow")
    s3_key = _get_variable("S3_KEY", "sample_events.csv")
    aws_access_key_id = _get_variable("AWS_ACCESS_KEY_ID", "")
    aws_secret_access_key = _get_variable("AWS_SECRET_ACCESS_KEY", "")

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

    create_stage = SnowflakeOperator(
        task_id="create_external_stage",
        snowflake_conn_id="snowflake_default",
        sql=f"""
        create stage if not exists {database}.{schema}.{stage}
        url='s3://{s3_bucket}'
        credentials=(aws_key_id='{aws_access_key_id}' aws_secret_key='{aws_secret_access_key}')
        file_format=(type=csv field_delimiter=',' skip_header=1);
        """,
    )

    load_from_s3 = SnowflakeOperator(
        task_id="load_s3_to_snowflake",
        snowflake_conn_id="snowflake_default",
        sql=f"""
        copy into {database}.{schema}.{table}
        from @{database}.{schema}.{stage}/{s3_key}
        file_format=(type=csv field_delimiter=',' skip_header=1)
        on_error=continue;
        """,
    )

    create_table >> create_stage >> load_from_s3
