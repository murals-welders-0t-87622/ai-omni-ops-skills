> 历史专家团文档：运行时应以当前 MCP 实际工具、参数、用户要求和账号状态为准。

# 抖音视频制作参考手册（旧结构映射 + 历史踩坑清单）

> 本文件是抖音视频层的深度技术参考。现行结构已经改成
> **数字人视频专家 / 剧情视频专家 + 具体 Skill**，
> 本文件保留旧生产经验、完整命令和踩坑清单，供新 Skill 继承。
> 遇到问题先查本文件"踩坑清单"，大概率已经有答案。
>
> **剧情类视频的完整规范不在本文件**，见 `microdrama-commerce-chain.md`。
> 本文件第一节保留旧三通道映射，只用于说明当前 Skill 从哪里继承而来。

---

## 一、旧三通道与当前 Skill 映射

| 维度 | 旧通道 A | 旧通道 B | 旧通道 C |
|---|---|---|---|
| 当前 Skill | `douyin-dh-landscape-html-video` | `douyin-dh-vertical-abroll-video` | `douyin-microdrama-commerce-video` |
| 旧技能 / 工具来源 | `shiguang-daily-dh-html` | `talking-head-broll-video` | RunningHub `minimax-h3-fl2va-first-frame-video` |
| 目标成片 | 3-5 分钟数字人口播 | 5-10 分钟精细化数字人口播 | **30 秒剧情短片，结尾带货** |
| 画面结构 | 3 段数字人独立成段 + 2 段 FULL 全幅 HTML | 数字人小窗 + 多镜型 HTML B-roll 同屏混剪 | 六段式剧情（5 秒 × 6），无数字人、无 HTML |
| 画幅 | 竖屏 1080×1920 | 竖屏 1080×1920 | 竖屏 1080×1920（`select="4"`，**模板默认是 4:3 必须覆盖**） |
| 镜数规模 | 每 HTML 段 1-5 镜 | 数十镜（参考实践为 59 镜） | 六段时间轴，AI 内部自行分镜 |
| 字幕 | 烧（单行 ≤12 字） | 烧（单行 ≤12 字） | **默认不烧**（AI 音频无精确时间轴 + 技能负面词含"不要字幕"） |
| 耗时 | 30-90 分钟 | 2-5 小时 | 20-40 分钟（两段串行生成 + 拼接） |
| 成本 | 低 | 高 | 中 |
| 留人机制 | 信息密度 | 信息密度 | **戏剧冲突** |
| 触发条件 | 文案简单：单概念、事件解读、≤2 核心点 | 文案复杂：多概念、案例连连看、数据对比、深度专题 | **上游产出了短剧分镜提示词** |

**A/B 共享素材**：TTS 音频（5 段）、SRT 字幕、IP 形象图、封面、5 部分口播结构、**B-roll 组件库**。
**A/B 差异仅在**：画面结构（分段式 vs 同屏混剪）、镜数规模、确认流程深度。

### 1.1 现行理解方式

1. 旧通道 A 已映射为 `douyin-dh-landscape-html-video`。
2. 旧通道 B 已映射为 `douyin-dh-vertical-abroll-video`。
3. 旧通道 C 已映射为 `douyin-microdrama-commerce-video`。
4. 现行任务分发以 `references/video-skill-routing.md` 为准，不再直接使用“通道 A/B/C”做交接。
5. 剧情类视频与数字人视频不共享生产专家，但仍共享这里沉淀下来的技术经验。

### 已作废路线（禁止回退）

| 作废路线 | 作废时间 | 原因 |
|---------|---------|------|
| PIL 静态幻灯片 | 2026-08-12 | 视觉质感与通道 B 差距过大，改用统一组件库 |
| Ken Burns 静态图平移 | — | 属未授权降级手段 |
| hyperframes 渲染 | — | 被组件化 CSS 渲染管线取代 |
| 短剧 30 秒单次生成 | — | `duration_seconds` 上限 15，超限被截断；必须拆两段 |
| 短剧用文生图画产品当首帧 | — | 包装失真 = 虚假宣传，合规事故 |

---

## 二、通道 B 完整执行 SOP

### 2.1 文件布局

当天素材文件夹必须包含：

