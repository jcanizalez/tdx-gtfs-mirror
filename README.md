# tdx-gtfs-mirror

Daily mirror of Taiwan's national GTFS feed from [TDX](https://tdx.transportdata.tw)
(Transport Data eXchange, Ministry of Transportation and Communications) to a
stable, keyless URL:

```
https://github.com/jcanizalez/tdx-gtfs-mirror/releases/download/latest/tw-gtfs.zip
```

## Why

TDX publishes one excellent national GTFS covering every mode — TRA, THSR,
metros, city and intercity buses — but behind an OAuth2 client-credentials
gate. Community routing projects like [Transitous](https://transitous.org)
fetch feeds with plain HTTP and therefore can't consume it, which is why
Taiwan has been missing from their coverage.

The data's license ([TDX terms](https://tdx.transportdata.tw/term), Taiwan's
Open Government Data License) permits redistribution with attribution, so this
repository does the token dance once a day and republishes the zip. The
oversized GTFS-Fares v2 tables are stripped (as Transitland's fetcher also
does) — they dwarf the rest of the feed and no consumer reads them.

## Attribution

Data: Ministry of Transportation and Communications Transportation Data
Circulation Service Platform (TDX), Taiwan. This mirror adds nothing and
removes only the Fares v2 tables.

## Setup (for forks)

1. Register a free TDX account and create an API key (Client ID + Secret).
2. Set repository secrets `TDX_CLIENT_ID` and `TDX_CLIENT_SECRET`.
3. The `Mirror TDX GTFS` workflow runs daily at 03:30 Taipei time; run it
   manually once from the Actions tab to seed the release.
