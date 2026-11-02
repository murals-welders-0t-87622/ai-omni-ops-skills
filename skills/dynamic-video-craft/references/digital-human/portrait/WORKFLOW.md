---
name: douyin-dh-vertical-abroll-video
description: 口播数字人 + 竖屏 + ABroll。基于原始 `talking-head-broll-video` 技能重构而来，用于把已成型口播内容制作成竖屏精细化数字人口播视频。强调配置文档先行、预览页与生产页同源、组件点名硬约束、门禁与验收闭环。适合互联网产品、付费产品、科普、教程、案例拆解等需要更强画面组织与镜头节奏的内容。
---

> 当前技能库适配：本文件保留用户提供的原业务流程与完整随包文件；旧专家团路径通过邻近 team-references 提供，历史模型、账号和并发经验不能代替当前 MCP 实际定义。按用户当前要求、品牌及授权执行。

# 口播数字人 + 竖屏 + ABroll

## 本地补充：高级视觉与动态设计

当用户要求高级网站、海报或原创多镜头视频时，执行 [高级视觉与动态设计](references/editorial-video-art-direction.md)。保留竖屏 A/B 分工、三份配置先确认以及预览与生产同源的硬约束。

## 一、定位

这条 Skill 不是对旧单专家技能的“替代品”，而是对它的**专家团执行化重构**。

它的来源有两层：

1. 业务与执行铁律，继承自：
   - `references/talking-head-broll-video.source.md`
   - `references/upstream-talking-head-broll-video/`
2. 竖屏 ABroll 的现行业务目标，来自当前专家团：
   - 数字人作为 A-roll 叙述锚点
   - B-roll 负责图表、结构、页面、插画、证据与信息组织
   - 正式制作前先出 `DESIGN.md`、`STORYBOARD.md`、`demo.html`

因此，本 Skill 的核心不是“做一个更花的竖屏视频”，而是：

1. 用原技能的执行深度
2. 做成适合当前专家团链路的竖屏执行版
3. 并且全部只引用本技能目录内的本地真源

---

## 二、本地真源与继承关系

### 1. 本技能目录内已落地的核心真源

#### 原技能基线

- `references/talking-head-broll-video.source.md`
- `references/upstream-talking-head-broll-video/`

#### 当前专家团基础配置真源

- `references/base-config/DESIGN.base.md`
- `references/base-config/STORYBOARD.base.md`
- `references/base-config/demo.base.html`
- `references/base-config/成品.base.mp4`（原包未附带）

#### 当前技能自身模板与示例

- `template.md`
- `examples/DESIGN.example.md`
- `examples/STORYBOARD.example.md`
- `examples/demo.example.html`
- `examples/production.example.html`

#### 当前技能补充参考

- `references/video-shotcraft-README_CN.source.md`

### 2. 继承规则

本 Skill 的规则分两层：

1. **本文档是现行执行版**
   - 负责匹配当前专家团的视频路由、确认闸口、竖屏目标和交付方式
2. **原技能本地镜像是全量保底基线**
   - 凡是本文档没有显式覆写的执行细节，默认以：
     - `references/talking-head-broll-video.source.md`
     - `references/upstream-talking-head-broll-video/`
     为准

这样处理的目的就是：

- 不丢原技能元素
- 不再把原技能外部路径悬在技能外面
- 同时让当前 Skill 保持专家团化、结构化和可单独打包

---

## 三、适用场景

优先用于：

1. 互联网产品
2. 付费产品
3. 科普视频
4. 干货讲解
5. 教程 / 案例拆解
6. 需要更精细镜头组织、更强视觉密度和更强 A/B 关系的口播内容

不优先用于：

1. 极简单概念、极低制作成本需求
2. 只需要 3 段数字人 + 2 段 HTML 的快速稳定交付

这些情况应优先评估：

- `../landscape/WORKFLOW.md`

---

## 四、执行铁律

### 1. 配置文档先于一切生产

正式生产前，必须先生成并确认：

1. `DESIGN.md`
2. `STORYBOARD.md`
3. `demo.html`

本地真源：

