> 历史专家团文档：运行时应以当前 MCP 实际工具、参数、用户要求和账号状态为准。

# 视频技能路由表（video-skill-routing）

> 本文件是 `douyin-fullflow-ops` 视频层的单一真源。
> 只回答三件事：
> 1. 现在有哪些视频专家；
> 2. 每个专家下面有哪些 Skill；
> 3. 什么业务场景该走哪个专家和 Skill。
>
> 选中视频 Skill 后，直接读取该 Skill 根部唯一的 `SKILL.md`。只有当主流程走到明确标注的制作阶段时，才按该文件提示读取本技能 `references/` 下的专项规则。

## 一、视频层现行结构

当前视频层分为 5 个专家域：

1. `douyin-digital-human-video-expert`
2. `douyin-drama-video-expert`
3. `douyin-brand-promo-video-expert`
4. `douyin-explainer-video-expert`
5. `douyin-creative-video-expert`

## 二、专家层职责边界

| 专家 | 负责什么 | 典型业务目标 | 不负责什么 |
|---|---|---|---|
| `douyin-digital-human-video-expert` | 数字人口播、ABroll、口播 Broll 规划 | 教育、解释、信任建立、稳定日更 | 剧情冲突型、强广告片、实验性创意片 |
| `douyin-drama-video-expert` | 短剧、第一视角、3D 剧情、国风剧情 | 强停留、情绪卷入、带货转化 | 标准数字人口播与纯品牌广告片 |
| `douyin-brand-promo-video-expert` | 品牌广告、产品广告、数字产品宣传片 | 品牌势能、卖点表达、活动传播、销售转化 | 纯知识讲解和剧情短剧 |
| `douyin-explainer-video-expert` | 图解、拼贴、定格、MG、Vox 风格 | 讲清机制、科普、干货、数据解释 | 纯剧情转化和高实验创意片 |
| `douyin-creative-video-expert` | 手绘融合、FPV、动态显影等高概念创意 | 抓眼、点赞、记忆点、品牌新鲜感 | 需要强事实讲解的标准内容 |

## 三、技能路由矩阵

