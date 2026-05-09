# 报告生成状态记录

本文为项目辅助说明文档，用于解释项目文件、数据边界、复核过程或 AI 辅助方式。

## 本文依据的文件

- `portfolio/game_community_app_analysis_report.md`
- `portfolio/game_community_app_analysis_report.pdf`
- `portfolio/game_community_app_analysis_portfolio_final.pdf`
- `portfolio/portfolio_final_for_pdf.md`
- `portfolio/archive/20260505/`
- `slides/game_community_app_analysis_presentation_v2.pptx`
- `outputs/reports/pdf_final_check_report.md`
- `outputs/reports/report_final_text_check_20260509.md`
- `outputs/reports/pdf_generation_check_20260509.md`
- `outputs/reports/ppt_v2_check_report.md`
- `outputs/reports/project_cleanup_round2_report.md`
- `README.md`
- `outputs/charts/`

## 当前正式报告

当前已确认的正式报告文件：

- Markdown：`portfolio/game_community_app_analysis_report.md`
- PDF：`portfolio/game_community_app_analysis_report.pdf`

当前正式报告最后修改时间为 2026-05-09，较旧版作品集文件更新。

## 2026-05-09 报告与 PDF 同步记录

本轮确认当前正式报告入口为：

- Markdown：`portfolio/game_community_app_analysis_report.md`
- PDF：`portfolio/game_community_app_analysis_report.pdf`

文本检查记录见 `outputs/reports/report_final_text_check_20260509.md`。该检查报告结论为“需小修”，主要小修点是两处 blockquote 形式的概括评论样例。后续已将这两处改为普通段落，并明确说明其为概括表达、并非评论原文，避免把概括后的评论样例呈现为直接原文引用。

PDF 生成与检查记录见 `outputs/reports/pdf_generation_check_20260509.md`。本轮 PDF 已重新生成，页数为 13 页。6 张报告图表均已加载，4 张表格均未横向溢出，未发现必须修改的问题。

本轮报告修订性质主要是降低 AI 味和运营 SOP 味，将报告从“求职包装 / 运营建议清单”进一步调整为“公开数据观察报告”。报告继续强调数据边界：公开评论、关键词、七麦 iPhone 新增下载预估和公开版本日志只作为观察链，不作为因果证明链。

## 当前正式 PPT

当前正式 PPT 文件：

- `slides/game_community_app_analysis_presentation_v2.pptx`

`outputs/reports/ppt_v2_check_report.md` 显示，v2 保留 v1 的 12 页结构、视觉系统、主图和主线顺序，并完成指定小修。该检查报告同时说明 v2 主图沿用 `final_03`、`final_06`、`final_09`、`final_11`。

## 正式报告使用图表清单

当前正式 Markdown 报告引用以下图表：

- `outputs/charts/final_01_review_sentiment_structure.png`
- `outputs/charts/final_03_xhh_negative_issue_categories.png`
- `outputs/charts/final_06_keyword_operation_support_matrix.png`
- `outputs/charts/final_09_download_monthly_compare.png`
- `outputs/charts/final_11_version_monthly_updates.png`
- `outputs/charts/final_14_tga_daily_window_compare.png`

这些图表不应移动，否则可能影响 Markdown 报告预览或后续 PDF 再生成。

## PDF 生成方式记录

旧版 PDF 生成记录可从 `outputs/reports/pdf_final_check_report.md` 确认：

- 旧版源文件：`portfolio/portfolio_final_for_pdf.md`
- 旧版 HTML：`portfolio/portfolio_final_for_pdf.html`
- 旧版 PDF：`portfolio/game_community_app_analysis_portfolio_final.pdf`
- 导出方式：本机 Microsoft Edge headless，使用 `--print-to-pdf` 和 `--no-pdf-header-footer` 参数。

本轮正式 PDF 基于 Markdown 转换 HTML，并通过 Microsoft Edge headless / DevTools `Page.printToPDF` 输出。最终版本使用内嵌图片方式，避免相对路径在 headless 环境中丢图；本轮未生成临时 HTML 文件。后续如需复现，应优先参考本地生成记录；若命令环境变化，需要重新检查图片路径、分页和字体。

## 旧版报告保留情况

项目中仍保留旧版交付物：

- `portfolio/game_community_app_analysis_portfolio_final.pdf`
- `portfolio/portfolio_final_for_pdf.md`

旧版生成过程文件已部分位于：

- `portfolio/archive/20260505/`

旧版文件当前只是历史文件，不再是 `README.md` 的主入口。若后续考虑移动或归档旧版文件，仍应先做全项目链接检查。

## README 当前状态

当前 `README.md` 已指向新版正式报告：

- `portfolio/game_community_app_analysis_report.md`
- `portfolio/game_community_app_analysis_report.pdf`

当前 `README.md` 已不再引用以下旧版报告路径：

- `portfolio/game_community_app_analysis_portfolio_final.pdf`
- `portfolio/portfolio_final_for_pdf.md`
- `outputs/reports/pdf_final_check_report.md`

旧版报告文件仍保留在项目中，但不再是 README 主入口。后续如需归档旧版文件，应先进行全项目链接检查。

## 待人工确认事项

- 是否需要归档或保留旧版报告文件。
- 是否需要进行全项目链接一致性检查。
- PPT v2 是否需要和新版报告 `final_14` 图保持一致，或继续沿用原 4 张主图。