```text
YYYYMMDD/
├── DESIGN.md                 # 视觉系统说明
├── STORYBOARD.md             # 逐镜分镜表
├── design-tokens.css         # 全局 token
├── _shell.css / _shell.js    # 舞台壳与初始化
├── _ambient.css              # 自动运行的 infinite 装饰动效 + 信息条
├── _components.css           # 组件样式
├── gen_v2.py                 # composition + preview 生成器
├── render-frames-css.py      # Playwright 确定性抽帧渲染器
├── assemble_premium.py       # 通道 B 合成器
├── gate-rich-check.py        # 富度门禁
├── gate-comp-check.py        # 几何/居中门禁
├── gate-occlude-check.py     # 遮挡门禁
├── gate-text-probe.py        # 文字对比度/溢出探针
├── gate-scrim-probe.py       # 纸幕遮盖度探针
├── gate-chart-probe.py       # 图表畸变探针
├── P1.mp3 … P5.mp3           # TTS
├── P2.srt / P4.srt / output.srt
├── _norm_P1.mp4 … _norm_P5.mp4   # 归一化后的数字人段
├── dh_frames/                # DH 占位帧（仅调试用，成片禁用静态图）
├── compositions/             # 生产页
├── previews/                 # 预览页（门禁 ratio 基线来源）
└── _seg60/                   # 渲染片段
```

### 2.2 执行顺序（禁止跳步）

1. **配置确认闸**：读 `talking-head-broll-video` Skill 与参考范例，明确镜头结构与布局（SPLIT / HERO / FULL）
2. **拆镜 + 写 `STORYBOARD.md`**：每镜给出时间码、布局（A+B 或 B-only）、B-roll 类型、口播 cue、组件 class、数字人源与段内 `data-off`
3. **视觉系统 + Demo 预览页**：写 `design-tokens.css` 与 `demo.html`，**经用户确认后**才允许下一步
4. **生成 composition + preview**：`python gen_v2.py` + `python gen_v2.py --preview`
5. **六道机械门禁全绿**：任一 FAIL 必须返回修改，禁止带病渲染
6. **渲染**：`render-frames-css.py --force` → `_seg60/`
7. **合成成片**：`python assemble_premium.py`
8. **交付前三层验收**：六门禁 + 像素核验 + 并排目视

### 2.3 镜头分类铁律

全片仅两类镜头，**绝不允许纯 A-roll 段**：

- **A+B**：数字人 `frame-a`（小窗）+ B-roll 板 `frame-b` 同屏
- **B-only**：FULL 布局，无 `frame-a`

原则：**有数字人的地方就是 A+B，A-roll 就是数字人；没有数字人的地方就只有 B-roll。**

### 2.4 frame_a 必须嵌真视频

```html
<video src="../_norm_P2.mp4" data-off="段内起点" muted playsinline></video>
```

- `data-off` = 该镜在对应 DH 段的**段内起点** = 全片 start − 该段全片起点
- 渲染器的 `SEEK_JS` 按 `data-off + 镜内时间` 精确定帧，保证唇形与旁白同步
- CSS 选择器需 `.frame-a > video, .frame-a > img` 同步兼容
- 🚫 **禁止用静态占位图**（`<img src="../dh_frames/xxx.jpg">`）——会让数字人变成"照片"，与口播不同步

### 2.5 六道门禁

门禁使用 Playwright Edge headless，必须用隔离 venv：

| 门禁 | 脚本 | 核心断言 |
|---|---|---|
| **富度** | `gate-rich-check.py` | `frame-b` 内 `n_dom>=12`、`getAnimations()>=3`、`@keyframes>=2`、分镜表点名 class 命中、ratio>=0.8（相对 preview 基线）|
| **几何/居中** | `gate-comp-check.py` | HERO 居中（±0.5px）、SPLIT gutter 一致、FULL B 占比达标 |
| **遮挡** | `gate-occlude-check.py` | 数字人小窗不遮挡文字 |
| **文字探针** | `gate-text-probe.py [sid]` | 文字对比度 Δ>=100、无溢出 |
| **纸幕探针** | `gate-scrim-probe.py` | 纯纸面 B-roll 无视频层时 N/A 跳过 |
| **图表畸变** | `gate-chart-probe.py` | SVG 高度 >=240、容器/ViewBox 宽高比偏差 <=1.35 |

**⚠️ 重要**：`gate-rich` 的 ratio 基线取自 `previews/*.html`，**预览页必须与生产页同步刷新**，否则基线失真。

**门禁纪律**：任一 FAIL 立即返回修改。**禁止删断言、放宽阈值、改文件名凑通过。**

### 2.6 生成器关键设计（`gen_v2.py`）

- `build_stage()` 同时产出生产页与预览页的 stage 本体 → 保证**预览页 = 生产页**
- `classes_for()` 读分镜表 JSON 的 component 字段，合并多组件 class
- `ambient_html()` 注入信息条 + infinite 装饰动画，解决纯 CSS 场景 anim/kf 数量不足
- `takeaway_html()` / `hero_tag_html()` 为薄版式场景注入真实信息节点，抬高 DOM 以满足富度门禁 —— **禁止靠放宽阈值通过**
- `frame_a()` 对所有有数字人的镜头输出真 `<video>`，FULL 镜头无 frame-a

