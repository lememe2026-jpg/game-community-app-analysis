from pathlib import Path
from textwrap import dedent

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
TABLE_DIR = ROOT / "outputs" / "tables"
REPORT_DIR = ROOT / "outputs" / "reports"
CHART_DIR = ROOT / "outputs" / "charts"

WARNINGS = []
READ_FILES = {}


SOURCE_FILES = {
    "review_sentiment": TABLE_DIR / "review_sentiment_summary.csv",
    "xhh_negative_issue_summary": TABLE_DIR / "xhh_negative_issue_summary.csv",
    "xhh_negative_issue_summary_problem_only": TABLE_DIR / "xhh_negative_issue_summary_problem_only.csv",
    "xhh_negative_review_examples": TABLE_DIR / "xhh_negative_review_examples.csv",
    "xhh_negative_issue_detail": TABLE_DIR / "xhh_negative_issue_detail.csv",
    "review_analysis_detail": TABLE_DIR / "review_analysis_detail.csv",
    "keyword_analysis_detail": TABLE_DIR / "keyword_analysis_detail.csv",
    "keyword_core_operation_clues": TABLE_DIR / "keyword_core_operation_clues.csv",
    "keyword_core_game_content_clues": TABLE_DIR / "keyword_core_game_content_clues.csv",
    "keyword_core_platform_ecology_clues": TABLE_DIR / "keyword_core_platform_ecology_clues.csv",
    "keyword_core_community_function_clues": TABLE_DIR / "keyword_core_community_function_clues.csv",
    "keyword_audience_background_clues": TABLE_DIR / "keyword_audience_background_clues.csv",
    "keyword_operation_scene_summary": TABLE_DIR / "keyword_operation_scene_summary.csv",
    "keyword_top30_interpretation": TABLE_DIR / "keyword_top30_interpretation.csv",
    "keyword_top50_search_index": TABLE_DIR / "keyword_top50_search_index.csv",
    "download_monthly_summary": TABLE_DIR / "download_monthly_summary.csv",
    "download_peak_dates": TABLE_DIR / "download_peak_dates.csv",
    "download_trend_detail": TABLE_DIR / "download_trend_detail.csv",
    "download_observation_points": TABLE_DIR / "download_observation_points.csv",
    "version_monthly_summary": TABLE_DIR / "version_monthly_summary.csv",
    "version_update_intervals": TABLE_DIR / "version_update_intervals.csv",
    "version_timeline": TABLE_DIR / "version_timeline.csv",
    "version_log_category_summary": TABLE_DIR / "version_log_category_summary.csv",
    "version_observation_points": TABLE_DIR / "version_observation_points.csv",
    "version_log_text_units": TABLE_DIR / "version_log_text_units.csv",
    "version_log_action_clusters": TABLE_DIR / "version_log_action_clusters.csv",
    "version_action_theme_summary": TABLE_DIR / "version_action_theme_summary.csv",
    "version_operation_problem_matrix": TABLE_DIR / "version_operation_problem_matrix.csv",
    "version_four_source_candidate_nodes": TABLE_DIR / "version_four_source_candidate_nodes.csv",
    "version_analysis_use_cases": TABLE_DIR / "version_analysis_use_cases.csv",
}

REPORT_INPUT_FILES = {
    "review_report": REPORT_DIR / "review_analysis_summary.md",
    "keyword_report": REPORT_DIR / "keyword_analysis_summary.md",
    "download_report": REPORT_DIR / "download_analysis_summary.md",
    "version_report": REPORT_DIR / "version_analysis_summary.md",
}

OUTPUT_FILES = {
    "summary": TABLE_DIR / "four_source_evidence_chain_summary.csv",
    "candidate_nodes": TABLE_DIR / "four_source_candidate_nodes.csv",
    "portfolio_plan": TABLE_DIR / "four_source_portfolio_usage_plan.csv",
    "risk_checklist": TABLE_DIR / "four_source_risk_boundary_checklist.csv",
    "summary_report": REPORT_DIR / "four_source_evidence_chain_summary.md",
    "next_steps_report": REPORT_DIR / "four_source_next_steps_for_portfolio.md",
}

EXISTING_CHARTS = [
    "final_01_review_sentiment_structure.png",
    "final_02_xhh_positive_negative_word_freq.png",
    "final_03_xhh_negative_issue_categories.png",
    "final_04_xhh_negative_issue_monthly_trend.png",
    "final_05_keyword_data_scope.png",
    "final_06_keyword_operation_support_matrix.png",
    "final_07_keyword_search_visibility_compare.png",
    "final_08_download_daily_trend.png",
    "final_09_download_monthly_compare.png",
    "final_10_download_7d_moving_average.png",
    "final_11_version_monthly_updates.png",
    "final_12_version_update_timeline.png",
    "final_13_version_log_category_summary.png",
]

