---
name: douyin-dh-landscape-remotion-video
description: 口播数字人 + 横屏 + Remotion 高动态视频。用于把已成型的口播内容制作成高质量横屏数字人口播视频：A-roll 仍是数字人，但允许透明背景贴边、缩位到角落或阶段性让位；B-roll 统一用 Remotion 渲出高质量动态效果，并按画面需要决定是否同时保留数字人。正式制作前必须先生成 `DESIGN.md`、`STORYBOARD.md`、`demo.html`，用户确认后再进入生产。
---

> 当前技能库适配：本文件保留用户提供的原业务流程与完整随包文件；旧专家团路径通过邻近 team-references 提供，历史模型、账号和并发经验不能代替当前 MCP 实际定义。按用户当前要求、品牌及授权执行。

# 口播数字人 + 横屏 + Remotion 高动态视频

## 本地补充：高级视觉与动态设计

高端网站或海报风格的横屏数字人 Remotion 项目执行 [高级视觉与动态设计](references/editorial-video-art-direction.md)，保留三份配置、确认门槛及预览生产同源。

> 脚本实测提示：`scripts/vad_align.py` 不支持 `--help`，直接运行会写入默认路径；必须提供独立任务目录 `--dir <任务目录>`，使用前先检查输出文件，避免覆盖现有时间轴。

## 一、这条 Skill 的定位

这是数字人视频专家下面的**横屏高质量口播** Skill。

它不是普通的“横屏数字人口播”，而是把下面两部分合并成一条高质量产线：

1. **数字人 A-roll**
   - 负责主持、连接、转段、结论
   - 不能消失成纯配音 PPT

2. **Remotion B-roll**
   - 负责证据、图表、界面、引用、截图、长页巡游、信息件、章法转场
   - 不能退化成静态 HTML 翻页

最终目标是：

1. A-roll 仍然是“这个人在讲”
2. B-roll 仍然是“真正的信息主舞台”
3. 两者在每个镜头内按主次切换，而不是机械地一人一页轮换

---

## 二、这次已经内化进本 Skill 的上游内容

这次不再把外链只当“参考链接”，而是已经把与本 Skill **直接相关**的上游真源和关键源码读进来了，并转写成本地规则。

### 1. 本地可直接打开的提取文档

- `video-talkcraft-source-SKILL.md`
- `talkcraft-extracted-playbook.md`
- `talkcraft-source-manifest.md`
- `talkcraft-upstream-read-index.md`
- `template.md`

### 2. 本地已提取的上游内容

下面这些文件都在当前 Skill 目录里。上游工艺以这些本地镜像和模板为准；专家团业务链路、数字人配置格式与交接字段以本 Skill 目录外的团队真源为准，路径在第十三节明确给出。

- `video-talkcraft-source-SKILL.md`
- `talkcraft-extracted-playbook.md`
- `talkcraft-source-manifest.md`
- `talkcraft-upstream-read-index.md`
- `template.md`
- `references/design-language.md`
- `references/shot-design.md`
- `references/cinematography.md`
- `references/taxonomy.md`
- `references/host-footage.md`
- `references/shotbook-example.md`
- `references/demo-spec.md`
- `references/card-motion-mapping.md`（卡片动效映射规范，STORYBOARD 必填字段的真源）
- `references/cards/highlighter-sweep.md`
- `references/cards/focus-dim-spotlight.md`
- `references/cards/evidence-scroll-tour.md`
- `references/cards/host-shrink-to-chip.md`
- `references/cards/`（已完整落地 78 张卡片参考文档）
- `template/cards/highlighter-sweep.tsx`
- `template/cards/focus-dim-spotlight.tsx`
- `template/cards/evidence-scroll-tour.tsx`
- `template/cards/host-shrink-to-chip.tsx`
- `template/cards/`（已完整落地 78 份卡片 tsx 源码）
- `template/motion-systems/camera.tsx`
- `template/motion-systems/life.tsx`
- `template/motion-systems/transitions.tsx`
- `template/motion-systems/theme.ts`
- `template/motion-systems/Subtitles.tsx`
- `template/motion-systems/`（已完整落地上游 motion systems 目录）
- `demos/`（已完整落地上游 demos 目录）
- `assets/`（已完整落地上游 assets 目录）
- `scripts/`（已完整落地上游 scripts 目录）
- `examples/DESIGN.example.md`
- `examples/STORYBOARD.example.md`
- `examples/demo.example.html`

