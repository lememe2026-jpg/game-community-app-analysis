"""
05_analyze_keywords.py

关键词需求与运营线索分析脚本（V3.4）
输入： data/cleaned/cleaned_keywords.csv
输出： outputs/tables/、outputs/charts/、outputs/reports/

本脚本的分析目标：
1. 不是做 ASO 投放建议，也不是判断某个关键词“该不该优化”。
2. cleaned_keywords.csv 在本项目中用于观察公开搜索场景下的游戏社区 App 相关需求。
3. 重点把关键词转译为：内容运营、社区运营、功能/工具运营、活动运营、平台生态与竞品观察线索。
4. 搜索指数仅作为 App Store 搜索需求热度观察，不等同于真实下载量、真实流量或真实商业价值。
5. 关键词排名仅作为 App Store 搜索可见性的辅助对比，排名数值越小，可见性越靠前。
6. 关键词分类使用透明规则，不使用复杂模型；一条关键词只归入一个主类别。
7. V3.4 起，图表控制在 3 张以内：数据边界说明图、核心运营场景支持力矩阵、代表关键词搜索可见性对比。
8. Top30 不再强行画图，而是输出解释表，并把“主结论代表词/辅助观察词/背景/复核”分开。
9. 新增分类样例表、代表词选择表和输出文件清单，降低“规则分词”“代表词选择”和“文件堆积”的黑箱感。
10. 运行脚本时会自动给历史冗余输出加 experimental_ 或 deprecated_ 前缀，避免旧图旧表污染当前分析。
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import font_manager
import warnings

warnings.filterwarnings("ignore", message="Glyph .* missing from font.*")


# =========================================================
# 1. 路径配置
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT_FILE = PROJECT_ROOT / "data" / "cleaned" / "cleaned_keywords.csv"
OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables"
OUTPUT_CHART_DIR = PROJECT_ROOT / "outputs" / "charts"
OUTPUT_REPORT_DIR = PROJECT_ROOT / "outputs" / "reports"


# =========================================================
# 2. 字段配置
# =========================================================

COL_KEYWORD = "keyword"
COL_SEARCH_INDEX = "search_index"
COL_SEARCH_RESULT_COUNT = "search_result_count"
COL_POPULARITY = "popularity"
COL_XHH_RANK = "xhh_rank"
COL_YM_RANK = "ym_rank"
COL_XHH_HAS_RANK = "xhh_has_rank"
COL_YM_HAS_RANK = "ym_has_rank"

REQUIRED_COLUMNS = [
    COL_KEYWORD,
    COL_SEARCH_INDEX,
    COL_SEARCH_RESULT_COUNT,
    COL_POPULARITY,
    COL_XHH_RANK,
    COL_YM_RANK,
    COL_XHH_HAS_RANK,
    COL_YM_HAS_RANK,
]


# =========================================================
# 3. 关键词分类规则
#
# 说明：
# - 按列表顺序匹配，命中后即停止。
# - 一条关键词只进入一个主类别，方便后续做类别汇总。
# - 分类目标不是“给每个词找投放机会”，而是把搜索词转译为游戏运营可理解的需求方向。
# =========================================================

CATEGORY_RULES = [
    {
        "category": "非目标/噪声词",
        "patterns": [
            "w p s", "wps", "卖手机", "手机回收", "记账", "timi记账",
            "凤凰商城", "邮宝", "进佣", "拥金宝", "远离手机", "ps修图",
            "ps抠图", "修图", "打印", "邕有家", "彬果", "控客", "小控",
            "jumo", "gump", "应用商店下载", "付费", "小二", "女性社区", "91社区", "51社区", "芒果社区",
            "ps教程", "制造新闻", "简影", "女主播经纪公司", "快手m",
        ],
    },
    {
        "category": "品牌/竞品平台词",
        "patterns": [
            "小黑盒", "黑盒", "xhh", "小盒", "小盒子", "游民星空", "gamersky", "游民",
            "游明星空", "游名星空", "mga",
            "七麦", "游侠", "3dm", "机核", "游研社", "篝火营地", "电玩巴士",
            "taptap", "tap tap", "taotap", "tptp", "tsptap", "手游快爆", "好游快爆",
            "应用宝", "九游", "nga", "17173", "4399", "游戏时光", "好游戏快爆", "好游戏快爆社区", "好游快爆社区", "游戏盒子",
            "凤凰游戏商城", "游戏折扣商城", "凤凰游戏商城-游戏折扣商城", "巴哈姆特", "psnine",
            "bilibili游戏", "b站游戏", "gamekee", "bigfun", "米游社",
        ],
    },
    {
        "category": "交易/库存/消费信任词",
        "patterns": [
            "steam交易", "steam库存", "steam市场", "steam退款", "steam钱包",
            "库存", "饰品", "交易", "市场", "cdk", "激活", "退款", "钱包",
            "余额", "钥匙", "开箱", "租号", "账号交易", "皮肤交易", "买号", "卖号",
        ],
    },
    {
        "category": "Steam/PC/主机生态词",
        "patterns": [
            "steam", "蒸汽", "蒸汽平台", "stmbuy", "switch", "ns游戏", "任天堂",
            "ps5", "ps4", "playstation", "palystation", "psremoteplay", "psn",
            "xbox", "xobx", "xgp", "xcloud", "主机", "掌机", "单机",
            "pc游戏", "pc端", "电脑游戏", "端游", "主机游戏", "买断制", "e宝",
        ],
    },
    {
        "category": "热门游戏/IP词",
        "patterns": [
            "原神", "王者荣耀", "和平精英", "英雄联盟", "lol", "pubg", "绝地求生",
            "cs2", "csgo", "无畏契约", "无畏契", "无限契约", "valorant", "瓦罗兰特", "打瓦",
            "永劫无间", "永劫", "永杰", "永结无间", "永杰无间", "永恒无间",
            "yjwj", "yong'jie'wu'jian", "永jiewujian", "勇劫无间", "鸣潮", "崩铁", "星穹铁道",
            "明日方舟", "第五人格", "蛋仔派对", "金铲铲", "逆水寒", "阴阳师",
            "碧蓝航线", "炉石", "魔兽", "dnf", "地下城与勇士", "穿越火线", "cf",
            "三角洲行动", "暗区突围", "燕云十六声", "黑神话", "神话悟空",
            "我的世界", "mc", "泰拉瑞亚", "饥荒", "赛博朋克", "艾尔登法环",
            "荒野大镖客", "塞尔达", "幽灵行者", "部落冲突", "怪物猎人",
            "彩六", "极乐迪斯科", "底特律变人", "消逝的光芒", "奇异人生",
            "隐形的守护者", "飞跃13号房", "完蛋了我被美女包围了", "灵魂摆渡者",
            "致命解药", "艾迪芬奇的记忆", "神佑释放", "albion", "deceit",
            "加拿大不归路", "我的朋友佩德罗", "野餐大冒险", "暖雪", "扫雷",
            "魔晶猎人", "热血猎人", "猎龙", "全职猎人", "王者猎人",
        ],
    },
    {
        "category": "手游/二游生态词",
        "patterns": [
            "手游", "二游", "抽卡", "角色", "卡池", "米哈游", "b服", "官服",
            "渠道服", "日服", "国服", "国际服", "养成", "氪金", "体力",
        ],
    },
    {
        "category": "攻略资讯词",
        "patterns": [
            "攻略", "资讯", "新闻", "评测", "评分", "图鉴", "wiki", "资料库",
            "百科", "教程", "指南", "配装", "天赋", "阵容", "打法", "任务",
            "剧情", "更新", "版本", "补丁", "公告", "数据库",
        ],
    },
    {
        "category": "社区互动词",
        "patterns": [
            "社区", "论坛", "玩家社区", "游戏社区", "评论", "帖子", "发帖",
            "组队", "开黑", "讨论", "公会", "战队", "好友", "聊天", "吐槽",
            "圈子", "贴吧", "同好", "玩家交流",
        ],
    },
    {
        "category": "工具服务词",
        "patterns": [
            "加速器", "加速", "战绩", "查战绩", "游戏库", "助手",
            "账号绑定", "绑定账号", "steam绑定", "绑定steam", "绑定", "账号",
            "登录失败", "登陆失败", "无法登录", "无法登陆", "注册", "扫码", "令牌",
            "云存档", "存档", "mod", "地图", "安卓模拟器", "手游模拟器", "游戏模拟器",
            "模拟器助手", "下载器", "启动器", "大脚",
        ],
    },
    {
        "category": "活动福利词",
        "patterns": [
            "活动", "福利", "礼包", "兑换码", "抽奖", "领取", "奖励", "签到",
            "预约", "内测", "测试资格", "资格", "返利", "优惠券",
        ],
    },
    {
        "category": "内容平台/直播视频词",
        "patterns": [
            "b站", "bilibili", "直播", "视频", "主播", "up主", "up 主", "弹幕",
            "斗鱼", "虎牙", "抖音", "快手", "小红书", "微博", "赛事直播",
        ],
    },
    {
        "category": "泛游戏/休闲游戏词",
        "patterns": [
            "小游戏", "休闲游戏", "无网游戏", "联网游戏", "手机小游戏",
            "游戏", "网游", "电竞", "玩家", "游戏盒", "游戏中心", "游戏平台",
            "游戏推荐", "好玩的", "排行榜", "消消乐", "猎鹿", "小狗爱旅行",
            "无忧小院", "熊猫爱旅行", "百变熊猫", "羊羊爱吃菜", "我在桃源有个家",
            "再来一次火锅店", "模拟器", "不需要登录的游戏", "不用登录的游戏",
        ],
    },
]

# 评论专项中需要回看关键词侧是否存在交叉观察点的主题。
REVIEW_ALIGNMENT_THEMES = {
    "Steam": ["steam", "蒸汽"],
    "社区": ["社区", "论坛", "帖子", "评论", "组队", "讨论", "开黑"],
    "攻略": ["攻略", "wiki", "资料库", "教程", "指南", "图鉴"],
    "活动": ["活动", "福利", "礼包", "兑换码", "领取", "奖励", "签到"],
    "交易/库存": ["交易", "库存", "饰品", "市场", "钱包", "cdk", "激活"],
    "退款/消费信任": ["退款", "钱包", "余额", "消费", "付费"],
    "客服/反馈": ["客服", "反馈", "工单"],
    "工具": ["工具", "助手", "战绩", "游戏库", "存档", "mod", "地图"],
    "加速器": ["加速器", "加速"],
    "登录/绑定": ["登录", "登陆", "绑定", "账号", "注册"],
}

# 运营线索输出时优先保留的需求等级。
HIGH_DEMAND_LEVELS = ["极高搜索需求", "高搜索需求", "较高搜索需求"]


# =========================================================
# 4. 通用工具函数
# =========================================================

def ensure_output_dirs() -> None:
    OUTPUT_TABLE_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_CHART_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_REPORT_DIR.mkdir(parents=True, exist_ok=True)


def _rename_if_exists(path: Path, new_prefix: str, reason_slug: str) -> Path | None:
    """给历史输出加前缀。若目标名已存在，则自动追加序号，避免覆盖。"""
    if not path.exists():
        return None
    if path.name.startswith(("deprecated_", "experimental_")):
        return None

    target = path.with_name(f"{new_prefix}_{path.stem}__{reason_slug}{path.suffix}")
    if target.exists():
        idx = 2
        while True:
            candidate = path.with_name(f"{new_prefix}_{path.stem}__{reason_slug}_{idx}{path.suffix}")
            if not candidate.exists():
                target = candidate
                break
            idx += 1
    path.rename(target)
    return target


def label_legacy_outputs() -> pd.DataFrame:
    """
    V3.4 输出整理：
    - deprecated_：明确不再建议使用的历史图/表，通常是容易误导的旧口径。
    - experimental_：曾经有探索价值，但不作为当前主线结论的历史图/表。

    这个函数只处理历史冗余文件，不会移动 V3.4 的正式输出。
    """
    legacy_plan = [
        (OUTPUT_CHART_DIR / "final_05_keyword_top30.png", "deprecated", "superseded_by_top30_interpretation_table", "旧 Top30 图容易变成“为了画图而画图”，已由 keyword_top30_interpretation.csv 替代。"),
        (OUTPUT_CHART_DIR / "final_06_keyword_category_distribution.png", "deprecated", "superseded_by_operation_support_matrix", "旧分类分布图会被待复核/噪声干扰，已由核心运营场景支持力矩阵替代。"),
        (OUTPUT_CHART_DIR / "final_06_keyword_category_distribution_rgb.png", "deprecated", "old_color_test", "旧配色测试图，不进入当前分析。"),
        (OUTPUT_CHART_DIR / "final_07_keyword_ranking_advantage.png", "deprecated", "renamed_to_search_visibility_compare", "旧文件名 advantage 容易被误读为运营强弱，已改为搜索可见性辅助对比。"),
        (OUTPUT_CHART_DIR / "final_07_keyword_ranking_advantage_rgb.png", "deprecated", "old_color_test", "旧配色测试图，不进入当前分析。"),
        (OUTPUT_CHART_DIR / "final_08_keyword_operation_scene_distribution.png", "experimental", "v32_data_scope_draft", "V3.2 数据分层探索图，有参考价值，但已由 final_05_keyword_data_scope.png 替代。"),
        (OUTPUT_TABLE_DIR / "keyword_core_opportunity_list.csv", "deprecated", "aso_opportunity_draft", "旧 ASO 机会词口径，与当前运营线索主线不一致。"),
        (OUTPUT_TABLE_DIR / "keyword_opportunity_list.csv", "deprecated", "legacy_aso_name", "旧文件名容易误导为 ASO 投放机会，V3.4 不再生成。"),
        (OUTPUT_TABLE_DIR / "keyword_core_gap_list.csv", "experimental", "weak_visibility_draft", "旧双方弱可见词探索表，可参考但不作为当前主线输出。"),
    ]

    rows = []
    for path, prefix, reason_slug, reason in legacy_plan:
        new_path = _rename_if_exists(path, prefix, reason_slug)
        rows.append({
            "original_file": path.name,
            "new_file": new_path.name if new_path else "未发现或已处理",
            "status": prefix,
            "reason": reason,
        })
    return pd.DataFrame(rows)


def set_chinese_font() -> None:
    """设置中文字体。Windows 下优先使用微软雅黑；Linux 测试环境下尝试加载 Noto CJK。"""
    candidate_font_files = [
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc",
    ]
    loaded_font_name = None
    for font_file in candidate_font_files:
        if Path(font_file).exists():
            try:
                font_manager.fontManager.addfont(font_file)
                loaded_font_name = font_manager.FontProperties(fname=font_file).get_name()
                break
            except Exception:
                loaded_font_name = None

    if loaded_font_name:
        plt.rcParams["font.sans-serif"] = [
            "Microsoft YaHei", "SimHei", loaded_font_name, "PingFang SC", "Heiti SC", "Arial Unicode MS", "DejaVu Sans",
        ]
    else:
        plt.rcParams["font.sans-serif"] = [
            "Microsoft YaHei", "SimHei", "PingFang SC", "Heiti SC", "Noto Sans CJK SC", "Arial Unicode MS", "DejaVu Sans",
        ]
    plt.rcParams["axes.unicode_minus"] = False


def read_keywords_data(input_file: Path) -> pd.DataFrame:
    if not input_file.exists():
        raise FileNotFoundError(f"未找到输入文件：{input_file}")
    return pd.read_csv(input_file)


def check_required_columns(df: pd.DataFrame) -> None:
    missing_columns = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_columns:
        raise ValueError(f"cleaned_keywords.csv 缺少必要字段：{missing_columns}")


def to_bool_series(series: pd.Series) -> pd.Series:
    if series.dtype == bool:
        return series

    true_values = {"true", "1", "yes", "y", "有", "是", "排名", "covered"}
    false_values = {"false", "0", "no", "n", "无", "否", "未覆盖", "无排名", "not covered"}

    def convert(value: Any) -> bool:
        if pd.isna(value):
            return False
        if isinstance(value, bool):
            return value
        value_str = str(value).strip().lower()
        if value_str in true_values:
            return True
        if value_str in false_values:
            return False
        return bool(value)

    return series.apply(convert)


def contains_any(keyword_lower: str, patterns: list[str]) -> bool:
    return any(pattern.lower() in keyword_lower for pattern in patterns)


# =========================================================
# 5. 数据清洗与衍生字段
# =========================================================

def clean_keyword_text(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df[COL_KEYWORD] = df[COL_KEYWORD].fillna("").astype(str)
    df["keyword_clean"] = df[COL_KEYWORD].str.strip()
    df["keyword_lower"] = df["keyword_clean"].str.lower()
    df = df[df["keyword_clean"] != ""].copy()
    return df


def convert_numeric_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    numeric_columns = [
        COL_SEARCH_INDEX,
        COL_SEARCH_RESULT_COUNT,
        COL_POPULARITY,
        COL_XHH_RANK,
        COL_YM_RANK,
    ]
    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def normalize_rank_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    标准化排名字段。
    排名为空、<=0、has_rank=False 时，统一视为未覆盖/无排名，用 NaN 表示。
    注意：NaN 不等于排名很差，只表示当前数据没有有效排名。
    """
    df = df.copy()
    df[COL_XHH_HAS_RANK] = to_bool_series(df[COL_XHH_HAS_RANK])
    df[COL_YM_HAS_RANK] = to_bool_series(df[COL_YM_HAS_RANK])

    for rank_col, has_rank_col, clean_col in [
        (COL_XHH_RANK, COL_XHH_HAS_RANK, "xhh_rank_clean"),
        (COL_YM_RANK, COL_YM_HAS_RANK, "ym_rank_clean"),
    ]:
        df[clean_col] = df[rank_col]
        invalid_rank_mask = df[clean_col].isna() | (df[clean_col] <= 0) | (~df[has_rank_col])
        df.loc[invalid_rank_mask, clean_col] = np.nan

    return df


