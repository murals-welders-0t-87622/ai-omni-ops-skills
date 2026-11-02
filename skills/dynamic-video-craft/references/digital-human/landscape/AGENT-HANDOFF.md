# Agent 交接文档

> 交接对象：后续接手 `douyin-dh-landscape-remotion-video` 的 Agent
>  
> 交接范围：本次围绕 `video-talkcraft` 完整迁移、专家团适配、本地资产落盘的全部上下文

---

## 1. 当前任务是什么

用户当前要做的是：

1. 在 `douyin-fullflow-ops` 专家团里，新增并完善一个**数字人视频专家**下面的横屏技能：
   - `douyin-dh-landscape-remotion-video`
2. 这个技能不是普通横屏数字人口播，而是：
   - A-roll 仍然是数字人
   - 数字人支持透明背景贴边、缩位到一角、阶段性让位
   - B-roll 走 **Remotion 高质量动态效果**
3. 严格参考并完整吸收：
   - `https://github.com/Vincentwei1021/video-talkcraft/blob/main/SKILL.md`
   - `https://vincentwei1021.github.io/video-talkcraft/`
4. 用户明确要求：
   - **不是临时读取外链再生成**
   - 而是要把上游技能、参考文档、卡片库、源码等**真正落到本地文件夹里**
   - 后续其他 agent 应该直接依赖本地资产工作
5. 这条技能仍然要遵守当前专家团已有规则：
   - 正式生产前必须先生成并确认：
     - `DESIGN.md`
     - `STORYBOARD.md`
     - `demo.html`

---

## 2. 用户对之前结果为什么不满意

前面已经踩过几次坑，后续接手时必须避免重复：

### 坑 1：只写“参考 talkcraft”，没有真正落地

用户明确指出：

- 不能只在 `SKILL.md` 里写几个外链
- 不能把执行责任丢给后续 agent 再临时去读

### 坑 2：把上游仓库相对路径写成了像本地路径

之前在 `SKILL.md` 里写过类似：

- `references/design-language.md`
- `template/motion-systems/Subtitles.tsx`

但当时这些文件在本地并不存在，导致用户认为在糊弄。

这个问题后来已经修正为：

- 这些文件现在已真实落盘到本地 skill 目录
- 主 `SKILL.md` 也已同步改到和本地真实文件一致

### 坑 3：只提炼了 4 张卡，不是完整卡库

用户点名问过：

- 页面里有 `78` 张卡，为什么只提了 4 张？

后续已按用户要求改成**完整迁移**

---

## 3. 当前已经完成了什么

### 3.1 已完成：本地完整镜像落盘

当前目录：

`本技能包目录`

已经真实存在这些目录：

- `assets/`
- `demos/`
- `examples/`
- `references/`
- `scripts/`
- `template/`

以及这些关键文件：

- `SKILL.md`
- `video-talkcraft-source-SKILL.md`
- `talkcraft-extracted-playbook.md`
- `talkcraft-source-manifest.md`
- `talkcraft-upstream-read-index.md`
- `template.md`

### 3.2 已完成：78 张卡和 78 份 tsx 已落盘

已现场核对：

- `references/cards/` = `78`
- `template/cards/` = `78`

这点已经不是口头说明，是真实文件数。

### 3.3 已完成：上游主 Skill 本地镜像

已复制：

- `video-talkcraft-source-SKILL.md`

作用：

- 作为上游主技能文档的本地镜像
- 便于后续 agent 不用回 GitHub 也能读主 Skill

### 3.4 已完成：本地 `SKILL.md` 初步改造

当前本地 `SKILL.md` 已经：

1. 明确这是专家团里的本地技能，不是上游原始 skill
2. 保留了适合当前专家团的本地说明
3. 写清了本地已有：
   - `references/`
   - `references/cards/`
   - `template/cards/`
   - `template/motion-systems/`
   - `demos/`
   - `assets/`
   - `scripts/`