| Skill ID | 归属专家 | 适用场景 | 优先目标 | 主要产物 / 前置要求 |
|---|---|---|---|---|
| `douyin-dh-landscape-html-video` | 数字人 | 互联网产品、付费产品、事件解读 | 稳定日更、教育 | `DESIGN.md` / `STORYBOARD.md` / `demo.html` + 横屏成片 |
| `douyin-dh-landscape-remotion-video` | 数字人 | 横屏高质量口播、复杂讲解、评测、证据截图巡游 | 质感、留存、信息密度 | 已确认口播创作包 + 证据规划；先生成并确认三件套，再制作 Remotion 横屏成片 |
| `douyin-dh-vertical-abroll-video` | 数字人 | 科普、案例拆解、教程、干货 | 结构化表达、留存 | `DESIGN.md` / `STORYBOARD.md` / `demo.html` + 竖屏成片 |
| `douyin-transcript-broll-planner` | 数字人 | 口播文案已有、需要镜头和 Broll 规划 | 降低生产摩擦 | Broll 规划、素材清单、镜头说明 |
| `dynamic-video-craft` | 数字人 | 数字人 A-roll + Remotion B-roll 混合成片；也支持纯 B-roll 动态视频（产品片 / 解说片 / 单镜头复刻） | 质感、动态强度、一套工程覆盖两种形态 | 已确认口播创作包 + 证据规划；数字人路线另需透明背景人物图与配音；先生成并确认三件套，再制作成片 |
| `douyin-microdrama-commerce-video` | 剧情短片 | 短剧带货 | 停留 + 转化 | 短剧脚本、分镜提示词、真实产品图 |
| `douyin-3d-animation-short-video` | 剧情短片 | 抽象概念剧情化、品牌设定世界观 | 吸睛、差异化 | 3D 分镜表、镜头表、模型与风格约束 |
| `douyin-pov-short-film-video` | 剧情短片 | 第一视角代入、体验流 | 沉浸、点赞、评论 | POV 脚本、路径动作、视角纪律 |
| `douyin-chinese-style-short-drama-video` | 剧情短片 | 国风、古风、东方叙事 | 风格化停留、文化感 | 人物设定、东方美术规则、剧情脚本 |
| `douyin-micro-expression-video` | 剧情短片 | 人物特写、情绪转折、细腻表演 | 情绪卷入 | 人物授权/虚构设定、情绪曲线、特写分镜 |
| `douyin-suspense-title-sequence-video` | 剧情短片 | 悬疑开场、标题序列、氛围钩子 | 前 3 秒停留 | 钩子、标题文案、声音与风险约束 |
| `douyin-brand-promo-video` | 品牌广告 | 品牌认知、品牌主张、品牌气质传播 | 品牌势能 | 品牌主张、情绪板、镜头语言 |
| `douyin-minimalist-product-ad-video` | 品牌广告 | 单产品、单卖点、高级感产品广告 | 卖点聚焦、转化 | 产品图、关键卖点、极简镜头节奏 |
| `douyin-silkscreen-illustration-short-video` | 品牌广告 | 插画风、装饰风、海报感视频 | 风格记忆点 | 插画元素、丝印配色、版式节奏 |
| `douyin-digital-product-promo-video` | 品牌广告 | 软件、SaaS、课程、数字工具 | 讲价值、讲场景、促转化 | 界面清单、用户路径、卖点层级 |
| `douyin-promo-video` | 品牌广告 | 通用宣传视频、活动传播片 | 曝光、传播、活动承接 | 主题、卖点、镜头节奏、CTA |
| `douyin-surreal-spot-video` | 品牌广告 | 超现实产品隐喻、新品强记忆点广告 | 品牌记忆、互动 | 产品真图、创意隐喻、合规边界 |
| `douyin-paper-collage-explainer-video` | 科普讲解 | 纸拼贴讲解、知识拆解 | 易懂、记忆 | 讲解结构、拼贴元素、旁白 |
| `douyin-papercraft-stop-motion-explainer-video` | 科普讲解 | 纸艺定格、逐步拆解 | 节奏感、解释性 | 定格镜头表、纸艺元素、镜头顺序 |
| `douyin-vox-style-video` | 科普讲解 | 数据新闻、观点拆解、议题解释 | 留存、转发 | 论点结构、地图/图表/字幕层 |
| `douyin-line-doodle-explainer-video` | 科普讲解 | 线条图解、流程解释 | 易懂、低成本高信息密度 | 线条元素、关系图、步骤图 |
| `douyin-mg-voiceover-animation-video` | 科普讲解 | MG 口播动画、图文配音讲解 | 高信息密度 | 旁白、动效规则、图表/字幕脚本 |
| `douyin-handdrawn-live-video` | 创意 | 手绘与实拍融合 | 抓眼、记忆点 | 实拍基底、手绘叠加规则 |
| `douyin-fpv-tour-video` | 创意 | 第一视角穿越、空间游走 | 新鲜感、停留 | 路线、场景点位、速度控制 |
| `douyin-live-sketch-motion-video` | 创意 | 实景动态手绘显影 | 风格化传播 | 关键帧、描边逻辑、显影顺序 |
| `douyin-ip-toy-grid-motion-video` | 创意 | IP 玩具、角色集合、宫格动态陈列 | IP 记忆、周边展示 | 授权 IP 图、格局、材质与动效 |
| `douyin-music-video-subtitle-video` | 创意 | 音乐节拍、歌词/字幕动效 | 情绪、互动、完播 | 已授权音频/文本、节拍与字幕规则 |
| `douyin-film-reference-prompt-writer` | 创意（辅助） | 拆解影视/广告视觉参考 | 提升主 Skill 的视觉一致性 | 参考来源、可借鉴范围；不单独成片 |

### 备注：横屏 Remotion 数字人链路的两个 Skill 如何择一