### 3. 上游文件清单放哪里看

如果你想核对我到底吸收了哪些 `video-talkcraft` 上游文件：

1. 先看 `video-talkcraft-source-SKILL.md`
2. 再看 `talkcraft-source-manifest.md`
3. 再看 `talkcraft-upstream-read-index.md`

主 Skill 里不再铺“当前工作区并不存在”的上游相对路径，避免误导。

---

## 三、适用场景

优先用于：

1. 产品评测
2. 复杂机制讲解
3. 案例拆解
4. 数据或证据型讲解
5. 界面演示
6. 需要更高质感、更强动态表达的横屏解说视频

不优先用于：

- 只求快速日更的简单横屏口播
- 主要依赖竖屏 AB 节奏的教程视频
- 纯剧情类叙事

---

## 四、必须继承的上游铁律

这些不是建议，是这条 Skill 的硬规则。

### 1. 语义切镜，不是一句一个新元素

来自上游主 Skill 的核心定版：

- 画面是**按语义段落切**，不是机械“一句一个新元素”
- 新元素只在**语义拍边界**进场
- 同一时刻只允许一个主角
- 说完就让位

### 2. 七层反 PPT 系统必须存在

任何镜头都不能只有“一个静态页面 + 两个淡入字”。

至少要考虑这 7 层：

1. L1 相机
2. L2 焦点
3. L3 主体
4. L4 附着效果
5. L5 配角
6. L6 环境
7. L7 遮罩

**任何镜头不允许只有 1 层在动。**

### 3. 先装全局系统，再写镜头

对横屏数字人视频，本 Skill 明确继承上游这 4 套全局系统：

1. **CameraRig**
   - 每场景一条连续相机曲线
   - 冲击脉冲只能叠加，不能重置慢曲线

2. **Plane 视差层**
   - 背景 0.5
   - 主内容 1.0
   - 前景 1.2

3. **Live / Retire 生命周期**
   - 元素入场后不能死掉
   - resolved 期间必须有 idle 微动
   - 新主体来时旧主体提前让位

4. **Environment**
   - vignette 呼吸
   - 色温
   - 扫光
   - 曝光脉冲

### 4. 底部字幕必须素排

本 Skill 继承上游定版纪律：

- 底部跟读字幕**不加任何动效**
- 整句硬现、整句硬走
- 唯一例外：
  - `keyword-pop-highlight`
  - 全片最多 3 次

这意味着：

- 花字可以做
- 金句卡可以做
- 标题卡可以做
- 但**底部字幕本身**不能被做成弹跳字幕或花哨逐字字幕

### 5. 默认横屏 1920x1080

用户没有明确要竖屏时：

- 默认横屏 `1920x1080`

### 6. 卡片实现必须照抄真实源码，禁止凭一句话脑补（2026-09-01 血泪教训）

这是本 Skill **代价最高的一条**。曾发生过的翻车：只读了 `SKILL.md` 主文档
和 `_卡片索引_*.md` 的「一句话语义描述」（例如 `impact-open-title` →
「整句一次砸出…末词延后 3 帧换色」），就据此**凭空脑补**整个 HTML 实现，
导致 41 镜全部走样（尺寸、构图、配色、字号、动效参数全错），返工数轮。

**真实源码就在本 Skill 目录内，必须先读再写**：

| 内容 | 路径（本 Skill 内） |
|---|---|
| 78 张卡的自包含 Remotion 源码 | `template/cards/<slug>.tsx` |
| 同画面的 HTML 预览 | `demos/<slug>/index.html` |
| 卡片分类与选型 | `references/taxonomy.md` → `references/cards/<slug>.md` |

**照抄纪律（实现 demo.html 或 Remotion 工程时逐条核对）**：

1. **先读源码再动手**：打开 `template/cards/<slug>.tsx`，抄它的 `CONFIG`
   （全部数值、点位表、颜色、文案）、CSS（类名、`position/left/top/width/height`、
   `fontSize/fontWeight/color`）、以及顶部注释里的「时间表（demo 秒）」与「命门」
2. **坐标/字号/间距原样照搬，不做脑补换算**。真实卡的画布是 `960x540`
   （见源码 `export const meta = { width: 960, height: 540 }`）；要在 `1920x1080`
   画幅里呈现，用 `960x540` 容器 + `transform: scale(2)` 整体放大，**不要手动乘 2**
