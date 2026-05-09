# 游戏社区 App 公开数据观察：以小黑盒与游民星空为例

本仓库是一个个人学习型公开数据分析项目，用于练习数据清洗、公开信息整理、游戏社区 App 行业理解和项目文档表达。项目主要目的是帮助我理解游戏社区 App 的用户反馈、搜索需求、下载趋势和版本节奏，并尝试从用户视角转向运营视角进行观察。

本项目不代表行业研究结论，也不用于评价小黑盒、游民星空或相关公司的真实运营能力。报告中的分析均基于七麦苹果端公开导出数据和公开页面信息，只作为个人学习、复盘和项目展示使用。

## 1. 项目简介

本项目基于七麦公开导出数据与 App Store 公开信息，围绕小黑盒与游民星空两款游戏社区 App，进行用户反馈、搜索需求、下载趋势和版本节奏的描述性观察。

项目目标是在公开数据边界内，将评论、关键词、下载预估和版本日志整理为可讨论的问题线索，例如用户反馈处理、内容供给、社区氛围、工具服务和产品协同观察。这里的“观察”不等于业务复盘，也不等于因果证明。

## 2. 正式报告

- PDF：[`portfolio/game_community_app_analysis_report.pdf`](portfolio/game_community_app_analysis_report.pdf)
- Markdown：[`portfolio/game_community_app_analysis_report.md`](portfolio/game_community_app_analysis_report.md)
- PPT：[`slides/game_community_app_analysis_presentation_v2.pptx`](slides/game_community_app_analysis_presentation_v2.pptx)

当前项目报告建议优先阅读 PDF；Markdown 用于查看正文结构、图表引用和后续维护。

## 3. 公开数据观察框架

本项目使用四类公开数据，并为每类数据限定不同角色：

| 数据类型 | 角色 | 适合观察的问题 |
| --- | --- | --- |
| 评论 | 被动反馈 | 用户在公开评论中表达了哪些体验问题 |
| 关键词 | 主动需求 | App Store 搜索场景中出现了哪些内容、社区、工具或平台线索 |
| 下载趋势 | 结果背景 | 七麦预估下载在样本期内呈现出哪些月份或日期窗口 |
| 版本节奏 | 动作背景 | 公开版本日志中出现了哪些功能、内容、体验或活动相关文本 |

四源数据是观察链，不是因果链。评论、关键词、下载趋势和版本日志可以互相补充观察角度，但不能直接串成“动作到结果”的解释。

## 4. 主要观察

用户反馈处理是游戏社区 App 的基础观察议题。公开评论中出现了客服反馈、功能体验、账号绑定、交易库存、性能稳定性和社区秩序等问题线索，适合被整理为问题标签和后续复核入口。

内容供给与热门游戏话题是搜索需求中的重要线索。关键词侧显示，用户搜索心智不只围绕“社区”本身，也包括热门游戏、攻略资讯、平台生态和工具服务。

社区氛围与治理具有持续观察价值。评论侧的举报、反馈、封禁、帖子秩序等表达，以及关键词侧的社区相关搜索心智，可以作为治理议题的观察入口。

工具服务与功能体验需要产品协同。评论和关键词中都能看到登录绑定、战绩查询、库存展示、工具服务、加载稳定性等相关线索，适合进入产品与运营协同问题池。

下载趋势与版本节奏只能作为辅助观察。七麦下载为第三方预估，版本日志为公开文本，二者适合帮助标记观察窗口和公开动作背景。TGA 等外部事件窗口也只能作为外部观察变量，不能写成下载增长原因。

## 5. 项目文件结构

主要目录说明：

- `portfolio/`：正式报告 Markdown 与 PDF。
- `slides/`：展示用 PPT。
- `docs/`：数据边界、AI 辅助、Excel/SQL 复核、报告生成与修订记录。
- `outputs/charts/`：正式报告引用图表。
- `outputs/tables/`：关键汇总表。
- `scripts/`：主要数据处理与分析脚本。

本仓库为精简公开展示版，仅保留正式报告、核心图表、关键汇总表、主要脚本和必要说明文档。

## 6. 数据来源与限制

详细说明见：[`docs/data_source_and_limitations.md`](docs/data_source_and_limitations.md)

本公开仓库不包含完整 raw 数据。原始数据来自七麦苹果端公开导出和公开页面信息；考虑到评论文本、作者信息、平台导出文件和再分发边界，公开仓库仅保留报告所需的汇总表、图表和脚本。

使用本项目结论时需要注意：

- 本项目不代表官方数据或真实业务复盘。
- 七麦下载为第三方预估，只适合做趋势背景观察。
- App Store 公开评论不代表全体用户。
- 关键词搜索指数和排名不代表真实流量或真实用户规模。
- 版本日志只代表公开更新文本，不代表完整产品战略，也不能证明功能效果。
- 四源数据不能做强因果归因。

## 7. AI 辅助与人工复核

相关说明见：

- [`docs/ai_assisted_workflow.md`](docs/ai_assisted_workflow.md)
- [`docs/excel_sql_validation_notes.md`](docs/excel_sql_validation_notes.md)

AI / Codex 主要用于代码阅读、脚本解释、格式清理、检查清单、文档草稿、口径风险检查和流程记录辅助。人工负责项目选题、报告手动修改、数据解释边界、关键结论取舍、Excel 复核、图表取舍和最终口径判断。

AI / Codex 是辅助工具，不是独立完成项目。关键数字、文件路径、图表引用和边界表达需要回到项目文件中复核。

## 8. 如何阅读本项目

建议阅读顺序：

1. [`portfolio/game_community_app_analysis_report.pdf`](portfolio/game_community_app_analysis_report.pdf)
2. [`portfolio/game_community_app_analysis_report.md`](portfolio/game_community_app_analysis_report.md)
3. [`docs/data_source_and_limitations.md`](docs/data_source_and_limitations.md)
4. [`docs/ai_assisted_workflow.md`](docs/ai_assisted_workflow.md)
5. [`docs/excel_sql_validation_notes.md`](docs/excel_sql_validation_notes.md)
6. [`docs/project_revision_and_learning_log.md`](docs/project_revision_and_learning_log.md)
7. [`docs/report_generation_log.md`](docs/report_generation_log.md)

以上文档覆盖正式报告、数据边界、AI 辅助方式、Excel/SQL 复核说明、修订学习记录和报告生成记录。

## 9. 复现说明

主流程脚本包括：

- `scripts/02_clean_data.py`
- `scripts/04_analyze_reviews.py`
- `scripts/05_analyze_keywords.py`
- `scripts/06_analyze_downloads.py`
- `scripts/07_analyze_versions.py`
- `scripts/09_integrate_four_source_evidence.py`

说明：

- 本项目当前不建议随意重跑归档清理脚本。
- 如果需要重跑分析，应先备份项目，并检查输入输出路径。
- `outputs/charts/` 和 `outputs/tables/` 是正式报告和复核链路的重要依赖，整理前应先检查引用关系。
- SQL 当前未作为正式产出工具，仅作为后续复刻关键汇总的训练方向。

## 10. 后续优化方向

后续可以继续补充：

- 使用 SQL 复刻评论、关键词、下载和版本的关键汇总表。
- 在真实业务数据可用时，引入站内行为、留存、活动曝光、下载来源和客服工单等数据。
- 增加用户访谈或定性反馈，对公开评论中出现的问题线索做进一步验证。
- 为报告生成流程补充更完整的本地复现记录。