### 2.7 合成器逻辑（`assemble_premium.py`）

- 视觉：按 `_timeline.json` 的 num 顺序把静音 `scene-{num}.mp4` concat 为 `silent_full.mp4`
- 音频：`_norm_P1..P5.mp4` 五段口播音轨按序 concat 为 `full_audio.m4a`（与视觉段边界对齐）
- mux：`[0:v]tpad=stop_mode=clone:stop_duration=5[v];[v]trim=duration=<音频总长>,setpts=PTS-STARTPTS`
  把视觉补齐/截到音频长度 —— **绝不用 `-shortest` 直接砍音频尾**
- 烧录字幕：`subtitles='D\:/.../output.srt':force_style=...`（Windows 路径必须 `D\:/` 转义）

---

## 三、字幕系统（最容易出事的模块）

### 3.1 单行铁律（硬闸口）

- **硬上限 12 中文字/条**，超限**截断**（不是折行），在 ≤12 字处找最后一个标点切断，末尾补 `…`
- `build_srt()` / `wrap_text()` 必须 `assert len(text) <= 12`，超限直接 raise
- DH 段与 B-roll 段**共用同一份 SRT（单一真源）**

**血泪教训**：某次 SRT 有 6 条 > 12 字（最长 16 字），`build_srt` 未做二次断行 →
HTML 段字幕被 libass 折成 2-4 行，审核截图直接打回。改用截断模式重生成（245 条全部 ≤12 字）后解决。

### 3.2 三大真因（连续多轮返工后定位）

| 症状 | 真因 | 排查方式 |
|------|------|---------|
| **画面卡住** | **第一嫌疑人是 HTML/B-roll 段，不是数字人** | 检查 `.stage` 是否有 `.run` class、`getAnimations()` 数量 |
| **字幕双层** | 字幕跨段 overhang / **SRT 时间重叠**（不是折行）| 校验任意时刻激活字幕 ≤ 1 条 |
| **字幕对不上** | **帧率混用**（隐藏最深）| 所有段必须统一 30fps |

### 3.3 样式金标准（照抄不改）

```
FontName=SimHei,FontSize=18,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,
BackColour=&H66000000,BorderStyle=4,Outline=1,Shadow=0,
MarginV=8,MarginL=40,MarginR=40,Alignment=2
```

| 参数 | 值 | 为什么 |
|------|-----|-------|
| FontSize | 18 | 比默认 22 更精致 |
| BorderStyle | **4** | 半透明背景框；**用 3 会在底部形成难看黑带** |
| BackColour | &H66000000 | 半透明黑 40% |
| Outline | 1 | 细描边，非 4 的粗描边 |
| MarginV | **8** | 贴底；**值越大字幕越往上飘**，设 50+ 会推离画面看似无字幕 |
| Bold | 不加 | 加粗视觉过重 |

**libass 中文字体坑**：需 `fontsdir=.` 指定本地字体目录，把 `simhei.ttf` 拷到工作目录：
```
subtitles=xxx.srt:fontsdir=.:force_style='...'
```

### 3.4 字幕问题排查铁律

1. **不要盲目调样式参数** —— 一改就越改越坏
2. **先查历史最近一次成功的脚本，照抄样式**再做小微调
3. **抽帧验证是硬信号**：抽 5 个时间点（2s/5s/20s/45s/90s）
   - 无字幕帧 ≈ 40-50 KB
   - 正确字幕帧 ≈ 80-200 KB
   - **文件大小差异是最快的判定信号**（不用一张张打开看）
4. **用 Read 工具人工核验预览帧**的位置、字体、透明度

---

## 四、音频管线铁律

### 4.1 concat filter 会"静默丢路"

必须先归一化 + 拼完必须硬断言：

```bash
# 1) 两路各自归一化到统一格式（必做，不可省）
ffmpeg -y -i a.mp4 -c:v libx264 -crf 20 -r 30 -pix_fmt yuv420p -c:a aac -b:a 128k -ar 44100 -ac 2 _norm_a.mp4
ffmpeg -y -i b.mp4 -c:v libx264 -crf 20 -r 30 -pix_fmt yuv420p -c:a aac -b:a 128k -ar 44100 -ac 2 _norm_b.mp4

# 2) concat
ffmpeg -y -f concat -safe 0 -i concat.txt -c copy merged.mp4

# 3) 🚨 硬断言（缺此行 = 违规）
ffprobe -v error -show_entries format=duration -of csv=p=0 merged.mp4
ffprobe -v error -select_streams a -show_entries stream=codec_name -of csv=p=0 merged.mp4
```

