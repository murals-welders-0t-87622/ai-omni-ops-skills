# 卡片动效映射规范（card-motion-mapping）

> 本文件是 `douyin-dh-landscape-remotion-video` 的**分镜落地真源**之一。
> 规定：`STORYBOARD.md` 的每个 `SHOT` 必须标注它使用的**卡片动效 ID**，
> 且 ID 必须来自 `references/cards/` 下那 78 张卡片之一。
>
> 用户 2026-08-31 定版：分镜里写的动效名，必须是卡片库里的命名，不能是自造的内部动效名，
> 也不能是"弹入 / 淡入 / idle 呼吸"这类通用动作描述。

---

## 一、为什么必须有这一层

卡片（card）是本 Skill 的**可执行 B-roll 单元**：每张卡片同时定义了动效、参数口径、
源码母本（`template/cards/<id>.tsx`）和已知坑。分镜里写了卡片 ID，Remotion 制作阶段
才能直接取源码、按参数复现，不需要二次翻译。

三种写法的差别：

| 写法 | 能不能直接用 | 问题 |
|---|---|---|
| `evidence-scroll-tour` | ✅ 能 | 卡片库有，源码在 `template/cards/evidence-scroll-tour.tsx` |
| `长页从下往上滚` | ❌ 不能 | 是动作描述，执行者要猜用哪张卡 |
| `custom-page-scroll` | ❌ 不能 | 自造名，卡片库里没有，源码不存在 |

---

## 二、卡片库在哪

```
references/cards/          78 张卡片说明文档（frontmatter 含 标题/类别/能量/优先级/一句话/适用）
template/cards/            78 份卡片 Remotion tsx 源码
demos/<card-id>/           每张卡的可播放 HTML demo
```

**文件名即卡片 ID**。例如 `references/cards/danmu-bubble-praise.md` → 卡片 ID `danmu-bubble-praise`。

读取卡片元信息（不依赖 yaml 库）：

```python
import re, io
raw = io.open('references/cards/<id>.md', encoding='utf-8').read()
m = re.match(r'---\s*\n(.*?)\n---\s*\n', raw, re.DOTALL)
# frontmatter 里的键：name / 标题 / 优先级 / 代码 / 一句话 / 适用 / 时长 / 能量 / 类别
```

批量建索引用 `scripts/match_cards.py --index`。

---

## 三、STORYBOARD 的字段规范

每个 `SHOT` 在「动效」字段**之后**必须有「卡片动效」字段：

```markdown
### SHOT 03-2 ｜ 央视 41% · 权威背书 ｜ `01:25.0 – 01:33.0`（8.0s）

- **口播原文**：…
- **A/B 主次**：`B 主`
- **数字人形态**：`HOST_HIDDEN`
- **画面内容**：…
- **字幕**（`SUB_CHIP`）：…
- **动效**：
  - `0.00s` 人完全让位（淡出 0.30s + 下沉 8px）
  - `0.60s` `bar-chart-growth`：中国柱 `0 → 41%`
- **卡片动效**：`news-card-desk`、`bar-chart-growth`、`highlighter-sweep`
- **七层**：…
- **素材**：…
- **转场**：…
```

规则：

1. 每个镜头 **1~3 张卡片**，按主次排序，第一张是本镜的**主卡**
2. 转场镜头把转场卡列入（如 `overexpose-flip-transition`），但转场卡排在末位
3. 一个镜头里数字人形态变化用 `host-shrink-to-chip` 标注，不要另造"人物缩位"
4. 没有合适卡片时宁可少填，**禁止硬凑**
5. 卡片 ID 必须与 `references/cards/` 文件名完全一致

---

## 四、映射方法

### 1. 命名动效 → 卡片（直接映射）

分镜里已出现的内部动效名，按此表转成卡片 ID：

| 内部动效名 | 卡片 ID |
|---|---|
| `black-slam` | `black-slam-transition` |
| `push-through` | `push-through-transition` |
| `overexpose-flip` | `overexpose-flip-transition` |
| `whip-pan` | `whip-pan-transition` |
| `slab-punch` / `slab` | `slab-punch-title` |
| `pop` | `media-pop-in` |
| `retire` | `strike-and-replace` |
| `stroke-dasharray` | `line-chart-story-draw` |
| `typewriter` | `typewriter-reveal` |
| `number-slab-pop` | `number-slab-pop` |
| `number-counter` | `number-counter` |
| `bar-chart-growth` | `bar-chart-growth` |
| `highlighter-sweep` | `highlighter-sweep` |
| `scribble-annotation` | `scribble-annotation` |
| `evidence-scroll-tour` | `evidence-scroll-tour` |
| `focus-dim-spotlight` | `focus-dim-spotlight` |
| `host-shrink-to-chip` | `host-shrink-to-chip` |
| `converging-arrows` | `converging-arrows` |
| `keyword-pop-highlight` | `keyword-pop-highlight` |
| `soft-blur-in` | `soft-blur-in` |
| `callout-line-label` | `callout-line-label` |
| `strike-and-replace` | `strike-and-replace` |
| `numbered-step-stack` | `numbered-step-stack` |
| `sway-parallax` / `sway` | `sway-parallax` |
| `slow-pull-reveal` / `slow-pull` | `slow-pull-reveal` |
| `life.tsx` | 无对应卡，它是全局 idle 微动系统，不占卡片位 |