ISSUES = [
    ("社区氛围与治理", "P0"),
    ("用户反馈与客服处理", "P0"),
    ("内容供给与热门游戏话题", "P0"),
    ("工具服务与功能体验", "P1"),
    ("交易 / 库存 / 消费信任", "P1"),
    ("活动福利与存量用户体验", "P1"),
]

REVIEW_CATEGORY_MAP = {
    "社区氛围与治理": ["社区氛围与治理"],
    "用户反馈与客服处理": ["客服与反馈处理", "账号登录与绑定问题", "活动福利与领取问题"],
    "内容供给与热门游戏话题": ["内容质量与资讯价值", "社区氛围与治理"],
    "工具服务与功能体验": ["功能体验与产品设计", "性能与稳定性", "账号登录与绑定问题", "加速器与绑定体验"],
    "交易 / 库存 / 消费信任": ["交易与库存相关", "商业化与消费信任问题"],
    "活动福利与存量用户体验": ["活动福利与领取问题"],
}

KEYWORD_SCENE_MAP = {
    "社区氛围与治理": ["社区运营/互动关系"],
    "用户反馈与客服处理": ["功能运营/交易消费信任", "功能运营/工具服务"],
    "内容供给与热门游戏话题": ["内容运营/热点游戏线索", "内容运营/攻略资讯"],
    "工具服务与功能体验": ["功能运营/工具服务"],
    "交易 / 库存 / 消费信任": ["功能运营/交易消费信任", "平台生态/玩家圈层"],
    "活动福利与存量用户体验": ["社区运营/互动关系", "功能运营/交易消费信任"],
}

KEYWORD_TERMS_MAP = {
    "社区氛围与治理": ["游戏社区", "游戏论坛", "玩家社区"],
    "用户反馈与客服处理": ["退款", "账号", "绑定", "交易", "活动"],
    "内容供给与热门游戏话题": ["永劫无间", "无畏契约", "瓦罗兰特", "黑神话悟空", "塞尔达", "荒野大镖客", "游戏攻略", "游戏新闻"],
    "工具服务与功能体验": ["游戏库", "助手", "战绩", "加速器", "掌上 Steam", "永劫无间战绩查询", "图鉴", "成就", "存档"],
    "交易 / 库存 / 消费信任": ["Steam", "库存", "饰品", "游戏饰品", "CDK", "激活", "退款", "付费", "交易", "买游戏", "折扣", "好评率"],
    "活动福利与存量用户体验": ["活动", "福利", "领取", "兑换", "任务", "新用户", "金币"],
}

DOWNLOAD_HINTS = {
    "社区氛围与治理": "下载趋势仅作为结果波动背景，不纳入强解释。",
    "用户反馈与客服处理": "可对照反馈集中期与下载峰值/高位区间是否时间接近，但不能判断反馈或客服动作影响下载。",
    "内容供给与热门游戏话题": "下载波动可作为内容供给窗口的结果背景，不证明内容动作有效。",
    "工具服务与功能体验": "可查看工具相关版本附近是否存在下载波动，仅作为背景。",
    "交易 / 库存 / 消费信任": "游民星空 2025-06 局部高点可作为交易/售后相关观察的结果背景。",
    "活动福利与存量用户体验": "游民星空 2025-07、2025-11 局部高点可作为活动/存量体验观察背景。",
}

VERSION_HINTS = {
    "社区氛围与治理": "版本日志支撑较弱，公开动作背景不足。",
    "用户反馈与客服处理": "游民星空出现购买售后流程优化等动作线索；小黑盒日志信息不足。",
    "内容供给与热门游戏话题": "游民星空 2026-01 至 2026-03 出现榜单、热榜、推荐、图鉴、构筑、存档工具等动作线索。",
    "工具服务与功能体验": "游民星空出现 Steam 名片、Xbox 成就、游戏成就工具、图鉴、构筑、存档工具等线索；小黑盒日志信息不足。",
    "交易 / 库存 / 消费信任": "游民星空 2025-06 附近多次出现购买售后流程优化，后续还有购买指南、Steam 好评率等动作线索。",
    "活动福利与存量用户体验": "游民星空 2025-07 出现实名认证与金币任务，2025-11 出现新用户立减券，新春祝福类日志可作为弱背景。",
}

