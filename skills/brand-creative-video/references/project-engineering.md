# 项目工程、版本与接续

## 两种项目构建能力

默认构建本技能的文件工程，不依赖另装软件、数据库或常驻服务。可选接入用户明确指定且已运行的 LocalMiniDrama，用其项目/集/资产/分镜/任务与导出能力。两种工程不能声称格式天然兼容；转换前核对源对象ID、字段、媒体引用和API版本。

需要时从LocalMiniDrama官方仓核读其openclaw-skill、当前实现及short-drama接口文档；本包未缓存这些原文件。软件安装、依赖执行、监听端口与部署属于另一个实际行动，不因阅读项目文档就自动进行。

## 文件工程

```text
project.json                  项目、品牌、集数、目标、授权范围
research/reference-ledger.json 来源阅读和原创转化记录
brief/                        品牌事实、受众、解决办法与风格
scripts/                      不可变剧本修订
assets/assets.json            图片母版/场景/道具/品牌/首帧注册
assets/{characters,scenes,props,logos,keyframes}/
storyboard/shots.json          叙事镜头、可生成片段、依赖与状态
storyboard/prompts/            逐片段图片词、视频词及槽位映射
runs/events.jsonl             本地提交意图、实际回执、状态和费用
runs/{requests,responses,raw}/ 请求、原回执、原始输出
edit/                        时间线、裁切、音轨及字幕
exports/                     成片/预览
qa/                          资产、逐镜、声音、成片检查
state/checkpoint.json          当前状态与下一步恢复入口
```

标识分开：项目ID、集ID、剧本修订、资产ID+版本、镜头ID+修订、供应商job ID、剪辑时间线版本。用户改一句台词不新建整个项目；新资产版本不覆盖旧图片；重剪不把供应商原片改掉。

## 数据关系

剧本→角色/场景/道具清单→图片母版→镜头首帧→生成片段→剪辑段→成片。资产记录包含`id/revision/type/master_id/appearance/inherit/exclude/file/sha256/status`。镜头记录包含`id/episode/start/end/scene_id/asset_refs/keyframe_id/entry_state/action/camera/exit_state/dialogue/audio/generation_duration/trim/prompt/status`。

一个叙事段可有多个生成片段，例如“飞机→接车→酒店”不能当一个连续地点、一个首帧硬生成。用`segment_of`记录母段，片段都引用稳定母版。单段模型最短4秒而剪辑只用2秒时，生成4秒、记录实际可用区间，裁掉多余部分；不得把所有片段原长相加当最终时长。

品牌片尾是允许独立排版的设计镜头；不能用它代替缺失剧情。原片、裁切片和最终合成都留来源hash和时间偏移。

## 状态与授权

`planned → assets_pending → assets_ready → reserved → submitted → running/queued → generated → reviewed → edited → delivered`。另有`failed`、`outcome_unknown`、`stale`。这些只是本地工程状态，不覆盖供应商原始状态。

用户确认脚本、允许生成、允许发布分别记真实范围；不要由程序捏造用户批准。`authorization`为空表示未记录，不是自动拒绝一切；AI先回读聊天中明确授权，按项目范围记录来源，然后执行，不强迫用户重复已经说过的话。

## 关键命令

```text
project.py init --root <目录> --brand <品牌> --title <名称>
project.py init --root <目录> --brand 虚构教学品牌 --title 形状教学 --example demo-two
project.py validate --root <目录>
project.py validate --root <目录> --for-generation
project.py status --root <目录>
project.py reserve --root <目录> --shot <ID> --request <请求json> --provider <名称>
project.py event --root <目录> --shot <ID> --state submitted --job-id <真实ID> --evidence <实际回执文件>
project.py event --root <目录> --shot <ID> --state generated --job-id <真实ID> --evidence <实际结果回执>
project.py invalidate --root <目录> --asset <ID> --reason <实际修改>
```

初始化不覆盖已有目录；提交意图用排他锁写入。`reserve`不发网络请求，只为宿主下一次实际调用准备可恢复的记录。供应商返回之后保存原回执，再登记`event`。`failed`只表示该次明确失败；是否可重提仍由当前授权和预算决定。无任务ID的`reserved/outcome_unknown`不能简单当失败重试。

## 改动与恢复

改人物母版→标记使用它的首帧及片段待审；已生成片段不删除。改台词→复核相关片段的口型/声线/时长；改镜头顺序→复核连续性和剪辑；只改品牌落版→不重生成全片。

每个检查点写“已证实、待核实、当前文件版本、真实运行任务、下一步”。异常退出后先读事件日志，找未对账的提交意图；HTTP超时不等于没有扣费。先查供应商或MCP回执，不创建重复任务。
