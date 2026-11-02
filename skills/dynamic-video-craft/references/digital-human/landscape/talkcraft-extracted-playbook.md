# talkcraft 本地提取执行手册

> 这是为 `douyin-dh-landscape-remotion-video` 本地提取的执行手册。
> 作用：让后续 agent 不需要先回外网读 `video-talkcraft`，就能直接按已内化的方法和源码映射开工。

---

## 一、已提取的上游核心结论

### 1. 这不是“做几个炫动效”，而是一条口播成片管线

上游主线是：

`口播稿 -> 配音 / 时间戳 -> 素材 -> SHOTBOOK -> 全局系统 -> 镜头实现 -> 渲染 -> 三重验收`

对这条本地 Skill 最重要的是：

1. 语义段落切镜
2. 一个节拍只有一个主角
3. 说完就让位
4. 任何镜头都不能像 PPT 一样死掉

### 2. 七层模型是消除 PPT 感的根结构

1. 相机层
2. 焦点层
3. 主体层
4. 附着层
5. 配角层
6. 环境层
7. 遮罩层

### 3. 四套全局系统先于场景

1. `camera.tsx`
2. `life.tsx`
3. `transitions.tsx`
4. `theme.ts`

### 4. 底部字幕必须素排

- 不做动效
- 唯一例外是 `keyword-pop-highlight`
- 全片最多 3 次

### 5. 人物和 B-roll 同屏有明确定版纪律

1. B-roll 是这拍主角
2. 数字人缩位为角标常驻
3. 角标只能在左下或右下
4. 角标一旦落位就锁死
5. 人必须继续是视频，不许静态头像化

---

## 二、本地 Skill 默认采用的 4 张骨干卡

### 1. `host-shrink-to-chip`

用于：

- 人物让台给图表 / 界面 / 长页 / 截图

关键口径：

- shrink: 0.42s
- chipRatio: 0.18
- gfxLag: 0.15s
- chipScale: 0.72

### 2. `highlighter-sweep`

用于：

- 引用文字
- 报告段落
- 新闻摘要

关键口径：

- sweep: 0.6s
- dimTo: 0.4
- liftScale: 1.03

### 3. `focus-dim-spotlight`

用于：

- 表格
- 参数对比
- 清单
- 多卡版面

关键口径：

- dimTo: 0.40
- jump: 0.20s
- hold: 1.0~1.5s
- restore: 0.40s

### 4. `evidence-scroll-tour`

用于：

- README
- 协议
- 长文档
- 搜索结果页

关键口径：

- scrollSpeed: 130px/s（约 10% 页高/s）
- stopHold: 1.5s
- stopAlign: 0.5

---

## 三、本地 Skill 默认采用的镜头关系

### 1. 开场

- 数字人全高或贴边建立人物
- 不要一开场就直接缩成角标

### 2. 讲证据 / 界面 / 数据

- 数字人缩位让台
- B-roll 主导
- 优先使用：
  - `focus-dim-spotlight`
  - `evidence-scroll-tour`
  - `highlighter-sweep`

### 3. 强证据段

- 允许纯 B-roll
- 但下一段主持人回归时要保持系统连续

### 4. 结论段

- 数字人回到主导位
- B-roll 只做托底和结论强调

---

## 四、生产母本映射

### 1. 卡源码

- `template/cards/host-shrink-to-chip.tsx`
- `template/cards/highlighter-sweep.tsx`
- `template/cards/focus-dim-spotlight.tsx`
- `template/cards/evidence-scroll-tour.tsx`

### 2. 系统源码

- `template/motion-systems/camera.tsx`
- `template/motion-systems/life.tsx`
- `template/motion-systems/transitions.tsx`
- `template/motion-systems/theme.ts`
- `template/motion-systems/Subtitles.tsx`

### 3. 方法论文档

- `references/design-language.md`
- `references/shot-design.md`
- `references/cinematography.md`
- `references/host-footage.md`
- `references/taxonomy.md`
- `references/demo-spec.md`

---

## 五、这条 Skill 使用时的固定顺序

1. 先定画幅和视觉 token
2. 再定数字人三种模式怎么分配
3. 再定哪几段用哪几张骨干卡
4. 再写 `DESIGN.md`
5. 再写 `STORYBOARD.md`
6. 再做 `demo.html`
7. 用户确认后再正式制作

---

## 六、禁止事项

- 禁止把外链当成本 Skill 的主要执行依据
- 禁止只写“参考 talkcraft”
- 禁止跳过骨干卡和系统映射，临时随手拼效果
- 禁止没有 demo 就直接做成片
