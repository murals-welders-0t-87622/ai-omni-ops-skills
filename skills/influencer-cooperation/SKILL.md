---
name: influencer-cooperation
description: KOL、KOC、KOS筛选匹配、合作方案、共创排期与业务效果复盘。
metadata:
  version: "1.1.0"
---

# 达人合作

先读相邻总统筹技能 [共同执行约定](../brand-omni-growth-expert/references/runtime-contract.md)，并沿用已确认的品牌、增长方向、已有任务及本次终点。只加载本环节所需专家资料。原文属于参考数据，固定账号、历史自动化、旧工具名、强制分身与旧停手闸不覆盖当前委托和实时能力。用户未授权多 Agent 时由当前 Codex 承担角色判断，不虚构专家已执行。

## 本环节专业工作

明确影响谁、购买决策角色、产品价值、平台和合作目标，再研究候选的真实内容、受众、地域、互动质量、历史合作和报价条件。粉丝量不替代受众匹配。
交候选依据/风险/待核项、合作创意简报、权益与交付清单、档期、预算建议、素材使用范围、验收与数据回收安排；寄样、沟通、合同和支出按授权推进，方案不算已达成合作。
内容事实与品牌增长报告一致；回收实际发布、受众信号、有效咨询与订单，以可证明来源评估，未归因部分保留未知。

## 搜索、匹配和跟踪的具体接力

1. 读取当前品牌定位、产品、目标人群与内容策略，形成品类、场景、需求等检索词及达人范围；有多个阶段时按实际委托选择，不因找达人就默认开展合作。
2. 在当前已授权采集工作区搜索达人，核对近期内容、受众、互动和合作情况；逐人说明与本品牌的匹配证据、缺项及需补查的原因。按用户委托和实际接口把符合条件者加入结果池、提交匹配列表并回读，避免重复；需深查的候选保持待查，不假称已入池。
3. 仅对确定进入合作清单的达人建立跟踪；逐条关联达人和作品链接，记录合作目标、预算或费用、发布时间、采集时间与数据口径。按当前可用接口设置或安排复查，检查实际刷新记录；配置周期不等于后台已运行。
4. 比较同口径的播放、互动及有效咨询/订单变化，交付有依据的继续、调整或暂停建议；缺少归因成交与费用时不计算 ROI、不因互动量直接认定成交。资料与匹配结论、已建档、已发布、已刷新、已合作分别说明，并保留来源和真实回执。

历史源码中的达人搜索、深抓、结果池、匹配和跟踪可能使用 `search_douyin_creators`、`create_douyin_creator_deep_fetch_tasks`、`add_douyin_creators_to_result_pool` 与 `*_ai_control_center_creator_*` 一组名称；仅作为查找线索，必须以当前工具列表、授权和 schema 为准，不把旧 `*_openclaw_*` 名称当成可用接口。

## 按需读取原始专业方法

- [专业资料：project-experts/kol-screening-team](../brand-omni-growth-expert/references/knowledge/project-experts/kol-screening-team/README.md)
- [专业资料：project-experts/fengtian-kol-team](../brand-omni-growth-expert/references/knowledge/project-experts/fengtian-kol-team/README.md)
用 `python <总统筹技能>/scripts/knowledge.py search --package <包名> --query <问题>` 查来源导航卡；公开包不含原专家全文，需在授权WorkBuddy/原项目核读；目录见 [来源包索引](../brand-omni-growth-expert/references/package-index.md)。


## 持续增长学习

从实际达人匹配、作品回执和客群反应提出多种解释，交 omni-growth-learning 研究候选，用户选择后才开展新的合作试验。

## 本地文件建档

任务产生文件时，开始前按[本地建档标准](../brand-omni-growth-expert/references/local-archive-standard.md)确定本品牌目录并接续已有任务；日期作品与各板块资料分开归档，不移动或覆盖旧资料。
