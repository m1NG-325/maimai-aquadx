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

2026-10-18：DX／标准类型标识统一采用用户提供的 Topaz Wonder 中文超分透明 PNG（232×84）。上游原始图为 KarenBot-Resources/data/maimai/templates/course/type_DX.png、type_SD.png。用户文件像素和透明通道均未改动；Qt 屏幕与导出共用等比绘制。逐图 SHA256 与来源见 type_manifest.json。版权仍归原权利人，保留原有 KarenBot-Resources 许可。

2026-10-18: Map artwork now uses the original Sprite for the last NamePlate reward along each route, extracted from the user-provided local game nameplate AssetBundles with UnityPy. Route/treasure references: data/map_details.json. Sprite mappings: archive/manifest.json. 205 of 226 maps have a matched NamePlate reward; remaining maps have no fallback island art. Game artwork belongs to SEGA and respective rights holders. This is public reference metadata, without player records.

2026-10-18: Map reward thumbnails use original game Sprite assets for Character, NamePlate, Frame and Icon entries. MusicNew/MapTaskMusic use existing song covers; Challenge uses the explicit Challenge.xml Music/id relationship. All 2625 related route nodes have images. Title/numeric gifts without individual artwork remain textual. 688 distinct NamePlate/Frame/Icon references resolved without missing files; manifest entries carry resource IDs. Ownership remains with the original rights holders.

2026-10-18: Course/login-bonus metadata comes from local Course.xml, LoginBonus.xml and Ticket.xml. All 72 bonus definitions have matching artwork; the 1.5x ticket uses the explicitly named UI_CMN_Tix_Icon_Free Sprite. 956 fixed-course song slots have covers. Random course placeholders are not presented as actual played songs. Extraction uses UnityPy; original artwork ownership remains with respective rights holders. See activity_details.json and archive/manifest.json for ID mappings.
# 无损资源兼容

发布包和公开源码中的收藏图片可使用逐像素校验的无损 WebP；原始 PNG 名称由同目录 `image_aliases.json` 映射到对应文件，完全重复的图片可共用一个资源。此处理不更改分辨率、透明度或来源归属，不需要联网补图。

