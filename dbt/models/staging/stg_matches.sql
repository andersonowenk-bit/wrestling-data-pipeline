-- Clean, standardized match rows. One row per bout.
-- Handles: name variations (via alias seed), casing, forfeits.
with src as (
    select * from {{ source('raw', 'matches') }}
),

aliases as (
    select alias, canonical_name from {{ ref('name_aliases') }}
),

cleaned as (
    select
        cast(s.season as integer)                         as season,
        cast(s.match_date as date)                        as match_date,
        trim(s.event)                                     as event,
        lower(trim(s.event_type))                         as event_type,
        cast(s.weight_class as integer)                   as weight_class,
        coalesce(a1.canonical_name, trim(s.wrestler_a))   as wrestler_a,
        trim(s.team_a)                                    as team_a,
        coalesce(a2.canonical_name, trim(s.wrestler_b))   as wrestler_b,
        trim(s.team_b)                                    as team_b,
        coalesce(a3.canonical_name, trim(s.winner))       as winner,
        upper(trim(s.result_type))                        as result_type,
        try_cast(s.score_a as integer)                    as score_a,
        try_cast(s.score_b as integer)                    as score_b
    from src s
    left join aliases a1 on trim(s.wrestler_a) = a1.alias
    left join aliases a2 on trim(s.wrestler_b) = a2.alias
    left join aliases a3 on trim(s.winner)     = a3.alias
)

select
    md5(concat_ws('|', season, match_date, event, weight_class, wrestler_a, wrestler_b)) as match_id,
    md5(lower(wrestler_a)) as wrestler_a_id,
    md5(lower(wrestler_b)) as wrestler_b_id,
    md5(lower(winner))     as winner_id,
    *,
    result_type = 'FOR'    as is_forfeit
from cleaned
