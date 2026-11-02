# `douyin-dh-landscape-remotion-video` 交接模板

> 用途：给“口播数字人 + 横屏 + Remotion 高动态视频”这个 Skill 做任务交接。
> 这不是固定成稿，而是最小完整输入模板。

使用前先读：

1. `talkcraft-extracted-playbook.md`
2. `talkcraft-source-manifest.md`

---

## 一、任务基础信息

- 任务日期：
- 品牌 / 项目名：
- 内容标题：
- 当天任务目录绝对路径：
- 推荐视频专家：`douyin-digital-human-video-expert`
- 推荐 Skill：`douyin-dh-landscape-remotion-video`
- 推荐理由：

---

## 二、上游输入清单

必须附齐：

1. `【XX年XX月XX日抖音文案.md】` 或已确认口播稿
2. 选题报告
3. 创作专家交接提示

建议补充：

- 配音音频或 TTS 方案：
- 主持人素材：
- 主持人是否可透明背景：
- 产品截图 / 网页截图 / 数据图：
- 关键证据画面：
- 希望参考的 talkcraft 配方卡方向：
- 是否有可复用的人物透明背景素材：
- 是否需要人脸安全区检测：

---

## 三、内容理解摘要

### 1. 这条视频要讲清什么

- 核心主题：
- 目标用户：
- 要解决的问题：
- 希望用户记住的一句话：

### 2. 为什么适合横屏 Remotion 数字人视频

- 为什么不走普通横屏 HTML：
- 为什么需要更强 B-roll：
- 哪些信息必须靠动态镜头讲清：

---

## 四、配置文档包

正式生产前必须先生成：

1. `DESIGN.md`
2. `STORYBOARD.md`
3. `demo.html`

### 4.1 `DESIGN.md` 约束

- 画幅：横屏
- 视觉关键词：
- 主色 / 高亮色：
- 数字人默认模式：
- 是否允许缩位让台：是 / 否
- 是否允许纯 B-roll 段：是 / 否
- 字幕风格：
- 默认主题来源：`theme.ts` / 自定义
- 底部字幕是否坚持素排：是 / 否（默认必须是）

### 4.2 `STORYBOARD.md` 约束

- 预计总时长：
- 预计总段数：
- A-roll 主导段：
- B-roll 主导段：
- 双主导段：
- 配方卡或动效系统建议：
- 选用的核心卡 slug：
- 选用的 motion-systems：

### 4.3 `demo.html` 约束

- 页面必须可预览
- 必须能看出横屏布局
- 必须能看出数字人贴边或缩位关系
- 必须能看出 B-roll 的高动态结构

---

## 五、镜头级规则

### 1. 数字人模式

每段必须指定以下其一：

- 贴边主持
- 缩位让台
- 暂时隐藏

并明确：

- 左贴边 / 右贴边
- 左下角 / 右下角
- 是否需要 chip 方案

### 2. B-roll 模式

每段必须指定以下其一或多个：

- 聚焦压暗
- 图表生长
- 证据巡游
- 素材堆叠
- 画中画放大
- 缓推 / 缓拉 / 巡游

推荐直接用 slug 写清：

- `focus-dim-spotlight`
- `highlighter-sweep`
- `evidence-scroll-tour`
- `host-shrink-to-chip`
- `push-through-transition`
- `overexpose-flip-transition`
- `whip-pan-transition`

---

## 六、最终输出清单

至少输出：

- `DESIGN.md`
- `STORYBOARD.md`
- `demo.html`
- 配音音频
- 数字人主持素材
- Remotion B-roll 段
- 最终作品 mp4

---

## 七、验收清单

- [ ] 配置文档三件套已生成
- [ ] `demo.html` 不是空壳
- [ ] 横屏结构清晰
- [ ] 已明确每段数字人模式
- [ ] 已明确每段 B-roll 动效方式
- [ ] 用户已确认三件配置文档
