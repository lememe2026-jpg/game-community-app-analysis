# 项目修订与学习日志

本文为项目辅助说明文档，用于解释项目文件、数据边界、复核过程或 AI 辅助方式。

## 本文依据的文件

- `portfolio/game_community_app_analysis_report.md`
- `portfolio/game_community_app_analysis_report.pdf`
- `portfolio/game_community_app_analysis_portfolio_final.pdf`
- `portfolio/portfolio_final_for_pdf.md`
- `docs/analysis_plan.md`
- `outputs/reports/review_analysis_summary.md`
- `outputs/reports/keyword_analysis_summary.md`
- `outputs/reports/download_analysis_summary.md`
- `outputs/reports/version_analysis_summary.md`
- `outputs/reports/four_source_evidence_chain_summary.md`
- `outputs/reports/report_final_text_check_20260509.md`
- `outputs/reports/pdf_generation_check_20260509.md`
- `outputs/reports/ppt_v2_check_report.md`
- `outputs/reports/project_cleanup_round2_report.md`
- `README.md`

## 当前正式报告文件

当前已确认的正式报告文件为：

- Markdown：`portfolio/game_community_app_analysis_report.md`
- PDF：`portfolio/game_community_app_analysis_report.pdf`

项目中仍保留旧版作品集相关文件：

- `portfolio/game_community_app_analysis_portfolio_final.pdf`
- `portfolio/portfolio_final_for_pdf.md`

当前 `README.md` 已完成新版入口更新，指向 `portfolio/game_community_app_analysis_report.pdf` 和 `portfolio/game_community_app_analysis_report.md`。旧版作品集相关文件仍保留在项目中，但不再是 README 主入口；如需移动或归档，应先做全项目链接一致性检查。

## 2026-05-09 报告与 PDF 同步记录

本轮正式报告继续以以下两个文件为入口：

- `portfolio/game_community_app_analysis_report.md`
- `portfolio/game_community_app_analysis_report.pdf`

文本检查记录为 `outputs/reports/report_final_text_check_20260509.md`。该检查结论为“需小修”，主要问题是两处 blockquote 形式的概括评论样例可能被误读为直接原文引用。后续已将这两处改为普通段落，并说明其为概括表达、并非评论原文。

PDF 检查记录为 `outputs/reports/pdf_generation_check_20260509.md`。本轮 PDF 已重新生成并完成检查：总页数为 13 页，6 张图表全部加载，4 张表格均未横向溢出，未发现必须修改的问题。PDF 生成方式为基于 Markdown 转换 HTML，并通过 Microsoft Edge headless / DevTools `Page.printToPDF` 输出；最终版本使用内嵌图片方式，避免相对路径在 headless 环境中丢图，且未生成临时 HTML 文件。

本轮修订的主要方向不是新增分析，而是继续降低 AI 味和运营 SOP 味：减少“求职包装 / 运营建议清单”的表达，把报告稳定为“公开数据观察报告”。报告仍保持数据边界：公开评论、关键词、七麦 iPhone 新增下载预估和公开版本日志只构成观察链，不构成因果证明链。

## 项目定位变化

早期项目更接近“作品集交付物”口径，文件名和 README 中仍保留作品集表述。新版正式报告已收束为“基于公开数据的游戏社区 App 运营分析报告”，重点从求职包装转为数据来源、解释边界、问题拆解和运营观察。

当前报告强调：

- 不评价小黑盒和游民星空谁更好。
- 不判断公司真实运营能力。
- 不把公开评论、关键词、下载预估、版本日志拼接成因果链。
- 将四类公开数据作为观察入口，而不是效果证明。

## 评论章学习

评论分析从简单评分观察，调整为“公开反馈问题入口”的拆解。

已形成的学习点：

- 评分分组用于区分正向、负向、中性公开评论，但不能代表整体满意度。
- 小黑盒负向评论使用规则分类进行主题命中，负向评论数为 338 条。
- 问题分类存在多标签命中，一条评论可能命中多个主题。
- “强负向情绪表达”和“其他”不应直接作为具体运营问题展开。
- 公开评论只能说明样本中出现过相关表达，不能代表全部用户或真实问题发生率。

建议后续继续保留“评论样例只作为表达入口”的写法，避免把个别评论放大为整体判断。

## 关键词章学习

关键词分析的定位从“搜索优化”调整为“公开搜索需求观察”。

已形成的学习点：

- 关键词不是 ASO 优化方案，也不应写成投放词分析。
- 搜索指数、排名、Top50 数量只能作为 App Store 公开搜索场景下的观察指标。
- `keyword_count` 表示场景内关键词数量，`core_clue_count` 表示被保留为核心运营线索的数量，两者不能混用。
- 内容运营、平台生态、社区运营、工具服务等场景可以作为运营线索，但不能代表真实流量或真实用户规模。
- 对“待人工复核”和“非目标/噪声复核”类关键词，应保留人工复核空间。

## 下载趋势学习

下载趋势分析已从“结果解释”收束为“七麦预估结果波动背景”。

已形成的学习点：

- 七麦 iPhone 新增下载为第三方预估值，不等于官方真实下载量。
- 月度汇总适合观察样本期内的高位月份，例如小黑盒 2025-12 月度预估较高。
- 单日峰值适合提示观察窗口，例如小黑盒 2025-12-13 单日预估高点。
- 单日峰值不应单独解释，应结合连续高位窗口观察。
- 下载波动只能作为后续复盘入口，不能写成运营动作效果。

## 版本节奏学习

版本节奏分析已明确为“公开动作背景”。

已形成的学习点：

- 版本日志只代表 App Store 公开更新文本。
- 简略日志如“修复已知问题”不适合强行拆解具体功能方向。
- 版本日志不能证明评论问题已经被处理。
- 版本日志不能说明某次下载波动的原因。
- 若要验证版本动作效果，需要内部功能使用、故障、客服、留存等数据。

## TGA 案例学习

新版报告加入了 TGA 事件窗口观察，引用图表：

- `outputs/charts/final_14_tga_daily_window_compare.png`

该案例的写法重点是方法边界：

- TGA 2025 与小黑盒 2025-12 下载高位在时间上接近。
- 两款产品存在相关公开活动线索。
- 这些信息只能提示“外部事件窗口值得观察”。
- 不能写成 TGA、活动或版本更新带来下载增长。

## 人工修改与复核原则

后续修订建议继续遵守以下原则：

- 先确认文件路径，再写引用。
- 先看数据和报告，再写结论。
- 先写边界，再写建议。
- 对无法确认的信息标注“待人工确认”。
- 对下载、版本、关键词、评论之间的关系，只写观察，不写强因果。

## 待人工确认事项

- 是否保留旧版作品集阶段记录。
- 是否进行全项目链接一致性检查。
- 是否建立公开 GitHub 仓库精简版。
- TGA 外部公开来源是否需要单独列出来源链接或截图存档。

