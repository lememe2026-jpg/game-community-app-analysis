# AI 辅助工作流与人工判断边界

本文为项目辅助说明文档，用于解释项目文件、数据边界、复核过程或 AI 辅助方式。

## 本文依据的文件

- `portfolio/game_community_app_analysis_report.md`
- `portfolio/game_community_app_analysis_report.pdf`
- `docs/analysis_plan.md`
- `outputs/reports/cleaning_report.md`
- `outputs/reports/review_analysis_summary.md`
- `outputs/reports/keyword_analysis_summary.md`
- `outputs/reports/download_analysis_summary.md`
- `outputs/reports/version_analysis_summary.md`
- `outputs/reports/four_source_evidence_chain_summary.md`
- `outputs/reports/pdf_final_check_report.md`
- `outputs/reports/pdf_generation_check_20260509.md`
- `outputs/reports/ppt_v2_check_report.md`
- `outputs/reports/project_cleanup_round2_report.md`
- `README.md`

## 文档目的

本文用于说明 AI / Codex 在项目中的辅助范围，以及哪些判断必须由人工完成。它不是工具宣传，也不用于说明 AI 独立完成项目。

AI 辅助不等于完全黑箱生成，也不等于人工没有参与；项目定位、证据边界、报告重写、Excel 复核和最终口径判断仍由人工负责。

## AI / Codex 辅助过的环节

根据项目文件和当前整理过程，AI / Codex 可作为以下环节的辅助工具：

- 代码阅读：帮助理解 `scripts/` 中清洗、评论、关键词、下载、版本和四源整合脚本的用途。
- 脚本解释：辅助解释输出表和图表如何由脚本产生，但不替代人工复核。
- 文档草稿：辅助生成报告、检查记录、交接文档、学习日志等草稿。
- 格式清理：辅助检查 Markdown 结构、路径引用、图表清单和边界表述。
- PDF 生成：旧版记录显示曾使用 HTML/CSS 与 Microsoft Edge headless 导出旧版 PDF；当前正式 PDF 已由 `outputs/reports/pdf_generation_check_20260509.md` 记录，生成方式为基于 Markdown 转 HTML，并通过 Microsoft Edge headless / DevTools `Page.printToPDF` 输出。最终版本使用内嵌图片方式，避免相对路径在 headless 环境中丢图，未生成临时 HTML 文件；检查结果为 13 页、6 张图全部加载、4 张表格未横向溢出，未发现必须修改的问题。
- 图表补充：辅助识别正式报告引用图表，包括 `final_14_tga_daily_window_compare.png` 的 TGA 窗口图。

## 人工负责的环节

以下环节应由人工负责最终判断：

- 项目定位：将项目从求职包装型作品集收束为公开数据运营分析报告。
- 证据边界：判断哪些结论可以写，哪些只能写成观察。
- 报告重写：确定正式报告的章节结构、论证顺序和最终口径。
- Excel 复核：核对关键表格、月份、峰值、评论数量和关键词场景数量。
- 图表保留：决定哪些图表进入正式报告，哪些仅作为过程图表保留。
- 最终口径判断：决定 README、docs、portfolio 中哪些文件作为正式入口。

## 被降级或删除的表达

项目写作中应避免或降级以下表达：

- “导致下载增长”
- “证明增长”
- “活动拉动下载”
- “版本更新解决了评论问题”
- “关键词证明真实需求规模”
- “下载预估代表真实下载”
- “版本日志证明产品策略”
- “社区治理成熟度强判断”
- “强制转化”“承接效率已验证”等效果判断

建议替换为：

- “提示观察窗口”
- “可作为公开动作背景”
- “可形成交叉观察”
- “适合后续结合内部数据验证”
- “公开数据不足以完成因果归因”

## 面试中可以如何真实解释 AI 使用

可采用克制表述：

- 本项目使用 AI / Codex 辅助阅读脚本、整理草稿、检查路径和统一边界表述。
- 数据理解、分析口径、报告是否保留某个结论，需要人工判断。
- 对关键结论，会回到 CSV、图表和正式报告中复核。
- AI 输出不直接作为最终结论，必须经过人工筛选和修订。

不建议表述为：

- AI 独立完成了项目。
- AI 证明了某个增长原因。
- AI 代替了人工分析和业务判断。
- AI 自动生成的内容无需复核。

## 使用 AI 时的复核原则

- 对数字、路径、日期必须回到项目文件核对。
- 对下载、关键词、版本和评论之间的关系，只写观察，不写效果证明。
- 对外部事件只写公开信息存在，不写真实影响。
- 对无法确认的信息标注“待人工确认”。
- 对正式交付物，优先以 `portfolio/game_community_app_analysis_report.md` 和 PDF 为准。

## 待人工确认事项

- 公开展示时是否需要压缩 PDF 生成方式说明，只保留正式 PDF 路径和检查报告路径。
- 哪些图表补充是 AI 辅助生成，哪些是人工手动生成或修订。
- 是否需要在正式文档中公开说明 AI 使用范围。
- 面试或展示时是否需要将该说明压缩为口头版本。

