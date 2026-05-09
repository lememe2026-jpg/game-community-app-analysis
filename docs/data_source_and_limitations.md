# 数据来源与解释边界说明

本文为项目辅助说明文档，用于解释项目文件、数据边界、复核过程或 AI 辅助方式。

## 本文依据的文件

- `docs/analysis_plan.md`
- `README.md`
- `portfolio/game_community_app_analysis_report.md`
- `outputs/reports/cleaning_report.md`
- `outputs/reports/review_analysis_summary.md`
- `outputs/reports/keyword_analysis_summary.md`
- `outputs/reports/download_analysis_summary.md`
- `outputs/reports/version_analysis_summary.md`
- `outputs/reports/four_source_evidence_chain_summary.md`
- `data/raw/`
- `data/cleaned/`

## 文档目的

本文集中说明项目使用的数据来源、清洗后文件路径和解释边界。所有结论均应保持在公开数据观察范围内，不应写成官方口径、真实用户规模或运营效果证明。

## raw 数据来源

项目原始数据位于 `data/raw/`，当前文件包括：

- `data/raw/keywords_comparison.csv`
- `data/raw/xhh_downloads.csv`
- `data/raw/xhh_reviews.xlsx`
- `data/raw/xhh_versions.csv`
- `data/raw/ym_downloads.csv`
- `data/raw/ym_reviews.xlsx`
- `data/raw/ym_versions.csv`

根据 `docs/analysis_plan.md` 和 `README.md`，这些数据来自七麦公开导出数据与 App Store 公开信息。

## cleaned 数据路径

清洗后数据位于 `data/cleaned/`，当前文件包括：

- `data/cleaned/cleaned_downloads.csv`
- `data/cleaned/cleaned_keywords.csv`
- `data/cleaned/cleaned_reviews.csv`
- `data/cleaned/cleaned_versions.csv`

`outputs/reports/cleaning_report.md` 显示：

- `cleaned_keywords`：765 行，8 列。
- `cleaned_downloads`：730 行，5 列。
- `cleaned_reviews`：1659 行，9 列。
- `cleaned_versions`：67 行，8 列。

## 评论数据限制

评论数据来自 App Store 公开评论。它适合观察用户在公开评论中表达过的问题入口，但存在明显限制：

- 只代表公开评论用户样本。
- 不能代表全部用户观点。
- 不能代表真实问题发生率。
- 不能用来判断整体满意度。
- 评论样例只能作为表达入口，不应作为普遍结论。

正式报告中对评论的使用方式是“被动反馈：用户在抱怨什么”。

## 关键词数据限制

关键词数据来自七麦导出的 App Store 关键词数据。它适合观察公开搜索场景下的需求线索，但存在限制：

- 搜索指数不等同真实流量。
- 关键词排名不等同真实用户规模。
- Top50 数量不代表运营能力强弱。
- 关键词场景分类不应写成 ASO 优化。
- `keyword_count` 与 `core_clue_count` 应分开解释。

正式报告中对关键词的使用方式是“主动需求：用户在寻找什么”。

## 下载预估限制

下载趋势来自七麦 iPhone 新增下载预估。它适合观察样本期内的波动背景，但存在限制：

- 七麦下载量为第三方预估值。
- 不能写成官方下载量。
- 不能写成真实新增用户。
- 不能证明活动、版本或内容带来下载变化。
- 单日峰值和月度高位只能作为观察窗口。

正式报告中对下载趋势的使用方式是“结果背景：七麦预估下载如何波动”。

## 版本日志限制

版本节奏来自 App Store 公开版本日志。它适合观察公开更新文本中出现的动作线索，但存在限制：

- 版本日志只代表公开文本。
- 不代表完整产品战略。
- 不代表真实迭代计划。
- 不能证明评论问题被处理。
- 不能证明某个功能动作产生效果。

正式报告中对版本节奏的使用方式是“动作背景：公开版本日志中出现什么”。

## 外部事件 / TGA 信息限制

正式报告加入了 TGA 事件窗口观察。该部分仅用于确认外部事件和公开活动线索存在，并结合七麦预估下载观察时间窗口。

限制包括：

- 外部事件信息不能证明下载变化原因。
- 公开活动页面不能证明活动转化效率。
- 公开下载预估不能证明真实新增用户。
- 缺少活动曝光、下载来源、端内参与、注册转化和留存等内部数据。

因此，TGA 案例应写成方法论边界案例，而不是下载峰值归因案例。

## 四源观察链不能写成因果链

本项目使用四类数据：评论、关键词、下载趋势、版本节奏。它们可以互相补充观察角度，但不能组成因果证明链。

可写：

- “评论侧和关键词侧存在交叉观察。”
- “下载趋势提示该时间段值得后续观察。”
- “版本日志提供公开动作背景。”
- “该方向需要结合内部数据进一步验证。”

不应写：

- “活动导致下载增长。”
- “版本更新解决评论问题。”
- “关键词证明真实用户需求规模。”
- “下载峰值证明运营动作有效。”

## 待人工确认事项

- raw 数据的具体导出时间和导出人是否需要记录。
- TGA 外部公开来源是否需要单独沉淀链接或截图。
- 是否需要补充 App Store 原始页面来源说明。
- 是否需要给 cleaned 数据补充字段字典。

