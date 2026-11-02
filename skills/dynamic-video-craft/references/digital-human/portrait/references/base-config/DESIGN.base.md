# DESIGN.md · 拾光抖音 B-roll 视觉规范 v7

> 本文件是**像素级视觉配置的单一真相源**。与 `STORYBOARD.md` v7、`demo.html` v10 严格一致；
> 渲视频前必须先提交给东哥**肉眼验收通过**（配置确认闸）。
> 东哥@继续·等效授权：本规范由拾光（自动化）维护。

---

## 〇、本版本要点

| 维度 | v6 旧版（已废） | v7 新版（按 demo v10） |
|---|---|---|
| 底色 | `#E9EDF3` 浅蓝灰学术风 | `#F6F5EC` **暖米底** + `rgba(26,26,26,.04)` 24px 细网格 |
| 卡片样式 | 无系统化规范 | **8px 黑粗边框 + 28 圆角 + 彩色偏移硬阴影**（禁模糊阴影） |
| 阴影类型 | 默认 `0 4px 12px rgba(0,0,0,.1)` 模糊 | **禁用**；只允许 colored offset hard shadow `box-shadow: 6px 6px 0 #C7FF2F` |
| 字体 | 默认 SimSun | SimHei 标题主 / STXingkai 随手记手写 / 默认 Arial 副文 |
| 字幕位置 | 不限 | 中部横板框 ≤2 行 + 关键词荧光色块 |
| 11 镜组件 | 5 组件模板 | **11 镜** = 5 原组件 + 2 主卡带图（mc-imgleft / mc-imgtop）+ 2 完整版式 + 2 横版真源 |
| 下半区 | 无 | **2/3 随手记 `.sticky` + 1/3 topics/dh/note**（Playwright 实测 ratio=2.000） |
| 时长铁律 | 单 DH 段 ≤35s | **每镜 ≤10s**（除非画面含较多字幕可延，但其它画面静止） |

---

## 一、画布与坐标系

### 1.1 主画布

| 项 | 值 |
|---|---|
| 像素 | **1080 × 1920** |
| 缩放比 | demo HTML 0.5 → 540 × 960 |
| 安全区 | x:40–1040，y:130–1810 |
| 字号基线 | **竖版主标题 100px / 副标 60px / 正文 36px** |
| 网格 | 24px 细网格 `rgba(26,26,26,.04)`（背景叠层） |

### 1.2 5 区坐标（每镜统一强制）

```
y=0
  ↓
① 顶（章节条）     y: 130–240   高 110    class .top-bar
  ↓
② 主卡（5 选1 组件） y: 280–1080  高 800    class .main > .plate
  ↓
③ 字幕条           y: 1110–1270 高 160    class .sub
  ↓
④ 下半区           y: 1310–1740 高 430    class .bot
       ├── .sticky    flex: 0 0 654.67px（占 2/3）
       └── .topics /  flex: 1 327.33px（占 1/3）
           .note /
           .dh
  ↓
⑤ 页脚             y: 1770–1810 高 40     class .foot
y=1920
```

> **绝不允许任何元素越出这 5 区边界**（#5.37 铁律 + Playwright 量化验收硬约束）。

---

## 二、颜色体系（palette）

### 2.1 基础色（base）

| 变量 | HEX | 用途 |
|---|---|---|
| `--cream` | `#F6F5EC` | **画布底色**（暖米，非浅蓝灰） |
| `--white` | `#FFFFFF` | 卡片底色 |
| `--ink` | `#1A1A1A` | 主文字 + 边框（黑） |
| `--gray` | `#8A94A6` | 副文字 + 弱描边 |

### 2.2 荧光色系（neon palette）

