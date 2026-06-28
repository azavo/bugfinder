import requests
import time

_species_cache = {}
CACHE_TTL = 86400

def get_user_seen_species(username):
    now = time.time()
    if username in _species_cache and now - _species_cache[username][0] < CACHE_TTL:
        return _species_cache[username][1]

    seen = set()
    page = 1
    per_page = 500

    while True:
        resp = requests.get(
            "https://api.inaturalist.org/v1/observations/species_counts",
            params={"user_login": username, "per_page": per_page, "page": page},
            headers={"User-Agent": "your-app-name (your-contact)"}
        )
        data = resp.json()
        results = data.get("results", [])
        seen.update(r["taxon"]["name"] for r in results)

        total = data.get("total_results", 0)
        if len(seen) >= total or len(results) < per_page:
            break

        page += 1
        time.sleep(0.5)

    _species_cache[username] = (now, seen)
    return seen