### 4.2 音频编码必须统一

数字人音频是 AAC，HTML 视频合 TTS（MP3）后是 MP3。
concat 用 `-c copy` 时异构音频编码会导致 **MP3 轨道被静默丢弃**（ffmpeg 无报错但 HTML 段无声音）。
**必须**在 scale+pad 阶段统一转码 `-c:a aac -b:a 128k`，**严禁** `-c:a copy`。

### 4.3 禁止相信文件扩展名

必须 `ffprobe` 核实真实编码，`.mp4` 里可能装着任何东西。

### 4.4 RMS 能量指纹法（判定"这段音轨到底是哪个音频"）

抽取时间窗算 RMS 能量，与候选源音频的 RMS 曲线比对，指纹匹配则确认来源。

### 4.5 音频 + 字幕双向核验

每个时间点：① 抽 0.9s 音频算 RMS（> 500 判为有人声）② 解析 SRT 查该时刻字幕。

| 音频 | 字幕 | 判定 |
|------|------|------|
| 有人声 | 有字幕 | ✅ 对齐 |
| 有人声 | 无字幕 | ❌ 错位 |
| 静音 | 有字幕 | ❌ 错位 |

### 4.6 TTS 音质提升（源头质量差的补救）

TTS 原始输出常为 **24kHz / 32kbps / mono**（电话音质）。合并到视频时强制上采样：

```bash
ffmpeg -i video.mp4 -i tts.mp3 \
  -c:v copy -c:a aac -b:a 192k -ar 44100 -ac 2 \
  -af "aresample=44100" -shortest output.mp4
```

- `-ar 44100` + `aresample`：24kHz → 44.1kHz 上采样（kaiser 窗插值）
- `-b:a 192k`：32kbps → 192kbps
- `-ac 2`：mono → stereo

⚠️ 上采样**无法恢复已丢失的高频信息**，只能避免二次编码进一步劣化。如仍反馈卡顿，需从 TTS 侧提高输出参数。

---

## 五、时长精确匹配（字幕漂移的根因）

**症状**：从第二个 B-roll 段开始字幕比语音超前 500ms+，累积到片尾 1.5s。

**根因**：帧序列拼出来的总时长**略长于** TTS 音频（如 55.13s vs 54.28s，多 850ms），
而 **`-shortest` 在 `-c:v copy` 场景下无法裁短视频轨**。

**正确做法**：生成 B-roll 视频后立即硬切：

```bash
ffmpeg -y -i html_video_N.mp4 -t {tts_dur:.3f} -c copy html_video_N_trim.mp4
```

用 trim 版进入拼接管线。

---

## 六、数字人相关

### 6.1 并发 = 1（见 Agent MD 顶部铁律）

### 6.2 VRAM 阈值

- 单段 **> 50s 必爆显存**，**≤ 38s 安全**
- 超阈值时：切分音频 → 生成新 TTS → 分别提交 DH（切分后同样遵守并发=1）

### 6.3 生成秒数节点必须显式设为 `"0"`

模板默认 `"10"`（10 秒）。不覆盖的话，无论音频多长，DH 视频都只有约 9.96 秒 → 后半段"哑掉"。

- 症状：`digital_human_X.mp4 时长 9.96s`，但音频段有 14-20 秒
- 错误补救（禁用）：`ffmpeg -stream_loop -1` 循环视频匹配音频
- **正确做法**：显式覆盖为字符串 `"0"`（代表整段音频）
- **验证**：`ffprobe` 检查每段 DH 时长 ≥ 对应音频时长

### 6.4 图片上传金标准

1. 读本地图片**原始字节** → base64（🚨 **严禁用 PIL 压缩重编码**，会损坏二进制导致 `UnidentifiedImageError`）
2. `get_app_detail` 获取 nodeInfoList 模板
3. IMAGE 节点：**删除旧 fieldValue**（含 hash / example.png），追加：
   ```json
   { "fileName": "xxx.png", "contentType": "image/png", "dataBase64": "<原始字节 base64>" }
   ```
4. 其余节点保持模板 `fieldValue`
5. 验证：返回 `sourceImageUrl` 形如 `runninghub-input-xxxx.png` 才算真正上传成功

**已证伪路径（务必避开）**：

