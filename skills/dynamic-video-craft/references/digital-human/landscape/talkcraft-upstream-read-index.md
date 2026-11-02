# talkcraft 上游阅读索引

> 这份文件专门解决一个问题：
> `SKILL.md` 里出现的那些 `SKILL.md`、`references/...`、`template/...` 路径，
> 是 **`video-talkcraft` 上游仓库中的相对路径**，不是当前工作区里的本地文件。

---

## 一、为什么你刚才会看不到

因为我上一版把“上游仓库路径”直接写进了本地 Skill，看起来像是本地文件路径。

这会造成误解：

- 你会以为当前目录下应该有 `video-talkcraft/SKILL.md`
- 但实际上我想表达的是：
  - 我读了上游仓库里的 `SKILL.md`
  - 并把内容提取到了本地文件

这个写法不严谨，已经在 `SKILL.md` 里改正了。

---

## 二、后续应该优先看哪些本地文件

这几个才是当前工作区里**真的存在**、并且应该优先打开的本地文件：

1. `talkcraft-extracted-playbook.md`
2. `talkcraft-source-manifest.md`
3. `template.md`
4. `examples/DESIGN.example.md`
5. `examples/STORYBOARD.example.md`
6. `examples/demo.example.html`

---

## 三、我实际读取过的上游文件

下面这些是 `video-talkcraft` 仓库里的相对路径：

### 方法论文档

- `SKILL.md`
- `references/design-language.md`
- `references/shot-design.md`
- `references/cinematography.md`
- `references/taxonomy.md`
- `references/host-footage.md`
- `references/shotbook-example.md`
- `references/demo-spec.md`

### 关键配方卡与源码

- `references/cards/highlighter-sweep.md`
- `references/cards/focus-dim-spotlight.md`
- `references/cards/evidence-scroll-tour.md`
- `references/cards/host-shrink-to-chip.md`
- `template/cards/highlighter-sweep.tsx`
- `template/cards/focus-dim-spotlight.tsx`
- `template/cards/evidence-scroll-tour.tsx`
- `template/cards/host-shrink-to-chip.tsx`

### 底层系统源码

- `template/motion-systems/camera.tsx`
- `template/motion-systems/life.tsx`
- `template/motion-systems/transitions.tsx`
- `template/motion-systems/theme.ts`
- `template/motion-systems/Subtitles.tsx`

---

## 四、本地化后的使用原则

后续使用这条 Skill 时：

1. 先读本地提取文档
2. 不把上游仓库相对路径当成本地文件路径
3. 外链只做溯源，不做一线执行入口
