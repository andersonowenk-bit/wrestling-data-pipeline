-- Match volume per weight class per season.
select
    weight_class,
    season,
    count(*)                              as matches,
    sum(case when is_forfeit then 1 else 0 end) as forfeits,
    sum(case when result_type = 'FALL' then 1 else 0 end) as falls
from {{ ref('stg_matches') }}
group by weight_class, season
order by weight_class, season
