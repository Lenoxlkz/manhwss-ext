#!/usr/bin/env python3
"""Generate the Mihon/Aniyomi extension repository files from the build artifacts.

Outputs (in the repo output dir, pushed to the `repo` branch):
- apk/<name>.apk, jar/<name>.jar      downloadable artifacts
- icon/<package>.png                  legacy icon (Mihon resolves icon/<pkg>.png)
- index.min.json                      legacy flat index (Mihon 0.15/0.16, Aniyomi)
- index.json / index.pb               structured store (v2, current Mihon/Komikku)
- repo.json                           entry point that points at index.pb
- index.html                          human readable APK list
"""

import gzip
import json
import sys
from pathlib import Path

import index_pb2
from google.protobuf import json_format

ARTIFACTS_DIR = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("artifacts")
REPO_DIR = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("repo")

# Repo source tree (checked out next to this working directory), for the icon
MAIN_DIR = Path(__file__).resolve().parents[2]

import os  # noqa: E402

GITHUB_REPOSITORY = os.environ["GITHUB_REPOSITORY"]  # owner/name
REPO_RAW_BASE = f"https://raw.githubusercontent.com/{GITHUB_REPOSITORY}/repo"

REPO_NAME = "ManhwaSS Ext"
BADGE_LABEL = "MSS"
WEBSITE = f"https://github.com/{GITHUB_REPOSITORY}"

CONTENT_WARNING_JSON = {
    1: "CONTENT_WARNING_SAFE",
    2: "CONTENT_WARNING_MIXED",
    3: "CONTENT_WARNING_NSFW",
}


def read_info(info_file: Path):
    with info_file.open(encoding="utf-8") as f:
        return json.load(f)


def main() -> None:
    fingerprint = (ARTIFACTS_DIR / "fingerprint.txt").read_text().strip()

    info_files = sorted(ARTIFACTS_DIR.rglob("keiyoushi-source-info.json"))
    if not info_files:
        raise SystemExit("No keiyoushi-source-info.json found in artifacts")

    REPO_DIR.mkdir(parents=True, exist_ok=True)

    proto_extensions = []
    legacy_entries = []

    for info_file in info_files:
        info = read_info(info_file)
        apk = next((info_file.parent / "outputs/apk/release").glob("*.apk"), None)
        jar = next((info_file.parent / "outputs/jar/release").glob("*.jar"), None)
        if apk is None:
            raise SystemExit(f"{info['packageName']}: no release apk found")

        module_dir = MAIN_DIR / f"src/{info['module'].replace('.', '/')}"
        icon_src = module_dir / "res/mipmap-xhdpi/ic_launcher.png"
        icon_name = f"{info['packageName']}.png"

        # Host artifacts in the branch itself
        (REPO_DIR / "apk").mkdir(exist_ok=True)
        (REPO_DIR / "jar").mkdir(exist_ok=True)
        (REPO_DIR / "icon").mkdir(exist_ok=True)
        (REPO_DIR / "apk" / apk.name).write_bytes(apk.read_bytes())
        if jar is not None:
            (REPO_DIR / "jar" / jar.name).write_bytes(jar.read_bytes())
        if icon_src.exists():
            (REPO_DIR / "icon" / icon_name).write_bytes(icon_src.read_bytes())

        apk_url = f"{REPO_RAW_BASE}/apk/{apk.name}"
        jar_url = f"{REPO_RAW_BASE}/jar/{jar.name}" if jar is not None else ""
        icon_url = f"{REPO_RAW_BASE}/icon/{icon_name}"

        proto_extensions.append(
            index_pb2.Extension(
                name=info["name"],
                packageName=info["packageName"],
                resources=index_pb2.Resources(apkUrl=apk_url, iconUrl=icon_url, jarUrl=jar_url),
                extensionLib=info["extensionLib"],
                versionCode=int(info["versionCode"]),
                versionName=info["versionName"],
                contentWarning=int(info["contentWarning"]),
                sources=[
                    index_pb2.Source(
                        id=int(source["id"]),
                        name=source["name"],
                        language=source["lang"],
                        homeUrl=source["baseUrl"],
                        mirrorUrls=source.get("mirrorUrls", []),
                    )
                    for source in info["sources"]
                ],
            ),
        )

        legacy_entries.append(
            {
                "name": info["name"],
                "pkg": info["packageName"],
                "apk": apk.name,
                "lang": info["sources"][0]["lang"],
                "code": int(info["versionCode"]),
                "version": info["versionName"],
                # Legacy schema only knows safe/not-safe; mixed counts as not safe
                "nsfw": 1 if int(info["contentWarning"]) >= 2 else 0,
                "sources": [
                    {
                        "id": str(source["id"]),
                        "lang": source["lang"],
                        "name": source["name"],
                        "baseUrl": source["baseUrl"],
                    }
                    for source in info["sources"]
                ],
            },
        )

    proto_extensions.sort(key=lambda e: e.packageName)
    legacy_entries.sort(key=lambda e: e["pkg"])

    index = index_pb2.Index(
        name=REPO_NAME,
        badgeLabel=BADGE_LABEL,
        signingKey=fingerprint,
        contact=index_pb2.Contact(website=WEBSITE),
        extensionList=index_pb2.ExtensionList(extensions=proto_extensions),
    )

    with (REPO_DIR / "index.json").open("w", encoding="utf-8") as f:
        f.write(
            json_format.MessageToJson(
                index,
                always_print_fields_with_no_presence=False,
                preserving_proto_field_name=True,
            ),
        )

    with (REPO_DIR / "index.pb").open("wb") as f:
        f.write(gzip.compress(index.SerializeToString(deterministic=True), mtime=0))

    with (REPO_DIR / "index.min.json").open("w", encoding="utf-8") as f:
        json.dump(legacy_entries, f, ensure_ascii=False, indent=2)
        f.write("\n")

    with (REPO_DIR / "repo.json").open("w", encoding="utf-8") as f:
        json.dump(
            {
                "index_v2": f"{REPO_RAW_BASE}/index.pb",
                "meta": {
                    "name": REPO_NAME,
                    "shortName": BADGE_LABEL,
                    "website": WEBSITE,
                    "signingKeyFingerprint": fingerprint,
                },
            },
            f,
            ensure_ascii=False,
            indent=2,
        )
        f.write("\n")

    import html

    with (REPO_DIR / "index.html").open("w", encoding="utf-8") as f:
        f.write('<!DOCTYPE html>\n<html>\n<head>\n<meta charset="UTF-8">\n<title>apks</title>\n</head>\n<body>\n<pre>\n')
        for ext in proto_extensions:
            apk_escaped = html.escape(ext.resources.apkUrl)
            name_escaped = html.escape(f"Tachiyomi: {ext.name}")
            f.write(f'<a href="{apk_escaped}">{name_escaped}</a>\n')
        f.write("</pre>\n</body>\n</html>\n")

    print(f"Published {len(proto_extensions)} extension(s) to {REPO_DIR}")


if __name__ == "__main__":
    main()
