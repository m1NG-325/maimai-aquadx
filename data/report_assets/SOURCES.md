# Public report artwork

Song covers: https://github.com/realtvop/SaltMeta/tree/main/covers
Additional public cover endpoint: https://assets2.lxns.net/maimai/jacket/{song_id}.png

Backgrounds, difficulty bases, rank and FC/FS badges, and level emblems:
https://github.com/xszqxszq/KarenBot-Resources/tree/main/data/maimai/templates

The renderer uses these assets in native Qt. Upstream license is included in docs/KarenBot-Resources-LICENSE.txt. Artwork remains the property of its respective rights holders.

Resource IDs use musicId % 10000. Only public song IDs are requested. No player scores, accounts or tokens are part of these resources. Missing artwork is shown as a placeholder.

Retrieval snapshots: 2026-10-14 and 2026-10-15. Public song metadata provenance and mapping evidence are recorded in data/private_music_data.json. Resource coverage is recorded in cover_manifest.json.

2026-10-17: Additional public covers for the three regional plate snapshots were fetched from the LXNS public jacket endpoint. See cover_manifest.json for counts and unresolved IDs. No game chart files or private player information are bundled.