| 变量 | HEX | 用途 |
|---|---|---|
| `--green` | `#C7FF2F` | **关键词高亮 / 章节点 / active 高亮** |
| `--coral` | `#FE6449` | 暖珊瑚 / 重要反转词高亮 |
| `--skyblue` | `#76D5FE` | 浅蓝 / 时点词高亮 |
| `--purple` | `#A588FD` | 紫 / 引用词高亮 |
| `--yellow` | `#FDE676` | 暖黄 / 强调词高亮 |
| `--pink` | `#F8B4D9` | 粉 / vs 类目左列 |
| `--skgray` | `#A8DADC` | 灰蓝 / vs 类目右列 |
| `--deeppink` | `#FF5A5F` | 深红 / 强警示 |

### 2.3 阴影（shadow）

> **禁止使用模糊阴影**（`box-shadow: 0 4px 12px rgba(0,0,0,.1)` 一律禁用）。

| 类型 | 写法 | 用途 |
|---|---|---|
| 彩色偏移硬阴影（推荐） | `box-shadow: 6px 6px 0 #C7FF2F` | 卡片正面 highlight |
| 强下沉阴影（推荐） | `box-shadow: 0 4px 0 #1A1A1A` | active 卡 / 字幕条 |
| 紫色偏移（mc-imgleft） | `box-shadow: 8px 8px 0 #A588FD` | 图占位卡 |
| 暖黄色偏移（.sticky） | `box-shadow: 6px 6px 0 #C7FF2F` | 随手记固定装饰 |
| 黑色硬偏移（数字人） | `box-shadow: 6px 6px 0 rgba(0,0,0,.5)` | 数字人占位 |
| 模糊阴影 | ❌ **禁用** | —— |

---

## 三、字体规范

| 用途 | 字体 | 字号（竖版 1080 基准） | 字重 | 颜色 |
|---|---|---|---|---|
| 主标题 | SimHei 或 Source Han Sans Bold | 80–100px | 900 | `#1A1A1A` |
| 副标题 | SimHei | 50–60px | 800 | `#1A1A1A` |
| 正文 | SimHei | 32–36px | 600 | `#1A1A1A` |
| 字幕条 | SimHei | 54px | 700 | `#1A1A1A`，关键词荧光色块高亮 |
| 章节条 `CH 0X` | SimHei | 36px | 900 | `#1A1A1A` |
| 随手记手写 | STXingkai / 华文行楷 / KaiTi | 42–54px | regular | `#1A1A1A` |
| 数字 / 数据 | Arial Black | 80–120px | 900 | `#1A1A1A` |

---

## 四、5 区元素规范

### 4.1 顶（章节条 `.top-bar`）

```
.class .top-bar {
  position: absolute;
  left: 40; width: 1000;
  top: 130; height: 110;
  display: flex; align-items: center; justify-content: space-between;
  padding: 0 36px;
  background: var(--white);
  border: 7px solid var(--ink);
  border-radius: 24;
  box-shadow: 0 4px 0 var(--ink);
}
.top-bar .dot { width: 18; height: 18; border-radius: 50%; background: var(--green); }
.top-bar .lbl { font-size: 36; font-weight: 900; letter-spacing: 2; }
.top-bar .ts  { font-size: 32; font-weight: 800; color: var(--gray); }
```

元素：左 `绿点 + CH 0X · 章节名` / 右 `MM:SS 时间码`。

### 4.2 主卡 `.main > .plate`（核心 11 镜组件模板）

> 5 选 1 组件模板；每镜必带；
> 主卡高 **800px**（y280–1080），禁止纯文字居中（必须丰满）。

#### 4.2.1 `ctitle`（镜 1 标题页）

| 元素 | 写法 |
|---|---|
| 顶部小徽章 | `<span class="badge t-c">拾光 · AI 工程化</span>` —— 黄底 + 7px 黑边框 + 22 圆角 |
| 主标题 | 80–100px 粗黑；三行；包含 1–2 个 `<span class="hl-g">荧光色块高亮</span>` 关键词 |
| 总结条 | `.summary` 紫底 + 黑粗边框 + 6px 紫偏移阴影 |

