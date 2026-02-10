create or replace warehouse DEMO_WH warehouse_size = 'XSMALL' auto_suspend = 60;

create or replace database DEMO_DB;
create or replace schema DEMO_DB.RAW;
create or replace schema DEMO_DB.ANALYTICS;

create or replace stage DEMO_DB.RAW.DEMO_STAGE;

create or replace table DEMO_DB.RAW.EVENTS_RAW (
    event_id string,
    event_type string,
    event_timestamp timestamp_ntz,
    user_id string
);
