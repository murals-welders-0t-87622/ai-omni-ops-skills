# 交换记录示意

下列是字段说明，不是真实品牌数据。结合项目需要添加记录，不将示意写入正式系统。未知值用null。

```json
{
  "evidence": {
    "id": "本地证据标识",
    "kind": "brand_fact|platform_metric|media_observation|comment|business_event|user_preference|hypothesis",
    "source_ref": "可回读的文件、URL或真实对象引用",
    "locator": "行号、时间段或具体段落",
    "published_at": null,
    "collected_at": null,
    "fact": "来源实际支持什么",
    "limitations": "不能说明什么"
  },
  "value_card": {
    "id": "本地价值卡标识",
    "user": "决策或使用角色",
    "scenario": "具体触发情境",
    "job": "用户想完成的事",
    "pain": "可观察障碍与代价",
    "alternatives": "目前怎样处理",
    "solution": "品牌怎样改善哪一步",
    "difference": "相对哪个替代基线的有意义差别",
    "evidence_ids": [],
    "status": "hypothesis|supported",
    "limits": "适用条件、例外、过期时间"
  },
  "content_item": {
    "id": "本地内容标识",
    "title": "用户语言的具体问题",
    "value_card_id": "引用价值卡",
    "primary_task": "T1|T2|T3|T4|T5|T6",
    "secondary_tasks": [],
    "strategy_ids": ["M01"],
    "narrative_structure": "推进的因果或论证关系",
    "format": "实际呈现形式",
    "brand_role": "品牌怎样进入",
    "script_path": null,
    "claims": [{"text": "事实性表述", "evidence_ids": [], "status": "pending"}],
    "assets": [{"id": "素材标识", "path": null, "sku_status": "unknown", "rights_status": "unknown"}],
    "next_step": "下一步行动或自然收束/账号承接",
    "measurement": "本条主指标与口径",
    "experiment_group": null,
    "variant_of": null
  },
  "artifact": {
    "id": "本地文件标识",
    "content_id": "内容标识",
    "revision": "本地修订标识，非猜造服务端revision",
    "kind": "script|image|video|report",
    "path": "项目目录内的相对文件",
    "status": "planned|produced|reviewed",
    "qa": {"technical_record": null, "visual_record": null, "audio_record": null},
    "content_approval_ref": null,
    "publish_authorization_ref": null
  },
  "metric": {
    "name": "明确名称",
    "source_ref": "原始指标快照",
    "window": "同一观察窗",
    "numerator": null,
    "denominator": null,
    "unit": "内部计算口径",
    "attribution": "direct|tracked|self_reported|association|unknown"
  }
}
```