数字人家族里 `douyin-dh-landscape-remotion-video` 与 `dynamic-video-craft` 都做「数字人 A-roll + Remotion B-roll」横屏成片。**同一条任务只能选一个，不并行。**

| 维度 | `douyin-dh-landscape-remotion-video` | `dynamic-video-craft` |
|---|---|---|
| 位置 | 本插件 `skills/` 内 | 用户级 `~/.workbuddy/skills/dynamic-video-craft/` |
| B-roll 实现 | 78 张 talkcraft 卡片源码，逐镜标注卡片动效 ID，必须照抄 `template/cards/<slug>.tsx` | 原创 Remotion 工程骨架 + shotcraft/talkcraft 镜头词汇索引，按镜头语义自写场景组件 |
| 适合 | 需要卡片级精确复刻、证据截图巡游、高信息密度评测 | 需要一套工程同时覆盖数字人片与纯 B-roll 片、镜头结构较自由、产品页面 2.5D 运镜 |
| 额外能力 | 卡片索引与校验脚本 | 同一技能可退化为纯 B-roll 动态视频，`video.json` 去掉 `host` 即可 |

选型口径：

1. 上游选题层或创作层已点名某一个，就按点名执行，不擅自换。
2. 自动化流程或用户未点名时，抖音日更数字人横屏链路默认走 `dynamic-video-craft`。
3. 明确要求「按卡名复刻」「证据长页巡游」「78 卡体系」时走 `douyin-dh-landscape-remotion-video`。
4. 两者的三件套确认闸、图像与视频接口约束完全一致，不因换 Skill 而放松。

## 四、行业到视频专家的优先关系

| 行业 / 业务 | 优先专家 | 典型次选 |
|---|---|---|
| 互联网产品 / SaaS / AI 工具 / 课程 | 数字人、品牌广告、科普讲解 | 创意 |
| 实体商家 / 家居日用 / 家清 / 快消 | 剧情短片、品牌广告 | 创意 |
| 本地生活 / 门店活动 | 剧情短片、品牌广告、创意 | 数字人 |
| 强监管行业 | 数字人、科普讲解 | 品牌广告（需更克制） |
| 品牌升级 / 新品发布 | 品牌广告、创意 | 数字人 |

## 五、路由铁律

1. 先判断业务目标，再判断视频专家
2. 同一条任务只选一个主视频专家，避免并行混用
3. 所有成片 Skill 均强制要求 `DESIGN.md / STORYBOARD.md / demo.html`，并在三件套确认后才生成；视觉参考和 B-roll 规划是辅助 Skill，不单独成片
4. `douyin-dh-landscape-remotion-video` 的完整输入、三件套时序、生产工程和验收规则以 `remotion-landscape-production-contract.md` 为准；必须明确 A-roll 是否透明背景全高主持人、缩位让台主持人或纯 B-roll 段
5. `dynamic-video-craft` 走同一份 `remotion-landscape-production-contract.md` 的上游输入与三件套时序；其工程内部规范以该 Skill 自带的 `references/digital-human-aroll.md` 为准，`video.json` 的 `host` 字段必填 `EDGE / CHIP / HIDDEN` 逐镜形态
6. 剧情类技能必须坚持真实产品图、人物一致性和证据位逻辑
7. 品牌广告、科普讲解、创意视频默认优先走 RunningHub，不要退回“大一统视频专家”

## 六、接口映射总原则

### 图像

- 优先先检查多元探索平台运行时是否可用
- 需要插画、概念图、辅助画面时，优先 `gpt-image-2.0`

### 视频

- 默认通过 `manage_douyin_video_production`
- `section=runninghub`
- 重点使用：
  - `MiniMax H3`
  - `Seedance 2.0`

## 七、扩展规则

后续再新增视频能力时，按这个顺序扩展：

1. 先判断应归属哪个视频专家
2. 新增对应本地 Skill 文档
3. 把路由补进本文件
4. 不把 Skill 细节倒灌回主理人和上游专家文档
