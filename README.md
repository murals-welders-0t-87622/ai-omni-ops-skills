# 品牌增长统一技能库

配合 **AI全域运营中台** 使用，让Codex从老板的业务委托出发，组织品牌、公域、电商、私域、销售和制作工作，并把任务、产物、版本和经营结果保存回中台。

**交流与中台合作：微信 `hbwangxiaodong`。** 本仓公开的是配套运营技能和方法；品牌数据、账号与中台服务需独立配置。

## 第一步：安装和更新整套系统

新电脑先取得本公开技能仓库，用 Codex 打开仓库后直接说：**“请读取 skills/00-omni-system-setup/SKILL.md，按它安装整套系统。”** 已在 Codex 中发现该技能时也可说：**“使用 $00-omni-system-setup 安装整套系统。”** 已安装的电脑说：**“使用 $00-omni-system-setup 更新整套系统。”** Codex 会按[安装更新技能](skills/00-omni-system-setup/SKILL.md)识别新装或更新、准备 Docker 中台和配套技能并逐项验证。中台发行源码公开，不需私有仓账号；Docker、Codex、网络和模型配置仍需在目标电脑具备。历史数据迁移和第三方业务授权分开核实。

## 结构化分工

|层次|内容|负责什么|
|---|---|---|
|总统筹|品牌全域增长策略专家团 · brand-omni-growth-expert|从生意模式、客户需求和经营事实判断阶段、方向、优先级与跨板块协同|
|业务与工艺|业务、制作及安装与持续学习入口|内容/GEO/全网/广告/达人、电商、私域/AI销售、制作/分发、资料/复盘/维护|
|专业知识|通用方法、209个来源包导航、279个角色及687个原Skill目录|按当前业务环节取用必要专业知识；目录数量含镜像和历史，不代表独立已验能力|

业务主线保持 **生意模式→战略→策略→执行→数据反馈**。战略说明先完成什么，策略说明通过哪些组合动作完成，执行落到产品、人群、内容、价格/库存、时间和负责人，反馈对照流量、转化、客单、复购等实际目标。

详见 [架构](docs/ARCHITECTURE.md)、[业务路由](skills/brand-omni-growth-expert/references/business-routing.md)、[全部25项](registry/skills.json)、[来源导航](skills/brand-omni-growth-expert/references/package-index.md)。

## 新电脑安装

准备Codex、Git、Python 3.10+，克隆本公开仓后让Codex执行安装：

```text
git clone https://github.com/murals-welders-0t-87622/ai-omni-ops-skills.git
cd ai-omni-ops-skills
python scripts/validate.py
python scripts/manage.py install --dry-run
python scripts/manage.py install
python scripts/manage.py doctor
```

也可以对Codex说：**“按照这个仓库的AGENTS和README，安装整套品牌增长技能，检查结果；连接器缺什么单独告诉我。”**

默认25项安装到用户的 `~/.agents/skills`。旧电脑已在 `~/.codex/skills` 使用同名技能时显式指定 `--target` 选择原目录，避免重复。只装总统筹/资料/复盘/维护可用 `--profile core`；单项 `--skill youzan-private-operations` 会补齐依赖。

已有同名未托管文件会阻止覆盖；审查后才用 `--adopt-existing` 纳管并备份。已受管但本地修改过的文件也不会被强覆盖。克隆本身不会执行安装。当前会话未发现新技能时开启新对话或重载客户端；安装和原生加载须分别核验。