VISUALS = {
    "社区氛围与治理": "final_01_review_sentiment_structure.png; final_03_xhh_negative_issue_categories.png; final_05_keyword_data_scope.png; final_06_keyword_operation_support_matrix.png",
    "用户反馈与客服处理": "final_03_xhh_negative_issue_categories.png; final_04_xhh_negative_issue_monthly_trend.png; final_08_download_daily_trend.png; final_12_version_update_timeline.png",
    "内容供给与热门游戏话题": "final_05_keyword_data_scope.png; final_06_keyword_operation_support_matrix.png; final_11_version_monthly_updates.png; final_13_version_log_category_summary.png",
    "工具服务与功能体验": "final_03_xhh_negative_issue_categories.png; final_06_keyword_operation_support_matrix.png; final_12_version_update_timeline.png; final_13_version_log_category_summary.png",
    "交易 / 库存 / 消费信任": "final_03_xhh_negative_issue_categories.png; final_07_keyword_search_visibility_compare.png; final_09_download_monthly_compare.png; final_12_version_update_timeline.png",
    "活动福利与存量用户体验": "final_04_xhh_negative_issue_monthly_trend.png; final_08_download_daily_trend.png; final_09_download_monthly_compare.png; final_12_version_update_timeline.png",
}

JD_MAPPING = {
    "社区氛围与治理": "社区运营、用户运营、内容安全与社区规则治理",
    "用户反馈与客服处理": "用户反馈闭环、客服协同、问题分层与体验优化",
    "内容供给与热门游戏话题": "游戏行业运营、内容运营、热点追踪、社区内容生态",
    "工具服务与功能体验": "产品运营、数据分析、工具型功能体验优化",
    "交易 / 库存 / 消费信任": "商业化运营、交易体验、消费信任与售后流程协同",
    "活动福利与存量用户体验": "活动运营、用户留存、存量用户体验与权益触达",
}

ACTION_MAP = {
    "社区氛围与治理": "建立社区氛围问题标签；拆分帖子/评论/举报/审核触点；设计低成本治理观察看板。",
    "用户反馈与客服处理": "把客服、反馈、退款、登录绑定、活动反馈拆为二级问题；设计反馈闭环路径和优先级分流。",
    "内容供给与热门游戏话题": "围绕热点游戏、攻略资讯、榜单推荐拆主题池；用关键词需求与内容动作形成选题矩阵。",
    "工具服务与功能体验": "把登录绑定、性能稳定、战绩/图鉴/成就/存档等工具场景拆为体验漏斗；沉淀产品协同建议。",
    "交易 / 库存 / 消费信任": "拆分交易、库存、退款、激活、购买指南、好评率等信任触点；形成消费信任风险清单。",
    "活动福利与存量用户体验": "拆分领取、兑换、任务、新用户权益、存量福利体验；形成活动执行检查表。",
}

PORTFOLIO_USAGE_MAP = {
    "社区氛围与治理": "正文主线之一，但标注为中等强度证据链；适合承接 A 方向社区生态运营表达。",
    "用户反馈与客服处理": "正文核心主线；适合作为用户反馈闭环和运营诊断能力展示。",
    "内容供给与热门游戏话题": "正文核心主线；适合服务 B 方向游戏行业运营和内容生态表达。",
    "工具服务与功能体验": "正文辅助主线 / 产品协同延展；适合体现数据向运营和产品协同意识，但不抢 P0 主线。",
    "交易 / 库存 / 消费信任": "正文次级案例或附录；可作为商业化与消费信任补充案例，不写成核心章节。",
    "活动福利与存量用户体验": "附录 / 面试案例 / 探索保留；适合展示活动执行检查意识，不作为正文论证主线，不能写成活动效果证明。",
}

PORTFOLIO_SECTION_MAP = {
    "社区氛围与治理": "A. 正文核心主线 / 主线之一（中等强度）",
    "用户反馈与客服处理": "A. 正文核心主线",
    "内容供给与热门游戏话题": "A. 正文核心主线",
    "工具服务与功能体验": "B. 正文辅助主线 / 产品协同延展",
    "交易 / 库存 / 消费信任": "C. 附录 / 次级案例",
    "活动福利与存量用户体验": "D. 探索保留 / 面试案例",
}


def safe_read_csv(path):
    path = Path(path)
    if not path.exists():
        WARNINGS.append(f"缺失文件：{path.relative_to(ROOT)}")
        return pd.DataFrame()
    try:
        df = pd.read_csv(path)
        READ_FILES[str(path.relative_to(ROOT))] = {
            "rows": len(df),
            "columns": list(df.columns),
        }
        return df
    except Exception as exc:
        WARNINGS.append(f"读取失败：{path.relative_to(ROOT)}；原因：{exc}")
        return pd.DataFrame()


def safe_read_text(path):
    path = Path(path)
    if not path.exists():
        WARNINGS.append(f"缺失报告：{path.relative_to(ROOT)}")
        return ""
    try:
        text = path.read_text(encoding="utf-8")
        READ_FILES[str(path.relative_to(ROOT))] = {
            "rows": text.count("\n") + 1,
            "columns": ["markdown_text"],
        }
        return text
    except UnicodeDecodeError:
        text = path.read_text(encoding="utf-8-sig")
        READ_FILES[str(path.relative_to(ROOT))] = {
            "rows": text.count("\n") + 1,
            "columns": ["markdown_text"],
        }
        return text


