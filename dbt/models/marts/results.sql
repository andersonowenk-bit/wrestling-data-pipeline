-- Winner and loser for every bout. This is what the Elo system reads.
select
    match_id, season, match_date, weight_class, event_type,
    wrestler_a_id, wrestler_b_id,
    winner_id,
    case when winner_id = wrestler_a_id then wrestler_b_id else wrestler_a_id end as loser_id,
    winner_id = wrestler_a_id as a_won,
    result_type,
    is_forfeit
from {{ ref('stg_matches') }}
