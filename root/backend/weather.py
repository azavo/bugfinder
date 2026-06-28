import requests
import pandas as pd
from datetime import datetime, timezone

WEATHER_VARS = "temperature_2m,relative_humidity_2m,cloud_cover,precipitation,snow_depth,soil_temperature_0cm"

_weather_cache = {}

def get_weather_for_datetime(lat, lon, dt: datetime):
    cache_key = (round(lat, 2), round(lon, 2), dt.strftime("%Y-%m-%d-%H"))
    if cache_key in _weather_cache:
        return _weather_cache[cache_key]

    now = datetime.now(timezone.utc)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)  # treat naive input as UTC
    days_offset = (dt - now).days

    if days_offset > 16:
        result = _historical_average(lat, lon, dt)
    elif days_offset >= -5:
        result = _fetch_timeseries(lat, lon, dt, "https://api.open-meteo.com/v1/forecast",
                                    {"past_days": 5, "forecast_days": 16})
    else:
        result = _fetch_timeseries(lat, lon, dt, "https://archive-api.open-meteo.com/v1/archive",
                                    {"start_date": dt.date().isoformat(), "end_date": dt.date().isoformat()})

    _weather_cache[cache_key] = result
    return result

def _fetch_timeseries(lat, lon, dt, url, extra_params):
    params = {"latitude": lat, "longitude": lon, "hourly": WEATHER_VARS, "timezone": "UTC", **extra_params}
    data = requests.get(url, params=params).json()["hourly"]

    times = pd.to_datetime(data["time"])
    idx = abs(times - dt.replace(tzinfo=None)).argmin()

    return {
        "hourly_temp_C": data["temperature_2m"][idx],
        "hourly_humidity_percent": data["relative_humidity_2m"][idx],
        "cloud_cover_pct": data["cloud_cover"][idx],
        "snow_depth_m": data["snow_depth"][idx] or 0,
        "soil_temp_C": data["soil_temperature_0cm"][idx] if data["soil_temperature_0cm"][idx] is not None else data["temperature_2m"][idx],
        "precip_mm": data["precipitation"][idx] or 0,
        "is_estimate": False,
    }

def _historical_average(lat, lon, dt, years_back=5):
    samples = []
    for y in range(1, years_back + 1):
        try:
            past_dt = dt.replace(year=dt.year - y)
        except ValueError:
            continue
        samples.append(_fetch_timeseries(lat, lon, past_dt, "https://archive-api.open-meteo.com/v1/archive",
                                          {"start_date": past_dt.date().isoformat(), "end_date": past_dt.date().isoformat()}))

    avg = {k: sum(s[k] for s in samples) / len(samples) for k in samples[0] if k != "is_estimate"}
    avg["is_estimate"] = True
    return avg

def precip_phase(temp_c, precip_mm):
    if precip_mm <= 0:
        return "none"
    elif temp_c < 0:
        return "snow"
    elif temp_c < 2:
        return "mixed/freezing"
    return "rain"