- `references/base-config/DESIGN.base.md`
- `references/base-config/STORYBOARD.base.md`
- `references/base-config/demo.base.html`
- `references/base-config/成品.base.mp4`（原包未附带）
- `template.md`
- `examples/`

**没有配置文档，禁止进入出图、TTS、数字人、渲染、拼接。**

### 2. 预览页与生产页必须同源

继承原技能的核心纪律：

1. `demo.html` 不是提案图
2. 预览页里确认过的组件、结构和动效关系，必须能进入生产页
3. 不允许“预览页一套、生产页一套”

### 3. 分镜表点名是硬约束

继承原技能的关键规则：

1. `STORYBOARD.md` 里点名的组件、镜型、主动作，不是备注
2. 不允许因为实现麻烦就偷偷换成通用兜底模板
3. 遇到做不到的组件，只能显式告知并等待用户裁决

### 4. 禁止未告知降级

以下行为一律禁止：

- 做不出 A/B 关系就偷偷改成普通竖屏图文页
- 做不出指定镜型就偷偷改成横屏 HTML 逻辑
- 图片不好处理就随手找图替代
- `demo.html` 没确认就直接出片

### 5. 用户需求优先于旧默认值

裁决顺序：

`用户当次明确指令 > 当前专家团确认闸口 > 本 Skill 现行文档 > 原技能本地镜像`

### 6. 引用只使用技能内相对路径

本文档、模板、示例都不应再出现：

- 绝对路径
- 旧专家包外部路径
- 直接引用外部 GitHub 文档作为执行入口

如果某个外部参考有用，先落本地，再引用本地文件。

---

## 五、输入契约

必须具备：

1. `【XX年XX月XX日抖音文案.md】`
2. 选题报告
3. 创作专家交接提示
4. 当天任务目录绝对路径

建议补充：

1. 封面主标题建议
2. 花字关键词
3. A-roll 角色设定
4. B-roll 需要承载的图表、流程、截图、示意图、对比表
5. 是否需要 MCP `gpt-image-2.0` 生成插画 / 信息图

### 输入理解要求

这条 Skill 必须先拆清三件事：

1. 哪些内容必须由数字人口播直接说
2. 哪些内容必须由 B-roll 承载
3. 哪些镜头要 A+B 同屏，哪些镜头只留 B-roll

不先拆清这三件事，后面的 `STORYBOARD.md` 会天然失真。

---

## 六、输出契约

至少产出：

1. `DESIGN.md`
2. `STORYBOARD.md`
3. `demo.html`
4. 封面图
5. TTS 音频
6. 数字人视频段
7. B-roll 相关素材 / 片段 / 组件页面
8. 最终成片 `mp4`

如果当前流程接平台入库，还应补齐：

1. 交付清单
2. 校验记录
3. 素材 / 作品上传结果

---

## 七、视觉系统要求

### 1. 竖屏基线

当前竖屏基线不是重新凭空定义，而是综合这几份本地真源：

- `references/base-config/成品.base.mp4`（原包未附带）
- `references/base-config/DESIGN.base.md`
- `references/video-shotcraft-README_CN.source.md`
- `examples/`

### 2. 版式基调

优先对齐：

1. 暖米底 / 纸面底
2. 黑粗边框 + 大圆角
3. 顶部章节条
4. 中部大主卡
5. 独立字幕条
6. 底部信息卡
7. 数字人作为右下或局部锚点

### 3. 数字人与 B-roll 的关系

数字人不是唯一主角，而是 A-roll 锚点。

默认三种状态：

1. 同屏小窗
2. 局部让位
3. B-roll 主导

这三种状态必须在 `STORYBOARD.md` 中逐镜写清，不允许到生产时再临时猜。

### 4. 图片与插画规则

当镜头需要插画、结构图、信息辅助视觉时：

1. 优先通过 MCP 的 `gpt-image-2.0` 生成
2. 画风必须和当前卡片系统一致
3. 不允许混入来源不明的随意网图

---

## 八、动效与镜长要求

### 1. 单镜时长

默认目标：

- 常规镜：`4-8 秒`
- 重信息镜：`6-10 秒`

超过 10 秒只能是例外，不应成为常态。

### 2. 每镜必须有主动作

例如：

