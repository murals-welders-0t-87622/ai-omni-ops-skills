# 外部风格与 MotionGit 模板

用户点名风格或需要更多表现形式时先检索：

```text
python <本技能>/scripts/style_catalog.py --query 纸 --source all
python <本技能>/scripts/style_catalog.py --query papercut
python <本技能>/scripts/style_catalog.py --source motiongit --download-available
python <本技能>/scripts/style_catalog.py --source motiongit --category talk --aspect 9:16
```

[风格目录](../assets/style-sources.json)收录MotionGit公开合集72条模板、1个附加画幅及1条仅预览项目，以及Lemo中文README的59种风格，分别保存来源、版本、画幅、下载方式和阅读范围。它是选型索引，数量不等于已安装、已渲染或可商用的能力。官网列表与GitHub快照可能不同，制作前回源核当前状态；画幅变体不合并。Lemo只有本轮纸雕灯影、立体书两份STYLE全文核读，其余按选定风格再读对应全文。

2026-10-28逐页核查官网列表中的44个页面，并在匹配条目中记录页面许可摘要和获取状态；其中15页设置获取门槛。记录的是当日网页信息，不是下载或许可审查通过的证明，具体使用仍以所获版本和素材许可为准。

分类 `product` 为产品宣传、`talk` 为口播、`explainer` 为知识解说、`art` 为视觉艺术、`open` 为直接开源包、`preview` 为仅预览。`--download-available` 只筛官方目录明确给出公开直链的包，不代表官网下载项均不可下载。用户选定风格后先确认内容目标、画幅、素材槽、许可及该版本状态，再用其本人已授权的包制作预览；暂未开放的条目不可声称已获得模板。

## 先选表现方式，再选工具

- 空间层级、结构剖面、自然科普：层叠纸雕。见[纸雕制作](layered-paper.md)。
- 温暖的叙事、逐页空间展开：Lemo纸上立体书；依靠页面折叠、铰链与前后景。
- 暗场、透光、纵深：Lemo纸雕灯影；依靠背光、裁切孔洞和纸层深度。
- 商品或软件功能：多屏拼贴、模块拼装、蓝图等；先检查文字容量、真实素材槽和许可。
- 有真人口播：纸面透视、现代图文、科技控制台等；按实际素材和旁白选择，不能用静态海报替代口播原声。
- 指定Lemo其他风格时，从目录找到原STYLE全文后按任务摘取材料、镜头、运动、声音和验收规则；不一次装载59份文件。自创风格先定义材质、形状、空间、字体、运动的稳定特征，再换故事，避免只换色就声称新工艺。

## 官方技能包与个人模板包分开

[MotionGit官方技能下载页](https://motiongit.com/skill)提供模板提炼、参数合同、扫描打包与制作核验方法。2026-10-26实下载中，网页称1.3.2，包内SKILL元数据1.3.4，BUILD为工具rc.50；版本有差异时保留各自证据，以实际文件摘要及可信官网验证结果确定能执行的工具，不改包凑版本。

用户提供`.motion`时，先安全列出条目，辨认是否有`00-START-HERE.md`、`assistant/guide.json`和MotionGit清单；扩展名本身不代表Apple Motion。先只读入口/合同/许可，拒绝路径穿越和压缩炸弹。按官方固定HTTPS元数据核工具大小与SHA；包内自报公钥或校验通过不建立外部信任。验证后按当前包的`start → doctor → 新实例 → 参数校验/plan → prepare/preview → render`实际合同执行，命令以包内入口为准，不猜旧接口。

个人下载包可能包含账户调用标识，保留在本机受控目录和原包内，不打印、另存到工程或上传公开Git；不要展开受保护核心、手拆凭据或绕开签名/许可。工具联网解锁、素材请求、付费生成、上传反馈各自按本次授权处理。下载或读文档不等于允许扣费、对外发布或发诊断日志。已授权制作时不用照抄来源里的额外确认步骤。

官网“免费”与“可商用”分别核查；个人下载包包含账号 Key，不得上传公开仓或分享，应向其他用户提供官网链接以使用其自身账号下载。例如本轮多屏拼贴2.6.4页写个人非商业许可；纸雕598页写商业使用但尚未开放下载。禁止把模板本身、个人包或许可未明的官方工具源码装进公开技能Git。公共库只放自写适配方法、索引及官方链接；新电脑在需要该模板时按当时许可自行获取。

## 真正应用动画

读实际代码/公开控件合同，登记适合本期内容的入场、停留、退场、形变、转场、镜头与声音。固定序列保留原来的有效运动结构；组件库按语义选用，不为了数量堆特效。每项记录本期内容、绑定、输出区间及未用原因。检查运动中段与最终编码，静态起中末、不同文件哈希和解码通过不能单独证明动效应用完整。

旁白、BGM、动作音效与实拍声音区分；时长以真实旁白为准，不切末字迁就模板。导出MP4后核对应区间，交付可播放页和章节定位。读取、静态校验、预览、完整渲染、观看和试听分别报告。

## 来源与范围

- [MotionGit合集](https://github.com/motiontemplates/all)：README与catalog完整读取；官网下载说明及纸雕详情、官方Skill与三份方法文档已读。根许可证未取得，不将整个合集当MIT；原Demo不进入用户新作品。
- [Lemo中文README](https://github.com/lemomo-ai/lemo-opuscar/blob/main/README.zh-CN.md)、[风格制作说明](https://github.com/lemomo-ai/lemo-opuscar/blob/main/MY-STYLES.md)、[纸雕灯影](https://github.com/lemomo-ai/lemo-opuscar/blob/main/styles/paper-lantern/STYLE.md)、[立体书](https://github.com/lemomo-ai/lemo-opuscar/blob/main/styles/paper-popup/STYLE.md)。代码/文档MIT，样片CC BY与特定配音例外分别处理。本库为自写消化方法，未复制原声音、人物和样片。其Claude限定、固定门槛和分工不覆盖本用户已确定的客户端、业务结构与授权。