| ❌ 错误做法 | 后果 |
|-----------|------|
| `localFilePath` 字段 | HTTP 模式不生效，图片从未上传，回退模板图 |
| 手动粘贴大 base64 | 会被截断 → `UnidentifiedImageError` |
| **带鉴权的站内图片 URL 当 fieldValue** | RunningHub 无法访问需登录态链接 → **静默回退模板默认图，生成完全陌生的人物** |
| 仅改 `fieldData` 不改 `fieldValue` | fieldData 里的 example.png 残留即出错误人物 |

### 6.5 🚨 形象验证 SOP（账号级事故后升级为最高优先级）

**事故回顾**：某次发布的视频全部 6 段数字人**人物全错**（西装领带男、白衬衫男、古装男等陌生人），
RunningHub 返回 `SUCCESS`，视频也成功上传发布，直到人工审核成片才发现。
**这是账号级事故**：IP 形象崩塌，公信力归零。

**根因**：IMAGE 节点 fieldValue 填了带鉴权的站内图片 URL → RunningHub 下载失败 → 静默回退模板默认图。

**验证 SOP（每段强制执行，禁止跳过）**：
1. DH 视频下载后**立即**抽帧：`ffmpeg -i dh_X.mp4 -ss 00:00:01 -frames:v 1 dh_X_frame.jpg`
2. **用 Read 工具查看该帧**，确认人物是品牌 IP 本人（面部特征一致度 ≥ 8/10）
3. **非本人 → 该段一律作废，重新提交，禁止进入拼接**
4. 全部段验证通过，才能继续剪辑

### 6.6 首尾卡顿修复 SOP

**症状**：开头 1 秒静止不开口 / 结尾没讲完最后半个字。

**根因诊断三步**：
1. **头静音检测**：`ffmpeg -i dh.mp4 -af "silencedetect=noise=-30dB:d=0.15" -f null -`
   → 前 1s+ 全静音 = TTS 前置引导静音被数字人保留
2. **尾部截断检测**：`ffprobe` 对比 DH 输出时长 vs 源 TTS mp3 时长
   → DH 通常短 **50-170ms** = 最后半个字被吃掉
3. **末尾音量验证**：`ffmpeg -i seg.mp4 -af "astats=metadata=1:reset=1" -f null -`
   → 尾部 RMS < -40 dB 确认已无有效音频

**修复模板**：
```bash
# A. 裁头：前 N 秒静音裁掉（N = 静音时长 - 0.3s 呼吸缓冲）
# B. 补尾：最后一段用 tpad 冻末帧 + 从原 mp3 尾部 atrim 补音频
ffmpeg -i dh_a.mp4 -i dh_b.mp4 -i b.mp3 -filter_complex "
  [0:v]trim=start=1.5,setpts=PTS-STARTPTS,scale=1920:1080[v0];
  [0:a]atrim=start=1.5,asetpts=PTS-STARTPTS[a0];
  [1:v]scale=1920:1080,tpad=stop_mode=clone:stop_duration=0.25[v1];
  [1:a][2:a]concat=n=2:v=0:a=1[a_pre];
  [a_pre]atrim=0:{new_dur}[a1];
  [v0][a0][v1][a1]concat=n=2:v=1:a=1[v][a]
" -map [v] -map [a] -c:v libx264 -crf 20 -c:a aac seg_fixed.mp4
```

**关键参数**：
- 裁头量：视 silencedetect 结果，留 0.3-0.4s 呼吸
- 补尾量：固定 0.25s（覆盖 50-170ms 截断有余量）
- **段时长变了 → SRT 必须重算前置延迟**
- **重拼必须 `filter_complex concat` 重编码**，不能 `-c copy`（旧 pts 会累积错位）
- 修复后必抽帧 QA（0.5s/1s/2s/尾-1s/尾-0.5s/尾-0.3s 共 6 帧）

---

## 七、封面图

### 7.0 唯一生图通道铁律

**所有图像生成任务——封面、B-roll、概念图、场景锚图、信息图、人物图等——只允许走一个通道：**

```
MCP 品牌运营助手 → create_design_work(module="image")
  modelSelection = "provider_runtime_image_duoyuanx_unified::gpt-image-2"
  injectBrandProfile = false
```

**严禁**使用以下任何替代方案：
- ❌ WorkBuddy 内置 ImageGen / VideoGen
- ❌ PIL / Pillow 手绘图、程序化生成图
- ❌ seedream / 即梦 / dall-e / stable diffusion / nano_banana / qwen_image 等其他模型
- ❌ 任何本地脚本、base64 占位图、纯色兜底图
- ❌ 从网络搜索下载的未授权图片

多元探索平台或 gpt-image-2.0 不可用时，**必须立即停止并上报用户**，说明缺口和影响，等待裁决。不得自行切换供应商、不得降级、不得用占位图凑数。

