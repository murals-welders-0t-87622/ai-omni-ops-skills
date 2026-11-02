# AI 图 / AI 视频素材通道

> ## ⛔ 默认不走这条路
>
> 用户已明确指令：**不需要 AI 生成图片和视频**。
> B-roll 一律用本地零成本形式实现（HTML 动效 / 卡片 / 打字机 / 数据动画 /
> 本地拼贴 / 现成素材 / 录屏）。
>
> **本文档仅在用户当次对话中明确要求生成 AI 图/视频时才查阅**，
> 目的是避免重新试错 —— 下面每一条都是实测踩出来的，不是推测。
>
> 实测依据：一个 65 镜的片子，41 种组件全部用 HTML/CSS 实现，
> 富度门禁 ratio 中位 1.07（基线 1.0），说明"表达不了所以要用 AI"
> 通常是实现偷懒的借口，不是真的技术限制。

---

## 一、工具通道是硬约束

- 图片 → 走 MCP「品牌运营助手」的 gpt-image-2.0
  （`get_design_workspace_options` 取 selectionKey
  `provider_runtime_image_duoyuanx_unified::gpt-image-2`，传给 `create_design_work.modelSelection`）
- 视频 → 走 MCP RunningHub 应用

**不要因为内置工具更方便就绕过。** 用户已声明的通道偏好不可替换 ——
历史上直接调用内置 `VideoGen` 被用户当场 reject。

正确工具：`mcp__ai-omni-ops-*__manage_douyin_video_production`，
`section="runninghub"` + `action`。

## 二、RunningHub 固定四步，顺序不可跳

`list_apps` → `get_app_detail` → 读 `nodeInfoList` 模板回填 → `generate`

铁律：
- 只回填 `fieldValue`，不猜 `nodeId`，不手改 `fieldData`
- 不保留 `example.png` 这类模板占位值（服务端会拦截）
- **提交 generate 前必须先 `get_app_detail` 读模板**，不许凭记忆拼参数

## 三、通道可用性实测结论（★ 直接看这张表，别重新试）

| 通道 | 状态 | 证据 |
|---|---|---|
| `ltx23-licon-msr-video`（文生视频） | ✅ **稳定可用** | 4 次连续 SUCCESS |
| `minimax-h3-fl2va-text-to-video`（文生视频） | ❌ **服务端故障** | 4 次全报 `节点 RHMiniMaxH3DirectModelLoader：Required input is missing`，而该节点在 `get_app_detail` 返回里根本不存在 |
| `minimax-h3-fl2va-first-frame-video`（图生视频） | ❌ **形态不支持** | 10 次全败，见第四节 |

**`ltx23-licon-msr-video` 节点映射**（唯一验证过可用的视频通道）：

| nodeId | 含义 | 处理 |
|---|---|---|
| 3 / 4 / 5 / 6 / 52 | LoadImage | **不要碰**，模板 fieldValue 是真实已上传文件的 hash 名，不是占位符 |
| 40 | 时长 | 5s |
| 41 | 帧率 | 24fps |
| 65 | 提示词 | 回填 |
| 38 / 39 | 宽 / 高 | 832 / 480 |

> 这 5 个 LoadImage 节点曾让我误以为必须上传图片。实际它们的模板值是
> **服务端已存在的文件 hash**，原样保留即可跑通 —— 这是破解该通道的关键。

## 四、图生视频最大的坑：`localFilePath` 只在 stdio MCP 下有效

症状演进（实测四轮）：

1. 不用 `localFilePath` → `errorCode=803 | JsonNull`，连续 8 次全失败
2. 用 `localFilePath`，路径含中文 → 提交返回 PENDING，
   **约 25 秒后才判 FAILED**，报「LoadImage 未收到真实上传文件，仍保留模板占位值」
3. 复制到纯 ASCII 路径 `C:/temp_rh/xxx.jpg` 再提交 → **仍然同样失败**
   ⇒ **证明根因不是中文路径**（早期文档写错过，已纠正）