3. **人物构图照抄 `.host-wrap`**：真实源码里主持人是右侧一列
   （`position:absolute; right:0; top:0; bottom:0; width:47%`），不是随意摆放
4. **语义色照抄源码**：绿 `#2fb344`（positive）、红 `#d8383a`（警示）、
   橙 `#e8720c`（强调）、灰 `#a8a8ad`（历史/非焦点）、墨 `#1d1d1f`。
   **不要**把本片主题橙 `#F97316` 套到所有卡上——那是全片强调色，不是每张卡的语义色
5. **动效时刻来自 CONFIG**：`lead → 主体入场 → 衬底慢淡入 → hold` 四段，
   数值取 `CONFIG.lead / countAt / countDur / lineDur / hold` 等；
   例如 `metric-with-sparkline` 的折线必须比数字先到位（`lineDur 0.6 < countDur 0.9`）
6. **命门注释必须落实**：源码里 `/* 命门：… */`、`/* 必须… */`、`/* 禁止… */`
   是解决「文字挤出容器 / 元素遮挡 / 换行挤掉箭头」的关键
   （如 `white-space:nowrap` 保证数字+单位+箭头同行、`font-variant-numeric:tabular-nums`
   保证滚动计数不跳宽）
7. **禁止的替代做法**：用「一句话描述」反推实现、用通用动画库（GSAP）随机参数
   代替源码时间表、把 78 张卡简化成少数几个「通用渲染器」导致全片风格雷同

**自检问句**：写每一张卡之前，问自己——「我打开过
`template/cards/<slug>.tsx` 吗？我的 `left/top/fontSize/color` 是从源码抄的，
还是我自己编的？」答不上来就是脑补，必须回去读源码。

---

## 五、A-roll 数字人的硬规则

### 1. A-roll 仍然是数字人

无论 B-roll 多强，A-roll 的主持角色仍然是数字人。

但数字人的存在方式必须明确落到以下三种之一：

1. **贴边主持**
2. **缩位让台**
3. **阶段性让位**

### 2. 贴边主持

适用于：

- 开场 Hook
- 结论段
- 章节转段
- 需要“这个人在对你说”的时刻

硬规则：

1. 数字人透明背景
2. 靠左或靠右贴边
3. 主信息区必须完整留出来
4. 数字人不能压住主标题、主证据或字幕区

### 3. 缩位让台

这是这条 Skill 的核心能力之一，直接继承 `host-shrink-to-chip` 的规则。

适用于：

- 界面开始上台
- 数据图开始上台
- 截图 / 长页证据开始上台
- 需要“人继续在讲，但画面主语已经不是人”的时刻

硬规则：

1. 数字人缩到左下或右下角
2. **只能在下角**
3. chip 圆心必须落在画面下 1/3 带内
4. 下缘贴 action-safe
5. 角标落定后**不漂、不呼吸、不换位**
6. 角标里的人必须继续是视频，不允许变成静态头像
7. 图形 / B-roll 必须晚于人物缩位 **0.15s 左右**再接位

### 4. 阶段性让位

适用于：

- 长页证据巡游
- 强图表段
- 纯界面巡游
- 需要整屏专注的证据段

硬规则：

1. 可以暂时隐藏数字人
2. 但隐藏后的下一次主持人回归，视觉系统必须连续
3. 不能像切到另一条视频

### 5. 人脸安全区

凡是数字人在场：

1. 主信息面板放人物对侧
2. 文字 / 卡片 / 字幕**及其背景**
3. 不得侵入人脸安全区

本 Skill 明确吸收了上游 `host-footage.md` 的纪律：

- 布局前优先拿真实人脸 bbox
- 不目测，不猜

---

## 六、B-roll 的硬规则

### 1. B-roll 一律走 Remotion 高动态表达

本 Skill 不接受：

- 静态图堆叠
- 静态网页翻页
- 只有 entrance 没有 hold 和 exit 的 PPT 动效

### 2. B-roll 的真正职责

它主要承担：

1. 证据
2. 图表
3. 截图
4. 长页
5. 界面
6. 信息件
7. 章节转场

### 3. 每个镜头必须先判定 A/B 主次

在 `STORYBOARD.md` 里，每段都要先回答：

