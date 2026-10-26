# 运营结果回写

读取当前 `tools/list` 中 `manage_growth_reports` 的 `payload.commerce` schema。本技能不直接调用未公开的千问后台，也不转存千问或淘宝Token；执行端取数后向品牌MCP回写。

所有请求形状：`{action:"commerce_...",payload:{commerce:{...}}}`。先 `commerce_get_workspace`，`area=operations`。

## 店铺

`commerce_bind_shop`：platform=taobao/tmall、externalShopId（真实稳定平台店铺ID，不能用掩码/臆造ID）、shopName、mappingEvidence、idempotencyKey。品牌Owner/Admin确认归属，后端核对角色和其他品牌关联。已有店铺继续其shopId，不重复绑定。若当前中台品牌与店铺不符，先找到正确品牌，不修改已有品牌名称来绕过。

## 快照

`commerce_save_shop_snapshot`：shopId、period={start,end,timezone:"Asia/Shanghai"}、currency=CNY、sourceStatus、toolName、sourceEvidence、sections、skillVersion、可选title、idempotencyKey。

sourceStatus：`unverified`=身份/原始回执未核验；`provider_reported`=已观察对应客户端取数回执，但仍是连接器上报而非平台独立审计；`test_data`=测试/演示。不要把模拟数据存成真实经营。

sections按6个业务面板组织：diagnosis经营体检、merchandising货品与转化、traffic流量推广、retention活动会员、service履约服务、review计划复盘。每项包含summary、metrics、evidence、limitations；缺接口只写缺口，不补0。metric含key、label、value（十进制字符串或null）、unit、definition。指标不跨周期/粒度混合，必要时用独立快照与明确列名。

sourceEvidence存安全的工具名/参数摘要/回执证据索引和核验说明，不放Token或无关客户信息。分页多页先核齐再写最终快照，不以第一屏代表全量。保存后读取快照核对品牌、店铺、周期、来源、字段。

## 运营方案与动作

`commerce_save_operations_plan`：shopId、snapshotId（如已有可信快照）、title、report完整方案、actions、skillVersion、expectedRevision、idempotencyKey；新方案expectedRevision=0，更新另传planId及最新revision。没有真实快照也能保存明确标注待核验的方案，但不能伪造快照引用。

每个action：stage（上述业务板块）、title、body、owner、dueDate（YYYY-MM-DD或空）、successMetric、status=proposed/in_progress/review/closed。状态是中台计划记录，不会在淘宝执行任何动作。未执行不写in_progress/closed；用户已执行的事实保留证据后再跟进。

更新保留不可变版本，冲突先回读。重试同一请求沿用原幂等键；内容变更用新键。不要把一轮取数另造为业务执行历史。页面入口 `/tabs/ecommerce/operations` 与这些动作同源。

## 1.1 增长链路扩展（兼容旧计划）

当前schema含可选growth；actions增加可选稳定key，使用复测时必须提供且唯一。growth包含businessModel、phase、direction，sequence数组每步title/outcome/exitCondition，objectives数组每项stage/metricKey/label/unit/target（十进制字符串）/direction（increase或decrease）/rationale。拟议目标必须有来源推导，未知不填0。

experiments每项actionKey/hypothesis/change/baselineSnapshotId/resultSnapshotId/stage/metricKey/executionEvidence/executedOn/comparability/review/decision（observe/continue/adjust/stop），可选同品牌内容projectId。未执行时结果快照、执行日期和证据填空串；有结果时必须先有真实执行日期YYYY-MM-DD与证据。基线/结果快照严格本品牌同店铺，项目严格同品牌。后端只保存调用者上报证据，不伪称独立审计。

workspace的plans[].growthReview给前后值、delta、targetMet、comparable/reason与来源状态。周期等长、非重叠、执行位于其间、同定义/单位只是最基本比较条件；还要核范围、成熟窗与干扰。普通前后观察不能称因果归因。旧计划没有growth仍可读取；新客户端保存须保留已有growth及行动key，不能孤立删除关联动作。全量report和旧版本继续保留。
