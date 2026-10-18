# AquaSync 2.0

[中文](README.md) · English

A Windows desktop app for viewing maimai scores exported as maimai2 JSON from an AquaDX private server. Browse scores, B50, plate progress and improvement recommendations locally.

## Getting started

1. Download either package from this repository's **[Releases](https://github.com/m1NG-325/maimai-aquadx/releases)**:
   - **Installer — `AquaSync-2.0-Setup.exe`**: choose an installation location and install. A desktop shortcut is created automatically.
   - **Portable — `AquaSync-2.0-Portable.zip`**: extract the entire archive and run `AquaSync.exe`. Keep the `_internal` folder beside it.
2. Click **Import AquaDX JSON (导入 AquaDX JSON)** and select your complete export file.
3. Browse B50, scores, plate progress, play history and your player profile.

Supports 64-bit Windows 10/11. Python is not required for the packaged app. Ordinary viewing and analysis work offline. This English README does not change the app's interface language.

## Features

- **Scores**: B50, side-by-side B50 comparison, sorting, chart details and high-resolution jackets.
- **Shared catalog**: score search, B50, the song library and recommendations share chart metadata. Plate progress offers private-server, Chinese-server and historical Japanese reference scopes, including removed songs where applicable.
- **Recommendations and Rating**: separate private-server and Chinese-server recommendations, a Rating calculator and a colored chart-constant × achievement reference table.
- **Play history**: individual plays, a calendar, daily play-count trends, filtering, sorting and CSV export.
- **Judgement analysis**: note judgements, FAST/LATE totals and achievement-range filtering.
- **Trends**: Rating changes, individual-chart achievement trends and date-range filters.
- **Progression**: map routes and rewards, characters, partner intimacy, course challenges, Kaleidx Scope and login bonuses.
- **Profile and collections**: player information, play settings, equipped items, favorite songs and item previews.
- **Other tools**: score statistics, course tables, song guessing, letter reveal, score-threshold tolerance and custom Best lists.
- **Backup and sync**: LXNS score backups, selected-difference synchronization and Diving-Fish/LXNS JSON export.
- **Local storage**: choose a data directory and migrate existing records.

## Data and updates

- By default, personal data is stored in `user-data` beside the app. The configuration file is `AquaSync-desktop.json`.
- Close the app before updating. Keep your data directory and configuration file. Uninstalling the installer version also preserves personal records.
- After upgrading from an older version, import your complete JSON again to enable play history and the additional profile sections.
- Available information depends on the fields retained in your export. The play log may not contain your entire play history.

## Version 1.1

- Expanded plate completion tables and separated Chinese, private-server and removed-song reference scopes.
- Added songs missing from version 1.0.
- Added chart metadata and 176 jackets.

## Version 1.2

- Unified catalog information across pages, including song titles and reference chart constants.
- Separated private-server and Chinese-server improvement recommendations.
- Added a colored Rating reference table.
- Made score cards more compact.
- Added sorting by latest play, chart constant, DX score, play count, achievement, Rating, FC and AP.
- Unified difficulty backgrounds and improved rank and FC/AP/FS icons.
- Added jackets to course tables and double-click access to song details.

## Version 2.0

- Added individual play logs, a calendar, daily play-count trends and judgement analysis.
- Added Rating and single-chart achievement trends with date and achievement-range filters.
- Added map rewards, characters, partner intimacy, course challenges, Kaleidx Scope, login bonuses and collections.
- Adopted the Studio interface and improved artwork, statistics, song guessing and advanced tools.

Reference chart constants can differ from your private server. Check the destination account before syncing to LXNS.

[English release notes](docs/RELEASE_NOTES_EN.md) · [Desktop guide (Chinese)](docs/DESKTOP.md) · [Algorithms and data sources](docs/ALGORITHMS_AND_SOURCES.md)

## Sources and acknowledgements

- [AquaDX](https://github.com/MewoLab/AquaDX)
- [KarenBot](https://github.com/xszqxszq/KarenBot)
- [LXNS](https://maimai.lxns.net/)
- [Diving-Fish](https://www.diving-fish.com/maimaidx/prober/)
- [Otoge DB](https://otoge-db.net/)
- [SaltMeta](https://github.com/reiwa/SaltyMeta)
- [mai-kit](https://github.com/mai-kit/mai-kit)