def join_items(items, limit=8):
    cleaned = []
    for item in items:
        if pd.isna(item):
            continue
        text = str(item).strip()
        if text and text not in cleaned:
            cleaned.append(text)
    return "；".join(cleaned[:limit]) if cleaned else "暂无可读取明细"


def value_text(value, fallback=""):
    if pd.isna(value):
        return fallback
    text = str(value).strip()
    if text.lower() in ["nan", "nat", "none"]:
        return fallback
    return text


def date_range_text(row):
    start = value_text(row.get("start_date", ""))
    end = value_text(row.get("end_date", ""))
    if start and end:
        return f"{start}至{end}"
    return start or end or "日期未标明"


def peak_text(row):
    peak = value_text(row.get("peak_date", ""))
    return f"，峰值日{peak}" if peak else ""


def issue_review_evidence(issue, review_issue_df, sentiment_df):
    if review_issue_df.empty:
        return "评论侧文件缺失或为空，暂不能形成评论证据。"

    categories = REVIEW_CATEGORY_MAP[issue]
    subset = review_issue_df[review_issue_df["issue_category"].isin(categories)].copy()
    if subset.empty:
        return f"评论侧未在既有问题分类中直接命中：{join_items(categories)}。"

    parts = []
    for _, row in subset.iterrows():
        parts.append(
            f"{row.get('issue_category', '')}命中{row.get('hit_count', '')}次"
            f"（负向评论占比{row.get('percent', '')}%）"
        )
    sentiment_part = ""
    if not sentiment_df.empty and {"app_display_name", "sentiment", "count", "percent"}.issubset(sentiment_df.columns):
        neg = sentiment_df[sentiment_df["sentiment"].astype(str) == "negative"]
        sentiment_part = "；负向评论结构：" + join_items(
            neg.apply(lambda r: f"{r['app_display_name']}负向{r['count']}条/{r['percent']}%", axis=1)
        )
    return join_items(parts, limit=10) + sentiment_part


def issue_keyword_evidence(issue, keyword_scene_df, keyword_detail_df):
    terms = KEYWORD_TERMS_MAP[issue]
    scene_names = KEYWORD_SCENE_MAP[issue]
    scene_part = ""
    term_part = ""

    if not keyword_scene_df.empty and "operation_scene" in keyword_scene_df.columns:
        subset = keyword_scene_df[keyword_scene_df["operation_scene"].isin(scene_names)].copy()
        if not subset.empty:
            scene_part = join_items(
                subset.apply(
                    lambda r: f"{r.get('operation_scene', '')}含{r.get('keyword_count', '')}个关键词"
                    f"（top关键词：{r.get('top_keywords', '')}）",
                    axis=1,
                ),
                limit=4,
            )

    if not keyword_detail_df.empty and "keyword_clean" in keyword_detail_df.columns:
        mask = keyword_detail_df["keyword_clean"].astype(str).apply(
            lambda value: any(term.lower() in value.lower() for term in terms)
        )
        subset = keyword_detail_df[mask].copy()
        if not subset.empty:
            if "search_index_rank" in subset.columns:
                subset["search_index_rank_num"] = pd.to_numeric(subset["search_index_rank"], errors="coerce")
                subset = subset.sort_values(["search_index_rank_num", "search_index"], ascending=[True, False])
            term_part = "代表词：" + join_items(
                subset.apply(
                    lambda r: f"{r.get('keyword_clean', '')}"
                    f"（搜索指数{r.get('search_index', '')}，排名{r.get('search_index_rank', '')}）",
                    axis=1,
                ),
                limit=8,
            )

    if scene_part and term_part:
        return scene_part + "；" + term_part
    if scene_part:
        return scene_part
    if term_part:
        return term_part
    return "关键词侧可按预设场景复核，但当前规则未直接抓取到代表词。"


def issue_download_evidence(issue, download_obs_df, peak_df):
    hint = DOWNLOAD_HINTS[issue]
    if download_obs_df.empty:
        return hint

    if issue == "交易 / 库存 / 消费信任":
        mask = (download_obs_df["app"].astype(str) == "游民星空") & (
            download_obs_df["start_date"].astype(str).str.startswith("2025-06")
        )
    elif issue == "活动福利与存量用户体验":
        mask = (download_obs_df["app"].astype(str) == "游民星空") & (
            download_obs_df["start_date"].astype(str).str.startswith("2025-07")
            | download_obs_df["start_date"].astype(str).str.startswith("2025-11")
        )
    elif issue == "用户反馈与客服处理":
        mask = download_obs_df["observation_type"].astype(str).str.contains("高位|峰值", na=False)
    elif issue in ["内容供给与热门游戏话题", "工具服务与功能体验"]:
        mask = download_obs_df["app"].astype(str).eq("游民星空")
    else:
        mask = pd.Series(False, index=download_obs_df.index)

    subset = download_obs_df[mask].copy()
    if subset.empty:
        return hint

    obs = join_items(
        subset.apply(
            lambda r: f"{value_text(r.get('app', ''))}{date_range_text(r)}"
            f"（{value_text(r.get('observation_type', ''))}{peak_text(r)}）",
            axis=1,
        ),
        limit=4,
    )
    return f"{hint} 可引用观察点：{obs}。"