中台MCP与所需有赞、3Chat、千问、豆包、生成或分发服务按本品牌独立连接，凭据不进Git。按 [连接说明](docs/CONNECTIONS.md) 和 [依赖清单](registry/external-dependencies.json) 核实真实工具，缺失能力不能靠技能文字补成已可用。安装位置与发现机制参见 [OpenAI官方技能文档](https://learn.chatgpt.com/docs/build-skills)。

## 怎么使用

产生本地文件的品牌任务，在开始前按[品牌业务本地建档标准](skills/brand-omni-growth-expert/references/local-archive-standard.md)确定品牌和板块目录；内容作品按日期与作品分别归档。目录初始化工具按当前任务创建，旧资料不会自动移动或覆盖。

直接说业务需求：“给这个品牌安排本周增长重点”“按今天选题做条视频先给我看”“本周私域先做什么”“复盘为什么转化下降”“继续昨天那项工作”。

总统筹先读有效品牌上下文，按环节调用领域方法；已经确认的专项成果可接着做。用户不用提供工具路径或参数。没有真实外部调用，不声称已调用某个专家；不强制启动多个Agent。

## 从经营反馈主动学习

执行品牌任务时，`omni-growth-learning` 根据实际数据或用户反馈发现问题，查找可用资源并提出多种解释；准备可验证的优化候选，用户选择后才推进实验和实际改变。实验结果先归本品牌，跨场景方法交维护技能整理到相应领域。每周汇报属于技能内的可用工作方式，不代表已设置定时任务或后台监控。

## 持续学习和优化

**WorkBuddy、GitHub、用户反馈及新资料是持续改进来源。** 运行出现缺口先查本库；需要补方法时搜索可用专业技能和官方/原作者项目，核读版本/文档/代码，分类写进对应领域，做必要验证后同步本仓。品牌事实留品牌中台，通用工艺和可靠性留技能库。

主框架、总职责和业务阶段受架构锁约束；需要改变时先向用户展示差异并确认，不能为了吸收新方法自行重构。此机制在执行委托时生效，不创建后台监控或定时任务。详见 [持续学习机制](docs/CONTINUOUS-LEARNING.md) 与 [维护技能](skills/omni-skill-maintenance/SKILL.md)。

本次视频教程补入按用途选视觉/绘制/引擎、Remotion与真实/生成媒体混合、统一声画时钟、稳定随机/投影、字体/解码/短段性能及Windows恢复。现有Remotion方法继续保留；新路线按验证状态使用，未把阅读教程当作全部成片已实测。 后续已真实完成白板、动态数据、3D概念商品和国风水墨四种工艺练习；具体已验/未验及可复用纠错见 [真实出样方法](skills/dynamic-video-craft/references/sample-validation.md)，不外推其他路线或经营效果。见 [来源采用记录](registry/learning-sources.json)。

新增 [MotionGit/Lemo风格与模板使用](skills/dynamic-video-craft/references/template-sources.md)：MotionGit与Lemo来源索引、官方.motion读取/许可分离、纸雕科普与中文旁白方法。已经真实制作原创纸雕样片，未把公开预览冒称模板已下载。

## 更新、验证与回退

```text
git pull --ff-only
python scripts/validate.py
python scripts/manage.py install --dry-run
python scripts/manage.py install
python scripts/manage.py doctor
python scripts/manage.py rollback --transaction <安装回执中的transaction>
```

回退检查安装后的本地修改，保存旧文件和回退后文件。中断先看目标目录 `.omni-skills-backups/<transaction>/transaction.json`，恢复文件不重放业务动作。贡献/维护先读AGENTS，更新方法版本、来源、CHANGELOG和发布清单再正常提交，不force。

## 公开范围

本版完整提供25项通用技能、自有工程/模板和专业方法；来源目录是导航，**不包含旧版私有原文全集、真实品牌项目、客户资料、凭据或未核清再分发的第三方全文**。旧完整私有历史另行保留。需要专有资料时从用户已授权WorkBuddy/中台或可访问原项目读取，拿不到就明确缺项，不能声称目录卡就是专家全文。

第三方代码、样片、字体、音乐、人物、数据与云服务各自核使用条件；本仓公开可访问不替代第三方授权，也不承诺经营效果。详见 [公开范围与来源](docs/PUBLIC-DISTRIBUTION.md) 和 [验收边界](docs/VALIDATION.md)。曾克隆旧私有版的电脑应保留旧目录另克隆新版，避免把旧完整历史推到公开仓。

MotionGit 官方模板入口及可获取状态已更新至视频技能目录；官网个人包含账号 Key，应保留本机，各用户使用自己的账号获取。目录不代表模板已下载或可商用。