#### 4.2.2 `items3`（镜 2 三色大卡）

| 元素 | 写法 |
|---|---|
| 容器 | `display: flex; gap: 24; flex: 1; margin-top: auto` |
| 3 横卡 | flex:1；粉/绿/蓝；8px 黑粗边框 + 28 圆角 + 彩色偏移硬阴影 |
| 每卡 | 标题（50px 粗）+ 1 行副文 + 1 个荧光胶囊 |

#### 4.2.3 `items4`（镜 3 四卡+数字圆）

| 元素 | 写法 |
|---|---|
| 容器 | `display: flex; flex-wrap: wrap; gap: 24; flex: 1` |
| 4 白卡 | flex 1 1 48%；白底 + 6px 黑粗边框 + 24 圆角 + 8px 紫/绿/黄偏移阴影 |
| 编号圆 | 左上角 60×60 圆环（黄/绿/珊瑚/紫轮替） |
| 标题下划线 | 4 段彩色横线（黑底 4px） |

#### 4.2.4 `versus`（镜 4 双栏对比）

| 元素 | 写法 |
|---|---|
| 容器 | `display: flex; align-items: center; gap: 24; flex: 1; max-height: 100%; overflow: hidden` |
| 左列（粉） | 标题 / 6 个 `.box` 胶囊标签（EPUB/PDF/TXT/MD/SRT/VTT） |
| 中央箭头 | `→` 80px 粗黑字 |
| 右列（浅蓝） | 标题 / 3 个 `.box` 胶囊标签 |
| 行 flex | `.row { display: flex; flex-wrap: wrap; gap: 8; margin-top: 10 }` |

#### 4.2.5 `bstat`（镜 5 数据大卡）

| 元素 | 写法 |
|---|---|
| 容器 | `display: flex; flex-wrap: wrap; gap: 24; flex: 1` |
| 3 大数据卡 | 4 黑粗边框 + 28 圆角；数字 **80–120px 粗体**；标签 28px 灰 |
| 配色 | 卡 1 = 绿底 + 绿色偏移 / 卡 2 = 浅蓝 + 浅蓝偏移 / 卡 3 = 粉 + 粉色偏移 |
| 总结条 | 黄底黑粗边框「增速翻倍 / 企业 90% 普及」 |

#### 4.2.6 `mc-imgleft`（镜 6 左图右文·**新增**）

| 元素 | 写法 |
|---|---|
| 容器 | `display: flex; gap: 32; flex: 1; align-items: stretch` |
| 左图 42% | `.img-ph`：暖米斜纹 + 7px 黑粗边框 + 20 圆角 + 紫偏移阴影 + 「AI 图」荧光角标 + 1024×1024 条码 |
| 右文 58% | kicker（紫底 + 22 圆角）/ 主标题（50px hl-g 高亮）/ 3 `.point`（黄底编号圆 + 文字）/ 2 `.mini`（浅蓝 mini 卡） |

#### 4.2.7 `mc-imgtop`（镜 7 上图下卡·**新增**）

| 元素 | 写法 |
|---|---|
| 容器 | `display: flex; flex-direction: column; gap: 24; flex: 1` |
| 上图 34% | `.img-ph` 宽幅 + 1280×720 条码 |
| 下卡 66% | 3 横卡（粉/绿/蓝固定配色）+ 标题 + 3 个 `.pill` 胶囊 |

### 4.3 字幕条 `.sub`

```css
.sub {
  position: absolute;
  left: 40; top: 1110; width: 1000; height: 160;
  padding: 24 36;
  display: flex; flex-direction: column; justify-content: center; align-items: center;
  background: var(--white);
  border: 7px solid var(--ink);
  border-radius: 20;
  box-shadow: 0 4px 0 var(--ink);
  font-family: SimHei;
  font-size: 54; font-weight: 700;
  text-align: center;
}
.sub .line { max-height: 60px; overflow: hidden; }
.sub .hl-g { background: var(--green); padding: 0 8; }
.sub .hl-c { background: var(--coral); padding: 0 8; color: var(--white); }
.sub .hl-b { background: var(--skyblue); padding: 0 8; }
.sub .hl-p { background: var(--purple); padding: 0 8; color: var(--white); }
.sub .hl-y { background: var(--yellow); padding: 0 8; }
```