### 7.0.1 两种子模式：自由生图 vs 海报模板（决定画面里有没有字）

同一个 `create_design_work(module="image")` 有两条完全不同的执行路径，**由是否传 `designType` 决定**：

| 传参 | 后端 skill | 画面文字 | 用途 |
|---|---|---|---|
| **不传 `designType`** | `design-openclaw-free-image`（OpenClaw 自由生图） | **零文字** | ✅ **B-roll / 纯背景 / 场景锚图** |
| 传任意 `designType` | `design-social-carousel` / `design-magazine-poster` / `design-motion-frames` … | **强制注入中文 Slogan** | 封面图 / 需要排版文案的成品图 |

**关键结论（2026-09-04 实测，13 张全带字 → 改法后 16 张全零字）：**
`designType` 的 7 个枚举值（社媒轮播图 / 杂志风海报 / 动效首帧 / 像素动画首帧 / 电商主视觉 / 品牌封面图 / 信息图海报）**全部**会在 skill 层强制注入中文标题模板（"洞见未来 连接无限可能"、"智联未来 创见无限"、"突破边界 创想未来" 等），且位置随机、无法用遮罩救。
**只要图是给 Remotion 当 B-roll 底图用的，就绝对不能传 `designType`。**

**B-roll 标准调用（可直接复制）：**
```
create_design_work
  module = "image"
  title = "broll_04"
  imageSize = "1920x1080"          ← 自由生图支持原生 1920×1080，无需 PIL 放大
  modelSelection = "provider_runtime_image_duoyuanx_unified::gpt-image-2"
  injectBrandProfile = false
  additionalInstruction = <风格前缀> + <主体描述> + <反文字约束后缀>
  # ⚠️ 不传 designType
```
返回体里应看到 `skillSlug: design-openclaw-free-image` / `skillLabel: OpenClaw 自由生图` / `设计类型：默认自由生图`——**看到这三个标记才算走对通道**，否则立刻停手重提。

### 7.0.2 反文字提示词范式（否定词堆叠会触发 400）

❌ **会被拦**：`"绝对不可以出现文字"` / `"画面中不能有任何可读字符"` / `"no text absolutely no words no letters"`
→ 返回 `400 非常抱歉，该提示可能违反了我们的内容政策`（否定词密度过高被判为对抗性提示）

✅ **正确写法**：正向描述主体 + 末尾一句柔和约束
```
<风格前缀>纯抽象几何科技背景图。深海军蓝底色 #1A1D2E，青色 #00D4FF 发光，
电影感边缘光，极简构图，只由光线与几何体构成。主体：
<主体>三个圆形发光节点由一条流动的青色能量线从左到右串联……
<约束后缀>。画面内不出现文字、汉字、字母、数字、标签、图标、界面元素、按钮、logo、标语。16:9 横版。
```

### 7.0.3 批量生成：走 MCP HTTP 直连而非逐条工具调用

16 张 B-roll 逐条 `DeferExecuteTool` 会耗尽上下文。改为脚本直连：
```
POST http://127.0.0.1:13011/api/openclaw/mcp
三步 handshake：initialize → notifications/initialized → tools/call
解析 SSE 的 data: 行 → result.content[].text → JSON.data.taskId / data.assetUrl
```
每张生成后**立即**下载校验：PNG/JPEG 魔数 → 落盘字节一致性断言 → PIL 回读尺寸。
参考实现：`抖音/<日期>/scripts/gen_broll_free.py`、`scripts/fetch_asset.py`。

### 7.1 封面图硬约束四条

1. **人物一致·垫图必传**：`referenceImage: {fileName, contentType, dataBase64}` 传**原始字节 base64**。
   ⚠️ 在 `additionalInstruction` 里写垫图路径是**无效的**——后端拿不到图片本体。
   只要 modelSelection 含 `gpt-image-2`，`referenceImage` **必传**，无一例外。
2. **禁止真实姓名**：封面任何文字禁止出现品牌负责人真实姓名/私人昵称；允许对外 IP 名。
3. **`injectBrandProfile: False` 必须显式传**：默认 True 会把品牌资料（含真名）注入生图 prompt，模型会把真名画进封面。
4. **主标题强绑定核心记忆点**：主标题是**普通用户看完会怎么跟朋友复述的那句话**，不是技术堆料词。
   ❌ "腾讯混元Hy3" → ✅ "腾讯AI 全免费"

### 7.2 additionalInstruction 双重约束

- **允许文字白名单**（只有这几组可出现）：
  1. 顶部小标签（胶囊形状）
  2. 主标题（4-8 字，本次视频爆点）
  3. 副标题（6-12 字）
  4. 右下角徽章（如 "¥0"、"免费"、日期）