def issue_version_evidence(issue, version_matrix_df, version_nodes_df):
    hint = VERSION_HINTS[issue]
    parts = []
    if not version_matrix_df.empty and "operation_problem" in version_matrix_df.columns:
        subset = version_matrix_df[version_matrix_df["operation_problem"].astype(str) == issue].copy()
        subset = subset[pd.to_numeric(subset.get("hit_unit_count", 0), errors="coerce").fillna(0) > 0]
        if not subset.empty:
            parts.append(
                join_items(
                    subset.apply(
                        lambda r: f"{r.get('app_name', '')}命中{r.get('hit_unit_count', '')}个日志单元/"
                        f"{r.get('hit_version_count', '')}个版本，样例：{r.get('sample_units', '')}",
                        axis=1,
                    ),
                    limit=3,
                )
            )

    if not version_nodes_df.empty and "operation_problems" in version_nodes_df.columns:
        subset = version_nodes_df[
            version_nodes_df["operation_problems"].astype(str).str.contains(issue, regex=False, na=False)
        ].copy()
        if not subset.empty:
            parts.append(
                "候选窗口：" + join_items(
                    subset.apply(
                        lambda r: f"{r.get('observation_label', '')}/{r.get('update_date', '')}/{r.get('action_themes', '')}",
                        axis=1,
                    ),
                    limit=4,
                )
            )

    if parts:
        return hint + " " + "；".join(parts)
    return hint


def evidence_strength(issue, review_text, keyword_text, download_text, version_text):
    if issue == "交易 / 库存 / 消费信任":
        return "中"
    if issue == "活动福利与存量用户体验":
        return "中"

    natural_sources = 0
    for text in [review_text, keyword_text, download_text, version_text]:
        weak_markers = ["缺失", "暂不能", "支撑较弱", "不纳入强解释", "未直接"]
        if text and not any(marker in text for marker in weak_markers):
            natural_sources += 1

    if issue == "社区氛围与治理":
        return "中"
    if natural_sources >= 3:
        return "强"
    if "评论侧" not in review_text and "关键词" not in keyword_text:
        return "中"
    return "弱"


def source_count_from_strength(strength):
    return {
        "强": "3-4类来源",
        "中": "2类主来源+1-2类辅助",
        "弱": "1-2类弱关联",
    }.get(strength, "")


def risk_boundary(issue):
    return (
        "仅能表述为公开数据交叉观察；不能写成因果链。"
        "不得表述为版本导致下载、活动导致下载、关键词需求导致版本更新、评论反馈导致版本更新，"
        "也不得把七麦预估下载、搜索指数、App Store 评论外推为全部真实用户表现。"
    )


def portfolio_usage(issue, strength):
    return PORTFOLIO_USAGE_MAP[issue]


def manual_review_flag(issue, strength):
    if issue in ["社区氛围与治理", "用户反馈与客服处理", "交易 / 库存 / 消费信任", "活动福利与存量用户体验"]:
        return "是"
    if strength != "强":
        return "是"
    return "否"


def make_summary(dfs):
    rows = []
    for issue, priority in ISSUES:
        review = issue_review_evidence(
            issue,
            dfs["xhh_negative_issue_summary_problem_only"],
            dfs["review_sentiment"],
        )
        keyword = issue_keyword_evidence(
            issue,
            dfs["keyword_operation_scene_summary"],
            dfs["keyword_analysis_detail"],
        )
        if issue == "用户反馈与客服处理":
            keyword += " 口径补充：关键词侧更多体现账号、交易、工具等服务场景需求，不能直接等同于客服诉求。"
        if issue == "活动福利与存量用户体验":
            keyword += " 口径补充：活动福利类关键词支撑较弱，更多作为存量用户体验的辅助线索。"
        download = issue_download_evidence(
            issue,
            dfs["download_observation_points"],
            dfs["download_peak_dates"],
        )
        version = issue_version_evidence(
            issue,
            dfs["version_operation_problem_matrix"],
            dfs["version_four_source_candidate_nodes"],
        )
        strength = evidence_strength(issue, review, keyword, download, version)
        rows.append(
            {
                "operation_issue": issue,
                "priority": priority,
                "evidence_strength": strength,
                "review_evidence": review,
                "keyword_evidence": keyword,
                "download_evidence": download,
                "version_evidence": version,
                "integrated_observation": (
                    f"{issue}在四源数据中可形成{source_count_from_strength(strength)}的交叉观察。"
                    "评论侧用于识别被动反馈，关键词侧用于识别主动需求，下载趋势仅作结果背景，"
                    "版本日志仅作公开动作背景。"
                ),
                "executable_actions": ACTION_MAP[issue],
                "jd_mapping": JD_MAPPING[issue],
                "risk_boundary": risk_boundary(issue),
                "portfolio_usage": portfolio_usage(issue, strength),
                "recommended_visuals_or_tables": VISUALS[issue],
                "needs_manual_review": manual_review_flag(issue, strength),
            }
        )
    return pd.DataFrame(rows)


