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