def add_demand_level(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, float]]:
    df = df.copy()
    quantiles = {
        "p50": float(df[COL_SEARCH_INDEX].quantile(0.50)),
        "p75": float(df[COL_SEARCH_INDEX].quantile(0.75)),
        "p90": float(df[COL_SEARCH_INDEX].quantile(0.90)),
        "p95": float(df[COL_SEARCH_INDEX].quantile(0.95)),
    }

    df["search_index_rank"] = df[COL_SEARCH_INDEX].rank(method="first", ascending=False).astype(int)
    df["is_top30_search_index"] = df["search_index_rank"] <= 30
    df["is_top50_search_index"] = df["search_index_rank"] <= 50

    conditions = [
        df[COL_SEARCH_INDEX] >= quantiles["p95"],
        df[COL_SEARCH_INDEX] >= quantiles["p90"],
        df[COL_SEARCH_INDEX] >= quantiles["p75"],
        df[COL_SEARCH_INDEX] >= quantiles["p50"],
    ]
    choices = ["极高搜索需求", "高搜索需求", "较高搜索需求", "中等搜索需求"]
    df["demand_level"] = np.select(conditions, choices, default="普通搜索需求")
    return df, quantiles


def get_rank_band(rank_value: Any) -> str:
    if pd.isna(rank_value):
        return "未覆盖/无排名"
    if rank_value <= 10:
        return "1-10 强可见"
    if rank_value <= 30:
        return "11-30 较强可见"
    if rank_value <= 50:
        return "31-50 中等可见"
    if rank_value <= 100:
        return "51-100 偏弱可见"
    return "100+ 弱可见"


