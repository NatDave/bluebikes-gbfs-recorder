# Bluebikes GBFS recorder

Saves the Bluebikes station status feed every 15 minutes, so there is a record of how many
classic bikes, e-bikes and empty docks each station had over time. Bluebikes only publishes
this feed live; there is no official history.

Started 2026-11-03 for the PPUA 5263 final project (where Bluebikes e-bike riding grew, and
whether e-bike supply explains it).

## What gets saved

| Path | What | How often |
|---|---|---|
| `data/status/YYYY/MM/DD/status_YYYYMMDDTHHMMZ.csv.gz` | one row per station: bikes, e-bikes, disabled bikes, docks, renting/returning flags | every run |
| `data/station_information/YYYY-MM-DD.json.gz` | station names, locations, capacity, IDs | once a day |
| `data/system_pricing_plans/YYYY-MM-DD.json.gz` | prices as published in the feed | once a day |

Times are UTC. `fetched_utc` is when the snapshot was taken; `feed_last_updated` is the
feed's own Unix timestamp. `station_id` is the feed's own ID; to match the trip files, join to
`station_information`, whose `short_name` is the trip-file station ID (e.g. `L32004`).

Source: https://gbfs.bluebikes.com/gbfs/gbfs.json (station status:
https://gbfs.lyft.com/gbfs/1.1/bos/en/station_status.json).

## Keep this repo private

The Bluebikes Data License Agreement (https://bluebikes.com/data-license-agreement) does not
allow publishing the data as a stand-alone dataset. Using it in published analyses is fine.

## Notes

- Schedule: `*/15 * * * *` in `.github/workflows/record.yml`. GitHub can delay or skip
  scheduled runs when it is busy, so expect some uneven gaps.
- Each run bills about 1 minute. 96 runs a day is about 2,900 minutes a month, just under the
  3,000 private-repo minutes on GitHub Pro / Education. Don't shorten the interval.
- To stop recording: Actions tab, "Record Bluebikes station status", Disable workflow.
- Run once by hand: Actions tab, Run workflow (or `gh workflow run record.yml`).
- Get the data locally: `git pull`, then read the CSVs with pandas (`pd.read_csv(path)`
  handles `.gz`).
