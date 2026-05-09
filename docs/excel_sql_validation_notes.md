# Excel 复核与 SQL 学习计划记录

本文用于记录当前公开仓库中可用 Excel 复核的关键汇总表，以及后续可用 SQL 复刻的学习方向。

## 定位说明

Excel 复核是为了帮助本人理解 Python 主程序输出、核对关键数字和检查报告口径，不是为了声称已经熟练掌握 Excel。

SQL 当前未作为正式产出工具，也没有作为本项目正式结论的来源。它只是后续学习方向，可用于复刻评论、关键词、下载和版本的关键汇总表。不应写成已经完成 SQL 数据库建模或熟练 SQL 分析。

## 本文依据的公开仓库文件

- `outputs/tables/review_sentiment_summary.csv`
- `outputs/tables/xhh_negative_issue_summary.csv`
- `outputs/tables/keyword_operation_scene_summary.csv`
- `outputs/tables/download_monthly_summary.csv`
- `outputs/tables/download_peak_dates.csv`
- `outputs/tables/version_monthly_summary.csv`
- `portfolio/game_community_app_analysis_report.md`
- `README.md`

## 评论情绪结构复核

对应文件：

- `outputs/tables/review_sentiment_summary.csv`
- `portfolio/game_community_app_analysis_report.md`

可用 Excel 复核：

- 按 `app_display_name` 和 `sentiment` 检查评论数量。
- 核对 `app_total` 与各情绪分组 `count` 是否一致。
- 核对小黑盒正向 1147、负向 338、中性 34，总计 1519。
- 核对游民星空正向 44、负向 92、中性 4，总计 140。
- 检查百分比仅代表公开评论样本，不代表全部用户满意度。

## 小黑盒负向评论问题分类复核

对应文件：

- `outputs/tables/xhh_negative_issue_summary.csv`
- `portfolio/game_community_app_analysis_report.md`

可用 Excel 复核：

- 筛选小黑盒负向评论样本，确认负向评论基数为 338。
- 检查 `issue_category`、`hit_count`、`percent`。
- 重点核对社区氛围与治理 54、功能体验与产品设计 50、客服与反馈处理 41、交易与库存相关 41、性能与稳定性 39。
- 注意一条评论可能命中多个主题，因此分类命中数不应简单加总为负向评论总数。
- “强负向情绪表达”和“其他”应作为情绪或未识别项看待，不直接等同具体运营问题。

## 关键词场景汇总复核

对应文件：

- `outputs/tables/keyword_operation_scene_summary.csv`
- `portfolio/game_community_app_analysis_report.md`

可用 Excel 复核：

- 按 `operation_dimension`、`operation_scene` 查看关键词分组。
- 区分 `keyword_count` 与 `core_clue_count`。
- 核对内容运营 / 热点游戏线索 `keyword_count` 为 85，`core_clue_count` 为 56。
- 核对内容运营 / 攻略资讯 `keyword_count` 为 4，`core_clue_count` 为 2。
- 核对社区运营 / 互动关系 `keyword_count` 为 15，`core_clue_count` 为 7。
- 不将关键词分析写成 ASO 优化，也不将搜索指数写成真实流量。

## 下载趋势月度汇总复核

对应文件：

- `outputs/tables/download_monthly_summary.csv`
- `portfolio/game_community_app_analysis_report.md`

可用 Excel 复核：

- 按 `app`、`month` 检查月度预估下载。
- 确认小黑盒 2025-12 月度预估为 731333，样本期内排名第 1。
- 确认游民星空 2025-06 月度预估为 78797，样本期内排名第 1。
- 区分完整月与非完整月，注意 2025-04 和 2026-04 为非完整月份。
- 所有下载字段均应写为七麦预估下载，不写成真实下载。

## 小黑盒 2025-12-13 峰值复核

对应文件：

- `outputs/tables/download_peak_dates.csv`
- `outputs/charts/final_14_tga_daily_window_compare.png`
- `portfolio/game_community_app_analysis_report.md`

可用 Excel 复核：

- 在 `download_peak_dates.csv` 中确认小黑盒排名第 1 的日期为 2025-12-13。
- 核对该日七麦 iPhone 新增下载预估为 87585。
- 结合 2025-12-12 至 2025-12-16 连续高位作为观察窗口。
- 不把该峰值写成活动、外部事件或版本动作带来的结果。

## 版本节奏汇总复核

对应文件：

- `outputs/tables/version_monthly_summary.csv`
- `portfolio/game_community_app_analysis_report.md`

可用 Excel 复核：

- 按 App 和月份检查公开版本更新次数。
- 只把版本日志作为公开动作背景。
- 不用版本日志证明功能效果、产品能力或下载变化原因。

## SQL 当前状态

SQL 当前不是正式产出工具，仅作为后续学习和复刻关键汇总的训练方向。后续可尝试使用 SQL 复刻 Excel 复核逻辑，但不应在本项目中伪造已完成的 SQL 结果。

可练习的 SQL 类型：

- `COUNT`：统计不同 app、情绪、场景、月份的记录数。
- `SUM`：汇总月度下载预估、搜索指数等数值。
- `GROUP BY`：按 app、month、sentiment、operation_scene 分组。
- `WHERE`：筛选小黑盒、负向评论、2025-12、Top50 等条件。
- `CASE WHEN`：复刻评分分组、关键词场景标记、日期窗口标记。

建议优先复刻：

- 评论情绪结构表。
- 小黑盒负向评论分类汇总表。
- 关键词场景汇总表。
- 下载月度汇总表。
- 版本月度更新汇总表。
- 2025-12-12 至 2025-12-16 TGA 窗口观察表。

