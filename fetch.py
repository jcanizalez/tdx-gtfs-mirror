#!/usr/bin/env python3
"""Mirror Taiwan's national GTFS from TDX to a stable public URL.

TDX publishes one national GTFS covering every mode, but behind an OAuth2
client-credentials gate that community fetchers (Transitous) can't speak.
The data's license (Taiwan OGDL, attribution required) permits
redistribution — so this script does the token dance once a day and
republishes the zip where a plain HTTP GET can reach it.

Keeps GTFS-Fares v1 (fare_attributes/fare_rules — Transitous may implement
support) and strips only the Fares v2 tables, which alone are ~300 MB of the
zip and which Transitland's own TDX fetcher also drops. Untouched the zip is
435 MB; with v2 stripped it is 127 MB.

Needs TDX_CLIENT_ID / TDX_CLIENT_SECRET in the environment.
"""
import io
import os
import sys
import urllib.parse
import urllib.request
import zipfile

TOKEN_URL = "https://tdx.transportdata.tw/auth/realms/TDXConnect/protocol/openid-connect/token"
GTFS_URL = "https://tdx.transportdata.tw/api/gtfs/V3/Map/GTFS/Static"
USER_AGENT = "tdx-gtfs-mirror/0.1 (+https://github.com/jcanizalez/tdx-gtfs-mirror)"


def get_token() -> str:
    body = urllib.parse.urlencode(
        {
            "grant_type": "client_credentials",
            "client_id": os.environ["TDX_CLIENT_ID"],
            "client_secret": os.environ["TDX_CLIENT_SECRET"],
        }
    ).encode()
    req = urllib.request.Request(
        TOKEN_URL,
        data=body,
        headers={"Content-Type": "application/x-www-form-urlencoded", "User-Agent": USER_AGENT},
    )
    with urllib.request.urlopen(req, timeout=60) as res:
        import json

        return json.load(res)["access_token"]


def fetch_gtfs(token: str) -> bytes:
    req = urllib.request.Request(
        GTFS_URL,
        headers={"Authorization": f"Bearer {token}", "User-Agent": USER_AGENT},
    )
    with urllib.request.urlopen(req, timeout=600) as res:
        return res.read()


# GTFS-Fares v2 tables; v1 stays in the feed.
DROP_TABLES = {"fare_leg_rules.txt", "fare_transfer_rules.txt", "fare_products.txt"}


def strip_fares_v2(raw: bytes) -> bytes:
    src = zipfile.ZipFile(io.BytesIO(raw))
    out_buf = io.BytesIO()
    with zipfile.ZipFile(out_buf, "w", zipfile.ZIP_DEFLATED) as out:
        for info in src.infolist():
            if info.filename in DROP_TABLES:
                continue
            out.writestr(info, src.read(info))
    return out_buf.getvalue()


def main() -> None:
    token = get_token()
    raw = fetch_gtfs(token)
    slim = strip_fares_v2(raw)
    with open("tw-gtfs.zip", "wb") as f:
        f.write(slim)
    print(f"fetched {len(raw)} bytes, published {len(slim)} bytes (fares v1 kept)", file=sys.stderr)


if __name__ == "__main__":
    main()