4. 定位真根因：**该 MCP 以 HTTP 服务形态运行（`127.0.0.1:3011`，
   `/api/health` 可验证），不是 stdio 子进程**，服务端进程读不到我本地磁盘上的文件。
   错误提示里那句「请确认 OpenClaw 通过 stdio MCP 脚本传入 localFilePath」
   就是在说这件事。

**判断方法**：错误信息里同时给出 `localFilePath` 和
`upload.fileName / upload.contentType / upload.dataBase64` 两条路子时，
说明服务端在提示「你现在这条路走不通，换另一条」。

**HTTP 模式下的可选方案** —— `upload.dataBase64`，体积是唯一门槛：

| 规格 | 文件字节 | base64 字符 | 可否传入工具参数 |
|---|---|---|---|
| 1536×1024 PNG 原图 | 1.61 MB | 2 140 000 | 否，必爆上下文 |
| 1024×701 JPEG q88 | 126 KB | 168 000 | 否，风险过高 |
| 512×350 JPEG q72 | 17 KB | 22 596 | 可，勉强 |
| 384×263 JPEG q62 | 8.7 KB | 11 608 | 可，推荐用于通道验证 |

用法分两步：先用 384px 版验证通道是否走得通（成本最低），通了再评估清晰度。
**注意参考图压到 384px 会明显掉质感**，通道验证与实际出片必须分开对待。

另有一条不占上下文的思路（未验证）：该 HTTP 服务 `/api/health` 显示
`bodyLimit: 100mb`，理论上可用 curl 直连提交大 base64。
但实测 `/api/mcp`、`/mcp`、`/api/tools`、`/api/douyin/runninghub/generate`
全部 404，**靠猜路由是浪费时间**。

**结论：图生视频链路在当前 HTTP MCP 形态下不可用。**

## 五、并发限制 = 1（用户明确指令）

`errorCode=421 | api queue limit reached` —— **批量提交必须严格串行**：
提交 → 等成功 → 再提交下一个。系统会自动退避重试，
但连续退避 6 次仍失败会改判 FAILED。

配套纪律（用户明确指出过）：
- **先核查已有成功记录**，不要盲目重试。历史任务里可能已经有跑成功的。
- **图生视频走不通时，先问用户再决定是否转文生视频**，不许自己拍板。

## 六、提示词要点（纸质拼贴风格）

- 锁死镜头：`static locked-off camera, no pan no zoom no dolly`
- 限定唯一运动：只让一个元素动 + 光晕缓慢脉动 + 微尘上浮
- 排斥 3D：`flat 2D handmade paper-craft, no 3D rendering, no glossy plastic, no photorealism`
- 禁文字（AI 极易产生文字幻觉）：
  `no text, no letters, no numbers, no captions, no watermark anywhere`
- 质感贯穿：`consistent paper collage texture preserved throughout the entire clip`

## 七、AI 视频镜的合成侧处理

AI 视频通常偏暗（实测 `mean 74~76 / dark% 96~100%`），直接铺在纸艺版式下
会让文字读不出来。处理要点：

- **抬 contrast 必须配合压 brightness**，判据是「原始层 mean 落到 ~110」。
  实测 broll-07 `con1.60/bri.46`、broll-08 `con2.40/bri.40`。
- 纸幕（scrim）遮盖度用 `gate-scrim-probe.py` 量，达成率 ≥ 80%。
  纸幕过重会把视频洗白，失去用 AI 视频的意义。
- **径向柔光罩不到边缘**：`.b-pad::before` 是 `ellipse 78% 66% at 50% 48%`，
  贴边元素处 alpha 已衰减到 0，需要单独补底衬。该根因命中过 4 次。
- AI 视频镜的文字必须跑 `gate-text-probe.py` **双模对照**
  （含视频 vs 基线），判据是 LOW 数的**增量**。