def make_candidate_nodes(summary_df, dfs):
    nodes = []
    for idx, row in summary_df.iterrows():
        nodes.append(
            {
                "node_id": f"CHAIN_{idx + 1:02d}",
                "operation_issue": row["operation_issue"],
                "priority": row["priority"],
                "node_type": "四源证据链候选",
                "evidence_strength": row["evidence_strength"],
                "review_signal": row["review_evidence"],
                "keyword_signal": row["keyword_evidence"],
                "download_signal": row["download_evidence"],
                "version_signal": row["version_evidence"],
                "candidate_usage": row["portfolio_usage"],
                "safe_wording": "可以写成交叉观察和运营诊断基础，不能写成因果证明。",
                "recommended_next_check": "人工复核代表评论、关键词样例和版本日志原文，确认表述边界。",
            }
        )

    boundary_download = "小黑盒 2025-12-13 单日下载预估峰值；2025-12 中旬至 2026-01 初连续高位区间。"
    download_obs = dfs["download_observation_points"]
    if not download_obs.empty:
        mask = (download_obs["app"].astype(str) == "小黑盒") & (
            download_obs["start_date"].astype(str).str.contains("2025-12", na=False)
        )
        subset = download_obs[mask]
        if not subset.empty:
            boundary_download = join_items(
                subset.apply(
                    lambda r: f"{value_text(r.get('observation_label', ''))}{value_text(r.get('app', ''))}"
                    f"{date_range_text(r)}{peak_text(r)}",
                    axis=1,
                ),
                limit=3,
            )

    boundary_version = "附近存在版本节点，但日志多为“修复已知问题”类信息不足文本。"
    version_nodes = dfs["version_four_source_candidate_nodes"]
    if not version_nodes.empty and "point_id" in version_nodes.columns:
        subset = version_nodes[version_nodes["point_id"].astype(str).str.contains("xhh_2025_12", na=False)]
        if not subset.empty:
            boundary_version = join_items(
                subset.apply(
                    lambda r: f"{value_text(r.get('update_date', ''))}/{value_text(r.get('version', ''))}/"
                    f"{value_text(r.get('log_units', ''), '日志信息不足')}",
                    axis=1,
                ),
                limit=4,
            )

    nodes.append(
        {
            "node_id": "BOUNDARY_XHH_2025_12",
            "operation_issue": "边界校验节点（不新增运营问题大类）",
            "priority": "边界",
            "node_type": "时间接近但日志不足案例",
            "evidence_strength": "弱",
            "review_signal": "可检查是否存在同期反馈，但不得强行解释。",
            "keyword_signal": "可检查是否存在同期需求背景，但不得强行解释。",
            "download_signal": boundary_download,
            "version_signal": boundary_version,
            "candidate_usage": "适合作为方法论边界案例，提醒作品集避免因果化表达。",
            "safe_wording": "时间接近不能等同于因果关系；日志信息不足时只能写成边界案例。",
            "recommended_next_check": "回看 2025-12 至 2026-01 小黑盒评论样例、关键词需求与版本日志原文。",
        }
    )
    return pd.DataFrame(nodes)


def make_portfolio_plan(summary_df):
    rows = []
    for _, row in summary_df.iterrows():
        placement = PORTFOLIO_SECTION_MAP[row["operation_issue"]]
        rows.append(
            {
                "operation_issue": row["operation_issue"],
                "priority": row["priority"],
                "evidence_strength": row["evidence_strength"],
                "portfolio_section": placement,
                "recommended_storyline": row["integrated_observation"],
                "recommended_visuals_or_tables": row["recommended_visuals_or_tables"],
                "action_output": row["executable_actions"],
                "jd_mapping": row["jd_mapping"],
                "manual_work_before_portfolio": "补充人工复核样例、统一措辞边界、避免因果化标题。",
            }
        )
    return pd.DataFrame(rows)