- **禁止文字黑名单**：真实姓名、任何签名/水印/AI 生成标识、与主题无关的文字
- **人物要求**：必须基于 referenceImage 保持面部特征一致，严禁画成其他形象
- 末尾加："无水印输出。禁止任何形式文字水印和图片水印。"

### 7.3 504 超时恢复

提交大 base64 时可能超网关 60s 返回 504，但**任务实际已创建成功**。
→ `get_recent_design_works` 找回 taskId，2-5 分钟后再查 SUCCESS 下载。
🚨 **严禁**因 504 切换到 ImageGen 或其他文生图工具。

### 7.4 下载后必检（任一不通过必须重跑）

- 清晰、无第三方水印
- **人物是品牌 IP 本人**（脸型/发型/服装/气质一致度 ≥ 8/10，不一致直接重跑禁止入库）
- 文字正确无乱码、**无真实姓名**
- 主标题与核心记忆点强绑定

**反面教材**：某次上传后审核发现"封面还是没有垫图"——排查是脚本 `spec` 只写了"人物在右下角占 30%"
但**漏了 `referenceImage` 字段**，模型自由发挥画成了不同人物。

---

## 八、左上角花字（仅中间数字人段）

- 位置：左上角，**y ≥ 95px**（不与顶部字幕重叠）
- 内容：核心概念关键词或标题（4-8 字）
- 样式：三层布局（彩色标签 + 白色主标题 + 灰色副标题），深色半透明背景色块

**ffmpeg drawtext 关键经验**：
- fontfile 路径中 `:` 必须转义为 `\:`，如 `C\:/Windows/Fonts/msyhbd.ttc`
- 粗体标题用 `msyhbd.ttc`，普通文字用 `msyh.ttc`
- `box=1:boxcolor=#0a0e1aCC:boxborderw=6~10`（CC = 80% 不透明）

三层叠加示例：
```
drawtext=fontfile='C\:/Windows/Fonts/msyh.ttc':text='核心观点':x=90:y=95:fontsize=24:fontcolor=#2ed573:box=1:boxcolor=#0a0e1aCC:boxborderw=6,
drawtext=fontfile='C\:/Windows/Fonts/msyhbd.ttc':text='主标题':x=90:y=155:fontsize=46:fontcolor=white:box=1:boxcolor=#0a0e1aCC:boxborderw=10,
drawtext=fontfile='C\:/Windows/Fonts/msyh.ttc':text='副标题说明文字':x=90:y=225:fontsize=26:fontcolor=#a0a8c0:box=1:boxcolor=#0a0e1aCC:boxborderw=6
```

---

## 九、踩坑清单速查表

| # | 症状 | 根因 | 正确做法 |
|---|------|------|---------|
| 1 | 数字人只有 9.96 秒 | 生成秒数节点用了模板默认 `"10"` | 显式设为字符串 `"0"` |
| 2 | 数字人是陌生人 | IMAGE 节点用了带鉴权 URL，静默回退模板图 | `upload` 传 base64 原始字节 + 抽帧验证 |
| 3 | `UnidentifiedImageError` | 用 PIL 压缩重编码损坏二进制 / base64 被截断 | 读原始字节，脚本直传 |
| 4 | HTML 段无声音 | concat `-c copy` 时 MP3 轨被静默丢弃 | 统一转码 `-c:a aac -b:a 128k` |
| 5 | 字幕比语音超前累积 1.5s | 帧序列时长略长于 TTS，`-shortest` 在 copy 下不裁视频 | 显式 `-t {tts_dur}` 硬切 |
| 6 | 字幕折成 2-4 行 | 单条 > 12 字，libass 自动换行 | `assert len<=12` + 截断（不折行）|
| 7 | 字幕双层 | SRT 时间重叠 | 校验任意时刻激活字幕 ≤ 1 条 |
| 8 | 字幕对不上 | 帧率混用 | 所有段统一 30fps |
| 9 | 画面卡住 | **B-roll 段静态**（不是数字人）| 查 `.stage` 有无 `.run` class、`getAnimations()` 数量 |
| 10 | B-roll 完全静态 | shell.js 子目录旧副本抛 null 异常中断初始化 | 统一引用根目录 `../_shell.js`，删子目录副本 |
| 11 | 生产页 CSS 全失效 | 生成器 `_head()` 漏了字符串格式化替换 | 补 `% (title, css)` |
| 12 | 装饰动画未加载 | `_ambient.css` 路径错位（页内相对路径解析到子目录）| 用 `../_ambient.css` 或复制到子目录 |
| 13 | 图表纵向拉伸 | SVG `preserveAspectRatio="none"` | 改 `xMidYMid meet` + CSS `aspect-ratio` |
| 14 | 两段 B-roll 同图 | 场景目录被覆盖 | 场景目录按段隔离 + 抽帧 PIL diff 断言 |
| 15 | 门禁 0 svg 却通过 | 门禁脚本文件名拼接 bug | 用真实 num 字段拼路径，不用 sid 切片 |
| 16 | 封面人物不对 | 漏传 `referenceImage` | gpt-image-2 系列必传垫图 |
| 17 | 封面出现真名 | `injectBrandProfile` 默认 True 注入品牌资料 | 显式传 `False` |
| 18 | 卡片文字溢出 | 数值字体过大（80px 粗体中文太宽）| 数值字体上限 52px + 渲染前边界断言 |
| 19 | TTS "AccessToken已失效" | 5 段并发提交 | 逐段串行提交 |
| 20 | DH 任务卡在 QUEUED | 并发提交（RH 并发=1）| 全部丢弃，逐段串行重跑 |
| 21 | 音频"一顿一顿" | 短语内部乱切逗号 + 每逗号叠 `<break>` | 标点只放语义边界；break ≤8/段 |
| 22 | 声音卡顿模糊 | 直接用 TTS 原始 24kHz/32kbps/mono | 上采样 44.1kHz + 192kbps + stereo |
| 23 | DH 开头静止/结尾吞字 | TTS 前置静音被保留 + RH 尾部裁切 50-170ms | 裁头 + `tpad` 补尾 + 重算 SRT |