1. 标题建立
2. 关键词高亮
3. 卡片分层进入
4. 图表生长
5. 流程连线
6. 当前激活项切换

### 3. 禁止的动效问题

- ❌ 纯静态页长时间停留
- ❌ 所有元素同时飞入
- ❌ 过度 bounce、旋转、乱飘
- ❌ 动效和信息主次相反

### 4. 动效参考

如果需要补充动效语言，可查本地化后的：

- `references/video-shotcraft-README_CN.source.md`

但执行入口仍然是本 Skill，而不是回外网临时找思路。

---

## 九、执行流程

### Stage 0：配置文档

先完成：

1. `DESIGN.md`
2. `STORYBOARD.md`
3. `demo.html`

并通过用户确认闸。

### Stage 1：需求对齐与镜头拆解

继承原技能的工作方式，但改造成当前专家团可执行版：

1. 先拆 A-roll / B-roll 职责
2. 先定镜型分布
3. 先定主动作，不是先做页面

### Stage 2：设计系统与分镜表

1. `DESIGN.md` 负责视觉真源
2. `STORYBOARD.md` 负责逐镜信息、镜型、组件、主动作
3. 点名组件是硬约束

### Stage 3：预览确认

`demo.html` 必须能看出：

1. 竖屏结构
2. A-roll / B-roll 关系
3. 至少几类关键镜型
4. 文字、卡片、图表、标签等进入关系

没有用户确认，不允许进入正式制作。

### Stage 4：素材生产

包含：

1. TTS
2. 数字人
3. B-roll 页面 / 组件 / 插图 / 结构图

### Stage 5：渲染与拼接

必须继承原技能的门禁思维：

1. 富度检查
2. 组件覆盖检查
3. 遮挡检查
4. 字幕可读性检查
5. 预览页与生产页一致性检查

### Stage 6：交付

至少交付：

1. 最终成片
2. 配置文档
3. 交付与上传记录

---

## 十、和当前专家团业务流程的匹配方式

### 1. 上游接收

来自：

1. 策略专家的内容形态判断
2. 选题专家的选题结论
3. 创作专家的视频交接

### 2. 路由判断

当内容满足以下特征时优先走本 Skill：

1. 需要竖屏
2. 需要更精细 A/B 关系
3. 需要更强的信息组织和视觉密度
4. 需要比横屏 HTML 通道更高的镜头控制力

### 3. 复盘回流

成片后的有效经验不应直接塞进本文档，而应优先回流给：

1. `douyin-data-review-expert`
2. `策略优化记录`
3. 相关视频专家的路由判断

这样才能持续优化又不把文档写爆。

---

## 十一、禁止未授权降级

- ❌ 竖屏 ABroll 偷偷降级成普通图文页
- ❌ 预览页和生产页分裂为两套实现
- ❌ `STORYBOARD.md` 点名组件未实现却用兜底模板代替
- ❌ `demo.html` 没确认就进入渲染
- ❌ 插画与图片不经本地流程，随便外找替代
- ❌ 继续在主文档里写绝对路径、旧专家路径或外链执行入口

---

## 十二、参考资料

### 1. 本技能内真源

- `references/talking-head-broll-video.source.md`
- `references/upstream-talking-head-broll-video/`
- `references/base-config/DESIGN.base.md`
- `references/base-config/STORYBOARD.base.md`
- `references/base-config/demo.base.html`
- `references/base-config/成品.base.mp4`（原包未附带）
- `references/video-shotcraft-README_CN.source.md`
- `template.md`
- `examples/DESIGN.example.md`
- `examples/STORYBOARD.example.md`
- `examples/demo.example.html`
- `examples/production.example.html`

### 2. 专家团通用真源

- `../team-references/video-skill-routing.md`
- `../team-references/video-production-playbook.md`
- `../team-references/digital-human-config-package-spec.md`

---

## 十三、执行备注

如果后续还要继续增强本 Skill，优先方向是：

1. 在本技能目录内补组件索引与门禁说明
2. 补充本技能自己的 `references/` 和 `examples/`
3. 继续让原技能的执行深度与当前专家团流程对齐

而不是再回到外部目录或绝对路径上取用。

