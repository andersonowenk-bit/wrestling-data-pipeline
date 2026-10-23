-- One row per bout, keyed by wrestler ids.
select
    match_id, season, match_date, event, event_type, weight_class,
    wrestler_a_id, team_a, wrestler_b_id, team_b,
    result_type, score_a, score_b, is_forfeit
from {{ ref('stg_matches') }}
