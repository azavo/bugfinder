import numpy as np
from shapely.geometry import Point
import rasterio
from rasterio.warp import transform

def get_ecoregion(lat, lon, ecoregions_gdf):
    point = Point(lon, lat)
    match = ecoregions_gdf[ecoregions_gdf.contains(point)]
    if len(match) > 0:
        return match.iloc[0]["US_L3NAME"]
    nearest_idx = ecoregions_gdf.distance(point).idxmin() 
    return ecoregions_gdf.loc[nearest_idx, "US_L3NAME"]

def get_land_cover(lat, lon, raster_path):
    with rasterio.open(raster_path) as src:
        xs, ys = transform("EPSG:4326", src.crs, [lon], [lat])
        value = list(src.sample([(xs[0], ys[0])]))[0][0]
    return int(value)

def time_features(dt):
    day_of_year = dt.timetuple().tm_yday
    return {
        "day_sin": np.sin(2 * np.pi * day_of_year / 365.25),
        "day_cos": np.cos(2 * np.pi * day_of_year / 365.25),
        "hour_sin": np.sin(2 * np.pi * dt.hour / 24.0),
        "hour_cos": np.cos(2 * np.pi * dt.hour / 24.0),
    }
