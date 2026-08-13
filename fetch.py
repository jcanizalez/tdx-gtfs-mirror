#!/usr/bin/env python3
"""Mirror Taiwan's national GTFS from TDX to a stable public URL.

TDX publishes one national GTFS covering every mode, but behind an OAuth2
client-credentials gate that community fetchers (Transitous) can't speak.
The data's license (Taiwan OGDL, attribution required) permits
redistribution — so this script does the token dance once a day and
republishes the zip where a plain HTTP GET can reach it.

Publishes the feed untouched: Transitous asked to keep the fare tables
(they may implement fares support), so nothing is stripped anymore.

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


def main() -> None:
    token = get_token()
    raw = fetch_gtfs(token)
    with open("tw-gtfs.zip", "wb") as f:
        f.write(raw)
    print(f"fetched and published {len(raw)} bytes untouched", file=sys.stderr)


if __name__ == "__main__":
    main()
