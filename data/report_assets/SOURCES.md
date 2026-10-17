# Public report artwork

Song covers: https://github.com/realtvop/SaltMeta/tree/main/covers
Additional public cover endpoint: https://assets2.lxns.net/maimai/jacket/{song_id}.png

Backgrounds, difficulty bases, rank and FC/FS badges, and level emblems:
https://github.com/xszqxszq/KarenBot-Resources/tree/main/data/maimai/templates

The renderer uses these assets in native Qt. Upstream license is included in docs/KarenBot-Resources-LICENSE.txt. Artwork remains the property of its respective rights holders.

Resource IDs use musicId % 10000. Only public song IDs are requested. No player scores, accounts or tokens are part of these resources. Missing artwork is shown as a placeholder.

Retrieval snapshots: 2026-10-14 and 2026-10-15. Public song metadata provenance and mapping evidence are recorded in data/private_music_data.json. Resource coverage is recorded in cover_manifest.json.

2026-10-17: Additional public covers for the three regional plate snapshots were fetched from the LXNS public jacket endpoint. See cover_manifest.json for counts and unresolved IDs. No game chart files or private player information are bundled.

2026-10-17: Rank badges D through SSS+ replaced with unmodified 256×120 transparent PNG assets from mai-kit/mai-kit, pinned revision 32572f7ffc5ae8fa3cc18dab6eff590fc4d17f4d, packages/assets/assets/rank/. Source URLs and SHA256 values are recorded in rank_manifest.json. MIT notice retained in docs/MaiKit-Assets-LICENSE.txt; game graphic ownership remains with SEGA and respective rights holders. No upstream program code was copied.


2026-10-17：FC/FC+/AP/AP+、FS/FS+/FSD/FSD+/SYNC 和空状态图标采用 mai-kit/mai-kit 固定提交 32572f7ffc5ae8fa3cc18dab6eff590fc4d17f4d 的 packages/assets/assets/bonus 原始 80×80 透明 PNG；未放大伪造源分辨率。逐文件来源和 SHA256 见 data/report_assets/status_manifest.json；许可见 docs/MaiKit-Assets-LICENSE.txt。游戏素材权利归 SEGA 及相应权利人。