铁律：
- ≤2 行
- 关键词荧光色块高亮（≤3 个/镜）
- 超长按句滚动（**主卡 + 数字人 必须静止**）
- 必有中文标点（`punctuate_subs()`）

### 4.4 下半区 `.bot`

```css
.bot {
  position: absolute;
  left: 40; top: 1310; width: 1000; height: 430;
  display: flex; gap: 18;
}

/* 左 sticky：2/3 */
.sticky {
  flex: 0 0 calc((1000px - 18px) * 2 / 3);  /* ≈ 654.67 */
  background: var(--white);
  border: 7px solid var(--ink);
  border-radius: 26;
  padding: 22 24;
  box-shadow: 6px 6px 0 var(--green);
  display: flex; flex-direction: column;
  font-family: STXingkai;
}
.sticky .st-corner {
  position: absolute; top: 18; right: 18;
  font-family: SimHei; font-size: 18; font-weight: 800;
  background: var(--green); color: var(--ink);
  padding: 4 14; border: 4px solid var(--ink); border-radius: 12;
}
.sticky .st-title {
  display: flex; align-items: center; gap: 10;
  font-family: SimHei; font-size: 42; font-weight: 900;
  margin: 24px 0 18px 0; letter-spacing: 1;
}
.sticky .st-title .diamond { color: var(--green); font-size: 50; }
.sticky .st-hand {
  flex: 1; font-family: STXingkai;
  font-size: 54; line-height: 1.5; color: var(--ink);
}
.sticky .st-hand .mark-y { background: var(--yellow); }
.sticky .st-hand .strike { text-decoration: line-through; color: var(--purple); }
.sticky .st-tag-row {
  display: flex; flex-wrap: wrap; gap: 8;
  margin-top: 16;
  font-family: SimHei;
}
.sticky .st-tag {
  font-size: 22; font-weight: 700;
  padding: 8 16; border-radius: 18; border: 3px solid var(--ink);
}
.sticky .st-tag.t-y { background: var(--yellow); }
.sticky .st-tag.t-g { background: var(--green); }
.sticky .st-tag.t-c { background: var(--coral); color: var(--white); }
.sticky .st-tag.t-p { background: var(--pink); }
.sticky .st-tag.t-b { background: var(--skyblue); }

/* 右侧 topics / dh / note：1/3 */
.topics { flex: 1; display: flex; flex-direction: column; gap: 14; }
.topic-card {
  height: 74;
  background: var(--white);
  border: 3px solid #b8c0cc;
  border-radius: 14;
  display: flex; align-items: center;
  padding: 0 26;
  font-size: 30; font-weight: 800; color: var(--ink);
  position: relative;
}
.topic-card.active {
  border: 5px solid var(--ink);
  background: var(--green);
  box-shadow: 0 4px 0 var(--ink);
}
.topic-card .arrow {
  position: absolute; left: -22px; top: 50%; transform: translateY(-50%);
  border-top: 14px solid transparent;
  border-bottom: 14px solid transparent;
  border-right: 16px solid var(--ink);
  display: none;
}
.topic-card.active .arrow { display: block; }

/* 数字人右下（镜 9 专用） */
.dh {
  flex: 1;
  background: linear-gradient(135deg, #5a5a5a 0%, #1a1a1a 100%);
  border: 10px solid var(--white);
  border-radius: 24;
  display: flex; align-items: center; justify-content: center;
  color: #888; font-size: 28; font-weight: 700;
  text-align: center;
  box-shadow: 6px 6px 0 rgba(0, 0, 0, .5);
}
.dh .inner {
  background: rgba(0,0,0,.4);
  padding: 24 32;
  border-radius: 14;
  line-height: 1.6;
}
```

