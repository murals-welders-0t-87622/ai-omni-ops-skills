# talkcraft 源码与配方卡映射清单

> 本文件记录这条本地 Skill 已读取并内化的上游文件，以及它们在本地 Skill 中的用途。
> 注意：表里的“上游文件”是 `video-talkcraft` 仓库里的相对路径，不是当前工作区的本地文件路径。

---

## 一、入口与方法论

| 上游文件 | 已吸收内容 | 本地用途 |
|---|---|---|
| `SKILL.md` | 总管线、78 卡、SHOTBOOK、三重验收、底部字幕纪律 | 本 Skill 的总执行流程 |
| `references/design-language.md` | 默认视觉语言、token、章节感 | `DESIGN.md` 的默认 token 口径 |
| `references/shot-design.md` | 三面工作单、7 类镜头预设、B-roll 同屏预设 | `STORYBOARD.md` 的镜头设计底稿 |
| `references/cinematography.md` | 七层反 PPT 系统、四套全局系统、转场哲学 | Remotion 实现纪律 |
| `references/host-footage.md` | 人物输入规格、CPU 抠像、人脸安全区、人物与 B-roll 同屏规则 | 数字人 A-roll 规范 |
| `references/taxonomy.md` | 78 卡分类体系与卡片总表 | 选卡范围和优先级 |
| `references/shotbook-example.md` | SHOTBOOK 写法示例 | 镜头分镜书写口径 |
| `references/demo-spec.md` | demo / tsx / 配方卡的约定 | 本地 demo 生成纪律 |

---

## 二、本 Skill 直接采用的关键卡

| 卡 slug | 上游文件 | 本地用途 |
|---|---|---|
| `host-shrink-to-chip` | `references/cards/host-shrink-to-chip.md` + `template/cards/host-shrink-to-chip.tsx` | 数字人缩位让台 |
| `highlighter-sweep` | `references/cards/highlighter-sweep.md` + `template/cards/highlighter-sweep.tsx` | 报告 / 引文高亮 |
| `focus-dim-spotlight` | `references/cards/focus-dim-spotlight.md` + `template/cards/focus-dim-spotlight.tsx` | 表格 / 清单 / 多卡聚焦 |
| `evidence-scroll-tour` | `references/cards/evidence-scroll-tour.md` + `template/cards/evidence-scroll-tour.tsx` | 长页证据巡游 |

---

## 三、底层系统源码

| 上游文件 | 已吸收内容 | 本地用途 |
|---|---|---|
| `template/motion-systems/camera.tsx` | 连续相机曲线 + 脉冲 | 横屏镜头相机系统 |
| `template/motion-systems/life.tsx` | idle 微动、retire 让位、defocus | 元素生命周期 |
| `template/motion-systems/transitions.tsx` | 六式运动承接转场 | 镜头边界处理 |
| `template/motion-systems/theme.ts` | 颜色、字体、网格底 | 默认主题 |
| `template/motion-systems/Subtitles.tsx` | 底部字幕素排与限次关键词 pop | 字幕纪律 |

---

## 四、本 Skill 直接继承的关键参数口径

### 1. 人物缩位

- `shrink`: `0.35~0.5s`
- `chipRatio`: `0.18`
- `gfxLag`: `0.15s`
- 方位：左下 / 右下
- 圆心：画面下 1/3 带

### 2. 荧光笔高亮

- `sweep`: `0.4~0.8s`
- `dimTo`: `0.4~0.55`
- `liftScale`: `1.03`

### 3. 聚焦压暗

- `dimTo`: 白底 `0.35~0.45`
- `jump`: `0.20s`
- `hold`: `1.0~1.5s`
- `restore`: `0.40s`

### 4. 长页巡游

- `scrollSpeed`: 约 `10% 页高/s`
- `stopHold`: `1.5s`
- `stopAlign`: `0.5`

---

## 五、执行要求

后续使用这条 Skill 时：

1. 先以本文件和 `talkcraft-extracted-playbook.md` 为准
2. 再去生成 `DESIGN.md`、`STORYBOARD.md`、`demo.html`
3. 外链仅用于溯源，不作为一线执行文档
4. 当前 Skill 目录下已落地本地镜像：
   - `references/`
   - `references/cards/`
   - `template/cards/`
   - `template/motion-systems/`