1. 这段谁主导？
   - A 主
   - B 主
   - 双主

2. 数字人现在是什么形态？
   - 贴边
   - 缩位
   - 隐藏

3. 这段 B-roll 用哪类卡或系统？
   - 高亮扫词
   - 聚焦压暗
   - 长页巡游
   - 图表生长
   - 信息卡堆叠
   - 过曝翻页
   - whip-pan
   - push-through

### 4. 每个镜头必须标注卡片动效 ID

`STORYBOARD.md` 的每个 `SHOT` 必须有「卡片动效」字段，值必须是 `references/cards/`
下那 78 张卡片之一的 ID，每个镜头 1~3 张，第一张是本镜主卡。

写法示例：

```markdown
- **卡片动效**：`news-card-desk`、`bar-chart-growth`、`highlighter-sweep`
```

硬规则：

1. **禁止自造动效名**。`custom-page-scroll` 这类名字在卡片库里没有源码，Remotion 阶段无法落地
2. **禁止用通用动作描述占位**。「弹入」「淡入」「idle 呼吸」「长页往上滚」都不是卡片名
3. **转场卡单独判**，且排在末位；普通内容镜头不要填转场卡
4. 没有合适卡片时宁可少填，不硬凑
5. 卡片 ID 必须与 `references/cards/` 文件名完全一致

映射方法、常见画面→卡片对照表、命名动效→卡片的转换表，一律以
`references/card-motion-mapping.md` 为准。批量写入与校验用 `scripts/match_cards.py`。

**注意**：脚本只做校验与写入，不做自动语义匹配。用「数字」这类宽泛词自动匹配会把
`number-counter` 塞进 20+ 个无关镜头，卡片归属必须逐镜人工判定。

---

## 七、这条 Skill 默认选用的配方卡

下面这 4 张卡，是本 Skill 最优先的“横屏数字人口播 + 证据 / 信息表达”骨干卡。

### 1. `host-shrink-to-chip`

用途：

- 人物从主舞台缩到角标
- 把舞台让给图表 / 界面 / 证据

本 Skill 继承的关键参数口径：

- `shrink`: `0.35s ~ 0.5s`
- `chipRatio`: `0.18`
- `gfxLag`: `0.15s`
- `chipScale`: 约 `0.72`

本 Skill 的执行纪律：

1. 人先缩位
2. B-roll 再入场
3. 角标只许下角
4. 角标期位置锁死
5. 人继续是视频，不许静态化

源码母本：

- `template/cards/host-shrink-to-chip.tsx`

### 2. `highlighter-sweep`

用途：

- 引用报告
- 文献
- 新闻截图
- “就是这一句”的证据强调

关键参数口径：

- `startDelay`: `0.7s`
- `sweep`: `0.4s ~ 0.8s`
- `dimTo`: `0.4 ~ 0.55`
- `liftScale`: `1.03`

执行纪律：

1. 荧光块不许盖住文字
2. 必须压暗其他内容
3. 扫速要对齐朗读
4. 不规则圆角保留笔触感

源码母本：

- `template/cards/highlighter-sweep.tsx`

### 3. `focus-dim-spotlight`

用途：

- 多行表格
- 多卡版面
- 参数对比
- 代码 / 清单 / 流程块

关键参数口径：

- `dimTo`: 白底 `0.35 ~ 0.45`
- `dimIn`: `0.30s`
- `jump`: `0.20s`
- `hold`: `1s ~ 1.5s`
- `restore`: `0.40s`

执行纪律：

1. 目标本身零改动
2. 靠“周围变暗”来聚焦
3. 焦点必须滑过去，不能硬切
4. 讲完整体恢复
5. 字幕层在蒙层之上

源码母本：

- `template/cards/focus-dim-spotlight.tsx`

### 4. `evidence-scroll-tour`

用途：

- README
- 协议
- 搜索结果
- 长页文档
- 长截图证据

关键参数口径：

- `scrollSpeed`: 约 `10% 页高/s`
- `stopHold`: `1.5s`
- `stopAlign`: `0.5`
- `decelDist`: `90px`
- `accelDist`: `45px`
- `breathScale`: `1.03`

执行纪律：

1. 页面是唯一持续运动体
2. 标注预置随页走，不现场画
3. 关键条目前提前减速
4. 停在视口中线
5. 停留时只做呼吸防死，不做乱抖

