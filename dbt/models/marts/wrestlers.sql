-- One row per wrestler. Tracks teams and weight class changes across seasons.
with appearances as (
    select wrestler_a_id as wrestler_id, wrestler_a as wrestler_name, team_a as team,
           weight_class, season, match_date
    from {{ ref('stg_matches') }}
    union all
    select wrestler_b_id, wrestler_b, team_b, weight_class, season, match_date
    from {{ ref('stg_matches') }}
)

select
    wrestler_id,
    any_value(wrestler_name)                         as wrestler_name,
    arg_max(team, match_date)                        as current_team,
    arg_max(weight_class, match_date)                as current_weight_class,
    mode(weight_class)                               as primary_weight_class,
    count(distinct weight_class)                     as weight_classes_competed,
    min(season)                                      as first_season,
    max(season)                                      as last_season,
    count(*)                                         as matches_wrestled
from appearances
group by wrestler_id
