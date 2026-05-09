# -*- coding: utf-8 -*-
"""
04_analyze_reviews.py

评论分析专项脚本

功能：
1. 读取 data/cleaned/cleaned_reviews.csv
2. 根据评分划分情绪：1-2星负向，3星中性，4-5星正向
3. 合并标题和正文
4. 文本清洗
5. jieba 分词和停用词过滤
6. 输出小黑盒正向/负向词频
7. 用透明关键词规则归纳小黑盒负向评论主题
8. 输出每个负向主题的数量、占比、命中词、代表评论
9. 按月份观察小黑盒负向主题变化
10. 游民星空只输出负向评论样例，作为辅助对比
11. 输出 CSV 表格、PNG 图表和 Markdown 摘要

运行方式：
在项目根目录运行：
python scripts/04_analyze_reviews.py
"""

from pathlib import Path
from collections import Counter
import re
import json

import jieba
import pandas as pd
import matplotlib.pyplot as plt


# =========================
# 1. 路径配置
# =========================

BASE_DIR = Path(__file__).resolve().parents[1]

DATA_PATH = BASE_DIR / "data" / "cleaned" / "cleaned_reviews.csv"

TABLE_DIR = BASE_DIR / "outputs" / "tables"
REPORT_DIR = BASE_DIR / "outputs" / "reports"
CHART_DIR = BASE_DIR / "outputs" / "charts"

TABLE_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)
CHART_DIR.mkdir(parents=True, exist_ok=True)


# =========================
# 2. 字段配置
# =========================

COL_DATE = "published_at"
COL_MONTH = "month"
COL_APP = "app"
COL_RATING = "rating"
COL_TITLE = "title"
COL_CONTENT = "content"

APP_NAME_MAP = {
    "xhh": "小黑盒",
    "ym": "游民星空",
}

# 不作为“具体问题类”展示的主题
# 说明：
# - “强负向情绪表达”是情绪层信号，不直接对应单一产品/运营问题
# - “其他”是未命中规则的评论，需要保留但不适合进入具体问题图表
EXCLUDED_PROBLEM_CATEGORIES = {
    "强负向情绪表达",
    "其他",
}

# =========================
# 3. 停用词配置
# =========================

STOPWORDS = {
    # 常见虚词
    "的", "了", "是", "我", "你", "他", "她", "它", "我们", "你们", "他们",
    "很", "也", "就", "都", "还", "和", "在", "吗", "吧", "啊", "呀", "呢",
    "一个", "这个", "那个", "这些", "那些", "什么", "怎么", "为什么",
    "有", "没有", "不是", "可以", "不能", "不会", "不要",

    # 评论中常见但分析价值较低的词
    "真的", "感觉", "就是", "一直", "现在", "之前", "然后", "但是", "因为",
    "所以", "还是", "直接", "已经", "这么", "这么个", "这么多", "这么久",
    "软件", "app", "APP", "应用", "平台",

    # 单字噪声
    "哈", "哦", "嗯", "啦", "嘛",

    # 本项目评论词频中的泛词/品牌词/低信息词
    "游戏", "黑盒", "小黑盒", "用户", "问题", "自己", "东西",
    "出来", "不了", "根本", "评论", "时候", "一下", "需要",
    "里面", "这种", "这么", "真的", "什么", "一点",

    # 词频图中不希望主导画面的情绪词
    # 注意：这些词仍然会用于主题规则匹配，因为主题匹配基于 clean_text，不基于 tokens
    "垃圾", "恶心", "烂", "太烂", "无语", "离谱", "答辩",
}


# =========================
# 4. 小黑盒负向主题规则
# =========================
# 说明：
# - 这是一版透明规则，不是机器学习模型。
# - 一条评论可以命中多个主题。
# - 没有命中任何主题的评论会归入“其他”。
# - 后续应结合代表评论人工复核并调整关键词。