源码母本：

- `template/cards/evidence-scroll-tour.tsx`

---

## 八、这条 Skill 默认使用的系统源码

这是后续真正做 Remotion 时最值得复用的底层文件映射。

### 1. 相机系统

- 本地模板文件：`template/motion-systems/camera.tsx`
- 本 Skill 用途：
  - 横屏段落慢推
  - 镜头脉冲
  - 2D/3D 镜头统一

### 2. 生命周期系统

- 本地模板文件：`template/motion-systems/life.tsx`
- 本 Skill 用途：
  - 元素 idle 微动
  - 旧主体让位
  - resolved / retiring 状态

### 3. 转场系统

- 本地模板文件：`template/motion-systems/transitions.tsx`
- 本 Skill 用途：
  - `push-through`
  - `overexpose-flip`
  - `whip-pan`
  - `black-slam`
  - `pullback-cool`
  - `particle-weld`

本 Skill 默认建议：

1. 递进关系优先 `push-through`
2. 翻页或章节切换优先 `overexpose-flip`
3. 并列关系优先 `whip-pan`
4. 最大反转才允许 `black-slam`
5. 一条视频不要把六式全用一遍

### 4. 主题系统

- 本地模板文件：`template/motion-systems/theme.ts`
- 本 Skill 用途：
  - 统一色板
  - 统一字体
  - 统一背景网格 / 科技感底

### 5. 字幕系统

- 本地模板文件：`template/motion-systems/Subtitles.tsx`
- 本 Skill 用途：
  - 底部素排跟读字幕
  - 限次 `keyword-pop-highlight`

---

## 九、视觉语言默认值

### 1. 如果用户没明确指定风格

本 Skill 默认遵循上游设计语言的核心原则：

1. 内容是主角，版式后退
2. 全片只有一个强调色
3. 全系统只有一个投影
4. 底色交替形成章节感

但因为你这条 Skill 偏向“高质量数字人口播 + Remotion 信息表达”，所以默认允许：

1. 更强的信息件层次
2. 更强的 B-roll 主区
3. 更明确的主持人让位机制

### 2. 如果用户明确指定风格

必须整套替换 token：

- 颜色
- 字体
- 背景
- 边框
- 强调色

不允许“这个镜头 Apple，那个镜头赛博”。

---

## 十、配置文档硬闸口

正式生产前，必须先生成：

1. `DESIGN.md`
2. `STORYBOARD.md`
3. `demo.html`

并且必须满足：

### `DESIGN.md`

至少写清：

1. 画幅与安全区
2. 默认视觉 token
3. 数字人三种模式
4. B-roll 主区的视觉主语
5. 底部字幕素排纪律
6. 主持人缩位的固定方位
7. 这条视频会用到的配方卡
8. 这条视频会用到的底层系统

### `STORYBOARD.md`

至少写清：

1. 每段时长
2. A/B 主次
3. 数字人形态
4. 采用的卡和系统
5. 什么时候切镜
6. 什么时候让位
7. 什么时候转场
8. 什么时候纯 B-roll
9. **每个镜头的卡片动效 ID**（见第六节第 4 条与 `references/card-motion-mapping.md`）

### `demo.html`

至少做到：

1. 模拟一次贴边主持
2. 模拟一次缩位让台
3. 模拟一次 B-roll 主导镜头
4. 模拟一次证据 / 图表 / 页面类配方卡
5. 模拟一次镜头承接或转场关系

**没有用户确认，禁止进入 TTS / 数字人合成 / Remotion 生产。**

配置三件套由本 Skill 在收到**已确认创作包**后生成，不是创作层预先要提供的输入。完整的上游输入、确认问题、生产工程与验收口径以 `../team-references/remotion-landscape-production-contract.md` 为准。

---

## 十一、执行流程

### Stage 0：验收上游创作包

必须先验收：

1. 已确认选题、目标指标和目标受众
2. 明确推荐 `douyin-digital-human-video-expert` 与本 Skill
3. 逐段口播创作包、证据 / B-roll 规划、资产清单、合规禁区
4. 本次任务目录绝对路径
5. 可用时读取策略优化记录

缺少任一关键项时，回传主理人补齐；不得直接生成三件套，更不得补造事实、素材或视频路由。

### Stage 1：读本地提取文件

先读：

