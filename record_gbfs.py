"""Save one snapshot of the Bluebikes GBFS station status feed.

Run every 15 minutes by .github/workflows/record.yml. Each run writes one
gzipped CSV under data/status/YYYY/MM/DD/. Station information and pricing
rarely change, so they are saved once per day.
"""
import csv
import gzip
import json
import os
import time
import urllib.request
from datetime import datetime, timezone

BASE = "https://gbfs.lyft.com/gbfs/1.1/bos/en/"
STATUS_FIELDS = [
    "station_id", "legacy_id", "num_bikes_available", "num_ebikes_available",
    "num_bikes_disabled", "num_docks_available", "num_docks_disabled",
    "is_installed", "is_renting", "is_returning", "last_reported",
]
DAILY_FEEDS = ["station_information", "system_pricing_plans"]


def fetch(feed, tries=3):
    for i in range(tries):
        try:
            with urllib.request.urlopen(BASE + feed + ".json", timeout=30) as r:
                return json.load(r)
        except Exception:
            if i == tries - 1:
                raise
            time.sleep(10)


def main():
    now = datetime.now(timezone.utc)
    status = fetch("station_status")
    stations = status["data"]["stations"]

    out = os.path.join("data", "status", now.strftime("%Y/%m/%d"),
                       now.strftime("status_%Y%m%dT%H%MZ.csv.gz"))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with gzip.open(out, "wt", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["fetched_utc", "feed_last_updated"] + STATUS_FIELDS)
        for s in stations:
            w.writerow([now.isoformat(timespec="seconds"), status.get("last_updated")]
                       + [s.get(k, "") for k in STATUS_FIELDS])

    for feed in DAILY_FEEDS:
        path = os.path.join("data", feed, now.strftime("%Y-%m-%d") + ".json.gz")
        if not os.path.exists(path):
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with gzip.open(path, "wt", encoding="utf-8") as f:
                json.dump(fetch(feed), f)

    print(f"{out}: {len(stations)} stations, "
          f"{sum(s.get('num_ebikes_available', 0) for s in stations)} e-bikes docked")


if __name__ == "__main__":
    main()