ISSUE_RULES = {
    "性能与稳定性": [
        "卡顿", "很卡", "太卡", "卡死", "卡住", "卡了", "闪退", "崩溃",
        "加载慢", "加载不出来", "加载失败", "打不开", "进不去",
        "黑屏", "白屏", "发热", "掉帧", "bug", "BUG", "报错",
        "转圈", "白屏转圈",
    ],

    "账号登录与绑定问题": [
        "账号", "账户", "验证码", "验证", "手机号", "实名", "认证",
        "封号", "冻结", "被封", "封禁", "账号异常", "无法登录",
        "登不上", "登不了", "密码", "绑定", "强制绑定", "强行绑定",
        "注销",
    ],

    "加速器与绑定体验": [
        "加速器", "高级加速", "免费加速", "付费加速",
        "强制绑定加速器", "强行绑定加速器",
    ],

    "商业化与消费信任问题": [
        "广告", "开屏", "弹窗", "推广", "会员", "充值", "付费",
        "诱导", "氪金", "营销", "恰饭", "赞助", "要钱", "收费",
        "消费", "充钱", "恰烂钱", "割韭菜", "诈骗", "骗钱", "骗子",
    ],

    "社区氛围与治理": [
        "喷子", "骂人", "引战", "吵架", "阴阳怪气", "带节奏",
        "水军", "举报", "审核", "封禁", "管理", "发帖", "删帖",
        "删评论", "删除", "被删除", "不让评论", "下架", "屏蔽",
        "禁言", "违规", "规矩", "低龄", "聚集地", "乌烟瘴气",
        "恶臭", "素质", "贴吧", "NGA", "nga", "论坛", "中文平台",
        "出征", "性暗示", "偷拍", "恶俗", "恶气熏天",
    ],

    "功能体验与产品设计": [
        "功能", "页面", "界面", "UI", "ui", "入口", "搜索",
        "更新", "改版", "难用", "不好用", "体验", "设计", "操作",
        "找不到", "不方便", "麻烦", "改得", "新版", "旧版",
        "查战绩", "战绩", "小卡片", "统计画面",
    ],

    "内容质量与资讯价值": [
        "资讯", "新闻", "攻略", "评测", "评分", "重复", "搬运",
        "质量", "没用", "不准", "云玩家", "测评", "没营养",
        "水文", "标题党", "编故事", "求爱",
    ],

    "交易与库存相关": [
        "交易", "市场", "库存", "饰品", "余额", "订单", "购买",
        "买入", "卖出", "退款", "钱包", "价格", "报价", "发货",
        "不退", "退钱", "退货", "CDK", "cdk", "激活码", "激活",
        "不给退", "不给下载", "吞钱", "发普通",
    ],

    "客服与反馈处理": [
        "客服", "反馈", "申诉", "处理", "回复", "没人管",
        "不解决", "联系", "人工", "售后", "工单", "工作人员",
        "没人处理", "石沉大海",
    ],

    "活动福利与领取问题": [
        "领取", "领不了", "领不到", "福利", "活动页面", "活动币",
        "活动规则", "任务", "拉新", "roll", "ROLL", "Roll",
        "抽奖", "兑换", "奖励", "礼包", "白嫖",
    ],

    "强负向情绪表达": [
        "垃圾", "答辩", "倒闭", "恶心", "烂", "太烂", "离谱",
        "无语", "捞", "小龟盒", "小红盒", "龟", "龟盒",
        "传家宝", "耍猴",
    ],
}


# =========================
# 5. 通用函数
# =========================

def setup_chinese_font():
    """
    设置中文字体，尽量兼容 Windows + VS Code 环境。
    如果本机没有这些字体，matplotlib 会自动回退。
    """
    plt.rcParams["font.sans-serif"] = [
        "Microsoft YaHei",
        "SimHei",
        "Arial Unicode MS",
        "DejaVu Sans",
    ]
    plt.rcParams["axes.unicode_minus"] = False


def load_data(path: Path) -> pd.DataFrame:
    """读取 cleaned_reviews.csv。"""
    if not path.exists():
        raise FileNotFoundError(f"没有找到文件：{path}")

    try:
        df = pd.read_csv(path, encoding="utf-8-sig")
    except UnicodeDecodeError:
        df = pd.read_csv(path, encoding="gbk")

    return df


def check_required_columns(df: pd.DataFrame):
    """检查必要字段是否存在。"""
    required_cols = [
        COL_DATE,
        COL_MONTH,
        COL_APP,
        COL_RATING,
        COL_TITLE,
        COL_CONTENT,
    ]

    missing_cols = [col for col in required_cols if col not in df.columns]

    if missing_cols:
        raise ValueError(
            "cleaned_reviews.csv 缺少必要字段："
            + ", ".join(missing_cols)
            + "\n当前字段为："
            + ", ".join(df.columns.tolist())
        )


def assign_sentiment(rating) -> str:
    """根据评分划分情绪。"""
    try:
        rating = float(rating)
    except Exception:
        return "unknown"

    if rating <= 2:
        return "negative"
    elif rating == 3:
        return "neutral"
    elif rating >= 4:
        return "positive"
    else:
        return "unknown"