### 2. 画面语义 → 卡片（描述型镜头）

| 画面在做什么 | 候选卡片 |
|---|---|
| 开场数字对撞 / 冲击大字 | `impact-open-title`、`number-slab-pop`、`black-slam-transition` |
| 人物出场 / 回归 | `soft-blur-in`、`lower-third-nameplate` |
| 人物缩到角标让位 | `host-shrink-to-chip` |
| 步骤 / 流程 / 编号清单 | `numbered-step-stack`、`step-timeline-vertical` |
| 时间轴 / 年份节点 | `step-timeline-vertical` |
| 划掉旧说法换成新说法 | `strike-and-replace` |
| 文件 / 图块被吸入聚合 | `gooey-morph`、`media-pop-in` |
| 长文档 / 搜索结果慢滚 | `evidence-scroll-tour`、`stage-keyframe-tour` |
| 手绘圈注重点 | `scribble-annotation`、`hand-drawn-ellipse` |
| 柱状图 / 占比对比 | `bar-chart-growth`、`chart-grow` |
| 折线 / 阶梯推演 | `line-chart-story-draw` |
| 单个数字跳动 | `number-counter`、`number-slab-pop` |
| 数字带趋势小图 | `metric-with-sparkline`、`count-badge-title` |
| 名词 / 概念解释卡 | `info-term-card` |
| 多行表格逐行聚焦 | `focus-dim-spotlight` |
| 双栏 / 对照表对比 | `type-contrast-emphasis`、`alt-block-lines` |
| 新闻 / 权威报道引用 | `news-card-desk`、`highlighter-sweep` |
| 界面 / 系统架构演示 | `ui-flow-theater`、`ui-prop-theater` |
| 终端 / 命令行推进 | `terminal-typing-log`、`claude-code` |
| 聊天 / 问答气泡 | `chat-message-flow`、`chat-gpt` |
| 警示 / 风险提示条 | `color-slam-beat-card` |
| 章节引入 / 切换 | `chapter-title-card`、`chapter-progress-list` |
| 金句 / 结论大字 | `quote-card`、`quote-hold-arrow`、`slab-punch-title` |
| 关键词弹出强调 | `keyword-pop-highlight`（**全片 ≤3 次**） |
| 收尾视差 / 缓拉全貌 | `sway-parallax`、`slow-pull-reveal` |
| 局部放大看细节 | `magnifier-detail`、`pip-zoom-box` |
| 评论区共识 / 弹幕氛围 | `danmu-bubble-praise` |

### 3. 转场卡单独判

| 段落关系 | 转场卡 |
|---|---|
| 递进 / 承接 | `push-through-transition` |
| 换章节 / 翻页 | `overexpose-flip-transition` |
| 并列关系 | `whip-pan-transition` |
| 最大反转（全片 ≤1 次） | `black-slam-transition` |
| 收束 | `slow-pull-reveal` |

同一条视频**不要把六式转场全用一遍**。

---

## 五、脚本

`scripts/match_cards.py` 提供两个能力：

```bash
# 生成 78 张卡片索引
python scripts/match_cards.py --index --cards references/cards --out _卡片索引.md

# 把卡片 ID 写进 STORYBOARD.md（在每个 SHOT 的「动效」字段后插入「卡片动效」）
python scripts/match_cards.py --storyboard STORYBOARD.md --cards references/cards --map mapping.json
```

`--map` 接受一个 JSON：

```json
{
  "01-1": ["black-slam-transition", "number-slab-pop", "impact-open-title"],
  "01-2": ["soft-blur-in", "push-through-transition", "impact-open-title"]
}
```

脚本会：

1. 校验每个 ID 都存在于 `references/cards/`，不存在直接报错并列出可用 ID
2. 先清理已有的「卡片动效」行再插入，可重复运行（幂等）
3. 输出每个镜头的映射结果供人工复核

---

## 六、踩坑

1. **不要用宽泛中文关键词自动匹配**。实测用"数字"做关键词会把 `number-counter`
   塞进 20+ 个无关镜头（时间轴、架构图、情绪落点都被污染）。**必须逐镜人工判定**，
   脚本只负责写入与校验。
2. **转场卡不要当内容卡**。镜头里有"转场"字样才填转场卡，普通内容镜头填 `whip-pan-transition`
   会让 Remotion 阶段误以为整镜都是转场。
3. **改了映射要重跑清理再插入**。脚本幂等，但如果手工改过 `STORYBOARD.md`，
   先跑一次 `--clean` 再 `--apply`，避免同一镜头出现两行「卡片动效」。
4. **78 张卡不是每张都适合口播解说**。`claude-code`、`tilt-3d-page`、`map-route-pin`、
   `logo-enter`、`subscribe-cta`、`x-follow-card` 这几张场景很窄，
   商业口播里基本用不上，不要为了"用满卡片库"硬塞。
5. **`subscribe-cta`、`x-follow-card` 属诱导关注卡**，抖音 / 公众号合规口径下默认禁用
   （团队红线 #47 零动作索取），分镜里出现要主动删掉。
