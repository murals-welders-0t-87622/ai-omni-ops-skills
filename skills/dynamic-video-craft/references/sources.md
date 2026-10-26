# 来源与复用说明

检查日期：2026-09-03。本技能由用户给出的以下四个入口形成，名称与路径用于定位原作：

- [video-shotcraft 仓库](https://github.com/Vincentwei1021/video-shotcraft)
- [Shotcraft 镜头画廊](https://vincentwei1021.github.io/video-shotcraft/library.html)
- [video-talkcraft 仓库](https://github.com/Vincentwei1021/video-talkcraft)
- [Talkcraft 演示站](https://vincentwei1021.github.io/video-talkcraft/)

固定索引版本：Shotcraft `6c116cbd24eeb43c99d396696b509f8d88e58789`；Talkcraft `6c43c0f8c7f260d372610c25ac9587f720db8d14`。数量以附带 JSON 的实际记录为准，不沿用 README 中可能滞后的数字。

Shotcraft 提供产品理解到镜头实现的流程、真实页面素材方法、镜头卡与多个变体；Talkcraft 提供语音时间锚、解说画面编排和连续空间运动的参考。新技能将其作为资料，重新组织中文制作指引，未照搬作者过去用户的确认习惯或宣传要求。

`assets/remotion-starter/`、本技能的 Python 脚本为独立编写，没有内置两项目的 TSX、语音识别脚本、音乐、模型或人物素材。`recipe-index.json` 为路径与标识索引，链接回上游；其中 Shotcraft 的样式标识与标签为精简后的目录元数据，附带 [Apache-2.0 许可证](licenses/shotcraft-APACHE-2.0.txt) 并在索引 notice 中注明来源及修改。参考同类动效不等于原版卡片已经实装，也不构成原作者背书。

直接使用上游文件时：

- Shotcraft 的 [LICENSE](https://github.com/Vincentwei1021/video-shotcraft/blob/6c116cbd24eeb43c99d396696b509f8d88e58789/LICENSE) 为 Apache-2.0。复制或修改其文件时携带许可证、保留相应通知，标明修改；音乐与图片还要读各自来源说明。
- Talkcraft 的 [LICENSE](https://github.com/Vincentwei1021/video-talkcraft/blob/6c43c0f8c7f260d372610c25ac9587f720db8d14/LICENSE) 为 PolyForm Noncommercial 1.0.0，仓库明确说明工具包商业使用需作者事先授权。未有适用授权时，商业制作不用其代码和资产；本技能自写骨架不依赖它。
- Remotion、字体、BGM、素材及其他依赖的许可各自适用，不能由上游视频归属说明推导出所有依赖都免费商用。需要判断具体组织的 Remotion 使用资格时查询其当前官方许可。

研究资料留在创建本技能的工作区 `research/`，不随技能包分发。技能不自动向任何作者、平台发送消息或上传用户视频。
