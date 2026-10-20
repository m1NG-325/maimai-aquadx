# AquaSync 2.1

[中文](README-2.1.md) · English

A Windows desktop app for viewing maimai scores from AquaDX maimai2 JSON exports or LXNS score CSV exports. Browse scores, B50, plate progress and improvement recommendations locally.

> Release candidate: the 2.1 installer and portable package are prepared locally. The GitHub Release is awaiting approval.

## Getting started

1. After release, download either `AquaSync-2.1-Setup.exe` or `AquaSync-2.1-Portable.zip` from [Releases](https://github.com/m1NG-325/maimai-aquadx/releases).
2. Install the app, or extract the complete portable archive and run `AquaSync.exe`. Keep the `_internal` folder.
3. Choose a local player ID, click **导入 AquaDX JSON** or **导入落雪 CSV**, and select your export.

Supports 64-bit Windows 10/11. Packaged versions do not require Python. Ordinary viewing and analysis work offline. The interface remains Chinese.

## Changes in 2.1

- Import LXNS CSV scores, retaining achievements, DX score, FC/FS and available play times.
- LXNS CSV imports open the estimated LXNS B50 view by default.
- Center the LXNS synchronization table text and narrow its selection column to fit its contents.
- Remove unused runtime dependencies. The `_internal` directory is approximately 65.7 MiB smaller than in 2.0.
- Keep the same image assets, dimensions and quality as 2.0, without re-encoding or requiring online asset downloads.

## Features

B50 and B50 comparison; score search, sorting and chart details; shared song metadata; plate progress; separate private-server and Chinese-server recommendations; Rating calculators; play history and judgement analysis; Rating and achievement trends; maps, characters, courses and login bonuses; player profiles and collections; local tools; LXNS backups and selected-difference synchronization; Diving-Fish/LXNS JSON export; and data-directory migration.

History, profiles and progression views require the corresponding records in an AquaDX export. LXNS CSV contains scores only: it does not supply full player profiles, original B50 groups, play logs or collection archives. Its B50 is estimated from local metadata. Upload timestamps are not treated as play times.

## Data and updates

- Importing replaces the selected local player's snapshot. Use a separate local player ID for LXNS CSV if you want to retain a complete AquaDX archive.
- Imports stay local and do not upload scores automatically. Review the account and selected changes before synchronization.
- Local data defaults to `user-data` beside the app, with `AquaSync-desktop.json` storing the data-directory setting.
- Close the app before updating. Preserve both the data directory and configuration file. The installer supports in-place upgrades and preserves personal data on uninstall.
- Reference chart constants and progress calculations may differ from the actual game version.

[Desktop guide (Chinese)](docs/DESKTOP.md) · [2.1 changelog (Chinese)](docs/CHANGELOG-2.1.md) · [Sources and algorithms](docs/ALGORITHMS_AND_SOURCES.md)

## Credits

[AquaDX](https://github.com/MewoLab/AquaDX), [KarenBot](https://github.com/xszqxszq/KarenBot), [LXNS](https://maimai.lxns.net/), [Diving-Fish](https://www.diving-fish.com/maimaidx/prober/), [Otoge DB](https://otoge-db.net/), [SaltMeta](https://github.com/reiwa/SaltyMeta), and [mai-kit](https://github.com/mai-kit/mai-kit).