def clean_text(text: str) -> str:
    """
    基础文本清洗：
    - 去掉平台噪声，例如“该条评论已经被删除”“开发者回复”
    - 保留中文、英文、数字
    - 去掉大部分符号
    - 合并多余空格
    """
    if pd.isna(text):
        return ""

    text = str(text)

    # 去掉 App Store / 七麦样本中的平台提示文本
    text = re.sub(r"（?该条评论已经被删除）?", " ", text)

    # 去掉开发者回复及其后面的内容
    # 因为本脚本分析的是用户评论，不分析官方回复
    text = re.sub(r"-{5,}.*?开发者回复[:：].*", " ", text, flags=re.S)
    text = re.sub(r"开发者回复[:：].*", " ", text, flags=re.S)

    # 基础清洗
    text = re.sub(r"[^\u4e00-\u9fa5a-zA-Z0-9]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    return text


def tokenize(text: str, stopwords: set) -> list:
    """
    jieba 分词 + 停用词过滤。
    """
    if not text:
        return []

    words = jieba.lcut(text)

    results = []
    for word in words:
        word = word.strip()

        if not word:
            continue

        # 过滤停用词
        if word in stopwords:
            continue

        # 过滤单个英文字母或数字
        if re.fullmatch(r"[a-zA-Z0-9]", word):
            continue

        # 过滤过短中文单字，避免噪声过多
        # 注意：这里不会过滤英文游戏名或 Steam 这类词
        if len(word) <= 1 and re.fullmatch(r"[\u4e00-\u9fa5]", word):
            continue

        results.append(word)

    return results


def build_word_freq(token_series: pd.Series, top_n: int = 100) -> pd.DataFrame:
    """根据 tokens 列生成词频表。"""
    counter = Counter()

    for tokens in token_series:
        if isinstance(tokens, list):
            counter.update(tokens)

    word_freq = pd.DataFrame(counter.most_common(top_n), columns=["word", "count"])

    return word_freq


def match_issue_categories(text: str, issue_rules: dict) -> tuple:
    """
    对单条负向评论匹配主题。

    返回：
    - matched_categories: 命中的主题列表
    - matched_keywords_dict: 每个主题命中的关键词
    """
    if pd.isna(text):
        text = ""

    text = str(text)
    text_lower = text.lower()

    matched_categories = []
    matched_keywords_dict = {}

    for category, keywords in issue_rules.items():
        matched_keywords = []

        for kw in keywords:
            kw_lower = kw.lower()
            if kw_lower in text_lower:
                matched_keywords.append(kw)

        if matched_keywords:
            matched_categories.append(category)
            matched_keywords_dict[category] = sorted(set(matched_keywords))

    return matched_categories, matched_keywords_dict


def build_sentiment_summary(df: pd.DataFrame) -> pd.DataFrame:
    """生成 App 情绪结构汇总表。"""
    summary = (
        df.groupby([COL_APP, "sentiment"])
        .size()
        .reset_index(name="count")
    )

    total_by_app = (
        df.groupby(COL_APP)
        .size()
        .reset_index(name="app_total")
    )

    summary = summary.merge(total_by_app, on=COL_APP, how="left")
    summary["percent"] = summary["count"] / summary["app_total"] * 100
    summary["percent"] = summary["percent"].round(2)
    summary["app_display_name"] = summary[COL_APP].map(APP_NAME_MAP).fillna(summary[COL_APP])

    sentiment_order = {
        "positive": 1,
        "neutral": 2,
        "negative": 3,
        "unknown": 4,
    }
    summary["sentiment_order"] = summary["sentiment"].map(sentiment_order).fillna(99)
    summary = summary.sort_values([COL_APP, "sentiment_order"])

    return summary[
        ["app", "app_display_name", "sentiment", "count", "app_total", "percent"]
    ]


def add_issue_matching_columns(xhh_negative_df: pd.DataFrame) -> pd.DataFrame:
    """给小黑盒负向评论添加主题匹配结果。"""
    df = xhh_negative_df.copy()

    matched_categories_list = []
    matched_keywords_json_list = []
    matched_category_count_list = []
    matched_keyword_count_list = []

    for text in df["clean_text"]:
        matched_categories, matched_keywords_dict = match_issue_categories(
            text=text,
            issue_rules=ISSUE_RULES,
        )

        matched_categories_list.append(matched_categories)
        matched_keywords_json_list.append(
            json.dumps(matched_keywords_dict, ensure_ascii=False)
        )
        matched_category_count_list.append(len(matched_categories))

        keyword_count = sum(len(v) for v in matched_keywords_dict.values())
        matched_keyword_count_list.append(keyword_count)

    df["matched_categories"] = matched_categories_list
    df["matched_keywords_json"] = matched_keywords_json_list
    df["matched_category_count"] = matched_category_count_list
    df["matched_keyword_count"] = matched_keyword_count_list

    return df


def summarize_issues(xhh_negative_df: pd.DataFrame) -> pd.DataFrame:
    """
    汇总小黑盒负向主题。

    注意：
    一条评论可以命中多个主题，因此各主题占比相加可能超过 100%。
    """
    negative_review_count = len(xhh_negative_df)

    rows = []

    for category, keywords in ISSUE_RULES.items():
        hit_count = xhh_negative_df["matched_categories"].apply(
            lambda cats: category in cats
        ).sum()

        percent = (
            hit_count / negative_review_count * 100
            if negative_review_count > 0
            else 0
        )

        rows.append({
            "issue_category": category,
            "hit_count": int(hit_count),
            "negative_review_count": negative_review_count,
            "percent": round(percent, 2),
            "keywords": "、".join(keywords),
        })

    other_count = xhh_negative_df["matched_categories"].apply(lambda cats: len(cats) == 0).sum()
    other_percent = (
        other_count / negative_review_count * 100
        if negative_review_count > 0
        else 0
    )

    rows.append({
        "issue_category": "其他",
        "hit_count": int(other_count),
        "negative_review_count": negative_review_count,
        "percent": round(other_percent, 2),
        "keywords": "未命中现有规则，建议人工复核",
    })

    issue_summary = pd.DataFrame(rows)
    issue_summary = issue_summary.sort_values("hit_count", ascending=False)

    return issue_summary

def build_problem_only_issue_summary(issue_summary: pd.DataFrame) -> pd.DataFrame:
    """
    生成“具体问题类”负向主题汇总表。

    排除：
    - 强负向情绪表达：属于情绪层信号
    - 其他：属于未命中规则评论

    这个表更适合用于作品集正文图表。
    """
    problem_only_df = issue_summary[
        ~issue_summary["issue_category"].isin(EXCLUDED_PROBLEM_CATEGORIES)
    ].copy()

    problem_only_df = problem_only_df.sort_values("hit_count", ascending=False)

    return problem_only_df


def build_issue_examples(xhh_negative_df: pd.DataFrame, examples_per_category: int = 3) -> pd.DataFrame:
    """
    为每个负向主题输出代表评论。

    代表评论选择规则：
    1. 命中关键词数量更多的优先
    2. 文本长度更长的优先
    3. 每个主题最多取 examples_per_category 条
    """
    rows = []

    for _, row in xhh_negative_df.iterrows():
        categories = row["matched_categories"]

        if not categories:
            categories = ["其他"]

        matched_keywords_dict = {}
        try:
            matched_keywords_dict = json.loads(row["matched_keywords_json"])
        except Exception:
            matched_keywords_dict = {}

        for category in categories:
            matched_keywords = matched_keywords_dict.get(category, [])

            rows.append({
                "issue_category": category,
                "app": row[COL_APP],
                "app_display_name": APP_NAME_MAP.get(row[COL_APP], row[COL_APP]),
                "published_at": row[COL_DATE],
                "month": row[COL_MONTH],
                "rating": row[COL_RATING],
                "title": row[COL_TITLE],
                "content": row[COL_CONTENT],
                "full_text": row["full_text"],
                "matched_keywords": "、".join(matched_keywords) if matched_keywords else "未命中现有规则",
                "category_keyword_count": len(matched_keywords),
                "matched_keyword_count": row["matched_keyword_count"],
                "content_length": len(str(row["full_text"])),
            })

    examples_df = pd.DataFrame(rows)

    if examples_df.empty:
        return examples_df

    examples_df = examples_df.sort_values(
        ["issue_category", "category_keyword_count", "content_length"],
        ascending=[True, False, False],
    )

    examples_df = (
        examples_df.groupby("issue_category", group_keys=False)
        .head(examples_per_category)
        .reset_index(drop=True)
    )

    return examples_df


def build_issue_monthly(xhh_negative_df: pd.DataFrame) -> pd.DataFrame:
    """
    按月份统计小黑盒负向主题变化。

    注意：
    一条评论可以命中多个主题，因此同一个月内各主题占比相加可能超过 100%。
    """
    rows = []

    if xhh_negative_df.empty:
        return pd.DataFrame(columns=[
            "month",
            "issue_category",
            "hit_count",
            "negative_review_count",
            "percent",
        ])

 
    for month, month_df in xhh_negative_df.groupby(COL_MONTH):
        negative_review_count = len(month_df)

        for category in ISSUE_RULES.keys():
            hit_count = month_df["matched_categories"].apply(
                lambda cats: category in cats
            ).sum()

            percent = (
                hit_count / negative_review_count * 100
                if negative_review_count > 0
                else 0
            )

            rows.append({
                "month": month,
                "issue_category": category,
                "hit_count": int(hit_count),
                "negative_review_count": negative_review_count,
                "percent": round(percent, 2),
            })

        other_count = month_df["matched_categories"].apply(lambda cats: len(cats) == 0).sum()
        other_percent = (
            other_count / negative_review_count * 100
            if negative_review_count > 0
            else 0
        )

        rows.append({
            "month": month,
            "issue_category": "其他",
            "hit_count": int(other_count),
            "negative_review_count": negative_review_count,
            "percent": round(other_percent, 2),
        })

    issue_monthly = pd.DataFrame(rows)
    issue_monthly = issue_monthly.sort_values(["month", "issue_category"])

    return issue_monthly


def build_ym_negative_examples(df: pd.DataFrame, n: int = 20) -> pd.DataFrame:
    """
    输出游民星空负向评论样例。

    游民星空样本量较小，只做辅助观察，不做过度推断。
    """
    ym_negative = df[
        (df[COL_APP] == "ym") &
        (df["sentiment"] == "negative")
    ].copy()

    ym_negative["content_length_for_sort"] = ym_negative["full_text"].astype(str).str.len()

    ym_examples = (
        ym_negative.sort_values("content_length_for_sort", ascending=False)
        .head(n)
        [[
            COL_APP,
            COL_DATE,
            COL_MONTH,
            COL_RATING,
            COL_TITLE,
            COL_CONTENT,
            "full_text",
        ]]
        .copy()
    )

    ym_examples["app_display_name"] = ym_examples[COL_APP].map(APP_NAME_MAP).fillna(ym_examples[COL_APP])

    return ym_examples


# =========================
# 6. 画图函数
# =========================

def plot_sentiment_structure(sentiment_summary: pd.DataFrame):
    """图1：评论情绪结构。"""
    plot_df = sentiment_summary.copy()

    sentiment_label_map = {
        "positive": "正向",
        "neutral": "中性",
        "negative": "负向",
        "unknown": "未知",
    }
    plot_df["sentiment_label"] = plot_df["sentiment"].map(sentiment_label_map).fillna(plot_df["sentiment"])

    pivot_df = plot_df.pivot_table(
        index="app_display_name",
        columns="sentiment_label",
        values="percent",
        fill_value=0,
    )

    desired_cols = ["正向", "中性", "负向", "未知"]
    pivot_df = pivot_df[[col for col in desired_cols if col in pivot_df.columns]]

    ax = pivot_df.plot(kind="bar", figsize=(9, 5))

    ax.set_title("评论情绪结构对比")
    ax.set_xlabel("App")
    ax.set_ylabel("占比（%）")
    ax.legend(title="情绪类型")
    plt.xticks(rotation=0)
    plt.tight_layout()

    output_path = CHART_DIR / "final_01_review_sentiment_structure.png"
    plt.savefig(output_path, dpi=200)
    plt.close()


def plot_word_freq_compare(positive_word_freq: pd.DataFrame, negative_word_freq: pd.DataFrame):
    """图2：小黑盒正向/负向词频对比。"""
    top_n = 20

    pos_df = positive_word_freq.head(top_n).copy()
    neg_df = negative_word_freq.head(top_n).copy()

    fig, axes = plt.subplots(1, 2, figsize=(14, 7))

    # 正向词频
    axes[0].barh(pos_df["word"][::-1], pos_df["count"][::-1])
    axes[0].set_title("小黑盒正向评论高频词 Top 20")
    axes[0].set_xlabel("出现次数")
    axes[0].set_ylabel("词语")

    # 负向词频
    axes[1].barh(neg_df["word"][::-1], neg_df["count"][::-1])
    axes[1].set_title("小黑盒负向评论高频词 Top 20")
    axes[1].set_xlabel("出现次数")
    axes[1].set_ylabel("词语")

    plt.tight_layout()

    output_path = CHART_DIR / "final_02_xhh_positive_negative_word_freq.png"
    plt.savefig(output_path, dpi=200)
    plt.close()


def plot_issue_categories(issue_summary: pd.DataFrame):
    """
    图3：小黑盒负向评论主题占比。

    说明：
    - 保留“强负向情绪表达”，因为它是负向评论中的重要情绪信号
    - 保留“其他”，用于提示规则未覆盖部分
    - 在报告文字中说明“强负向情绪表达”不是具体产品问题
    """
    plot_df = issue_summary.copy()
    plot_df = plot_df.sort_values("percent", ascending=True)

    plt.figure(figsize=(10, 7))
    plt.barh(plot_df["issue_category"], plot_df["percent"])

    plt.title("小黑盒负向评论主题命中占比")
    plt.xlabel("占小黑盒负向评论比例（%）")
    plt.ylabel("主题类型")

    for index, value in enumerate(plot_df["percent"]):
        plt.text(value + 0.5, index, f"{value:.1f}%", va="center")

    plt.tight_layout()

    output_path = CHART_DIR / "final_03_xhh_negative_issue_categories.png"
    plt.savefig(output_path, dpi=200)
    plt.close()


def plot_issue_monthly_trend(problem_only_issue_summary: pd.DataFrame, issue_monthly: pd.DataFrame):
    """
    图4：小黑盒具体问题类负向主题月度变化。

    为避免折线过多，只画具体问题类 Top 5。
    不画：
    - 强负向情绪表达
    - 其他
    """
    top_categories = (
        problem_only_issue_summary
        .sort_values("hit_count", ascending=False)
        .head(5)["issue_category"]
        .tolist()
    )

    plot_df = issue_monthly[
        issue_monthly["issue_category"].isin(top_categories)
    ].copy()

    if plot_df.empty:
        return

    pivot_df = plot_df.pivot_table(
        index="month",
        columns="issue_category",
        values="percent",
        fill_value=0,
    )

    pivot_df = pivot_df.sort_index()

    plt.figure(figsize=(12, 6))

    for category in pivot_df.columns:
        plt.plot(pivot_df.index, pivot_df[category], marker="o", label=category)

    plt.title("小黑盒主要具体问题类负向主题月度变化")
    plt.xlabel("月份")
    plt.ylabel("占当月负向评论比例（%）")
    plt.xticks(rotation=45)
    plt.legend(title="具体问题主题")
    plt.tight_layout()

    output_path = CHART_DIR / "final_04_xhh_negative_issue_monthly_trend.png"
    plt.savefig(output_path, dpi=200)
    plt.close()


# =========================
# 7. Markdown 摘要
# =========================

def save_summary_markdown(
    df: pd.DataFrame,
    sentiment_summary: pd.DataFrame,
    positive_word_freq: pd.DataFrame,
    negative_word_freq: pd.DataFrame,
    issue_summary: pd.DataFrame,
    problem_only_issue_summary: pd.DataFrame,
    issue_monthly: pd.DataFrame,
):
    """
    输出 review_analysis_summary.md。

    本摘要用于后续作品集写作参考，不是最终正文。
    重点区分：
    1. 情绪层观察：强负向情绪表达、其他
    2. 具体问题类观察：社区治理、功能体验、客服反馈等
    """

    xhh_count = len(df[df[COL_APP] == "xhh"])
    ym_count = len(df[df[COL_APP] == "ym"])

    xhh_negative_count = len(
        df[(df[COL_APP] == "xhh") & (df["sentiment"] == "negative")]
    )
    ym_negative_count = len(
        df[(df[COL_APP] == "ym") & (df["sentiment"] == "negative")]
    )

    top_positive_words = positive_word_freq.head(10)
    top_negative_words = negative_word_freq.head(10)

    # 情绪层：强负向情绪表达
    strong_negative_row = issue_summary[
        issue_summary["issue_category"] == "强负向情绪表达"
    ]

    strong_negative_percent = 0
    strong_negative_count = 0

    if not strong_negative_row.empty:
        strong_negative_percent = float(strong_negative_row.iloc[0]["percent"])
        strong_negative_count = int(strong_negative_row.iloc[0]["hit_count"])

    # 其他类
    other_row = issue_summary[issue_summary["issue_category"] == "其他"]

    other_percent = 0
    other_count = 0

    if not other_row.empty:
        other_percent = float(other_row.iloc[0]["percent"])
        other_count = int(other_row.iloc[0]["hit_count"])

    warning_text = ""
    if other_percent >= 30:
        warning_text = (
            "\n\n> 注意：当前“其他”类占比达到 "
            f"{other_percent:.2f}% ，说明现有主题规则仍有较多未覆盖评论。"
            "建议人工复核 `xhh_negative_review_examples.csv` 中“其他”类代表评论，"
            "再补充或调整关键词规则。"
        )
    elif other_percent >= 15:
        warning_text = (
            "\n\n> 提醒：当前“其他”类占比为 "
            f"{other_percent:.2f}% ，仍建议抽样查看“其他”类评论，"
            "确认是否存在尚未归纳出的新主题。"
        )
    else:
        warning_text = (
            "\n\n当前“其他”类占比相对可控，说明主题规则对主要负向评论已有一定覆盖。"
        )

    sentiment_table = sentiment_summary.to_markdown(index=False)

    issue_display_cols = [
        "issue_category",
        "hit_count",
        "negative_review_count",
        "percent",
    ]

    full_issue_table = issue_summary[issue_display_cols].to_markdown(index=False)
    problem_issue_table = problem_only_issue_summary[issue_display_cols].to_markdown(index=False)
    positive_words_md = "\n".join(
        [
            f"- {row['word']}：{row['count']}"
            for _, row in top_positive_words.iterrows()
        ]
    )

    negative_words_md = "\n".join(
        [
            f"- {row['word']}：{row['count']}"
            for _, row in top_negative_words.iterrows()
        ]
    )

    # 具体问题类 Top 3，用于摘要文字
    top_problem_lines = []
    for _, row in problem_only_issue_summary.head(3).iterrows():
        top_problem_lines.append(
            f"- 「{row['issue_category']}」：{row['hit_count']} 条，"
            f"占小黑盒负向评论的 {row['percent']:.2f}%"
        )

    top_problem_md = "\n".join(top_problem_lines)

    # 月度趋势：只基于具体问题类主题
    monthly_observation = ""
    if not issue_monthly.empty and not problem_only_issue_summary.empty:
        problem_categories = problem_only_issue_summary["issue_category"].tolist()

        monthly_top = (
            issue_monthly[
                issue_monthly["issue_category"].isin(problem_categories)
            ]
            .sort_values(["month", "percent"], ascending=[True, False])
            .groupby("month")
            .head(1)
        )

        monthly_lines = []
        for _, row in monthly_top.iterrows():
            monthly_lines.append(
                f"- {row['month']}：具体问题类中占比较高的主题为"
                f"「{row['issue_category']}」，占当月负向评论的 {row['percent']:.2f}%"
            )

        monthly_observation = "\n".join(monthly_lines)

    if not monthly_observation:
        monthly_observation = "暂无可用的月度主题观察结果。"

    content = f"""# 评论分析摘要

## 1. 数据说明

本次分析基于 `data/cleaned/cleaned_reviews.csv` 中的 App Store 公开评论样本。

- 小黑盒样本量：{xhh_count} 条
- 游民星空样本量：{ym_count} 条
- 小黑盒负向评论数：{xhh_negative_count} 条
- 游民星空负向评论数：{ym_negative_count} 条

情绪划分规则：

- 1-2 星：负向
- 3 星：中性
- 4-5 星：正向

注意：七麦数据和 App Store 评论属于公开样本观察，不等同于全部用户反馈，也不能直接代表全体用户态度。

## 2. 评分情绪结构

{sentiment_table}

观察时需要注意：游民星空样本量明显小于小黑盒，因此仅适合作为辅助对比，不宜做强结论。

## 3. 小黑盒正向评论高频词 Top 10

{positive_words_md}

这些词可以辅助观察用户在正向评论中更常提到的产品感知点，但词频结果仍需要结合原始评论语境理解。

## 4. 小黑盒负向评论高频词 Top 10

{negative_words_md}

负向高频词可以帮助定位用户吐槽集中区域，但不能仅凭单个词判断问题性质，需要结合主题规则和代表评论。

## 5. 小黑盒负向评论：情绪层观察

本脚本将「强负向情绪表达」单独作为情绪层信号处理，不直接等同于具体产品或运营问题。

- 强负向情绪表达：{strong_negative_count} 条，占小黑盒负向评论的 {strong_negative_percent:.2f}%
- 其他未命中规则评论：{other_count} 条，占小黑盒负向评论的 {other_percent:.2f}%

「强负向情绪表达」主要用于识别公开评论中的强烈不满表达，例如“垃圾”“烂”“恶心”等。这类评论可以提示口碑风险或用户情绪波动，但通常需要结合具体问题主题和代表评论进一步判断原因。

{warning_text}

完整主题汇总如下，关键词规则已保留在 `outputs/tables/xhh_negative_issue_summary.csv` 中，便于复核：

{full_issue_table}

## 6. 小黑盒负向评论：具体问题类归纳

为了服务运营分析，以下表格排除了「强负向情绪表达」和「其他」，只保留更能对应产品体验、社区治理、客服反馈、活动机制等方向的具体问题类主题。完整关键词规则已保留在 `outputs/tables/xhh_negative_issue_summary_problem_only.csv` 中。

{problem_issue_table}

具体问题类中，当前占比较高的主题包括：

{top_problem_md}

说明：本部分使用透明关键词规则进行归纳，不使用复杂模型。一条评论可以命中多个主题，因此各主题占比相加可能超过 100%。

## 7. 小黑盒负向主题月度变化观察

以下月度观察仅基于具体问题类主题，不包含「强负向情绪表达」和「其他」。结果只作为现象提示，不做因果判断。

{monthly_observation}

## 8. 游民星空辅助对比

游民星空样本量较小，本脚本仅输出负向评论样例文件：

`outputs/tables/ym_negative_review_examples.csv`

建议在作品集中仅作为辅助观察，不要对游民星空做过度推断。

## 9. 后续运营分析方向

后续可以围绕以下方向继续人工复核：

1. 对「社区氛围与治理」类评论，重点查看是否集中在喷子、引战、删帖、举报、审核等问题。
2. 对「客服与反馈处理」类评论，重点判断用户是否在表达反馈无响应、申诉失败或处理慢。
3. 对「活动福利与领取问题」类评论，关注是否涉及领取失败、活动规则不清、Roll 区或福利机制体验。
4. 对「商业化与消费信任问题」类评论，区分广告干扰、付费不满、消费纠纷和信任风险。
5. 最终作品集写作时，建议使用“公开评论样本显示”“样本中可观察到”“值得作为运营关注点”等谨慎表达。
"""

    output_path = REPORT_DIR / "review_analysis_summary.md"
    output_path.write_text(content, encoding="utf-8-sig")

# =========================
# 8. 主流程
# =========================

def main():
    setup_chinese_font()

    print("开始读取 cleaned_reviews.csv ...")
    df = load_data(DATA_PATH)
    check_required_columns(df)

    print(f"读取完成：{len(df)} 条评论，{len(df.columns)} 个字段。")

    # 评分字段转数值
    df[COL_RATING] = pd.to_numeric(df[COL_RATING], errors="coerce")

    # 根据评分重新生成情绪字段，保证分析规则自洽
    df["sentiment"] = df[COL_RATING].apply(assign_sentiment)

    # 合并标题和正文
    df[COL_TITLE] = df[COL_TITLE].fillna("")
    df[COL_CONTENT] = df[COL_CONTENT].fillna("")
    df["full_text"] = df[COL_TITLE].astype(str) + " " + df[COL_CONTENT].astype(str)

    # 文本清洗
    df["clean_text"] = df["full_text"].apply(clean_text)

    # 分词
    print("开始 jieba 分词 ...")
    df["tokens"] = df["clean_text"].apply(lambda x: tokenize(x, STOPWORDS))

    # 情绪结构汇总
    sentiment_summary = build_sentiment_summary(df)

    # 小黑盒正向/负向评论
    xhh_df = df[df[COL_APP] == "xhh"].copy()
    xhh_positive_df = xhh_df[xhh_df["sentiment"] == "positive"].copy()
    xhh_neutral_df = xhh_df[xhh_df["sentiment"] == "neutral"].copy()
    xhh_negative_df = xhh_df[xhh_df["sentiment"] == "negative"].copy()

    print(f"小黑盒评论数：{len(xhh_df)}")
    print(f"小黑盒正向评论数：{len(xhh_positive_df)}")
    print(f"小黑盒负向评论数：{len(xhh_negative_df)}")
    print(f"小黑盒中性评论数：{len(xhh_neutral_df)}")

    # 小黑盒词频
    xhh_positive_word_freq = build_word_freq(xhh_positive_df["tokens"], top_n=100)
    xhh_neutral_word_freq = build_word_freq(xhh_neutral_df["tokens"], top_n=100)
    xhh_negative_word_freq = build_word_freq(xhh_negative_df["tokens"], top_n=100)

    # 小黑盒负向主题匹配
    print("开始匹配小黑盒负向主题 ...")
    xhh_negative_df = add_issue_matching_columns(xhh_negative_df)

    issue_summary = summarize_issues(xhh_negative_df)
    problem_only_issue_summary = build_problem_only_issue_summary(issue_summary)
    issue_monthly = build_issue_monthly(xhh_negative_df)
    xhh_negative_examples = build_issue_examples(xhh_negative_df, examples_per_category=3)

    # 游民星空负向样例
    ym_negative_examples = build_ym_negative_examples(df, n=20)

    # 保存 CSV 表格
    print("开始保存 CSV 表格 ...")

    sentiment_summary.to_csv(
        TABLE_DIR / "review_sentiment_summary.csv",
        index=False,
        encoding="utf-8-sig",
    )

    xhh_positive_word_freq.to_csv(
        TABLE_DIR / "xhh_positive_word_freq.csv",
        index=False,
        encoding="utf-8-sig",
    )

    xhh_neutral_word_freq.to_csv(
        TABLE_DIR / "xhh_neutral_word_freq.csv",
        index=False,
        encoding="utf-8-sig",
    )
    
    xhh_negative_word_freq.to_csv(
        TABLE_DIR / "xhh_negative_word_freq.csv",
        index=False,
        encoding="utf-8-sig",
    )

    issue_summary.to_csv(
        TABLE_DIR / "xhh_negative_issue_summary.csv",
        index=False,
        encoding="utf-8-sig",
    )

    problem_only_issue_summary.to_csv(
        TABLE_DIR / "xhh_negative_issue_summary_problem_only.csv",
        index=False,
        encoding="utf-8-sig",
    )

    issue_monthly.to_csv(
        TABLE_DIR / "xhh_negative_issue_monthly.csv",
        index=False,
        encoding="utf-8-sig",
    )

    xhh_negative_examples.to_csv(
        TABLE_DIR / "xhh_negative_review_examples.csv",
        index=False,
        encoding="utf-8-sig",
    )

    ym_negative_examples.to_csv(
        TABLE_DIR / "ym_negative_review_examples.csv",
        index=False,
        encoding="utf-8-sig",
    )

    # 保存一份带有中间字段的分析明细，方便人工复核
    review_analysis_detail_cols = [
        COL_APP,
        COL_DATE,
        COL_MONTH,
        COL_RATING,
        "sentiment",
        COL_TITLE,
        COL_CONTENT,
        "full_text",
        "clean_text",
    ]

    df[review_analysis_detail_cols].to_csv(
        TABLE_DIR / "review_analysis_detail.csv",
        index=False,
        encoding="utf-8-sig",
    )

    # 保存小黑盒负向匹配明细，方便复核规则
    xhh_negative_detail_cols = [
        COL_APP,
        COL_DATE,
        COL_MONTH,
        COL_RATING,
        COL_TITLE,
        COL_CONTENT,
        "full_text",
        "clean_text",
        "matched_categories",
        "matched_keywords_json",
        "matched_category_count",
        "matched_keyword_count",
    ]

    xhh_negative_df[xhh_negative_detail_cols].to_csv(
        TABLE_DIR / "xhh_negative_issue_detail.csv",
        index=False,
        encoding="utf-8-sig",
    )

    # 画图
    print("开始生成图表 ...")
    plot_sentiment_structure(sentiment_summary)
    plot_word_freq_compare(xhh_positive_word_freq, xhh_negative_word_freq)
    plot_issue_categories(issue_summary)
    plot_issue_monthly_trend(problem_only_issue_summary, issue_monthly)

    # Markdown 摘要
    print("开始生成 Markdown 摘要 ...")
    save_summary_markdown(
        df=df,
        sentiment_summary=sentiment_summary,
        positive_word_freq=xhh_positive_word_freq,
        negative_word_freq=xhh_negative_word_freq,
        issue_summary=issue_summary,
        problem_only_issue_summary=problem_only_issue_summary,
        issue_monthly=issue_monthly,
    )

    # 控制台提示
    other_row = issue_summary[issue_summary["issue_category"] == "其他"]
    if not other_row.empty:
        other_percent = float(other_row.iloc[0]["percent"])
        if other_percent >= 30:
            print(
                f"提醒：“其他”类占比为 {other_percent:.2f}%，"
                "建议打开 outputs/tables/xhh_negative_review_examples.csv 人工复核。"
            )

    print("\n评论分析完成。")
    print(f"表格输出目录：{TABLE_DIR}")
    print(f"图表输出目录：{CHART_DIR}")
    print(f"报告输出目录：{REPORT_DIR}")


if __name__ == "__main__":
    main()