- `talkcraft-extracted-playbook.md`
- `talkcraft-source-manifest.md`

不要把外链当执行入口。

### Stage 2：生成并确认配置三件套

按团队统一配置规范生成 `DESIGN.md`、`STORYBOARD.md`、`demo.html`，三份文件必须使用同一镜头编号、版本号与 A/B 主次关系。向用户取得明确“配置通过，允许生产”的确认后，才能继续。

### Stage 3：确认声音与人物输入

1. 最终口播稿与配音逐字一致
2. 配音是单一完整 wav / mp3，已人工听核无爆音、截断和误读
3. 数字人素材可透明背景使用或可抠像
4. 人脸安全区可以用 `scripts/face_bbox.py` 实测
5. 运行 `scripts/timestamps_cpu.py` 后再运行 `scripts/make_timing.py`；句级匹配低于 `0.90` 必须人工听核
6. 所有 B-roll、证据截图和音效均已本地落盘

### Stage 3.5：数字人片段生成（**必须串行，一轮一段**）

数字人 A-roll 片段走 RunningHub。**同一时刻只允许一个 RunningHub 任务在跑，并行提交会全部失败。**

以 7 段口播为例，正确姿势是跑 7 轮：

```
提交第 1 段 → 轮询到 SUCCESS → 下载落盘 → 提交第 2 段 → … → 第 7 段
```

执行纪律：

1. 一次只 `generate` 一段，拿到 `taskId` 后再轮询
2. `get_task_detail` 间隔 2-3 分钟；`QUEUED` / `RUNNING` 都是正常态，不得据此判定失败
3. 只有 `SUCCESS` 才下载结果并写入任务目录，然后再提交下一段
4. `FAILED` 先读 `errorMessage` 定位根因，不要盲目重提
5. **严禁把多段放进同一批并行提交**——实测全败，更慢且浪费积分
6. 单段音频超过应用建议时长（如 LTX2.3 建议 ≤35 秒）时，先按语义边界切分再逐段提交

人物图来源优先级：

1. MCP `manage_brand_library` 的 `get_ip_library`，用品牌 IP 资料库里的真实人物照片
2. IP 资料库未提供时才退回本地生成图
3. 竖版 9:16 人物图在对口型类应用上通常优于横版

失败码 `errorCode=803 | JsonNull | RunningHub 未返回任务 ID` 表示**提交阶段被拒**（0.1 秒级失败），
优先怀疑：① 同一时刻已有其他 RunningHub 任务在跑；② 上传节点残留 `example.png` 占位值。
细节见 `../team-references/platform-mcp-map.md` §2.6。

### Stage 4：做 SHOTBOOK 思维的分镜

先按三面工作单设计：

1. 背景面
2. 主体面
3. 文字面

再展开成本 Skill 的 `STORYBOARD.md`。

分镜定稿后，按 `references/card-motion-mapping.md` 为**每个镜头**标注卡片动效 ID：

1. 先按映射表把已有的内部动效名转成卡片 ID
2. 描述型镜头按画面语义逐镜人工选卡（**不要脚本自动匹配**）
3. 用 `scripts/match_cards.py --apply` 写入并校验 ID 是否都在卡片库里
4. 用 `scripts/match_cards.py --report` 生成映射表交用户复核

### Stage 5：搭建并验证 Remotion 工程

在 `<任务目录>/remotion/` 创建独立工程，至少包含 `package.json`、`src/entry.ts`、`src/Root.tsx`、Composition、`shots.ts`、`timing.json`、`sfx.ts`、`public/` 与 `out/`。先用低分辨率预览渲染验证 Composition 和本地素材均可加载，再进入正式制作。

### Stage 5.5：字幕时间轴对齐（禁止用 proportional 兜底交付）

`timestamps_cpu.py` 在无法 ASR 时会退化成 **proportional（按字数均分）**，其 `_meta` 标为
`_fallback: proportional`、`ok: false`。这只能当占位，**不能进成片**：
它把句间停顿也计入可分配时长，误差随句序累积，实测偏差可达 3~4s（观众能明显感到字幕与口播脱节）。

**首选方案 —— VAD 语音时长域对齐（零外部模型依赖）**：

```bash
python scripts/vad_align.py --dir <任务目录>          # 全部段
python scripts/vad_align.py --dir <任务目录> 1,2      # 指定段
```

