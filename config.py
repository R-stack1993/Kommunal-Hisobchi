# config.py
import datetime
import calendar

# O'zbekistondagi tabaqalashtirilgan (ijtimoiy norma) tariflar.
TARIFFS = {
    'elektr': [
        (200, 650),
        (500, 900),
        (1000, 1100),
        (5000, 1600),
        (10000, 1900),
        (float('inf'), 2200)
    ],
    'gaz_isitish': [
        (500, 1100),
        (2500, 2000),
        (5000, 2300),
        (10000, 2700),
        (float('inf'), 3300)
    ],
    'gaz_oddiy': [
        (100, 1100),
        (2500, 2000),
        (5000, 2300),
        (10000, 2700),
        (float('inf'), 3300)
    ]
}

def is_heating_season(month: int) -> bool:
    return month in [11, 12, 1, 2]

def calculate_tiered_cost(usage: float, utility_type: str) -> tuple[float, str]:
    cost = 0.0
    remaining_usage = usage
    season_info = ""
    
    if utility_type == 'gaz':
        current_month = datetime.datetime.now().month
        if is_heating_season(current_month):
            tiers = TARIFFS.get('gaz_isitish', [])
            season_info = "Isitish mavsumi tarifi"
        else:
            tiers = TARIFFS.get('gaz_oddiy', [])
            season_info = "Oddiy mavsum tarifi"
    else:
        tiers = TARIFFS.get(utility_type, [])
    
    previous_limit = 0
    for limit, price in tiers:
        tier_capacity = limit - previous_limit
        if remaining_usage <= tier_capacity:
            cost += remaining_usage * price
            break
        else:
            cost += tier_capacity * price
            remaining_usage -= tier_capacity
        previous_limit = limit
        
    return cost, season_info

def get_days_in_month(year: int, month: int) -> int:
    return calendar.monthrange(year, month)[1]