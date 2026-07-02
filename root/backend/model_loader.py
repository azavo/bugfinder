from pathlib import Path
import urllib.request
import zipfile
import joblib
import geopandas as gpd

BASE_DIR = Path(__file__).resolve().parent
PKL_DIR = Path("/data/pkls")
GEO_DIR = Path("/data/geo")
PKL_DIR.mkdir(exist_ok=True, parents=True)
GEO_DIR.mkdir(exist_ok=True, parents=True)

RELEASE_BASE = "https://github.com/azavo/insecttargets_2.0/releases/download/v1.0.0"

def download_if_missing(filename, dest_path, unzip_to=None, tmp_dir=None):
    if dest_path.exists():
        return
    print(f"Downloading {filename}...")
    url = f"{RELEASE_BASE}/{filename}"
    save_dir = tmp_dir if tmp_dir else dest_path.parent
    tmp = save_dir / filename
    urllib.request.urlretrieve(url, tmp)
    if unzip_to:
        print(f"Unzipping {filename}...")
        with zipfile.ZipFile(tmp, 'r') as z:
            z.extractall(unzip_to)
        tmp.unlink()
    print(f"Done: {filename}")

for filename in ["gb_model.pkl", "gb_label_encoder.pkl", "gb_cat_categories.pkl",
                  "common_names.pkl", "order_map.pkl"]:
    download_if_missing(filename, PKL_DIR / filename)

download_if_missing("ecoregions.zip",
                     GEO_DIR / "us_eco_l3" / "us_eco_l3.shp",
                     unzip_to=GEO_DIR,
                     tmp_dir=GEO_DIR)

download_if_missing("nlcd_clip.tif", GEO_DIR / "nlcd_clip.tif")

MODEL = joblib.load(PKL_DIR / "gb_model.pkl")
LABEL_ENCODER = joblib.load(PKL_DIR / "gb_label_encoder.pkl")
CAT_CATEGORIES = joblib.load(PKL_DIR / "gb_cat_categories.pkl")
COMMON_NAMES = joblib.load(PKL_DIR / "common_names.pkl")
ORDER_MAP = joblib.load(PKL_DIR / "order_map.pkl")

ECOREGIONS = gpd.read_file(GEO_DIR / "us_eco_l3" / "us_eco_l3.shp").to_crs("EPSG:4326")
NLCD_RASTER_PATH = str(GEO_DIR / "nlcd_clip.tif")

FEATURE_ORDER = [
    "hourly_temp_C", "hourly_humidity_percent", "soil_temp_C",
    "cloud_cover_pct", "snow_depth_m", "precip_type",
    "hour_sin", "hour_cos", "day_sin", "day_cos",
    "ecoregion", "land_cover_code"
]

def get_common_name(species):
    return COMMON_NAMES.get(species, species)

def get_order(species):
    return ORDER_MAP.get(species, "Unknown")