流程：ffmpeg `silencedetect` 取真实停顿 → 只保留语音区间构成「语音时长域」→
在语音域内按字数比例分配每条短句（天然跳过停顿）→ 映射回真实时间轴 →
句末边界吸附到最近静音中点（默认容差 0.35s）。

- 若存在 `remotion/src/shotsReal.ts`，脚本自动沿用其段首偏移，**保证字幕时间轴与镜位完全同源**。
- 输出 `remotion/src/timing.json`；短句取自 `audio/script_NN.json`，按显示长度 ≤12 字筛选，
  超长自动按标点二次切分（时长按字数分摊）。
- 会自动剔除 `（…）` 形式的导演/旁白提示语——这类不是口播内容，混进字幕就是事故。

**次选方案 —— 真实 ASR（faster-whisper）**：仅在有可靠网络与磁盘时使用。
⚠️ 本环境 `~/.cache/huggingface` 快照为空，small/medium 权重需下载约 0.5~1.5GB，
且沙箱会拦截 HF 的临时文件删除（`SAFE_DELETE_FAIL_CLOSED`）导致下载中断；
强制离线（`HF_HUB_OFFLINE=1`）会因快照不完整直接报 `IncompleteSnapshotError`。
遇到这些情况直接走 VAD 方案，不要在下载上耗时间。

### Stage 5.6：数字人与卡片接入横屏

完整规范见 `references/host-compositing.md`。四条最常见的致命点：

1. 数字人源 704×1280 @25fps 竖屏且**自带音轨** → 必须 `volume={0}`，否则与全片音轨叠成回声。
2. `Sequence` 的帧是 **Composition fps（30）**，`OffthreadVideo` 的 `startFrom` 是 **源 fps（25）**，
   两者单位不同，混用会导致口型整体错位。
3. `startFrom` 必须是常量（每镜一个 Sequence），做成随 `useCurrentFrame()` 变化的值会每帧 seek，渲染慢数十倍。
4. 卡片 960×540，超出 `meta.durationInFrames` 的部分必须用 `Freeze` 定格，否则镜头尾段变空白。

卡片注册表用 `scripts/gen_card_index.py --dir <remotion工程>` 自动生成，勿手写。

### Stage 6：正式 Remotion 制作

生产时优先复用：

1. 关键卡源码
2. motion-systems 系统源码
3. 本地模板的布局和参数口径

### Stage 7：验收与交付

必须运行本地 `motion_check.py`、`sfx_check.py`、`qa_extract.py`，并由独立审查者按 P0 / P1 / P2 完成视觉验收；还必须检查角标数字人、人脸安全区、A/B 让位、证据可追溯性、转场连续性与 390px 手机宽度可读性。任何 P0、P1、关键事实不可追溯或 `≥0.8s` 非设计性静止段，均不得交付。

交付时回传实际 Skill、配置版本、成片路径、验收结论、主要卡 / 素材模式、异常与降级、归档状态，以及供周度复盘使用的视频形式反馈。

---

## 十二、禁止未授权降级

- ❌ 只把上游链接贴在文档里，让后续 agent 临时再读
- ❌ 只写“参考 talkcraft”，但没有写明本地要用哪些卡、哪些源码、哪些规则
- ❌ 数字人该让位时仍大面积挡住主体信息
- ❌ 把 Remotion B-roll 降级成静态 HTML 页面
- ❌ 底部字幕做成花哨逐字字幕
- ❌ 角标里的人变成静态头像
- ❌ 图形和人物同帧抢位
- ❌ 没有 `DESIGN.md / STORYBOARD.md / demo.html` 就直接进生产

---

## 十三、参考资料

### 1. 本地执行真源

- `talkcraft-extracted-playbook.md`
- `talkcraft-source-manifest.md`
- `talkcraft-upstream-read-index.md`
- `template.md`
- `../team-references/remotion-landscape-production-contract.md`
- `../team-references/video-skill-routing.md`
- `../team-references/video-production-playbook.md`
- `../team-references/digital-human-config-package-spec.md`
- `references/host-compositing.md`（数字人 + 卡片接入横屏的合成规范）
- `references/card-motion-mapping.md`（命名动效 → 卡片 ID 映射真源）

### 2. 上游溯源

- `https://github.com/Vincentwei1021/video-talkcraft`
- `https://vincentwei1021.github.io/video-talkcraft/`