def make_risk_checklist():
    forbidden = [
        "四源数据证明某运营动作有效",
        "版本导致下载",
        "活动导致下载",
        "关键词需求导致版本更新",
        "评论反馈导致版本更新",
        "下载趋势证明用户满意度变化",
        "搜索指数代表真实流量",
        "App Store 评论代表全部用户",
        "小黑盒或游民星空真实运营能力强弱",
        "四源时间接近等于因果关系",
    ]
    preferred = [
        "四源数据只能支持公开数据交叉观察，不能证明运营动作有效。",
        "版本日志仅提供公开动作背景，不能解释下载变化。",
        "活动相关日志只能作为运营动作线索，不能证明活动效果。",
        "关键词仅代表搜索需求线索，不能证明版本动作来源。",
        "评论仅代表公开反馈样本，不能证明版本更新原因。",
        "七麦预估下载仅作为结果波动背景，不能反推满意度。",
        "搜索指数仅作为 App Store 搜索需求热度的相对观察。",
        "评论仅代表公开评论样本中的反馈信号。",
        "只能比较公开数据下呈现出的观察线索。",
        "时间接近只能提示后续排查，不能单独判断因果。",
    ]
    rows = []
    for idx, text in enumerate(forbidden, start=1):
        rows.append(
            {
                "check_id": f"RISK_{idx:02d}",
                "risk_type": "禁用表达",
                "unsafe_expression": text,
                "safe_expression": preferred[idx - 1],
                "check_method": "报告成稿前逐条检索标题、图注、结论句和策略建议段落。",
                "status": "待人工复核",
            }
        )
    return pd.DataFrame(rows)


def chart_exists_warning():
    for chart in EXISTING_CHARTS:
        if not (CHART_DIR / chart).exists():
            WARNINGS.append(f"推荐图表不存在：outputs/charts/{chart}")


def write_summary_report(summary_df, candidate_df):
    lines = [
        "# 四源证据链整合摘要",
        "",
        "## 1. 整合口径",
        "本报告整合评论、关键词、下载趋势、版本节奏四类已生成结果。评论用于观察被动反馈，关键词用于观察主动需求，下载趋势仅作为七麦预估下载的结果波动背景，版本节奏仅作为公开版本日志中的动作背景。",
        "",
        "证据强度口径：强表示至少 3 类来源能形成较自然的交叉观察；中表示评论和关键词能对齐，下载或版本只能辅助；弱表示单源或两源弱关联，不适合作为核心结论。",
        "",
        "## 2. 六类运营问题证据链",
    ]
    for _, row in summary_df.iterrows():
        lines.extend(
            [
                f"### {row['priority']}｜{row['operation_issue']}｜{row['evidence_strength']}",
                f"- 评论侧：{row['review_evidence']}",
                f"- 关键词侧：{row['keyword_evidence']}",
                f"- 下载侧：{row['download_evidence']}",
                f"- 版本侧：{row['version_evidence']}",
                f"- 整合观察：{row['integrated_observation']}",
                f"- 作品集用法：{row['portfolio_usage']}",
                f"- 推荐图表/表格：{row['recommended_visuals_or_tables']}",
                "",
            ]
        )

    boundary = candidate_df[candidate_df["node_id"] == "BOUNDARY_XHH_2025_12"]
    if not boundary.empty:
        b = boundary.iloc[0]
        lines.extend(
            [
                "## 3. 边界案例",
                f"- 节点：{b['node_id']}",
                f"- 下载侧：{b['download_signal']}",
                f"- 版本侧：{b['version_signal']}",
                f"- 安全表述：{b['safe_wording']}",
                "",
            ]
        )

    lines.extend(
        [
            "## 4. 表达边界",
            "不得把四源交叉观察写成因果证明。不得写成版本导致下载、活动导致下载、关键词需求导致版本更新、评论反馈导致版本更新，或用下载趋势证明用户满意度变化。",
            "",
            "建议写成：四类公开数据可以形成交叉观察；该问题在评论侧和关键词侧均有信号；下载趋势提供结果波动背景；版本日志提供公开动作背景；暂不能判断因果关系。",
        ]
    )
    OUTPUT_FILES["summary_report"].write_text("\n".join(lines), encoding="utf-8")