def add_rank_bands(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["xhh_rank_band"] = df["xhh_rank_clean"].apply(get_rank_band)
    df["ym_rank_band"] = df["ym_rank_clean"].apply(get_rank_band)
    return df


def get_advantage_band(diff_value: Any) -> str:
    """
    diff = 小黑盒排名 - 游民星空排名。
    diff < 0 表示小黑盒更靠前；diff > 0 表示游民星空更靠前。
    """
    if pd.isna(diff_value):
        return "无法比较"
    if diff_value <= -50:
        return "小黑盒明显优势"
    if diff_value <= -20:
        return "小黑盒较明显优势"
    if diff_value <= -5:
        return "小黑盒轻微优势"
    if diff_value < 5:
        return "双方接近"
    if diff_value < 20:
        return "游民星空轻微优势"
    if diff_value < 50:
        return "游民星空较明显优势"
    return "游民星空明显优势"


def add_advantage_fields(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["rank_diff_xhh_minus_ym"] = df["xhh_rank_clean"] - df["ym_rank_clean"]
    df["advantage_band"] = df["rank_diff_xhh_minus_ym"].apply(get_advantage_band)
    df["advantage_side"] = np.select(
        [
            df["advantage_band"].str.startswith("小黑盒"),
            df["advantage_band"].str.startswith("游民星空"),
            df["advantage_band"] == "双方接近",
        ],
        ["小黑盒", "游民星空", "双方接近"],
        default="无法比较",
    )
    return df


# =========================================================
# 6. 关键词分类与运营转译
# =========================================================

def classify_keyword_with_rule(keyword_lower: str) -> tuple[str, str]:
    for rule in CATEGORY_RULES:
        category = rule["category"]
        for pattern in rule["patterns"]:
            if pattern.lower() in keyword_lower:
                return category, pattern
    return "其他/待复核", ""


def add_keyword_category(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    classified = df["keyword_lower"].apply(classify_keyword_with_rule)
    df["keyword_category"] = classified.apply(lambda x: x[0])
    df["matched_rule"] = classified.apply(lambda x: x[1])
    return df


def get_target_relevance(category: str) -> str:
    """
    目标相关性不再用于排除热门游戏词。
    它只是提醒：这个词更适合放在主线分析、内容/受众分析、平台竞品观察，还是人工复核。
    """
    if category == "非目标/噪声词":
        return "非目标/噪声"
    if category == "其他/待复核":
        return "待人工判断"
    if category == "品牌/竞品平台词":
        return "平台/竞品相关"
    if category in ["热门游戏/IP词", "手游/二游生态词", "泛游戏/休闲游戏词"]:
        return "内容/受众相关"
    return "核心运营相关"


def get_operation_scene(category: str) -> str:
    scene_map = {
        "品牌/竞品平台词": "平台生态/竞品观察",
        "热门游戏/IP词": "内容运营/热点游戏线索",
        "Steam/PC/主机生态词": "平台生态/玩家圈层",
        "手游/二游生态词": "内容运营/手游二游圈层",
        "攻略资讯词": "内容运营/攻略资讯",
        "社区互动词": "社区运营/互动关系",
        "工具服务词": "功能运营/工具服务",
        "交易/库存/消费信任词": "功能运营/交易消费信任",
        "活动福利词": "活动运营/福利激励",
        "内容平台/直播视频词": "内容生态/直播视频",
        "泛游戏/休闲游戏词": "泛游戏需求观察",
        "非目标/噪声词": "非目标/噪声复核",
        "其他/待复核": "待人工复核",
    }
    return scene_map.get(category, "待人工复核")


def get_operation_dimension(operation_scene: str) -> str:
    if operation_scene.startswith("内容运营") or operation_scene.startswith("内容生态"):
        return "内容运营"
    if operation_scene.startswith("社区运营"):
        return "社区运营"
    if operation_scene.startswith("功能运营"):
        return "功能/工具运营"
    if operation_scene.startswith("活动运营"):
        return "活动运营"
    if operation_scene.startswith("平台生态"):
        return "平台生态/竞品观察"
    if operation_scene.startswith("泛游戏"):
        return "受众需求背景"
    return "复核/排除"


def get_operation_clue_level(row: pd.Series) -> str:
    """
    运营线索等级主要由搜索需求热度和是否属于可解释的运营场景决定。
    注意：这里不再用“小黑盒排名靠后”作为机会判断核心，避免把分析带成 ASO。
    """
    relevance = row["target_relevance"]
    demand = row["demand_level"]

    if relevance == "非目标/噪声":
        return "不纳入运营线索"
    if relevance == "待人工判断":
        return "待人工判断"
    if demand in ["极高搜索需求", "高搜索需求"]:
        return "重点运营线索"
    if demand == "较高搜索需求":
        return "次重点运营线索"
    if demand == "中等搜索需求":
        return "补充观察"
    return "低优先观察"


def get_operation_reading(row: pd.Series) -> str:
    category = row["keyword_category"]
    if category == "热门游戏/IP词":
        return "可作为热点游戏、版本节点、攻略专题、社区话题和内容选题观察对象。"
    if category == "手游/二游生态词":
        return "可用于观察手游/二游用户圈层、版本活动、角色卡池和内容社区需求。"
    if category == "攻略资讯词":
        return "对应攻略、资讯、评测、资料库等内容供给需求。"
    if category == "社区互动词":
        return "对应玩家讨论、组队、帖子评论、社区氛围和治理相关需求。"
    if category == "工具服务词":
        return "对应战绩、账号绑定、加速器、游戏库、存档、MOD 等工具或功能服务需求。"
    if category == "交易/库存/消费信任词":
        return "对应 Steam 库存、饰品交易、退款、钱包等消费信任和工具服务需求。"
    if category == "Steam/PC/主机生态词":
        return "对应 PC、Steam、Switch、PS/Xbox、单机主机玩家圈层需求。"
    if category == "品牌/竞品平台词":
        return "对应游戏社区、资讯站、内容平台或竞品平台心智观察。"
    if category == "活动福利词":
        return "对应礼包、兑换码、抽奖、签到、奖励领取等活动运营需求。"
    if category == "内容平台/直播视频词":
        return "对应直播、视频、UP 主、弹幕和内容传播生态观察。"
    if category == "泛游戏/休闲游戏词":
        return "可作为泛游戏受众与休闲娱乐需求背景，不宜直接等同于核心社区运营机会。"
    if category == "非目标/噪声词":
        return "疑似非目标搜索词，建议从核心运营结论中排除。"
    return "未命中明确规则，建议人工复核后再决定是否纳入分析。"




def get_operation_scope(category: str) -> str:
    """
    V3.1 新增：区分核心主线、背景观察和复核/排除。
    - 核心主线：适合服务作品集里的内容运营、平台生态、社区/功能运营分析。
    - 背景观察：能说明泛游戏受众需求，但不直接作为小黑盒/游民星空核心运营线索。
    - 复核/排除：噪声或未判定词，不进入核心结论。
    """
    if category in ["非目标/噪声词", "其他/待复核"]:
        return "复核/排除"
    if category == "泛游戏/休闲游戏词":
        return "背景观察"
    return "核心主线"


def get_game_content_type(row: pd.Series) -> str:
    """
    V3.1 新增：给游戏内容线索打二级标签。
    这个字段不追求覆盖所有游戏，只用于把高搜索需求的游戏词转译成更容易解释的运营方向。
    """
    keyword_lower = row["keyword_lower"]
    category = row["keyword_category"]

    if category not in ["热门游戏/IP词", "手游/二游生态词", "攻略资讯词", "内容平台/直播视频词", "泛游戏/休闲游戏词"]:
        return ""

    if contains_any(keyword_lower, ["永杰", "永结", "永杰无间", "永恒无间", "yjwj", "yong'jie", "永jiewujian", "无限契约"]):
        return "误拼/变体词"
    if contains_any(keyword_lower, ["永劫", "勇劫", "无畏", "valorant", "瓦罗兰特", "cs2", "csgo", "pubg", "绝地求生", "和平精英", "穿越火线", "三角洲", "暗区", "彩六", "打瓦", "掌上csgo"]):
        return "竞技/射击/动作游戏"
    if contains_any(keyword_lower, ["原神", "崩铁", "星穹铁道", "鸣潮", "明日方舟", "碧蓝航线", "米哈游", "抽卡", "卡池", "二游", "角色"]):
        return "手游/二游内容"
    if contains_any(keyword_lower, ["黑神话", "塞尔达", "荒野大镖客", "艾尔登", "赛博朋克", "幽灵行者", "底特律", "奇异人生", "隐形的守护者", "飞跃13号房", "灵魂摆渡者", "暖雪", "极乐迪斯科", "野餐大冒险", "我的朋友佩德罗", "致命解药", "加拿大不归路", "艾迪芬奇", "主机"]):
        return "单机/主机/买断制游戏"
    if contains_any(keyword_lower, ["小游戏", "休闲", "消消乐", "猎鹿", "小狗爱旅行", "无忧小院", "桃源", "火锅店", "模拟器", "熊猫爱旅行", "羊羊爱吃菜", "免费游戏"]):
        return "泛游戏/休闲背景"
    if category == "攻略资讯词":
        return "攻略/资讯需求"
    if category == "内容平台/直播视频词":
        return "内容平台/直播视频"
    if category == "手游/二游生态词":
        return "手游/二游圈层"
    if category == "泛游戏/休闲游戏词":
        return "泛游戏/休闲背景"
    return "其他游戏/IP"

def add_operation_fields(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["target_relevance"] = df["keyword_category"].apply(get_target_relevance)
    df["operation_scene"] = df["keyword_category"].apply(get_operation_scene)
    df["operation_dimension"] = df["operation_scene"].apply(get_operation_dimension)
    df["operation_scope"] = df["keyword_category"].apply(get_operation_scope)
    df["game_content_type"] = df.apply(get_game_content_type, axis=1)
    df["operation_clue_level"] = df.apply(get_operation_clue_level, axis=1)
    df["operation_reading"] = df.apply(get_operation_reading, axis=1)
    df["is_operation_clue"] = df["operation_clue_level"].isin(["重点运营线索", "次重点运营线索", "补充观察"])
    df["is_core_operation_clue"] = df["is_operation_clue"] & (df["operation_scope"] == "核心主线")
    return df


# =========================================================
# 7. 辅助：双方弱可见与人工复核
# =========================================================

def get_gap_level(row: pd.Series) -> str:
    demand_level = row["demand_level"]
    xhh_rank = row["xhh_rank_clean"]
    ym_rank = row["ym_rank_clean"]

    if demand_level not in HIGH_DEMAND_LEVELS:
        return ""

    if pd.isna(xhh_rank) and pd.isna(ym_rank):
        return "双方未覆盖"

    if pd.notna(xhh_rank) and pd.notna(ym_rank):
        if xhh_rank > 100 and ym_rank > 100:
            return "双方明显弱可见"
        if xhh_rank > 50 and ym_rank > 50:
            return "双方偏弱可见"

    return ""


def add_gap_fields(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["gap_level"] = df.apply(get_gap_level, axis=1)
    df["is_both_weak_visibility"] = df["gap_level"] != ""
    return df


def build_manual_review_reason(row: pd.Series) -> str:
    reasons = []

    if row["keyword_category"] == "其他/待复核":
        reasons.append("未命中分类规则")
    if row["target_relevance"] == "待人工判断":
        reasons.append("目标相关性待判断")
    if row["target_relevance"] == "非目标/噪声" and row["demand_level"] in HIGH_DEMAND_LEVELS:
        reasons.append("高搜索指数但疑似非目标词")
    if not row["keyword_clean"]:
        reasons.append("关键词为空")
    if pd.isna(row[COL_SEARCH_INDEX]) or row[COL_SEARCH_INDEX] <= 0:
        reasons.append("搜索指数缺失或异常")
    if pd.isna(row["xhh_rank_clean"]):
        reasons.append("小黑盒无有效排名")
    if pd.isna(row["ym_rank_clean"]):
        reasons.append("游民星空无有效排名")

    return "；".join(reasons)


def add_manual_review_fields(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["manual_review_reason"] = df.apply(build_manual_review_reason, axis=1)
    df["need_manual_review"] = df["manual_review_reason"] != ""
    return df


# =========================================================
# 8. 汇总表生成
# =========================================================

def first_keywords(series: pd.Series, max_items: int = 8) -> str:
    return "、".join(series.head(max_items).astype(str).tolist())


def build_category_summary(df: pd.DataFrame) -> pd.DataFrame:
    summary = (
        df.groupby("keyword_category", dropna=False)
        .agg(
            keyword_count=("keyword_clean", "count"),
            search_index_sum=(COL_SEARCH_INDEX, "sum"),
            search_index_mean=(COL_SEARCH_INDEX, "mean"),
            search_index_median=(COL_SEARCH_INDEX, "median"),
            xhh_avg_rank=("xhh_rank_clean", "mean"),
            ym_avg_rank=("ym_rank_clean", "mean"),
            xhh_covered_count=("xhh_rank_clean", lambda x: x.notna().sum()),
            ym_covered_count=("ym_rank_clean", lambda x: x.notna().sum()),
            xhh_strong_visible_count=("xhh_rank_clean", lambda x: (x <= 10).sum()),
            ym_strong_visible_count=("ym_rank_clean", lambda x: (x <= 10).sum()),
            xhh_weak_visible_count=("xhh_rank_clean", lambda x: (x > 100).sum()),
            ym_weak_visible_count=("ym_rank_clean", lambda x: (x > 100).sum()),
        )
        .reset_index()
    )
    summary["search_index_mean"] = summary["search_index_mean"].round(2)
    summary["search_index_median"] = summary["search_index_median"].round(2)
    summary["xhh_avg_rank"] = summary["xhh_avg_rank"].round(2)
    summary["ym_avg_rank"] = summary["ym_avg_rank"].round(2)
    summary["xhh_minus_ym_avg_rank"] = (summary["xhh_avg_rank"] - summary["ym_avg_rank"]).round(2)
    return summary.sort_values(["search_index_sum", "keyword_count"], ascending=[False, False]).reset_index(drop=True)


def build_operation_scene_summary(df: pd.DataFrame) -> pd.DataFrame:
    sorted_df = df.sort_values(COL_SEARCH_INDEX, ascending=False)
    top_keyword_map = sorted_df.groupby("operation_scene")["keyword_clean"].apply(first_keywords).to_dict()

    summary = (
        df.groupby(["operation_dimension", "operation_scene"], dropna=False)
        .agg(
            keyword_count=("keyword_clean", "count"),
            search_index_sum=(COL_SEARCH_INDEX, "sum"),
            search_index_mean=(COL_SEARCH_INDEX, "mean"),
            xhh_avg_rank=("xhh_rank_clean", "mean"),
            ym_avg_rank=("ym_rank_clean", "mean"),
            top50_count=("is_top50_search_index", "sum"),
            high_demand_count=("demand_level", lambda x: x.isin(HIGH_DEMAND_LEVELS).sum()),
            core_clue_count=("is_core_operation_clue", "sum"),
        )
        .reset_index()
    )
    summary["search_index_mean"] = summary["search_index_mean"].round(2)
    summary["xhh_avg_rank"] = summary["xhh_avg_rank"].round(2)
    summary["ym_avg_rank"] = summary["ym_avg_rank"].round(2)
    summary["top_keywords"] = summary["operation_scene"].map(top_keyword_map)
    return summary.sort_values(["search_index_sum", "keyword_count"], ascending=[False, False]).reset_index(drop=True)


def build_relevance_summary(df: pd.DataFrame) -> pd.DataFrame:
    summary = (
        df.groupby("target_relevance", dropna=False)
        .agg(
            keyword_count=("keyword_clean", "count"),
            search_index_sum=(COL_SEARCH_INDEX, "sum"),
            search_index_mean=(COL_SEARCH_INDEX, "mean"),
            top50_count=("is_top50_search_index", "sum"),
            operation_clue_count=("is_operation_clue", "sum"),
        )
        .reset_index()
    )
    summary["search_index_mean"] = summary["search_index_mean"].round(2)
    return summary.sort_values(["search_index_sum", "keyword_count"], ascending=[False, False]).reset_index(drop=True)


def select_detail_columns(df: pd.DataFrame) -> pd.DataFrame:
    columns = [
        COL_KEYWORD,
        "keyword_clean",
        COL_SEARCH_INDEX,
        COL_SEARCH_RESULT_COUNT,
        COL_POPULARITY,
        COL_XHH_RANK,
        COL_YM_RANK,
        COL_XHH_HAS_RANK,
        COL_YM_HAS_RANK,
        "keyword_category",
        "matched_rule",
        "target_relevance",
        "operation_dimension",
        "operation_scene",
        "operation_scope",
        "game_content_type",
        "operation_clue_level",
        "operation_reading",
        "is_operation_clue",
        "is_core_operation_clue",
        "search_index_rank",
        "is_top30_search_index",
        "is_top50_search_index",
        "demand_level",
        "xhh_rank_clean",
        "ym_rank_clean",
        "xhh_rank_band",
        "ym_rank_band",
        "rank_diff_xhh_minus_ym",
        "advantage_side",
        "advantage_band",
        "is_both_weak_visibility",
        "gap_level",
        "need_manual_review",
        "manual_review_reason",
    ]
    return df[columns].copy()




# =========================================================
# 8.1 透明口径说明表
# =========================================================

def build_classification_rules_summary() -> pd.DataFrame:
    """输出分类规则说明，降低关键词归类的黑箱感。"""
    rows = []
    for idx, rule in enumerate(CATEGORY_RULES, start=1):
        patterns = rule.get("patterns", [])
        rows.append(
            {
                "match_priority": idx,
                "keyword_category": rule.get("category", ""),
                "pattern_count": len(patterns),
                "sample_patterns": "、".join(patterns[:12]),
                "rule_note": "按优先级从上到下匹配；命中后停止；一条关键词只进入一个主类别。",
            }
        )
    return pd.DataFrame(rows)


def build_operation_scene_definition() -> pd.DataFrame:
    """输出运营场景解释，说明哪些场景进入主图，哪些只做背景或复核。"""
    rows = [
        {
            "operation_scene": "内容运营/热点游戏线索",
            "operation_dimension": "内容运营",
            "chart_usage": "进入主图",
            "interpretation": "用于观察可转译为内容选题、版本节点、赛事节点、攻略专题和社区话题的游戏/IP词。",
        },
        {
            "operation_scene": "平台生态/玩家圈层",
            "operation_dimension": "平台生态/竞品观察",
            "chart_usage": "进入主图",
            "interpretation": "用于观察 Steam、Switch、PS/Xbox、主机/PC 玩家圈层需求。",
        },
        {
            "operation_scene": "平台生态/竞品观察",
            "operation_dimension": "平台生态/竞品观察",
            "chart_usage": "进入主图",
            "interpretation": "用于观察游戏社区、资讯站、内容平台、游戏盒子等平台心智和竞品生态。",
        },
        {
            "operation_scene": "社区运营/互动关系",
            "operation_dimension": "社区运营",
            "chart_usage": "进入主图",
            "interpretation": "用于观察社区、论坛、玩家交流等社区关系需求。",
        },
        {
            "operation_scene": "功能运营/工具服务",
            "operation_dimension": "功能/工具运营",
            "chart_usage": "进入主图",
            "interpretation": "用于观察游戏库、助手、加速器、令牌、战绩等工具服务需求。",
        },
        {
            "operation_scene": "功能运营/交易消费信任",
            "operation_dimension": "功能/工具运营",
            "chart_usage": "进入主图",
            "interpretation": "用于观察库存、饰品、交易、退款、钱包等消费信任相关需求。",
        },
        {
            "operation_scene": "内容运营/攻略资讯",
            "operation_dimension": "内容运营",
            "chart_usage": "进入主图",
            "interpretation": "用于观察攻略、资讯、新闻、评测、Wiki、资料库等内容需求。",
        },
        {
            "operation_scene": "内容运营/手游二游圈层",
            "operation_dimension": "内容运营",
            "chart_usage": "进入主图但谨慎解释",
            "interpretation": "用于观察手游、二游、抽卡、角色、卡池等圈层需求；当前样本较少，不宜过度解释。",
        },
        {
            "operation_scene": "泛游戏需求观察",
            "operation_dimension": "受众需求背景",
            "chart_usage": "不进入主图，单独作为背景",
            "interpretation": "用于观察轻量游戏、小游戏、休闲娱乐等泛需求；不直接等同于小黑盒/游民星空核心运营方向。",
        },
        {
            "operation_scene": "待人工复核",
            "operation_dimension": "复核/排除",
            "chart_usage": "不进入主图，作为数据质量说明",
            "interpretation": "用于保留未命中规则、误拼、疑似噪声或低相关词，避免强行解释。",
        },
        {
            "operation_scene": "非目标/噪声复核",
            "operation_dimension": "复核/排除",
            "chart_usage": "不进入主图，作为数据质量说明",
            "interpretation": "用于保留明显非游戏社区主题词，避免污染运营结论。",
        },
    ]
    return pd.DataFrame(rows)


def build_chart_selection_notes() -> pd.DataFrame:
    """说明每张图为什么画、选了什么、排除了什么。V3.3 只保留 3 张图。"""
    rows = [
        {
            "chart_file": "final_05_keyword_data_scope.png",
            "chart_name": "关键词样本分层说明图",
            "selected_data": "全量关键词按 operation_scope 分为核心主线、背景观察、复核/排除",
            "excluded_data": "无；该图本身用于说明数据边界",
            "purpose": "解释为什么待复核/噪声不进入主图：它们是数据质量边界，不是运营主结论。",
            "how_to_read": "核心主线用于后续结论；背景观察只说明泛游戏受众；复核/排除不强行解释。",
            "portfolio_usage": "放在关键词章节开头，作为数据口径说明。",
        },
        {
            "chart_file": "final_06_keyword_operation_support_matrix.png",
            "chart_name": "关键词运营场景支持力矩阵",
            "selected_data": "核心主线运营场景，且 core_clue_count > 0",
            "excluded_data": "待人工复核、非目标/噪声、泛游戏背景观察",
            "purpose": "回答哪些运营场景同时具备关键词数量、Top50 高需求词和搜索指数支撑。",
            "how_to_read": "越靠右=核心线索数量越多；越靠上=Top50 关键词越多；气泡越大=搜索指数总和越高。",
            "portfolio_usage": "关键词章节主图，用于支持需求结构结论。",
        },
        {
            "chart_file": "final_07_keyword_search_visibility_compare.png",
            "chart_name": "代表关键词搜索可见性对比",
            "selected_data": "由 keyword_chart_representative_terms.csv 记录的代表词",
            "excluded_data": "泛游戏、待复核、噪声、低解释价值长尾词",
            "purpose": "辅助比较小黑盒与游民星空在代表需求词下的 App Store 搜索可见性。",
            "how_to_read": "同一行两点越分散，两个 App 在该词下可见性差异越明显；排名数值越小越靠前。",
            "portfolio_usage": "放在后文作为辅助观察，不作为运营强弱或真实流量判断。",
        },
    ]
    return pd.DataFrame(rows)


def build_top30_interpretation(detail: pd.DataFrame) -> pd.DataFrame:
    """Top30 不再强行画图，而是输出解释表：哪些能进主结论，哪些只能做背景/复核。"""
    top30 = detail.sort_values("search_index_rank").head(30).copy()

    main_conclusion_keywords = {
        "小黑盒", "游民星空", "steam", "switch", "switch游戏", "蒸汽", "主机游戏", "主机",
        "永劫无间", "永劫无间手游", "无畏契约", "瓦罗兰特", "游戏社区", "游戏论坛",
        "游戏库", "游戏饰品", "游戏攻略", "游戏新闻", "黑神话悟空", "荒野大镖客",
    }

    def conclusion_usage(row: pd.Series) -> str:
        keyword = row["keyword_clean"]
        if row["operation_scope"] == "核心主线" and row["is_core_operation_clue"]:
            if keyword in main_conclusion_keywords:
                return "主结论代表词"
            return "辅助观察词"
        if row["operation_scope"] == "背景观察":
            return "仅作受众背景"
        return "复核/不进主结论"

    def why(row: pd.Series) -> str:
        usage = conclusion_usage(row)
        if usage == "主结论代表词":
            return "该词搜索指数靠前，且能直接支撑平台生态、热门游戏内容、社区功能或工具交易等主线结论。"
        if usage == "辅助观察词":
            return "该词属于核心主线，但代表性或可解释性弱于主结论代表词，更适合作为补充样例或竞品/内容生态观察。"
        if row["operation_scope"] == "背景观察":
            return "泛游戏/休闲娱乐需求可说明搜索样本背景，但不直接等同于小黑盒或游民星空的核心运营方向。"
        if row["keyword_category"] == "非目标/噪声词":
            return "疑似非目标搜索词，保留用于数据质量说明，不写入运营主结论。"
        return "未命中明确运营规则或相关性不足，建议人工复核后再解释。"

    keep_cols = [
        "keyword_clean", COL_SEARCH_INDEX, "search_index_rank", "keyword_category", "matched_rule",
        "operation_scene", "operation_scope", "demand_level", "xhh_rank_clean", "ym_rank_clean",
    ]
    out = top30[keep_cols].copy()
    out["conclusion_usage"] = top30.apply(conclusion_usage, axis=1)
    out["why"] = top30.apply(why, axis=1)
    return out


def build_classification_examples(detail: pd.DataFrame, max_examples: int = 8) -> pd.DataFrame:
    """每个分类给出样例，方便人工检查分类是否黑箱。"""
    rows = []
    sort_df = detail.sort_values(COL_SEARCH_INDEX, ascending=False).copy()
    for category, sub in sort_df.groupby("keyword_category", dropna=False):
        rows.append(
            {
                "keyword_category": category,
                "example_keywords": "、".join(sub["keyword_clean"].head(max_examples).tolist()),
                "matched_rules": "、".join([x for x in sub["matched_rule"].dropna().astype(str).unique().tolist() if x][:max_examples]),
                "operation_scene": "、".join(sub["operation_scene"].dropna().astype(str).unique().tolist()),
                "operation_scope": "、".join(sub["operation_scope"].dropna().astype(str).unique().tolist()),
                "note": "样例按搜索指数降序截取，用于人工检查规则是否符合运营理解；样例不等同于最终作品集代表词，写作时需结合 operation_scope 和 conclusion_usage 进一步筛选。",
            }
        )
    return pd.DataFrame(rows).sort_values("keyword_category").reset_index(drop=True)


def build_chart_representative_terms(detail: pd.DataFrame) -> pd.DataFrame:
    """选择可见性对比图代表词，并把选择规则输出成表，避免“随便挑词”。"""
    selection_plan = [
        ("steam", "平台生态 Top 搜索指数", "Steam/PC 玩家圈层代表词；与小黑盒工具、游戏库和社区心智相关。"),
        ("switch", "平台生态 Top 搜索指数", "Switch/主机玩家圈层代表词；用于观察主机内容需求。"),
        ("主机游戏", "平台生态强相关词", "主机/PC 圈层需求代表词。"),
        ("掌上steam", "平台生态强相关词", "Steam 工具/移动端使用场景代表词。"),
        ("小黑盒", "品牌/平台心智代表词", "本项目主分析对象之一。"),
        ("游民星空", "品牌/平台心智代表词", "本项目对比对象之一。"),
        ("游侠", "竞品平台代表词", "游戏资讯/攻略平台心智代表词。"),
        ("永劫无间", "热点游戏 Top 搜索指数", "竞技/动作游戏内容和社区话题代表词。"),
        ("无畏契约", "竞技/射击内容代表词", "竞技游戏内容、攻略、社区讨论代表词。"),
        ("黑神话悟空", "单机/主机热点代表词", "单机/买断制游戏热点内容代表词。"),
        ("荒野大镖客", "单机/主机内容代表词", "单机内容、攻略和评测需求代表词。"),
        ("游戏社区", "社区功能强相关词", "社区关系和玩家交流需求代表词。"),
        ("游戏论坛", "社区功能强相关词", "论坛/讨论场景代表词。"),
        ("游戏库", "工具服务强相关词", "游戏资产管理/工具服务代表词。"),
        ("游戏攻略", "攻略资讯强相关词", "攻略内容供给代表词。"),
        ("游戏饰品", "交易/库存强相关词", "饰品、库存和消费信任相关需求代表词。"),
    ]
    rows = []
    for keyword, rule, why in selection_plan:
        sub = detail[detail["keyword_clean"] == keyword]
        if sub.empty:
            continue
        row = sub.iloc[0].to_dict()
        if not row.get("is_core_operation_clue", False):
            continue
        rows.append(
            {
                "chart_file": "final_07_keyword_search_visibility_compare.png",
                "keyword_clean": row["keyword_clean"],
                "search_index": row[COL_SEARCH_INDEX],
                "keyword_category": row["keyword_category"],
                "operation_scene": row["operation_scene"],
                "selection_rule": rule,
                "why_selected": why,
                "xhh_rank_clean": row["xhh_rank_clean"],
                "ym_rank_clean": row["ym_rank_clean"],
                "advantage_band": row["advantage_band"],
            }
        )
    out = pd.DataFrame(rows)
    if out.empty:
        fallback = detail[detail["is_core_operation_clue"]].sort_values(COL_SEARCH_INDEX, ascending=False).head(14).copy()
        out = fallback.assign(
            chart_file="final_07_keyword_search_visibility_compare.png",
            selection_rule="核心运营线索搜索指数靠前",
            why_selected="自动兜底选择：核心运营线索中搜索指数靠前。",
        )[[
            "chart_file", "keyword_clean", COL_SEARCH_INDEX, "keyword_category", "operation_scene",
            "selection_rule", "why_selected", "xhh_rank_clean", "ym_rank_clean", "advantage_band",
        ]].rename(columns={COL_SEARCH_INDEX: "search_index"})
    return out.head(16).reset_index(drop=True)


def build_output_file_inventory() -> pd.DataFrame:
    """说明哪些文件是正式输出、哪些是实验/辅助、哪些旧文件已废弃。"""
    rows = [
        ("正式主表", "keyword_analysis_detail.csv", "全量关键词分析明细，供追溯每个词的分类、场景、排名和人工复核标记。"),
        ("正式主表", "keyword_core_operation_clues.csv", "核心运营线索总表，排除了泛游戏背景和复核/噪声词。"),
        ("正式主表", "keyword_core_game_content_clues.csv", "核心内容运营/热点游戏线索。"),
        ("正式主表", "keyword_core_platform_ecology_clues.csv", "核心平台生态/竞品观察线索。"),
        ("正式主表", "keyword_core_community_function_clues.csv", "社区、攻略、工具、交易等强相关线索。"),
        ("背景观察", "keyword_audience_background_clues.csv", "泛游戏/休闲娱乐需求背景，不进入核心运营主结论。"),
        ("透明说明", "keyword_top30_interpretation.csv", "Top30 逐词解释表，区分主结论代表词、辅助观察词、背景和复核。"),
        ("透明说明", "keyword_classification_examples.csv", "分类样例表，用于降低规则分类黑箱感；样例不等于最终代表词。"),
        ("透明说明", "keyword_chart_representative_terms.csv", "图 7 代表词选择说明表。"),
        ("透明说明", "keyword_chart_selection_notes.csv", "三张图的选数、排除项和使用位置说明。"),
        ("辅助观察", "xhh_keyword_advantage.csv", "小黑盒搜索可见性相对更靠前的关键词，仅作辅助。"),
        ("辅助观察", "ym_keyword_advantage.csv", "游民星空搜索可见性相对更靠前的关键词，仅作辅助。"),
        ("辅助观察", "keyword_gap_list.csv", "高需求下双方搜索可见性都相对偏弱的词，不等于双方空白。"),
        ("复核/排除", "keyword_manual_review.csv", "需要人工复核的词。"),
        ("复核/排除", "keyword_noise_review.csv", "疑似噪声和待人工判断词。"),
        ("正式图表", "final_05_keyword_data_scope.png", "关键词样本分层说明图，解释核心/背景/复核边界。"),
        ("正式图表", "final_06_keyword_operation_support_matrix.png", "关键词运营场景支持力矩阵，关键词章节主图。"),
        ("辅助图表", "final_07_keyword_search_visibility_compare.png", "代表关键词搜索可见性辅助对比图。"),
        ("废弃历史", "deprecated_*", "旧图旧表或容易误导的 ASO/柱状图口径，文件名前缀已标记废弃。"),
        ("实验历史", "experimental_*", "曾用于探索但不作为当前主线结论的中间文件。"),
    ]
    return pd.DataFrame(rows, columns=["file_role", "file_name", "description"])

def build_output_tables(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    detail = select_detail_columns(df).sort_values("search_index_rank")
    top30 = detail.head(30).copy()
    top50 = detail.head(50).copy()

    category_summary = build_category_summary(df)
    operation_scene_summary = build_operation_scene_summary(df)
    relevance_summary = build_relevance_summary(df)

    xhh_advantage = detail[detail["advantage_side"] == "小黑盒"].copy()
    xhh_advantage["advantage_abs"] = xhh_advantage["rank_diff_xhh_minus_ym"].abs()
    xhh_advantage = xhh_advantage.sort_values([COL_SEARCH_INDEX, "advantage_abs"], ascending=[False, False]).drop(columns=["advantage_abs"])

    ym_advantage = detail[detail["advantage_side"] == "游民星空"].copy()
    ym_advantage["advantage_abs"] = ym_advantage["rank_diff_xhh_minus_ym"].abs()
    ym_advantage = ym_advantage.sort_values([COL_SEARCH_INDEX, "advantage_abs"], ascending=[False, False]).drop(columns=["advantage_abs"])

    operation_clues = detail[
        detail["operation_clue_level"].isin(["重点运营线索", "次重点运营线索", "补充观察"])
    ].copy()
    clue_order = {"重点运营线索": 1, "次重点运营线索": 2, "补充观察": 3}
    operation_clues["clue_order"] = operation_clues["operation_clue_level"].map(clue_order)
    operation_clues = operation_clues.sort_values(["clue_order", COL_SEARCH_INDEX], ascending=[True, False]).drop(columns=["clue_order"])

    core_operation_clues = detail[detail["is_core_operation_clue"]].copy()
    core_operation_clues["clue_order"] = core_operation_clues["operation_clue_level"].map(clue_order)
    core_operation_clues = core_operation_clues.sort_values(["clue_order", COL_SEARCH_INDEX], ascending=[True, False]).drop(columns=["clue_order"])

    game_content_clues = operation_clues[
        operation_clues["keyword_category"].isin([
            "热门游戏/IP词", "手游/二游生态词", "攻略资讯词", "内容平台/直播视频词", "泛游戏/休闲游戏词",
        ])
    ].copy()

    platform_ecology_clues = operation_clues[
        operation_clues["keyword_category"].isin([
            "品牌/竞品平台词", "Steam/PC/主机生态词", "内容平台/直播视频词",
        ])
    ].copy()

    community_function_clues = operation_clues[
        operation_clues["keyword_category"].isin([
            "社区互动词", "工具服务词", "交易/库存/消费信任词", "活动福利词", "攻略资讯词",
        ])
    ].copy()

    core_game_content_clues = core_operation_clues[
        core_operation_clues["keyword_category"].isin([
            "热门游戏/IP词", "手游/二游生态词", "攻略资讯词", "内容平台/直播视频词",
        ])
    ].copy()

    core_platform_ecology_clues = core_operation_clues[
        core_operation_clues["keyword_category"].isin([
            "品牌/竞品平台词", "Steam/PC/主机生态词", "内容平台/直播视频词",
        ])
    ].copy()

    core_community_function_clues = core_operation_clues[
        core_operation_clues["keyword_category"].isin([
            "社区互动词", "工具服务词", "交易/库存/消费信任词", "活动福利词", "攻略资讯词",
        ])
    ].copy()

    audience_background_clues = operation_clues[
        operation_clues["keyword_category"].isin(["泛游戏/休闲游戏词"])
    ].copy()

    gap = detail[detail["is_both_weak_visibility"]].copy()
    gap_order = {"双方未覆盖": 1, "双方明显弱可见": 2, "双方偏弱可见": 3}
    gap["gap_order"] = gap["gap_level"].map(gap_order)
    gap = gap.sort_values(["gap_order", COL_SEARCH_INDEX], ascending=[True, False]).drop(columns=["gap_order"])

    manual_review = detail[detail["need_manual_review"]].copy().sort_values(["manual_review_reason", COL_SEARCH_INDEX], ascending=[True, False])
    noise_review = detail[detail["target_relevance"].isin(["非目标/噪声", "待人工判断"])].copy().sort_values(COL_SEARCH_INDEX, ascending=False)

    classification_rules_summary = build_classification_rules_summary()
    operation_scene_definition = build_operation_scene_definition()
    chart_selection_notes = build_chart_selection_notes()
    top30_interpretation = build_top30_interpretation(detail)
    classification_examples = build_classification_examples(detail)
    chart_representative_terms = build_chart_representative_terms(detail)

    return {
        "keyword_analysis_detail.csv": detail,
        "keyword_top_search_index.csv": top30,
        "keyword_top50_search_index.csv": top50,
        "keyword_category_summary.csv": category_summary,
        "keyword_operation_scene_summary.csv": operation_scene_summary,
        "keyword_relevance_summary.csv": relevance_summary,
        "xhh_keyword_advantage.csv": xhh_advantage,
        "ym_keyword_advantage.csv": ym_advantage,
        "keyword_operation_clues.csv": operation_clues,
        "keyword_core_operation_clues.csv": core_operation_clues,
        "keyword_game_content_clues.csv": game_content_clues,
        "keyword_core_game_content_clues.csv": core_game_content_clues,
        "keyword_platform_ecology_clues.csv": platform_ecology_clues,
        "keyword_core_platform_ecology_clues.csv": core_platform_ecology_clues,
        "keyword_community_function_clues.csv": community_function_clues,
        "keyword_core_community_function_clues.csv": core_community_function_clues,
        "keyword_audience_background_clues.csv": audience_background_clues,
        "keyword_gap_list.csv": gap,
        "keyword_noise_review.csv": noise_review,
        "keyword_manual_review.csv": manual_review,
        "keyword_classification_rules_summary.csv": classification_rules_summary,
        "keyword_operation_scene_definition.csv": operation_scene_definition,
        "keyword_chart_selection_notes.csv": chart_selection_notes,
        "keyword_top30_interpretation.csv": top30_interpretation,
        "keyword_classification_examples.csv": classification_examples,
        "keyword_chart_representative_terms.csv": chart_representative_terms,
        "keyword_output_file_inventory.csv": build_output_file_inventory(),
    }


def save_tables(tables: dict[str, pd.DataFrame]) -> None:
    for filename, table in tables.items():
        table.to_csv(OUTPUT_TABLE_DIR / filename, index=False, encoding="utf-8-sig")


# =========================================================
# 9. 图表输出
#
# V3.3 图表原则：
# - 不再为了画图而画图。
# - 主图不展示“待人工复核/非目标噪声”的大块占比，避免噪声淹没运营信息。
# - 复核/噪声单独用“数据分层说明卡”呈现，作为数据边界，而不是运营结论。
# - 图表控制在 3 张以内；Top30 改为解释表，不再为了“有图”而画图。
# =========================================================

def short_label(text: str, max_len: int = 12) -> str:
    text = str(text)
    return text if len(text) <= max_len else text[:max_len] + "…"


def plot_data_scope(operation_scene_summary: pd.DataFrame) -> None:
    """图 1：关键词样本分层说明图。用于解释待复核为什么不进入主结论。"""
    summary = operation_scene_summary.copy()
    total_keywords = int(summary["keyword_count"].sum())
    total_search_index = int(summary["search_index_sum"].sum())

    core_mask = (summary["core_clue_count"] > 0) & (~summary["operation_dimension"].isin(["复核/排除", "受众需求背景"]))
    background_mask = summary["operation_dimension"].isin(["受众需求背景"])
    review_mask = summary["operation_dimension"].isin(["复核/排除"])

    scope_rows = [
        {
            "scope": "核心主线",
            "keyword_count": int(summary.loc[core_mask, "core_clue_count"].sum()),
            "search_index_sum": int(summary.loc[core_mask, "search_index_sum"].sum()),
            "usage": "进入主结论：平台生态、热点游戏、竞品平台、社区/工具/交易/攻略。",
        },
        {
            "scope": "背景观察",
            "keyword_count": int(summary.loc[background_mask, "keyword_count"].sum()),
            "search_index_sum": int(summary.loc[background_mask, "search_index_sum"].sum()),
            "usage": "仅作受众背景：小游戏、休闲游戏、泛游戏需求。",
        },
        {
            "scope": "复核/排除",
            "keyword_count": int(summary.loc[review_mask, "keyword_count"].sum()),
            "search_index_sum": int(summary.loc[review_mask, "search_index_sum"].sum()),
            "usage": "不进主结论：待复核、非目标词、噪声词。",
        },
    ]

    plt.figure(figsize=(11, 6.5))
    plt.axis("off")
    plt.title("关键词样本分层：先解释数据边界，再讨论运营线索", loc="left", fontsize=15, fontweight="bold")

    y = 0.84
    plt.text(0.02, 0.93, f"全量关键词：{total_keywords} 个｜搜索指数总和：{total_search_index:,}", fontsize=11)
    for row in scope_rows:
        pct = row["keyword_count"] / total_keywords * 100 if total_keywords else 0
        line1 = f"{row['scope']}：{row['keyword_count']} 个关键词（{pct:.1f}%）｜搜索指数总和 {row['search_index_sum']:,}"
        plt.text(0.04, y, line1, fontsize=13, fontweight="bold", va="top")
        plt.text(0.07, y - 0.07, row["usage"], fontsize=10.5, va="top")
        y -= 0.20

    plt.figtext(
        0.02,
        0.03,
        "图表用途：这张图不是运营结论，而是说明为什么不把大块“待人工复核/噪声”画进主图，避免把低相关词强行解释。",
        ha="left",
        fontsize=9,
    )
    plt.tight_layout(rect=[0, 0.05, 1, 1])
    plt.savefig(OUTPUT_CHART_DIR / "final_05_keyword_data_scope.png", dpi=180)
    plt.close()


def plot_operation_support_matrix(operation_scene_summary: pd.DataFrame) -> None:
    """图 2：核心运营场景支持力矩阵。"""
    chart_df = operation_scene_summary.copy()
    chart_df = chart_df[
        (chart_df["core_clue_count"] > 0)
        & (~chart_df["operation_dimension"].isin(["复核/排除", "受众需求背景"]))
    ].copy()

    if chart_df.empty:
        return

    chart_df = chart_df.sort_values("search_index_sum", ascending=False).reset_index(drop=True)
    chart_df["scene_code"] = np.arange(1, len(chart_df) + 1)
    max_sum = chart_df["search_index_sum"].max()
    sizes = 260 + 1300 * chart_df["search_index_sum"] / max_sum

    plt.figure(figsize=(12, 8))
    plt.scatter(chart_df["core_clue_count"], chart_df["top50_count"], s=sizes, alpha=0.65)

    for _, row in chart_df.iterrows():
        plt.text(row["core_clue_count"], row["top50_count"], str(int(row["scene_code"])), fontsize=11, ha="center", va="center")

    legend_lines = []
    for _, row in chart_df.iterrows():
        legend_lines.append(
            f"{int(row['scene_code'])}. {row['operation_scene']}：核心词 {int(row['core_clue_count'])}，Top50 {int(row['top50_count'])}，搜索指数 {int(row['search_index_sum']):,}"
        )
    plt.text(0.02, 0.98, "\n".join(legend_lines), transform=plt.gca().transAxes, fontsize=8.5, va="top", ha="left")

    plt.xlabel("核心运营线索数量")
    plt.ylabel("搜索指数 Top50 中的关键词数量")
    plt.title("关键词运营场景支持力矩阵：哪些方向更有数据支撑", fontsize=14)
    plt.figtext(
        0.01,
        0.01,
        "读法：越靠右=核心线索数量越多；越靠上=Top50 关键词越多；气泡越大=搜索指数总和越高。待复核/噪声/泛游戏背景不进入该主图。",
        ha="left",
        fontsize=9,
    )
    plt.grid(True, linestyle="--", linewidth=0.5, alpha=0.35)
    plt.tight_layout(rect=[0, 0.07, 1, 1])
    plt.savefig(OUTPUT_CHART_DIR / "final_06_keyword_operation_support_matrix.png", dpi=180)
    plt.close()


def plot_search_visibility_compare(representative_terms: pd.DataFrame) -> None:
    """图 3：代表关键词搜索可见性对比。代表词来源见 keyword_chart_representative_terms.csv。"""
    chart_df = representative_terms.copy()
    if chart_df.empty:
        return

    # 为避免标签拥挤，最多展示 16 个代表词；按选择表顺序保留。
    chart_df = chart_df.head(16).copy()
    chart_df = chart_df.sort_values("search_index", ascending=True).copy()
    y = np.arange(len(chart_df))

    plt.figure(figsize=(11, 8.5))
    for i, (_, row) in enumerate(chart_df.iterrows()):
        plt.plot([row["xhh_rank_clean"], row["ym_rank_clean"]], [i, i], linewidth=1.2, color="#B0B0B0", alpha=0.85)

    plt.scatter(chart_df["xhh_rank_clean"], y, label="小黑盒排名", s=55, color="#1f77b4")
    plt.scatter(chart_df["ym_rank_clean"], y, label="游民星空排名", s=55, color="#ff7f0e")

    plt.yticks(y, chart_df["keyword_clean"])
    plt.xlabel("关键词排名（数值越小，可见性越靠前）")
    plt.ylabel("代表关键词")
    plt.title("代表关键词搜索可见性对比：小黑盒 vs 游民星空", fontsize=14)
    plt.legend(loc="lower right")
    plt.grid(True, axis="x", linestyle="--", linewidth=0.5, alpha=0.35)
    plt.figtext(
        0.01,
        0.01,
        "读法：同一行两点越分散，两个 App 在该关键词下的搜索可见性差异越明显；该图只做辅助观察，不代表真实流量或运营强弱。代表词选择规则见 keyword_chart_representative_terms.csv。",
        ha="left",
        fontsize=9,
    )
    plt.tight_layout(rect=[0, 0.06, 1, 1])
    plt.savefig(OUTPUT_CHART_DIR / "final_07_keyword_search_visibility_compare.png", dpi=180)
    plt.close()


def save_charts(tables: dict[str, pd.DataFrame]) -> None:
    set_chinese_font()
    plot_data_scope(tables["keyword_operation_scene_summary.csv"])
    plot_operation_support_matrix(tables["keyword_operation_scene_summary.csv"])
    plot_search_visibility_compare(tables["keyword_chart_representative_terms.csv"])


# =========================================================
# 10. Markdown 报告
# =========================================================

def df_to_markdown_table(df: pd.DataFrame, columns: list[str], max_rows: int = 10) -> str:
    if df.empty:
        return "暂无数据。"
    view = df[columns].head(max_rows).copy().fillna("")
    header = "| " + " | ".join(columns) + " |"
    separator = "| " + " | ".join(["---"] * len(columns)) + " |"
    rows = []
    for _, row in view.iterrows():
        rows.append("| " + " | ".join(str(row[col]) for col in columns) + " |")
    return "\n".join([header, separator] + rows)


def build_review_alignment_summary(df: pd.DataFrame) -> pd.DataFrame:
    records = []
    for theme, patterns in REVIEW_ALIGNMENT_THEMES.items():
        mask = pd.Series(False, index=df.index)
        for pattern in patterns:
            mask = mask | df["keyword_lower"].str.contains(pattern.lower(), regex=False, na=False)
        sub = df[mask].sort_values(COL_SEARCH_INDEX, ascending=False)
        records.append(
            {
                "theme": theme,
                "keyword_count": int(len(sub)),
                "search_index_sum": int(sub[COL_SEARCH_INDEX].sum()) if not sub.empty else 0,
                "top_keywords": "、".join(sub["keyword_clean"].head(6).tolist()),
            }
        )
    return pd.DataFrame(records).sort_values(["keyword_count", "search_index_sum"], ascending=[False, False])


def build_markdown_report(
    df: pd.DataFrame,
    tables: dict[str, pd.DataFrame],
    quantiles: dict[str, float],
) -> str:
    detail = tables["keyword_analysis_detail.csv"]
    top50 = tables["keyword_top50_search_index.csv"]
    category_summary = tables["keyword_category_summary.csv"]
    scene_summary = tables["keyword_operation_scene_summary.csv"]
    relevance_summary = tables["keyword_relevance_summary.csv"]
    operation_clues = tables["keyword_operation_clues.csv"]
    core_operation_clues = tables["keyword_core_operation_clues.csv"]
    game_content_clues = tables["keyword_game_content_clues.csv"]
    core_game_content_clues = tables["keyword_core_game_content_clues.csv"]
    platform_clues = tables["keyword_platform_ecology_clues.csv"]
    core_platform_clues = tables["keyword_core_platform_ecology_clues.csv"]
    community_function_clues = tables["keyword_community_function_clues.csv"]
    core_community_function_clues = tables["keyword_core_community_function_clues.csv"]
    audience_background_clues = tables["keyword_audience_background_clues.csv"]
    xhh_advantage = tables["xhh_keyword_advantage.csv"]
    ym_advantage = tables["ym_keyword_advantage.csv"]
    gap = tables["keyword_gap_list.csv"]
    manual_review = tables["keyword_manual_review.csv"]

    total_keywords = len(detail)
    manual_count = len(manual_review)
    top_keywords_text = "、".join(top50["keyword_clean"].head(10).tolist())
    review_alignment = build_review_alignment_summary(df)

    report = f"""# 关键词需求与运营线索分析摘要

## 1. 数据说明与口径限制

- 输入文件：`data/cleaned/cleaned_keywords.csv`
- 样本量：{total_keywords} 个关键词
- 核心字段：`keyword`、`search_index`、`search_result_count`、`popularity`、`xhh_rank`、`ym_rank`
- 搜索指数：仅作为 App Store 搜索场景下的需求热度观察，不等同于真实下载量或真实用户规模。
- 关键词排名：仅作为 App Store 搜索可见性的辅助对比，排名数值越小，可见性越靠前。
- 分析目标：本报告不做 ASO 投放建议，而是把关键词转译为游戏社区 App 的内容运营、社区运营、功能/工具运营、活动运营、平台生态与竞品观察线索。

搜索指数分位数：P50={quantiles['p50']:.0f}，P75={quantiles['p75']:.0f}，P90={quantiles['p90']:.0f}，P95={quantiles['p95']:.0f}。

## 2. 搜索指数 Top 关键词观察

搜索指数 Top 关键词包括：{top_keywords_text}。

这些词不直接代表下载量，而是帮助观察用户在公开搜索场景中可能关注的游戏、平台、工具、内容或社区需求。

{df_to_markdown_table(top50, ['keyword_clean', COL_SEARCH_INDEX, 'keyword_category', 'operation_scene', 'xhh_rank_clean', 'ym_rank_clean', 'demand_level'], 15)}

## 3. 关键词类别需求结构

{df_to_markdown_table(category_summary, ['keyword_category', 'keyword_count', 'search_index_sum', 'search_index_mean', 'xhh_avg_rank', 'ym_avg_rank'], 20)}

## 4. 运营线索结构

下表把关键词类别进一步转译为运营场景。相比单纯看“排名机会”，这部分更适合服务游戏社区运营分析。

{df_to_markdown_table(scene_summary, ['operation_dimension', 'operation_scene', 'keyword_count', 'search_index_sum', 'top50_count', 'high_demand_count', 'top_keywords'], 20)}

## 5. 目标相关性结构

{df_to_markdown_table(relevance_summary, ['target_relevance', 'keyword_count', 'search_index_sum', 'top50_count', 'operation_clue_count'], 10)}

## 6. 内容运营与热点游戏线索

这些词主要用于观察热门游戏、IP、手游/二游、攻略资讯和内容平台需求，可服务选题、专题、版本节点、攻略内容和社区话题策划。V3.1 中，泛游戏/休闲游戏词被单独降级为“受众背景”，不与核心内容线索混写。

### 核心内容运营线索

{df_to_markdown_table(core_game_content_clues, ['keyword_clean', COL_SEARCH_INDEX, 'keyword_category', 'game_content_type', 'operation_scene', 'operation_clue_level', 'operation_reading'], 20)}

### 泛游戏/休闲背景观察

{df_to_markdown_table(audience_background_clues, ['keyword_clean', COL_SEARCH_INDEX, 'keyword_category', 'game_content_type', 'operation_scene', 'operation_clue_level'], 12)}

## 7. 平台生态与竞品观察线索

这些词主要用于观察小黑盒、游民星空、Steam、Switch、主机/PC、TapTap、好游快爆、游侠、3DM、B站游戏等生态心智。

{df_to_markdown_table(core_platform_clues, ['keyword_clean', COL_SEARCH_INDEX, 'keyword_category', 'operation_scene', 'operation_clue_level', 'operation_reading'], 20)}

## 8. 社区、功能与活动运营线索

这些词主要对应社区互动、攻略资讯、战绩/账号/绑定/加速器/库存/交易/退款、活动福利等方向。后续可与评论分析中的具体问题建立交叉观察。

{df_to_markdown_table(core_community_function_clues, ['keyword_clean', COL_SEARCH_INDEX, 'keyword_category', 'operation_scene', 'operation_clue_level', 'operation_reading'], 20)}

## 9. 小黑盒与游民星空搜索可见性辅助对比

以下排名优势仅表示 App Store 搜索可见性相对更靠前，不代表真实流量、产品能力或运营效果更强。

### 小黑盒相对更靠前的关键词

{df_to_markdown_table(xhh_advantage, ['keyword_clean', COL_SEARCH_INDEX, 'keyword_category', 'operation_scene', 'xhh_rank_clean', 'ym_rank_clean', 'advantage_band'], 12)}

### 游民星空相对更靠前的关键词

{df_to_markdown_table(ym_advantage, ['keyword_clean', COL_SEARCH_INDEX, 'keyword_category', 'operation_scene', 'xhh_rank_clean', 'ym_rank_clean', 'advantage_band'], 12)}

## 10. 双方弱可见关键词辅助观察

`keyword_gap_list.csv` 仍然保留，但建议解释为“高搜索需求下双方搜索可见性都相对偏弱的关键词”，而不是“双方空白词”。

{df_to_markdown_table(gap, ['keyword_clean', COL_SEARCH_INDEX, 'keyword_category', 'operation_scene', 'xhh_rank_clean', 'ym_rank_clean', 'gap_level'], 20)}

## 11. 与评论分析的交叉观察

评论专项中出现过 Steam、社区、攻略、活动、交易、退款、客服、工具、加速器、登录/绑定等主题。关键词侧如果也出现这些主题，可以谨慎表述为“需求侧和反馈侧存在交叉观察点”。

{df_to_markdown_table(review_alignment, ['theme', 'keyword_count', 'search_index_sum', 'top_keywords'], 20)}

## 12. 人工复核提醒

本次需要人工复核的关键词数量：{manual_count}。主要包括未命中分类规则、疑似非目标词、或目标相关性待判断的关键词。建议优先复核高搜索指数但被标记为“非目标/噪声”或“其他/待复核”的词。

## 13. 输出文件说明

- `keyword_analysis_detail.csv`：关键词分析总明细表。
- `keyword_top_search_index.csv`：搜索指数 Top 30 原始表。
- `keyword_top30_interpretation.csv`：Top30 解释表，标注主结论代表词/辅助观察词/仅作背景/复核排除。
- `keyword_top50_search_index.csv`：搜索指数 Top 50。
- `keyword_category_summary.csv`：关键词类别需求结构汇总。
- `keyword_operation_scene_summary.csv`：运营线索场景汇总。
- `keyword_relevance_summary.csv`：目标相关性结构汇总。
- `keyword_operation_clues.csv`：运营需求线索总表，包含核心主线和背景观察。
- `keyword_core_operation_clues.csv`：核心运营线索表，排除了泛游戏背景和复核/噪声词。
- `keyword_game_content_clues.csv`：内容运营与热点游戏线索，含泛游戏背景。
- `keyword_core_game_content_clues.csv`：核心内容运营与热点游戏线索。
- `keyword_platform_ecology_clues.csv`：平台生态与竞品观察线索。
- `keyword_core_platform_ecology_clues.csv`：核心平台生态与竞品观察线索。
- `keyword_community_function_clues.csv`：社区、功能与活动运营线索。
- `keyword_core_community_function_clues.csv`：核心社区、功能与活动运营线索。
- `keyword_audience_background_clues.csv`：泛游戏/休闲游戏需求背景。
- `xhh_keyword_advantage.csv` / `ym_keyword_advantage.csv`：搜索可见性辅助对比。
- `keyword_gap_list.csv`：高需求下双方相对弱可见词。
- `keyword_noise_review.csv`：疑似噪声和待复核词。
- `keyword_manual_review.csv`：人工复核表。
- `keyword_classification_rules_summary.csv`：分类规则说明表。
- `keyword_classification_examples.csv`：分类样例表，用于人工检查分类规则。
- `keyword_chart_selection_notes.csv`：图表选择口径说明。
- `keyword_chart_representative_terms.csv`：代表关键词选择说明表。
- `keyword_output_file_inventory.csv`：输出文件清单，说明正式、辅助、背景、实验、废弃文件的用途。
- `deprecated_*`：历史废弃文件，通常是旧 ASO/旧柱状图/容易误导的口径。
- `experimental_*`：历史实验文件，有参考价值但不作为当前主线输出。
"""
    return report


def save_report(df: pd.DataFrame, tables: dict[str, pd.DataFrame], quantiles: dict[str, float]) -> None:
    report = build_markdown_report(df, tables, quantiles)
    (OUTPUT_REPORT_DIR / "keyword_analysis_summary.md").write_text(report, encoding="utf-8")


# =========================================================
# 11. 主流程
# =========================================================

def main() -> None:
    ensure_output_dirs()
    legacy_output_log = label_legacy_outputs()

    df = read_keywords_data(INPUT_FILE)
    check_required_columns(df)

    df = clean_keyword_text(df)
    df = convert_numeric_columns(df)
    df = normalize_rank_columns(df)
    df, quantiles = add_demand_level(df)
    df = add_rank_bands(df)
    df = add_advantage_fields(df)
    df = add_keyword_category(df)
    df = add_operation_fields(df)
    df = add_gap_fields(df)
    df = add_manual_review_fields(df)

    tables = build_output_tables(df)
    tables["keyword_legacy_output_cleanup_log.csv"] = legacy_output_log
    save_tables(tables)
    save_charts(tables)
    save_report(df, tables, quantiles)

    print("关键词需求与运营线索分析完成。")
    print(f"输入文件：{INPUT_FILE}")
    print(f"输出表格目录：{OUTPUT_TABLE_DIR}")
    print(f"输出图表目录：{OUTPUT_CHART_DIR}")
    print(f"输出报告目录：{OUTPUT_REPORT_DIR}")
    print("核心输出：")
    for filename in tables.keys():
        print(f"- {OUTPUT_TABLE_DIR / filename}")
    print(f"- {OUTPUT_REPORT_DIR / 'keyword_analysis_summary.md'}")


if __name__ == "__main__":
    main()