### 3.5 已完成：已有专家团链路中的接入

此前已把这个技能接入到这些文件中：

- `agents/douyin-digital-human-video-expert.md`
- `references/skill-registry.md`
- `references/video-skill-routing.md`
- `references/digital-human-config-package-spec.md`
- `README.md`

注意：这一部分是更早完成的，当前仍然有效。

---

## 4. 当前执行状态（2026-08-30 更新）

上游资产仍以本地镜像、78 张卡和 motion systems 为基础；但它们已不再只是“完整迁移 + 本地框架”。当前 `SKILL.md` 与专家团真源已完成以下适配：

1. 先验收“已确认选题 + 创作包 + 证据规划 + 资产清单 + 任务目录”，再由本 Skill 生成 `DESIGN.md / STORYBOARD.md / demo.html`；
2. 三件套必须经用户确认，确认后才允许 TTS、数字人、素材与 Remotion 生产；
3. 明确了配音 / 数字人素材是生产输入，不由本 Skill 自行伪造；字级时间戳、Remotion 工程和三重验收成为正式生产契约；
4. 新增团队真源 `../../references/remotion-landscape-production-contract.md`，统一约束输入、闸口、工程、验收和复盘回传；
5. `video-skill-routing.md`、`handoff-contracts.md`、`skill-registry.md`、数字人视频专家和创作专家均已同步引用该契约。

示例文件仍可持续增强，但不是当前生产链路的阻断项；新增卡片选择策略时，应优先更新生产契约或本 Skill，而不是重新把工艺细节堆回上游专家文档。

---

## 5. 后续接手时最重要的约束

### 5.1 绝对不能再做的事

1. 不要再只写外链
2. 不要再把“上游相对路径”写得像“本地路径”
3. 不要再说“我读过 78 张卡”，但本地只有 4 张
4. 不要把执行责任推给后续 agent 临时回外网读取

### 5.2 必须坚持的事

1. 一切以本地已落盘资产为主
2. 如果引用上游文件，优先引用本地镜像或本地复制文件
3. 这条 skill 必须服务于你们专家团，不是纯粹原样搬运 talkcraft
4. 正式生产前仍要先出并确认：
   - `DESIGN.md`
   - `STORYBOARD.md`
   - `demo.html`

---

## 6. 后续接手建议顺序

推荐按这个顺序继续：

1. 先读：
   - `video-talkcraft-source-SKILL.md`
   - 当前本地 `SKILL.md`
   - `talkcraft-source-manifest.md`
   - `talkcraft-upstream-read-index.md`
2. 再检查：
   - `references/cards/` 78 张卡
   - `template/cards/` 78 份 tsx
   - `template/motion-systems/`
3. 然后重构当前本地 `SKILL.md`
   - 从“已完整迁移”升级为“专家团执行版”
4. 最后升级：
   - `template.md`
   - `examples/DESIGN.example.md`
   - `examples/STORYBOARD.example.md`
   - `examples/demo.example.html`

---

## 7. 关键路径与文件

### 当前 skill 目录

`本技能包目录`

### 核心文件

- `SKILL.md`
- `video-talkcraft-source-SKILL.md`
- `talkcraft-extracted-playbook.md`
- `talkcraft-source-manifest.md`
- `talkcraft-upstream-read-index.md`
- `template.md`

### 完整卡库

- `references/cards/`
- `template/cards/`

### 底层系统

- `template/motion-systems/`

### 示例

- `examples/DESIGN.example.md`
- `examples/STORYBOARD.example.md`
- `examples/demo.example.html`

---

## 8. 当前状态一句话总结

当前状态不是“还没迁移”，也不是“已经完全适配完成”，而是：

**`video-talkcraft` 已经完整本地落盘到当前 skill 目录（含 78 张卡文档与 78 份 tsx），但还需要由后续 agent 继续把这套完整资产重构成更贴合当前专家团链路的执行版技能。**