def write_next_steps_report(summary_df):
    issue_rows = {row["operation_issue"]: row for _, row in summary_df.iterrows()}

    def bullet(issue):
        row = issue_rows[issue]
        return (
            f"- {row['priority']}｜{issue}｜{row['evidence_strength']}："
            f"{row['portfolio_usage']} 建议映射到：{row['jd_mapping']}。"
        )

    lines = [
        "# 四源证据链作品集后续处理建议",
        "",
        "## 1. 四层作品集使用口径",
        "本轮不再把六类问题都写成“优先进入作品集”。六类问题保留，但按正文主线、辅助主线、次级案例和探索保留分层使用。",
        "",
        "## A. 正文核心主线",
        bullet("用户反馈与客服处理"),
        bullet("内容供给与热门游戏话题"),
        bullet("社区氛围与治理"),
        "说明：社区氛围与治理可作为正文主线之一，但需要明确标注为中等强度证据链；用户反馈与内容供给是更适合展开的核心主线。",
        "",
        "## B. 正文辅助主线",
        bullet("工具服务与功能体验"),
        "说明：工具服务与功能体验适合放在产品协同延展中，体现数据向运营和产品协同意识，不抢 P0 主线。",
        "",
        "## C. 附录 / 次级案例",
        bullet("交易 / 库存 / 消费信任"),
        "说明：交易 / 库存 / 消费信任与 A 方向社区生态运营主线距离较远，可作为商业化与消费信任的次级案例，不写成核心章节。",
        "",
        "## D. 探索保留 / 边界案例",
        bullet("活动福利与存量用户体验"),
        "- 边界案例｜小黑盒 2025-12 下载高位：必须放入边界案例，不能放入正文论证链。该节点只能说明时间接近但日志信息不足，不能强行解释。",
        "",
        "## 2. 需要补充人工复核的内容",
        "- 用户反馈与客服处理：关键词侧更多体现账号、交易、工具等服务场景需求，不能直接等同于客服诉求，需要补充代表评论样例。",
        "- 活动福利与存量用户体验：关键词侧支撑较弱，建议保留为探索或面试案例。",
        "- 交易 / 库存 / 消费信任：与社区生态运营主线距离较远，成稿时应放在次级案例或附录。",
        "- 为每类正文问题各补 2-3 条代表评论原文，保留日期、评分、App 来源和问题标签。",
        "- 为关键词侧补充代表词截图或表格片段，避免把搜索指数表述为真实流量。",
        "- 对下载观察点只写“波动背景”，不写“效果证明”。",
        "- 对版本日志只写“公开动作背景”，不写“响应评论/需求”。",
        "",
        "## 3. 推荐作品集结构",
        "1. 项目背景与四源数据口径",
        "2. 正文核心主线：用户反馈闭环、内容供给与热门游戏话题、社区氛围与治理",
        "3. 正文辅助主线：工具服务与功能体验 / 产品协同延展",
        "4. 附录或次级案例：交易 / 库存 / 消费信任",
        "5. 探索保留与边界案例：活动福利与存量用户体验、小黑盒 2025-12 下载高位边界案例",
        "6. 风险边界与方法论反思",
        "",
        "## 4. 成稿检查",
        "- 标题、图注和结论句中避免出现“导致”“证明”“拉动”“验证效果”等因果化词语。",
        "- 每个正文建议都对应至少一个评论或关键词信号，下载和版本只作为背景层。",
        "- 小黑盒 2025-12 只能用于方法论边界说明，不能进入正文因果论证链。",
    ]
    OUTPUT_FILES["next_steps_report"].write_text("\n".join(lines), encoding="utf-8")


def print_csv_info(path):
    df = pd.read_csv(path)
    rel = path.relative_to(ROOT)
    print(f"- {rel}: {len(df)} 行；字段：{', '.join(df.columns)}")


def main():
    TABLE_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    dfs = {name: safe_read_csv(path) for name, path in SOURCE_FILES.items()}
    for path in REPORT_INPUT_FILES.values():
        safe_read_text(path)
    chart_exists_warning()

    summary_df = make_summary(dfs)
    candidate_df = make_candidate_nodes(summary_df, dfs)
    portfolio_df = make_portfolio_plan(summary_df)
    risk_df = make_risk_checklist()

    summary_df.to_csv(OUTPUT_FILES["summary"], index=False, encoding="utf-8-sig")
    candidate_df.to_csv(OUTPUT_FILES["candidate_nodes"], index=False, encoding="utf-8-sig")
    portfolio_df.to_csv(OUTPUT_FILES["portfolio_plan"], index=False, encoding="utf-8-sig")
    risk_df.to_csv(OUTPUT_FILES["risk_checklist"], index=False, encoding="utf-8-sig")
    write_summary_report(summary_df, candidate_df)
    write_next_steps_report(summary_df)

    print("四源证据链整合完成")
    print(f"读取到的关键文件数量：{len(READ_FILES)} / {len(SOURCE_FILES) + len(REPORT_INPUT_FILES)}")
    print("输出文件路径：")
    for path in OUTPUT_FILES.values():
        print(f"- {path.relative_to(ROOT)}")

    print("每个输出 CSV 的行数和字段：")
    for key in ["summary", "candidate_nodes", "portfolio_plan", "risk_checklist"]:
        print_csv_info(OUTPUT_FILES[key])

    print("warning 清单：")
    if WARNINGS:
        for warning in WARNINGS:
            print(f"- {warning}")
    else:
        print("- 无")


if __name__ == "__main__":
    main()