### 4.5 页脚 `.foot`

```css
.foot {
  position: absolute;
  left: 40; top: 1770; width: 1000; height: 40;
  font-size: 22; font-weight: 700; color: var(--gray);
  letter-spacing: 2;
  display: flex; justify-content: space-between; align-items: center;
}
```

元素：左「@拾光 · AI 工程化」/ 右「dh 2026」。

### 4.6 数字人位置铁律（#5.39 · 最高优先级·v7.1 新增）

> **08-22 真实成片曾犯过的错（铁证 `assemble_0822.py:82-83`）**：
> 旧代码 `[1:v]scale=1080:800:force_original_aspect_ratio=increase,crop=1080:800[dh];[0:v][dh]overlay=0:700` 把 DH 视频整块塞进 **y=700~1500 中区**，把中区主卡/字幕条位置全占了。东哥指出"数字人跑到中区了，中区不是放字幕的横板卡片吗"——**本节为永不再犯的铁律**。

| 项 | 规定 |
|---|---|
| **DH 唯一位置** | **下半区右下 1/3**（`.bot` flex 容器内的 `.dh`，flex:1，x≈676 / y=1310 / w≈324 / h=430） |
| **❌ 绝对禁止** | DH 出现在 **中区**（y=700~1500）、上半区（y=0~700）、左下 `.sticky` 区（占左 2/3） |
| **中区归属** | **主卡**（`.main > .plate`，11 模板）+ **字幕条**（`.sub`，y=1110~1270）—— 严禁 DH 侵占 |
| **渲染 overlay 坐标硬约束** | DH 视频必须 `overlay=<x≥676>:<y≥1310>`，缩放后必须 `≤324×430`；**禁止 `overlay=0:700` 等占据中区的写法** |
| **下半区左 2/3** | `.sticky`（随手记便签），与 DH 间距 ≥30px |
| **DH 段判定（v7.1 修正）** | **P1a / P1b / P3a / P3b / P6 共 5 段为 DH 段**；其余 P2 / P4 / P5 用 `.topics` 5 主题卡 |
| **末尾必须有 DH** | P6 = DH 收尾段（v7.1 新增），见 STORYBOARD.md §5.1 / §5.4。**禁止把 P5 三层带走作为整片末尾** |

违反后果：直接报东哥决策，**禁止**为兼容旧代码而降级 DH 位置；禁止以"实现成本高"为由删除 P6 收尾。

---

## 五、镜位组件模板总览（11 模板 → 9 出镜 + 2 横版参考）

> ⚠️ 本节只是**可复用的版面模板**（"样子"），**不是视频分镜顺序**。
> 真·顺序分镜（7 段 TTS / 4 段数字人 / ≈50+ 镜 / 总时长 ≈298s）见 `STORYBOARD.md` **§五 成片顺序架构**。

| 镜# | 模板 | 主卡类 | 出图需求 | 时长 |
|---|---|---|---|---|
| 1 | `ctitle` | `.plate > ctitle` | 无 | ≤8s |
| 2 | `items3` | `.plate > items3` | 无 | ≤10s |
| 3 | `items4` | `.plate > items4` | 无 | ≤10s |
| 4 | `versus` | `.plate > versus` | 无 | ≤10s |
| 5 | `bstat` | `.plate > bstat` | 无 | ≤10s |
| 6 | `mc-imgleft` | `.plate > mc-imgleft` | **gpt-image-2 1024×1024** | ≤10s |
| 7 | `mc-imgtop` | `.plate > mc-imgtop` | **gpt-image-2 1280×720** | ≤10s |
| 8 | `no-DH` (完整版式) | `.plate` 内含 bstat/b/items… + `.bot` = sticky + topics | 无 | ≤10s |
| 9 | `with-DH` (完整版式) | `.plate` 内含 ctitle/mc-summary + `.bot` = sticky + DH | **DH 由 RunningHub LTX2.3 出** | ≤10s |
| 10 | `horiz-frame` | `.horiz-frame` 横版 1280×720 | —— | 不计时（仅参考） |
| 11 | `horiz-frame` | 同上 | —— | 不计时（仅参考） |

