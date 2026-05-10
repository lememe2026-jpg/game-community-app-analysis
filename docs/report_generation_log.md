# 报告生成状态记录

本文用于记录当前公开仓库中项目报告的生成状态、展示文件和图表引用情况。

## 项目定位

本报告作为个人学习型公开数据分析项目的正式输出文件，主要用于展示分析过程、公开数据边界和报告表达，不代表官方业务结论。

## 本文依据的公开仓库文件

- `portfolio/game_community_app_analysis_report.md`
- `portfolio/game_community_app_analysis_report.pdf`
- `slides/game_community_app_analysis_presentation_v3.pptx`
- `outputs/charts/`
- `README.md`

## 当前项目报告

当前已确认的项目报告文件：

- Markdown：`portfolio/game_community_app_analysis_report.md`
- PDF：`portfolio/game_community_app_analysis_report.pdf`

当前 PDF 与 Markdown 对应的是公开仓库正式展示版本。公开仓库不包含旧版报告、旧版 PPT、归档目录或过程检查报告。

## 2026-05-09 报告与 PDF 同步记录

本轮确认当前项目报告入口为：

- Markdown：`portfolio/game_community_app_analysis_report.md`
- PDF：`portfolio/game_community_app_analysis_report.pdf`

本轮 PDF 已完成生成与检查：页数为 13 页，6 张报告图表均已加载，4 张表格均未横向溢出，未发现必须修改的问题。

PDF 生成方式为基于 Markdown 转换 HTML，并通过 Microsoft Edge headless / DevTools `Page.printToPDF` 输出。最终版本使用内嵌图片方式，避免相对路径在 headless 环境中丢图；本轮未生成临时 HTML 文件。

本轮报告修订性质主要是降低 AI 味和运营 SOP 味，将报告从过强展示和运营建议清单进一步调整为“个人学习型公开数据观察项目”。报告继续强调数据边界：公开评论、关键词、七麦 iPhone 新增下载预估和公开版本日志只作为观察链，不作为因果证明链。

## 当前展示 PPT

当前展示 PPT 文件：

- `slides/game_community_app_analysis_presentation_v3.pptx`

v3 已根据当前正式报告和 README 的“个人学习型公开数据观察项目”定位重做，用于辅助展示项目思路，不替代正式 PDF 报告。公开仓库不保留旧版 PPT 或过程检查文件。

## 正式报告使用图表清单

当前正式 Markdown 报告从 `portfolio/` 目录引用以下图表路径：

- `../outputs/charts/final_01_review_sentiment_structure.png`
- `../outputs/charts/final_03_xhh_negative_issue_categories.png`
- `../outputs/charts/final_06_keyword_operation_support_matrix.png`
- `../outputs/charts/final_09_download_monthly_compare.png`
- `../outputs/charts/final_11_version_monthly_updates.png`
- `../outputs/charts/final_14_tga_daily_window_compare.png`

这些图表实际文件保存在 `outputs/charts/`，不应移动，否则可能影响 Markdown 报告预览或后续 PDF 再生成。

## 后续注意事项

- 不应在公开仓库中新增临时 HTML、过程检查报告或旧版报告归档。
- 如需重新生成 PDF，应先确认是否真的需要，并重新检查图片、分页和表格显示。
- 本轮公开仓库清理不重新生成 PDF，也不重跑分析脚本。
