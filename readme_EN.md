# AquaSync 2.2

[中文](README.md) · English

A Windows desktop app for viewing maimai scores from AquaDX maimai2 JSON exports or LXNS score CSV exports. Browse scores, B50, plate progress and improvement recommendations locally.

## Getting started

1. Download `AquaSync-2.2-Portable.zip` from [Releases](https://github.com/m1NG-325/maimai-aquadx/releases).
2. Extract the complete archive and run `AquaSync.exe`. Keep the `_internal` folder and do not run the app inside the ZIP.
3. Choose a local player ID, click **导入 AquaDX JSON** or **导入落雪 CSV**, and select your export.

Supports 64-bit Windows 10/11. Python is not required. Ordinary viewing and analysis work offline. The interface is Chinese.

The app is free. Official builds are published in this repository's Releases.

## Features

- B50 and B50 comparison, score search and sorting, chart details and cover art
- Shared song metadata, plate progress and separate private-server and Chinese-server recommendations
- Rating calculators and chart-constant/achievement reference tables
- Play history, calendars, daily play counts, judgement analysis and CSV export
- Rating and achievement trends with date filters
- Maps, characters, courses, login bonuses, player profiles and collections
- Local tools, LXNS backups and selected-difference synchronization, and Diving-Fish/LXNS JSON export
- Data-directory migration
- Manual update checks in **功能与数据说明**, with official release notes and a link to the download page

## Importing data

- Use a complete AquaDX JSON export for original B50 groups, play logs and player profiles, when available.
- LXNS CSV contains scores only. It does not supply full player profiles, original B50 groups, play logs or collection archives. Its B50 is estimated from local metadata. Upload timestamps are not treated as play times.
- Importing replaces the selected local player's snapshot. Use a separate local player ID for LXNS CSV to retain a complete AquaDX archive.
- Imports stay local and do not upload scores automatically. Review the account and selected changes before synchronization.
- Available views depend on the records in your export. Missing records are not fabricated.

## Data and upgrades

- Local data defaults to `user-data` beside the app. `AquaSync-desktop.json` stores the data-directory setting.
- Close the app before upgrading. Preserve both the data directory and configuration file, including any custom data directory.
- Extract the new build and replace the program files, keeping your existing data and configuration.

Reference chart constants, Rating and plate progress may differ from the actual game version.

[Desktop guide (Chinese)](docs/DESKTOP.md) · [Releases and changelog](https://github.com/m1NG-325/maimai-aquadx/releases) · [Sources and algorithms](docs/ALGORITHMS_AND_SOURCES.md)

## Credits

[AquaDX](https://github.com/MewoLab/AquaDX), [KarenBot](https://github.com/xszqxszq/KarenBot), [LXNS](https://maimai.lxns.net/), [Diving-Fish](https://www.diving-fish.com/maimaidx/prober/), [Otoge DB](https://otoge-db.net/), [SaltMeta](https://github.com/reiwa/SaltyMeta), and [mai-kit](https://github.com/mai-kit/mai-kit).
