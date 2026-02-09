with source as (
    select
        event_id,
        event_type,
        event_timestamp,
        user_id
    from {{ source('raw', 'events_raw') }}
)

select * from source