### 通道 C（短剧带货）专项踩坑

| # | 症状 | 真因 | 硬约束 |
|---|---|---|---|
| C1 | 短剧成片是横构图，发抖音黑边 | `ImpactSwitch` 节点 `select` **模板默认 `"3"`（4:3）** | 每次显式传 `select="4"`（9:16） |
| C2 | 只出 15 秒，剧情没落地 | `duration_seconds` **上限 15**（`fieldData.max=15`），传 30 被截断 | 30 秒必须拆两段生成后 concat |
| C3 | 成片里的产品不是自家产品 | 图片上传失败时 RH **静默用模板默认图**（薄荷绿长发墨镜女）且仍返回 SUCCESS | 双验证：`sourceImageUrl` 前缀 + 抽帧比对"肉眼可见特征"清单 |
| C4 | 第 2 段人物变了脸/换了衣服/换了场景 | 第 2 段首帧没用第 1 段尾帧 | `ffmpeg -sseof -0.1 -i part1.mp4 -frames:v 1` 抽尾帧作首帧 |
| C5 | 拼接处花屏 / 音画不同步 | 两段参数不一致就直接 concat，或用了 `-c copy` | 先各自归一化（1080×1920/30fps/AAC 44100）再 concat，禁 `-c copy` |
| C6 | 成片 30.4 秒有多余尾巴 | AI 出片时长不精确 | concat 时加 `-t 30` 硬切 |
| C7 | IMAGE 节点传了图但没生效 | 模板原有 `fieldValue` 未删除，模板图优先 | 先删 `fieldValue`，再追加 `upload` 传原始字节 base64 |
| C8 | 前 20 秒就露产品，像硬广 | 时间轴没守节奏铁律 | 抽帧验证 0-20 秒无产品；违反打回创作专家 |
| C9 | 结尾看不清产品是什么 | 25-30 秒未做正面标识露出 | 抽帧验证结尾段标识清晰 |
| C10 | 烧上的字幕全错位 | AI 生成音频**无精确时间轴**，硬凑时间 | 短剧默认不烧字幕；必须烧则先人工听写对齐 |
| C11 | 两段任务都卡 QUEUED | 并发提交（RH 并发=1，且第 2 段依赖第 1 段尾帧） | 严格串行，第 1 段 SUCCESS 且抽帧后才提第 2 段 |

---

## 十、元教训

1. **素材改完 ≠ 成片改完** —— 这是连续 9 轮返工的真正根因。任何"我改好了"必须以成片重新渲染并通过六步硬检查为准。
2. **前置校验 > 事后验证** —— 把闸口从"渲染完再看"提前到"不合规就拒绝渲染"。
3. **门禁不能放宽** —— 删断言、调阈值、改文件名凑通过，都是把问题推到用户眼前。
4. **优雅是奖励项，稳定是生死线** —— 除非明确要求，不为"更优雅"重构已能稳定跑的模块。
5. **同一个坑连踩 2 次 → 必须升级为硬约束**（加 🚨 标识写进 Agent MD）。
