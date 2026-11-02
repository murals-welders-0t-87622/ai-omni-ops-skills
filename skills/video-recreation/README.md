# 视频复刻：上游完整方法与中台适配

本技能基于 [gnipbao/minimax-h3-video-reverse-skill](https://github.com/gnipbao/minimax-h3-video-reverse-skill/tree/codex/initial-release) 的 `2fd1cc182606b81b69e0a9dca31c6cc7c2e973af`，保留原项目的技能主体、8 份参考、脚本、原创示例、测试和版本演进文档。作者版权和 MIT 许可见 [LICENSE](LICENSE)。上游 README 中的第三方赞助商图标及宣传不属于复刻能力，未复制。

AI 中台按 [中台衔接](references/mcp-handoff.md) 获取当前品牌资料、参考作品和运行时实际工具，用户要求成片时使用其指定且可用的生成能力；上游提示词与事实契约仍作为观察及反推主体。当前入口的名称、版本、生成和品牌改编交接，以及仓库检查脚本的 frontmatter 校验，因中台技能库结构进行了适配。原项目没有声称生成相似度已验收，本适配也没有。

从 [技能入口](SKILL.md) 开始；观察证据、音轨、用户确认、T2VA/I2V/DUAL 和分镜校验各有独立参考文档。`scripts/check_repo.py` 可运行上游回归；工具检查结构和证据声明，不能代替连续观看、听审或生成质量验收。