---

## 六、出图铁律（最高优先级·#62·#71·禁止降级）

1. **唯一生图通道**：`create_design_work`
   - `modelSelection="provider_runtime_image_duoyuanx_unified::gpt-image-2"`
   - `designType="信息图海报"`（中文类型名）
   - `imageSize="1024x1024"` 或 `"1280x720"`
   - `injectBrandProfile=false`
   - **完整中文画面描述必须放 `additionalInstruction` 字段**
   - **`spec` 仅填尺寸**（绝不可塞整段提示词 —— 平台会截断回退到「社媒轮播图」品牌模板）
2. **PIL / Pillow 绝对禁用**（#71 铁律）：
   - 不允许用 PIL 创建图片
   - 不允许用 PIL 合成/叠字/兜底
   - 通道故障期用 `.ai-pending` / `.img-ph` 占位，**绝不允许降级 PIL**
3. **数字人**（镜 9）：RunningHub LTX2.3 模板；prompt 必须含 `no microphone, no handheld items, no glasses, plain black t-shirt only`（#75 铁律）。

---

## 七、动效

| 类 | 动效 | 时长 | 缓动 |
|---|---|---|---|
| 主标题行 stagger | `fade-in + translateY(20px → 0)` | 0.4s/行 | ease-out |
| 卡 stagger | `fade-in` | 0.3s/卡 | ease-out |
| 数字人 | LTX2.3 实时口型 | 跟随 TTS | —— |
| `topic-card.active` | 下沉阴影闪烁（持续） | 1.5s loop | ease-in-out |
| `.sticky .diamond` | 闪烁 | 2s loop | linear |
| 主卡垂直晃动 | **禁用**（`BREATH_JS return 0`） | —— | —— |

---

## 八、配置确认闸（强制）

每轮视频生产前**必须**走完：

1. ✅ `STORYBOARD.md` v7 + `DESIGN.md` v7 像素级对齐 demo v10。
2. ✅ Playwright 实测：
   - 9 镜竖版 5 区齐全
   - sticky:topics 宽比 = 2.000 ±0.05
   - 主卡内组件 `mcOver=0`
   - 图占位不超主卡边界
3. ✅ 出图铁律校验：`create_design_work` 通道可用 + token 未过期（`~/.workbuddy/mcp.json`）。
4. ✅ TTS 通道可用 + `punctuate_subs()` 输出非空。
5. ✅ DH 通道（镜 9）RunningHub 任务不超 60s 失败率（每镜 ≤30s）。

5 项全绿，才允许进入正式视频渲染。

---

## 九、版本与变更日志

| 版本 | 日期 | 主要变更 |
|---|---|---|
| v1–v5（已废） | 2026-08 之前 | `#E9EDF3` 浅蓝灰学术风 |
| v6（已废） | 2026-08-22 上午 | 浅蓝灰 + 5 区域雏形 |
| v7 | 2026-08-22 23:15 | 暖米底 + 8px 粗边框 + 彩色偏移硬阴影 + 11 镜完全对位 demo v10 + 每镜 ≤10s |
| **v7.1（当前）** | **2026-08-23 00:10** | **新增 §4.6 数字人位置铁律（#5.39）：DH 唯一位置 = 下半区右下 1/3，渲染 overlay 必须 `x≥676 / y≥1310`，禁止 `overlay=0:700` 占中区；P6 收尾段必须为 DH 段** |

---

> 任何与本文件冲突的旧规范一律作废；
> 以本文件 + `STORYBOARD.md` v7 + `demo.html` v10 像素级裁决。
