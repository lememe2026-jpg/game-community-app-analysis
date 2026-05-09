# -*- coding: utf-8 -*-
"""
版本节奏专项分析脚本（07 修正版）

用途：
1. 读取 data/cleaned/cleaned_versions.csv；
2. 生成版本节奏统计、版本日志文本处理、四源整合候选节点；
3. 重画 final_12，不再把全年版本号堆在同一张图上。

运行方式：
    python scripts/07_analyze_versions.py

可选参数：
    python scripts/07_analyze_versions.py --input data/cleaned/cleaned_versions.csv

注意边界：
- 版本日志只作为公开版本动作背景；
- 不判断版本导致下载增长；
- 不判断版本解决评论问题；
- 不用“修复已知问题”强行解释具体功能方向。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import textwrap
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

SCRIPT_VERSION = "07_refined_v5_2026-05-04_no_overlap_timeline_text_units"

# -----------------------------
# 路径与基础配置
# -----------------------------

ROOT = Path(__file__).resolve().parents[1] if "scripts" in Path(__file__).parts else Path.cwd()
DEFAULT_INPUT = ROOT / "data" / "cleaned" / "cleaned_versions.csv"
FALLBACK_INPUT = ROOT / "cleaned_versions.csv"

TABLE_DIR = ROOT / "outputs" / "tables"
CHART_DIR = ROOT / "outputs" / "charts"
REPORT_DIR = ROOT / "outputs" / "reports"

APP_LABEL = {
    "xhh": "小黑盒",
    "ym": "游民星空",
    "小黑盒": "小黑盒",
    "游民星空": "游民星空",
}
APP_KEY = {
    "小黑盒": "xhh",
    "游民星空": "ym",
    "xhh": "xhh",
    "ym": "ym",
}

# 固定下载观察点：来自下载趋势专项，不在此处重做下载分析
OBSERVATION_POINTS = [
    {
        "point_id": "xhh_2025_12_13_peak",
        "app_key": "xhh",
        "app_name": "小黑盒",
        "label": "小黑盒 2025-12-13 单日下载预估峰值",
        "kind": "date",
        "center": "2025-12-13",
        "core_start": "2025-12-06",
        "core_end": "2025-12-20",
    },
    {
        "point_id": "xhh_2025_12_mid_to_2026_01_high",
        "app_key": "xhh",
        "app_name": "小黑盒",
        "label": "小黑盒 2025-12 中旬至 2026-01 初下载高位区间",
        "kind": "period",
        "center": "2025-12-24",
        "core_start": "2025-12-10",
        "core_end": "2026-01-07",
    },
    {
        "point_id": "ym_2025_06_local_high",
        "app_key": "ym",
        "app_name": "游民星空",
        "label": "游民星空 2025-06 局部高点",
        "kind": "period",
        "center": "2025-06-15",
        "core_start": "2025-06-01",
        "core_end": "2025-06-30",
    },
    {
        "point_id": "ym_2025_07_local_high",
        "app_key": "ym",
        "app_name": "游民星空",
        "label": "游民星空 2025-07 局部高点",
        "kind": "period",
        "center": "2025-07-15",
        "core_start": "2025-07-01",
        "core_end": "2025-07-31",
    },
    {
        "point_id": "ym_2025_11_local_high",
        "app_key": "ym",
        "app_name": "游民星空",
        "label": "游民星空 2025-11 局部高点",
        "kind": "period",
        "center": "2025-11-15",
        "core_start": "2025-11-01",
        "core_end": "2025-11-30",
    },
]

# 透明规则分类。不是模型，只有关键词命中。
CATEGORY_RULES: Dict[str, List[str]] = {
    "修复与稳定性": ["修复", "bug", "Bug", "BUG", "已知问题", "问题", "错误", "异常"],
    "功能体验优化": ["优化", "升级", "体验", "支持", "全新", "新增", "改版", "流程", "频道", "推荐", "分享", "名片"],
    "社区 / 内容 / 帖子相关": ["社区", "帖子", "评论", "互动", "话题", "动态", "关注", "发布"],
    "活动 / 福利 / 运营相关": ["活动", "福利", "金币", "任务", "签到", "奖励", "优惠", "立减", "券", "新春", "礼包"],
    "登录 / 账号 / 绑定相关": ["登录", "账号", "账户", "绑定", "实名", "认证", "Xbox", "PSN", "Steam", "EPIC", "Switch", "名片"],
    "交易 / 商城 / 库存 / 饰品相关": ["交易", "商城", "库存", "饰品", "购买", "售后", "退款", "订单", "支付", "好价", "价格", "Steam好评率", "购买指南"],
    "攻略 / 资讯 / 内容供给相关": ["攻略", "资讯", "新闻", "图鉴", "构筑", "存档", "榜单", "热榜", "奖项", "推荐", "频道", "游戏库", "购买指南"],
    "性能 / 兼容性 / Bug 修复": ["性能", "兼容", "崩溃", "卡顿", "闪退", "bug", "Bug", "修复", "已知问题"],
}

OPERATION_PROBLEM_RULES: Dict[str, List[str]] = {
    "社区氛围与治理": ["社区", "帖子", "评论", "话题", "动态", "互动", "举报", "治理"],
    "用户反馈与客服处理": ["反馈", "客服", "售后", "退款", "申诉", "工单", "问题", "修复", "已知问题"],
    "内容供给与热门游戏话题": ["攻略", "资讯", "新闻", "图鉴", "构筑", "存档", "榜单", "热榜", "奖项", "推荐", "频道", "购买指南"],
    "工具服务与功能体验": ["工具", "名片", "绑定", "查询", "成就", "图鉴", "构筑", "存档", "分享", "升级", "优化", "支持", "新增", "体验"],
    "交易 / 库存 / 消费信任": ["交易", "商城", "库存", "饰品", "购买", "售后", "订单", "支付", "退款", "好评率", "价格", "购买指南"],
    "活动福利与存量用户体验": ["活动", "福利", "金币", "任务", "签到", "奖励", "优惠", "立减", "券", "新春", "礼包"],
}

ACTION_TYPE_RULES: Dict[str, List[str]] = {
    "新增": ["新增", "上线", "加入", "增加"],
    "优化": ["优化", "提升", "改善", "调整"],
    "升级": ["升级", "全新升级", "改版", "重构"],
    "支持": ["支持", "适配", "接入"],
    "修复": ["修复", "解决", "bug", "Bug", "BUG"],
    "活动运营": ["活动", "福利", "金币", "任务", "立减", "券", "优惠", "奖励", "新春"],
}

THEME_RULES: Dict[str, List[str]] = {
    "购买售后 / 消费信任": ["购买", "售后", "退款", "订单", "支付", "购买指南", "Steam好评率", "好评率", "价格"],
    "平台账号 / 绑定名片": ["绑定", "名片", "Steam", "PSN", "Xbox", "EPIC", "Switch", "实名", "认证"],
    "工具服务 / 查询功能": ["工具", "查询", "成就", "图鉴", "构筑", "存档", "分享图", "分享"],
    "内容供给 / 攻略资讯": ["攻略", "资讯", "新闻", "频道", "榜单", "热榜", "奖项", "推荐", "游戏库"],
    "活动福利 / 用户运营": ["活动", "福利", "金币", "任务", "奖励", "立减", "券", "新春", "礼包"],
    "社区内容 / 帖子互动": ["社区", "帖子", "评论", "话题", "动态", "互动"],
    "稳定性 / Bug 修复": ["修复", "已知问题", "bug", "Bug", "问题", "异常", "兼容", "性能"],
}

GENERIC_PATTERNS = [
    r"^修复(部分)?已知问题$",
    r"^修复.*问题$",
    r"^提升用户体验$",
    r"^优化体验$",
    r"^优化用户体验$",
    r"^问题修复$",
    r"^bug修复$",
]

SPECIFIC_HINT_WORDS = [
    "Steam", "PSN", "Xbox", "EPIC", "Switch", "奖项单", "购买指南", "售后", "好评率", "简中",
    "榜单", "热榜", "图鉴", "构筑", "存档", "杀戮尖塔", "名片", "分享图", "实名", "认证",
    "金币", "任务", "立减券", "频道", "个性化", "推荐",
]

# -----------------------------
# 工具函数
# -----------------------------

def ensure_dirs() -> None:
    for p in [TABLE_DIR, CHART_DIR, REPORT_DIR]:
        p.mkdir(parents=True, exist_ok=True)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def first_existing(paths: Iterable[Path]) -> Path:
    for p in paths:
        if p.exists():
            return p
    raise FileNotFoundError("找不到 cleaned_versions.csv，请确认 data/cleaned/cleaned_versions.csv 存在。")


def normalize_app(value: str, app_title: str = "") -> Tuple[str, str]:
    raw = str(value).strip()
    title = str(app_title).strip()
    if raw in APP_KEY:
        key = APP_KEY[raw]
        return key, APP_LABEL.get(key, raw)
    text = raw + " " + title
    if "小黑盒" in text or "xhh" in text.lower():
        return "xhh", "小黑盒"
    if "游民" in text or "ym" in text.lower():
        return "ym", "游民星空"
    return raw, raw


def clean_log_text(text: object) -> str:
    s = "" if pd.isna(text) else str(text)
    s = s.replace("\r\n", "\n").replace("\r", "\n")
    s = re.sub(r"[\t\u3000]+", " ", s)
    s = re.sub(r" +", " ", s)
    return s.strip()


def split_log_units(text: str) -> List[str]:
    """把版本日志拆成动作单元。仅做规则拆分，不做语义模型。"""
    s = clean_log_text(text)
    if not s:
        return []
    # 先按换行拆，再去掉 1. / 1、/ - 等项目符号
    rough: List[str] = []
    for line in re.split(r"[\n；;]+", s):
        line = line.strip()
        if not line:
            continue
        # 把一行中类似“1、新增A 2、修复B”也拆开
        parts = re.split(r"(?:(?<=\D)|^)\s*\d+\s*[、\.\)]\s*", line)
        for part in parts:
            part = part.strip(" -—:：，,。")
            if part:
                rough.append(part)
    # 二次清理
    units = []
    for u in rough:
        u = re.sub(r"^\d+\s*[、\.\)]\s*", "", u).strip(" -—:：，,。")
        u = re.sub(r"\s+", " ", u)
        if u:
            units.append(u)
    return units or [s]


def hit_labels(text: str, rules: Dict[str, List[str]]) -> List[str]:
    out = []
    for label, kws in rules.items():
        if any(kw.lower() in text.lower() for kw in kws):
            out.append(label)
    return out


def is_generic_unit(unit: str) -> bool:
    u = unit.strip().replace(" ", "")
    for pat in GENERIC_PATTERNS:
        if re.search(pat, u, flags=re.I):
            return True
    return False


def action_types(unit: str) -> List[str]:
    hits = hit_labels(unit, ACTION_TYPE_RULES)
    return hits or ["未明确动作词"]


def themes(unit: str) -> List[str]:
    hits = hit_labels(unit, THEME_RULES)
    return hits or ["其他 / 无法明确判断"]


def categories(unit: str) -> List[str]:
    if is_generic_unit(unit):
        return ["信息不足 / 日志过简"]
    hits = hit_labels(unit, CATEGORY_RULES)
    return hits or ["其他 / 无法明确判断"]


def operation_problems(unit: str) -> List[str]:
    if is_generic_unit(unit):
        return []
    return hit_labels(unit, OPERATION_PROBLEM_RULES)


def specificity_score(unit: str) -> int:
    """0=信息不足；1=泛化；2=有明确方向；3=具体动作/对象较清晰。"""
    if is_generic_unit(unit):
        return 0
    score = 0
    ats = action_types(unit)
    ths = themes(unit)
    if ats != ["未明确动作词"]:
        score += 1
    if ths != ["其他 / 无法明确判断"] and ths != ["稳定性 / Bug 修复"]:
        score += 1
    if any(w.lower() in unit.lower() for w in SPECIFIC_HINT_WORDS) or len(unit) >= 12:
        score += 1
    return min(score, 3)


def info_level(score: int) -> str:
    return {
        0: "信息不足 / 不做具体解释",
        1: "偏泛化 / 仅作弱线索",
        2: "有方向 / 可作辅助观察",
        3: "较具体 / 可进四源候选池",
    }[int(score)]


def compress_theme_text(items: Iterable[str], max_items: int = 3) -> str:
    counts: Dict[str, int] = {}
    for item in items:
        if not item or item == "nan":
            continue
        for part in str(item).split("|"):
            part = part.strip()
            if part:
                counts[part] = counts.get(part, 0) + 1
    if not counts:
        return "无具体动作主题"
    top = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[:max_items]
    return "；".join([f"{k}×{v}" for k, v in top])


def join_unique(values: Iterable[str]) -> str:
    seen = []
    for v in values:
        if pd.isna(v):
            continue
        for part in str(v).split("|"):
            p = part.strip()
            if p and p not in seen:
                seen.append(p)
    return "|".join(seen)

# -----------------------------
# 数据生成
# -----------------------------

def load_versions(input_path: Path) -> pd.DataFrame:
    df = pd.read_csv(input_path)
    required = ["app", "version", "update_date", "update_log"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"cleaned_versions.csv 缺少必要字段：{missing}。当前字段：{list(df.columns)}")
    df = df.copy()
    df["update_date"] = pd.to_datetime(df["update_date"], errors="coerce")
    df = df.dropna(subset=["update_date"]).copy()
    app_info = df.apply(lambda r: normalize_app(r.get("app", ""), r.get("app_title", "")), axis=1)
    df["app_key"] = [x[0] for x in app_info]
    df["app_name"] = [x[1] for x in app_info]
    df["update_log_clean"] = df["update_log"].map(clean_log_text)
    df["month"] = df["update_date"].dt.to_period("M").astype(str)
    df = df.sort_values(["app_key", "update_date", "version"]).reset_index(drop=True)
    return df


def build_text_units(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, r in df.iterrows():
        units = split_log_units(r["update_log_clean"])
        for i, unit in enumerate(units, 1):
            sc = specificity_score(unit)
            rows.append({
                "app_key": r["app_key"],
                "app_name": r["app_name"],
                "version": r["version"],
                "update_date": r["update_date"].date().isoformat(),
                "month": r["month"],
                "unit_index": i,
                "log_unit": unit,
                "is_generic_or_insufficient": bool(sc == 0),
                "specificity_score": sc,
                "info_level": info_level(sc),
                "action_types": "|".join(action_types(unit)),
                "action_themes": "|".join(themes(unit)),
                "categories": "|".join(categories(unit)),
                "operation_problems": "|".join(operation_problems(unit)),
            })
    return pd.DataFrame(rows)


def enrich_timeline(df: pd.DataFrame, units: pd.DataFrame) -> pd.DataFrame:
    g = units.groupby(["app_key", "version", "update_date"], as_index=False).agg(
        unit_count=("log_unit", "count"),
        concrete_unit_count=("specificity_score", lambda s: int((s >= 2).sum())),
        max_specificity=("specificity_score", "max"),
        log_units=("log_unit", lambda s: " || ".join(s.astype(str))),
        action_types=("action_types", join_unique),
        action_themes=("action_themes", join_unique),
        categories=("categories", join_unique),
        operation_problems=("operation_problems", join_unique),
    )
    g["update_date"] = pd.to_datetime(g["update_date"])
    out = df.merge(g, on=["app_key", "version", "update_date"], how="left")
    out["info_level"] = out["max_specificity"].fillna(0).astype(int).map(info_level)
    out["evidence_role"] = np.where(
        out["max_specificity"].fillna(0).astype(int) >= 2,
        "可作为公开版本动作背景，进入四源候选池",
        "仅保留时间节点；日志信息不足，不做具体动作解释",
    )
    cols = [
        "app_key", "app_name", "version", "update_date", "month", "update_log_clean",
        "unit_count", "concrete_unit_count", "max_specificity", "info_level",
        "action_types", "action_themes", "categories", "operation_problems", "evidence_role",
        "app_title", "app_subtitle", "app_description",
    ]
    existing = [c for c in cols if c in out.columns]
    return out[existing].sort_values(["app_key", "update_date"])


def build_interval_table(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for app_key, g in df.sort_values("update_date").groupby("app_key"):
        dates = g["update_date"].sort_values().drop_duplicates()
        intervals = dates.diff().dt.days.dropna()
        rows.append({
            "app_key": app_key,
            "app_name": APP_LABEL.get(app_key, app_key),
            "version_count": int(len(g)),
            "first_update_date": dates.min().date().isoformat(),
            "last_update_date": dates.max().date().isoformat(),
            "avg_update_interval_days": round(float(intervals.mean()), 2) if len(intervals) else np.nan,
            "median_update_interval_days": round(float(intervals.median()), 2) if len(intervals) else np.nan,
            "min_update_interval_days": int(intervals.min()) if len(intervals) else np.nan,
            "max_update_interval_days": int(intervals.max()) if len(intervals) else np.nan,
            "interpretation_boundary": "仅说明公开版本更新节奏，不代表产品能力或运营能力强弱",
        })
    return pd.DataFrame(rows)


def build_monthly_summary(timeline: pd.DataFrame) -> pd.DataFrame:
    all_months = pd.period_range(timeline["update_date"].min().to_period("M"), timeline["update_date"].max().to_period("M"), freq="M").astype(str)
    apps = timeline[["app_key", "app_name"]].drop_duplicates()
    base = pd.MultiIndex.from_product([apps["app_key"].tolist(), all_months], names=["app_key", "month"]).to_frame(index=False)
    base = base.merge(apps, on="app_key", how="left")
    m = timeline.groupby(["app_key", "month"], as_index=False).agg(
        update_count=("version", "count"),
        concrete_version_count=("concrete_unit_count", lambda s: int((s.fillna(0) > 0).sum())),
        max_specificity=("max_specificity", "max"),
        action_theme_summary=("action_themes", compress_theme_text),
    )
    out = base.merge(m, on=["app_key", "month"], how="left")
    out["update_count"] = out["update_count"].fillna(0).astype(int)
    out["concrete_version_count"] = out["concrete_version_count"].fillna(0).astype(int)
    out["max_specificity"] = out["max_specificity"].fillna(0).astype(int)
    out["action_theme_summary"] = out["action_theme_summary"].fillna("无版本更新")
    out["interpretation_boundary"] = "月度次数仅代表公开版本节奏，不解释能力强弱或下载变化原因"
    return out[["app_key", "app_name", "month", "update_count", "concrete_version_count", "max_specificity", "action_theme_summary", "interpretation_boundary"]]


def build_category_summary(units: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, r in units.iterrows():
        for cat in str(r["categories"]).split("|"):
            rows.append({
                "app_key": r["app_key"],
                "app_name": r["app_name"],
                "category": cat,
                "version": r["version"],
                "update_date": r["update_date"],
                "log_unit": r["log_unit"],
                "specificity_score": r["specificity_score"],
            })
    long = pd.DataFrame(rows)
    if long.empty:
        return pd.DataFrame()
    out = long.groupby(["app_key", "app_name", "category"], as_index=False).agg(
        hit_unit_count=("log_unit", "count"),
        hit_version_count=("version", pd.Series.nunique),
        concrete_unit_count=("specificity_score", lambda s: int((s >= 2).sum())),
        sample_units=("log_unit", lambda s: "；".join(s.astype(str).drop_duplicates().head(4))),
    )
    out["interpretation_boundary"] = np.where(
        out["category"].eq("信息不足 / 日志过简"),
        "只能说明日志过简，不做具体功能解释",
        "可作为版本日志文本线索，不做因果解释",
    )
    return out.sort_values(["app_key", "hit_unit_count"], ascending=[True, False])


def build_action_theme_summary(units: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, r in units.iterrows():
        for th in str(r["action_themes"]).split("|"):
            rows.append({
                "app_key": r["app_key"],
                "app_name": r["app_name"],
                "month": r["month"],
                "action_theme": th,
                "version": r["version"],
                "update_date": r["update_date"],
                "log_unit": r["log_unit"],
                "specificity_score": r["specificity_score"],
            })
    long = pd.DataFrame(rows)
    if long.empty:
        return pd.DataFrame()
    out = long.groupby(["app_key", "app_name", "month", "action_theme"], as_index=False).agg(
        unit_count=("log_unit", "count"),
        version_count=("version", pd.Series.nunique),
        concrete_unit_count=("specificity_score", lambda s: int((s >= 2).sum())),
        sample_versions=("version", lambda s: "|".join(s.astype(str).drop_duplicates().head(6))),
        sample_units=("log_unit", lambda s: "；".join(s.astype(str).drop_duplicates().head(4))),
    )
    out["can_feed_four_source"] = np.where(out["concrete_unit_count"] > 0, "是，作为动作主题候选", "否或弱，仅作背景")
    return out.sort_values(["app_key", "month", "concrete_unit_count", "unit_count"], ascending=[True, True, False, False])


def build_action_clusters(units: pd.DataFrame) -> pd.DataFrame:
    concrete = units[units["specificity_score"] >= 2].copy()
    if concrete.empty:
        return pd.DataFrame(columns=["app_key", "app_name", "action_theme", "first_date", "last_date", "unit_count", "version_count", "months", "sample_units", "cluster_use"])
    rows = []
    for _, r in concrete.iterrows():
        for th in str(r["action_themes"]).split("|"):
            if th and th != "稳定性 / Bug 修复" and th != "其他 / 无法明确判断":
                rows.append({**r.to_dict(), "action_theme_one": th})
    long = pd.DataFrame(rows)
    if long.empty:
        return pd.DataFrame()
    long["update_date_dt"] = pd.to_datetime(long["update_date"])
    out = long.groupby(["app_key", "app_name", "action_theme_one"], as_index=False).agg(
        first_date=("update_date_dt", lambda s: s.min().date().isoformat()),
        last_date=("update_date_dt", lambda s: s.max().date().isoformat()),
        unit_count=("log_unit", "count"),
        version_count=("version", pd.Series.nunique),
        months=("month", lambda s: "|".join(sorted(s.drop_duplicates()))),
        sample_units=("log_unit", lambda s: "；".join(s.astype(str).drop_duplicates().head(5))),
    ).rename(columns={"action_theme_one": "action_theme"})
    out["cluster_use"] = np.where(
        out["version_count"] >= 2,
        "连续/重复出现，可作为四源整合优先候选",
        "单点出现，仅作辅助观察",
    )
    return out.sort_values(["app_key", "version_count", "unit_count"], ascending=[True, False, False])


def build_operation_problem_matrix(units: pd.DataFrame) -> pd.DataFrame:
    problem_names = list(OPERATION_PROBLEM_RULES.keys())
    rows = []
    for app_key, g in units.groupby("app_key"):
        for p in problem_names:
            hit = g[g["operation_problems"].str.contains(re.escape(p), na=False)]
            rows.append({
                "app_key": app_key,
                "app_name": APP_LABEL.get(app_key, app_key),
                "operation_problem": p,
                "hit_unit_count": int(len(hit)),
                "hit_version_count": int(hit["version"].nunique()) if len(hit) else 0,
                "max_specificity": int(hit["specificity_score"].max()) if len(hit) else 0,
                "sample_units": "；".join(hit["log_unit"].astype(str).drop_duplicates().head(5)) if len(hit) else "",
                "support_level": "较强辅助线索" if len(hit) >= 3 and hit["specificity_score"].max() >= 2 else ("弱辅助线索" if len(hit) else "不适合用版本日志支撑"),
                "boundary": "只能作为公开版本动作背景，不证明运营问题成立或已被解决",
            })
    return pd.DataFrame(rows)


def build_observation_candidates(timeline: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    rows = []
    summary_rows = []
    for obs in OBSERVATION_POINTS:
        core_start = pd.to_datetime(obs["core_start"])
        core_end = pd.to_datetime(obs["core_end"])
        expanded_start = core_start - pd.Timedelta(days=14)
        expanded_end = core_end + pd.Timedelta(days=14)
        center = pd.to_datetime(obs["center"])
        app_key = obs["app_key"]
        tg = timeline[(timeline["app_key"] == app_key) & (timeline["update_date"].between(expanded_start, expanded_end))].copy()
        tg["in_core_window"] = tg["update_date"].between(core_start, core_end)
        tg["days_from_center"] = (tg["update_date"] - center).dt.days
        if tg.empty:
            summary_rows.append({
                "point_id": obs["point_id"], "app_key": app_key, "app_name": obs["app_name"], "observation_label": obs["label"],
                "core_window": f"{core_start.date()}~{core_end.date()}", "expanded_window": f"{expanded_start.date()}~{expanded_end.date()}",
                "core_version_count": 0, "expanded_version_count": 0, "concrete_candidate_count": 0,
                "theme_summary": "无版本节点", "safe_wording": "观察窗口附近未发现公开版本节点；不做进一步解释。",
            })
            continue
        for _, r in tg.iterrows():
            concrete = int(r.get("concrete_unit_count", 0) or 0)
            max_spec = int(r.get("max_specificity", 0) or 0)
            if bool(r["in_core_window"]):
                relation = "核心窗口内"
            elif r["update_date"] < core_start:
                relation = "核心窗口前14天内"
            else:
                relation = "核心窗口后14天内"
            role = "仅时间接近，日志信息不足" if max_spec == 0 else ("时间接近 + 可作为具体动作背景" if max_spec >= 2 else "时间接近 + 弱动作线索")
            rows.append({
                "point_id": obs["point_id"],
                "app_key": app_key,
                "app_name": obs["app_name"],
                "observation_label": obs["label"],
                "observation_kind": obs["kind"],
                "core_window": f"{core_start.date()}~{core_end.date()}",
                "expanded_window": f"{expanded_start.date()}~{expanded_end.date()}",
                "window_relation": relation,
                "in_core_window": bool(r["in_core_window"]),
                "days_from_center": int(r["days_from_center"]),
                "version": r["version"],
                "update_date": r["update_date"].date().isoformat(),
                "max_specificity": max_spec,
                "concrete_unit_count": concrete,
                "categories": r.get("categories", ""),
                "action_themes": r.get("action_themes", ""),
                "operation_problems": r.get("operation_problems", ""),
                "log_units": r.get("log_units", ""),
                "candidate_role": role,
                "safe_wording": "版本节点与下载波动存在时间接近观察，值得后续综合排查；暂不能判断因果关系。",
            })
        summary_rows.append({
            "point_id": obs["point_id"],
            "app_key": app_key,
            "app_name": obs["app_name"],
            "observation_label": obs["label"],
            "core_window": f"{core_start.date()}~{core_end.date()}",
            "expanded_window": f"{expanded_start.date()}~{expanded_end.date()}",
            "core_version_count": int(tg["in_core_window"].sum()),
            "expanded_version_count": int(len(tg)),
            "concrete_candidate_count": int((tg["max_specificity"].fillna(0).astype(int) >= 2).sum()),
            "theme_summary": compress_theme_text(tg.get("action_themes", pd.Series(dtype=str))),
            "safe_wording": "版本节点与下载波动存在时间接近观察，值得后续综合排查；暂不能判断因果关系。",
        })
    return pd.DataFrame(rows), pd.DataFrame(summary_rows)


def build_use_cases(clusters: pd.DataFrame) -> pd.DataFrame:
    # 固定输出“怎么用这些版本数据”的接口说明；若数据命中则附上样例。
    use_case_definitions = [
        {
            "version_signal": "购买售后 / 消费信任",
            "how_to_use_in_four_source": "回到评论与关键词中查购买、售后、退款、客服、价格、好评率、买游戏决策等线索；只能写动作背景，不能写版本解决消费信任。",
            "related_operation_problem": "交易 / 库存 / 消费信任|用户反馈与客服处理",
        },
        {
            "version_signal": "平台账号 / 绑定名片",
            "how_to_use_in_four_source": "回到评论与关键词中查绑定、登录、账号、Steam/PSN/Xbox、战绩名片等线索；只能作为功能服务背景。",
            "related_operation_problem": "工具服务与功能体验|用户反馈与客服处理",
        },
        {
            "version_signal": "工具服务 / 查询功能",
            "how_to_use_in_four_source": "回到关键词中查工具、成就、图鉴、构筑、存档、战绩查询；回到评论中查功能体验和稳定性问题。",
            "related_operation_problem": "工具服务与功能体验|内容供给与热门游戏话题",
        },
        {
            "version_signal": "内容供给 / 攻略资讯",
            "how_to_use_in_four_source": "回到关键词中查攻略、资讯、榜单、热榜、推荐、奖项单、游戏库；判断是否可作为内容供给动作背景。",
            "related_operation_problem": "内容供给与热门游戏话题",
        },
        {
            "version_signal": "活动福利 / 用户运营",
            "how_to_use_in_four_source": "回到评论和关键词中查活动、福利、金币、任务、优惠券、新用户等；只能作为存量/拉新运营动作背景。",
            "related_operation_problem": "活动福利与存量用户体验",
        },
        {
            "version_signal": "信息不足 / 日志过简",
            "how_to_use_in_four_source": "只保留版本时间节点，不进入具体功能或运营动作结论；尤其小黑盒‘修复已知问题’不能强行拆解。",
            "related_operation_problem": "不适合支撑具体运营问题",
        },
    ]
    rows = []
    for d in use_case_definitions:
        sig = d["version_signal"]
        if not clusters.empty and "action_theme" in clusters.columns:
            hit = clusters[clusters["action_theme"].eq(sig)]
            examples = "；".join(hit["sample_units"].dropna().astype(str).head(3)) if len(hit) else ""
            months = "|".join(hit["months"].dropna().astype(str).head(5)) if len(hit) else ""
        else:
            examples, months = "", ""
        rows.append({
            **d,
            "hit_months_in_version_logs": months,
            "sample_version_units": examples,
            "safe_boundary": "只用于四源综合排查，不单独推出因果结论。",
        })
    return pd.DataFrame(rows)


def build_description_clues(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for app_key, g in df.groupby("app_key"):
        desc = str(g["app_description"].dropna().iloc[0]) if "app_description" in g and g["app_description"].notna().any() else ""
        for label, kws in THEME_RULES.items():
            hits = [kw for kw in kws if kw.lower() in desc.lower()]
            if hits:
                rows.append({
                    "app_key": app_key,
                    "app_name": APP_LABEL.get(app_key, app_key),
                    "positioning_theme": label,
                    "hit_keywords": "|".join(hits),
                    "use_boundary": "应用描述只作为产品定位背景，不代表版本动作，也不证明运营问题成立",
                })
    return pd.DataFrame(rows)


def build_audit(df: pd.DataFrame, units: pd.DataFrame, clusters: pd.DataFrame, candidates: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for app_key, g in df.groupby("app_key"):
        ug = units[units["app_key"] == app_key]
        cg = clusters[clusters["app_key"] == app_key] if not clusters.empty and "app_key" in clusters.columns else pd.DataFrame()
        candg = candidates[candidates["app_key"] == app_key] if not candidates.empty and "app_key" in candidates.columns else pd.DataFrame()
        rows.append({
            "script_version": SCRIPT_VERSION,
            "app_key": app_key,
            "app_name": APP_LABEL.get(app_key, app_key),
            "version_rows": int(len(g)),
            "log_unit_rows": int(len(ug)),
            "generic_or_insufficient_units": int((ug["specificity_score"] == 0).sum()),
            "concrete_units_score_ge_2": int((ug["specificity_score"] >= 2).sum()),
            "concrete_action_clusters": int(len(cg[cg["version_count"] >= 1])) if len(cg) else 0,
            "four_source_candidate_nodes": int(len(candg)),
            "audit_note": "本表用于确认脚本确实做了文本拆分、具体度识别和四源候选筛选。",
        })
    return pd.DataFrame(rows)

# -----------------------------
# 图表
# -----------------------------

def set_chinese_font() -> None:
    # 不强绑某个字体；按常见系统字体优先级尝试，避免本地/Windows/服务器环境报错。
    plt.rcParams["font.sans-serif"] = [
        "Microsoft YaHei", "SimHei", "Noto Sans CJK SC", "Source Han Sans CN", "Arial Unicode MS", "DejaVu Sans"
    ]
    plt.rcParams["axes.unicode_minus"] = False


def plot_monthly_updates(monthly: pd.DataFrame, out: Path) -> None:
    set_chinese_font()
    pivot = monthly.pivot(index="month", columns="app_name", values="update_count").fillna(0)
    months = pivot.index.tolist()
    x = np.arange(len(months))
    width = 0.38
    fig, ax = plt.subplots(figsize=(14, 5.2), dpi=180)
    apps = pivot.columns.tolist()
    for i, app in enumerate(apps):
        ax.bar(x + (i - (len(apps)-1)/2) * width, pivot[app].values, width=width, label=app)
    ax.set_title("版本月度更新次数（公开版本节奏，仅作背景）", fontsize=13, pad=12)
    ax.set_xlabel("月份")
    ax.set_ylabel("版本更新次数")
    ax.set_xticks(x)
    ax.set_xticklabels(months, rotation=45, ha="right")
    ax.legend(title="App")
    ax.grid(axis="y", alpha=0.25)
    fig.text(0.01, 0.01, "注：更新次数仅代表公开版本节奏，不代表产品能力或运营能力强弱。", fontsize=9)
    fig.tight_layout(rect=[0, 0.03, 1, 1])
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)


def plot_observation_timeline(candidates: pd.DataFrame, summary: pd.DataFrame, out: Path) -> None:
    """重画 final_12：按下载观察点分面，不在点位上标注版本号。"""
    set_chinese_font()
    n = len(OBSERVATION_POINTS)
    fig, axes = plt.subplots(nrows=n, ncols=1, figsize=(16, 10.5), dpi=180, sharex=False)
    if n == 1:
        axes = [axes]

    for ax, obs in zip(axes, OBSERVATION_POINTS):
        point_id = obs["point_id"]
        core_start = pd.to_datetime(obs["core_start"])
        core_end = pd.to_datetime(obs["core_end"])
        expanded_start = core_start - pd.Timedelta(days=14)
        expanded_end = core_end + pd.Timedelta(days=14)
        center = pd.to_datetime(obs["center"])
        sub = candidates[candidates["point_id"] == point_id].copy() if not candidates.empty else pd.DataFrame()
        if not sub.empty:
            sub["update_date_dt"] = pd.to_datetime(sub["update_date"])

        # 核心窗口阴影 + 日期基准线
        ax.axvspan(core_start, core_end, alpha=0.10, label="下载观察核心窗口")
        if obs["kind"] == "date":
            ax.axvline(center, linestyle="--", linewidth=1.2, alpha=0.75)
        else:
            ax.axvline(core_start, linestyle=":", linewidth=1, alpha=0.55)
            ax.axvline(core_end, linestyle=":", linewidth=1, alpha=0.55)

        # 版本节点：只画点，不贴版本号。点大小和透明度体现具体度。
        if not sub.empty:
            rng = np.random.default_rng(42)  # 固定轻微抖动，避免同日/近日期重叠
            y = np.zeros(len(sub)) + rng.normal(0, 0.018, len(sub))
            sizes = 55 + sub["max_specificity"].fillna(0).astype(int).values * 35
            # 颜色用默认循环色，不手动指定具体颜色，避免风格突兀
            ax.scatter(sub["update_date_dt"], y, s=sizes, alpha=0.85, edgecolors="black", linewidths=0.35)
            # 对核心窗口内节点加一行很短的汇总，不逐点贴版本号
            core_n = int(sub["in_core_window"].sum())
            exp_n = int(len(sub))
            concrete_n = int((sub["max_specificity"].fillna(0).astype(int) >= 2).sum())
            theme_text = compress_theme_text(sub["action_themes"], max_items=3)
            summary_text = f"核心窗口 {core_n} 个｜±14天 {exp_n} 个｜具体动作 {concrete_n} 个｜{theme_text}"
        else:
            summary_text = "±14天内未发现公开版本节点"

        ax.set_xlim(expanded_start, expanded_end)
        ax.set_ylim(-0.18, 0.18)
        ax.set_yticks([])
        ax.grid(axis="x", alpha=0.22)
        ax.set_title(obs["label"], loc="left", fontsize=10.5, pad=4)
        ax.text(0.995, 0.70, summary_text, transform=ax.transAxes, ha="right", va="center", fontsize=9)

        # 控制 x 轴标签密度：每个分面最多显示约 5 个日期
        ticks = pd.date_range(expanded_start, expanded_end, periods=5)
        ax.set_xticks(ticks)
        ax.set_xticklabels([t.strftime("%m-%d") for t in ticks], fontsize=8)

    fig.suptitle("下载观察点附近版本节点排查（仅作时间接近观察，不作因果解释）", fontsize=14, y=0.985)
    fig.text(
        0.01, 0.012,
        "读图方法：每个分面只展示对应下载观察点前后范围；点为版本节点；点越大表示日志动作越具体；版本号与日志明细见 version_four_source_candidate_nodes.csv。",
        fontsize=9,
    )
    fig.tight_layout(rect=[0, 0.035, 1, 0.965])
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)


def plot_category_summary(category_summary: pd.DataFrame, out: Path) -> None:
    set_chinese_font()
    if category_summary.empty:
        return
    # 只画每个 app 的前 8 类；用横向条形减少标签挤压
    rows = []
    for app, g in category_summary.groupby("app_name"):
        rows.append(g.sort_values("hit_unit_count", ascending=False).head(8))
    plot_df = pd.concat(rows, ignore_index=True)
    plot_df["label"] = plot_df["app_name"] + "｜" + plot_df["category"]
    plot_df = plot_df.sort_values("hit_unit_count", ascending=True)
    fig, ax = plt.subplots(figsize=(12, max(5, len(plot_df) * 0.35)), dpi=180)
    ax.barh(plot_df["label"], plot_df["hit_unit_count"])
    ax.set_title("版本日志分类分布（按动作单元计数）", fontsize=13, pad=12)
    ax.set_xlabel("命中动作单元数")
    ax.grid(axis="x", alpha=0.25)
    fig.text(0.01, 0.01, "注：小黑盒‘修复已知问题’单独标为信息不足，不做具体功能拆解。", fontsize=9)
    fig.tight_layout(rect=[0, 0.03, 1, 1])
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)

# -----------------------------
# 报告与主流程
# -----------------------------

def write_report(
    input_path: Path,
    df: pd.DataFrame,
    intervals: pd.DataFrame,
    monthly: pd.DataFrame,
    category_summary: pd.DataFrame,
    audit: pd.DataFrame,
    obs_summary: pd.DataFrame,
    op_matrix: pd.DataFrame,
    use_cases: pd.DataFrame,
    out: Path,
) -> None:
    def app_num(app_key: str, col: str):
        row = intervals[intervals["app_key"] == app_key]
        return row[col].iloc[0] if len(row) else "NA"

    xhh_count = app_num("xhh", "version_count")
    ym_count = app_num("ym", "version_count")
    xhh_avg = app_num("xhh", "avg_update_interval_days")
    ym_avg = app_num("ym", "avg_update_interval_days")

    obs_lines = []
    for _, r in obs_summary.iterrows():
        obs_lines.append(
            f"- {r['observation_label']}：核心窗口 {r['core_version_count']} 个版本节点，±14天 {r['expanded_version_count']} 个版本节点；{r['theme_summary']}。{r['safe_wording']}"
        )

    op_lines = []
    for _, r in op_matrix.iterrows():
        op_lines.append(f"- {r['app_name']}｜{r['operation_problem']}：{r['support_level']}；命中动作单元 {r['hit_unit_count']} 个。")

    report = f"""# 版本节奏分析摘要

脚本版本：`{SCRIPT_VERSION}`  
输入文件：`{input_path}`  
生成时间：由本地运行脚本时决定。

## 1. 数据说明

本专项使用 `cleaned_versions.csv`，字段包括 App、版本号、版本更新日期、版本日志、应用标题、应用副标题、应用描述与月份。版本日志只作为公开文本线索，不能代表完整产品战略，也不能直接解释下载、评论或关键词变化。

本脚本新增了日志文本处理：先把版本日志拆成动作单元，再用透明关键词规则识别动作类型、动作主题、六类运营问题映射和具体度分数。

## 2. 整体更新频率

- 小黑盒版本记录数：{xhh_count}；平均更新间隔：{xhh_avg} 天。
- 游民星空版本记录数：{ym_count}；平均更新间隔：{ym_avg} 天。

这些指标只说明公开版本节奏，不判断产品能力强弱。

## 3. 月度版本节奏

详见：`outputs/tables/version_monthly_summary.csv` 与 `outputs/charts/final_11_version_monthly_updates.png`。  
该图适合作为作品集中的背景图，但图注必须强调：月度更新次数不代表运营能力，也不解释下载变化原因。

## 4. 版本更新时间线与下载观察点

本脚本重画了 `final_12_version_update_timeline.png`：不再展示全年所有版本标签，而是按下载观察点拆成多个分面，只看观察窗口附近版本节点。

{chr(10).join(obs_lines)}

## 5. 版本日志分类观察

详见：

- `version_log_text_units.csv`：每条版本日志拆成动作单元；
- `version_log_action_clusters.csv`：重复动作主题；
- `version_action_theme_summary.csv`：按月份聚合的动作主题；
- `version_log_category_summary.csv`：透明规则分类汇总。

重要边界：小黑盒大量日志为“修复已知问题”，本脚本统一标记为“信息不足 / 日志过简”，不做具体功能拆解。

## 6. 与评论专项的关系

版本日志可以辅助观察评论中的功能体验、稳定性、账号绑定、交易售后等问题，但不能写“版本解决了评论问题”。安全写法是：版本日志显示某时段存在公开版本动作，可作为评论问题的动作背景，仍需四源综合判断。

## 7. 与关键词专项的关系

版本日志可以辅助观察攻略、资讯、工具、交易、平台绑定、活动福利等关键词需求是否有公开动作背景。不能写关键词需求导致版本更新，也不能写版本更新满足了关键词需求。

## 8. 与下载趋势专项的关系

版本节点与下载波动只能写时间接近观察：

{chr(10).join(obs_lines)}

## 9. 对六类运营问题的辅助价值

{chr(10).join(op_lines)}

## 10. 可进入作品集的内容

推荐进入：

- `final_11_version_monthly_updates.png`：公开版本节奏背景；
- `final_12_version_update_timeline.png`：下载观察点附近版本节点排查图；
- `version_four_source_candidate_nodes.csv`：给四源整合使用，不一定直接放正文；
- `version_analysis_use_cases.csv`：给主控判断每类版本信号后续怎么查评论/关键词。

## 11. 不建议进入正文的内容

- 小黑盒“修复已知问题”的具体功能解释；
- 单独用版本频率比较产品能力；
- 单独用版本节点解释下载峰值；
- 无具体动作对象的泛化日志。

## 12. 对四源整合的回传建议

优先把以下表交给主控：

- `version_four_source_candidate_nodes.csv`：哪些版本节点靠近下载观察点；
- `version_log_text_units.csv`：每个版本动作单元怎么分类；
- `version_analysis_use_cases.csv`：这些动作线索应该回到评论/关键词中查什么。

## 13. 必须遵守的表达边界

不能写：

- 某版本导致下载增长；
- 某版本导致评论变化；
- 某版本解决了用户问题；
- 小黑盒产品能力更强；
- 游民星空产品能力更弱；
- 版本更新频率代表运营能力；
- 版本日志代表完整产品战略；
- “修复已知问题”可以直接解释为具体功能优化。

建议写：

- 版本日志显示……
- 可作为公开版本动作背景……
- 与某下载波动时间接近，值得后续综合排查……
- 日志信息不足，暂不做具体功能解释……
- 暂不能判断因果关系……
- 不建议单独作为核心结论……
"""
    out.write_text(report, encoding="utf-8")


def write_manifest(files: List[Path], out: Path) -> pd.DataFrame:
    rows = []
    for p in files:
        if p.exists():
            rows.append({
                "script_version": SCRIPT_VERSION,
                "file": str(p.relative_to(ROOT) if p.is_relative_to(ROOT) else p),
                "size_bytes": p.stat().st_size,
                "sha256": sha256_file(p),
            })
    mf = pd.DataFrame(rows)
    mf.to_csv(out, index=False, encoding="utf-8-sig")
    return mf


def main() -> None:
    parser = argparse.ArgumentParser(description="版本节奏专项分析（重写版）")
    parser.add_argument("--input", type=str, default=None, help="cleaned_versions.csv 路径，默认读取 data/cleaned/cleaned_versions.csv")
    args = parser.parse_args()

    ensure_dirs()
    input_path = Path(args.input) if args.input else first_existing([DEFAULT_INPUT, FALLBACK_INPUT])
    if not input_path.is_absolute():
        input_path = (ROOT / input_path).resolve()

    df = load_versions(input_path)
    units = build_text_units(df)
    timeline = enrich_timeline(df, units)
    intervals = build_interval_table(df)
    monthly = build_monthly_summary(timeline)
    category_summary = build_category_summary(units)
    theme_summary = build_action_theme_summary(units)
    clusters = build_action_clusters(units)
    op_matrix = build_operation_problem_matrix(units)
    candidates, obs_summary = build_observation_candidates(timeline)
    use_cases = build_use_cases(clusters)
    desc_clues = build_description_clues(df)
    audit = build_audit(df, units, clusters, candidates)

    # 表格输出：保留原要求 + 新增可用分析表
    files: List[Path] = []
    output_tables = {
        "version_monthly_summary.csv": monthly,
        "version_update_intervals.csv": intervals,
        "version_timeline.csv": timeline,
        "version_log_category_summary.csv": category_summary,
        "version_observation_points.csv": obs_summary,
        "version_log_text_units.csv": units,
        "version_log_action_clusters.csv": clusters,
        "version_action_theme_summary.csv": theme_summary,
        "version_operation_problem_matrix.csv": op_matrix,
        "version_four_source_candidate_nodes.csv": candidates,
        "version_analysis_use_cases.csv": use_cases,
        "version_description_positioning_clues.csv": desc_clues,
        "version_text_processing_audit.csv": audit,
    }
    for name, table in output_tables.items():
        path = TABLE_DIR / name
        table.to_csv(path, index=False, encoding="utf-8-sig")
        files.append(path)

    # 图表输出
    final_11 = CHART_DIR / "final_11_version_monthly_updates.png"
    final_12 = CHART_DIR / "final_12_version_update_timeline.png"
    final_13 = CHART_DIR / "final_13_version_log_category_summary.png"
    plot_monthly_updates(monthly, final_11)
    plot_observation_timeline(candidates, obs_summary, final_12)
    plot_category_summary(category_summary, final_13)
    files.extend([final_11, final_12, final_13])

    # 报告输出
    report_path = REPORT_DIR / "version_analysis_summary.md"
    write_report(input_path, df, intervals, monthly, category_summary, audit, obs_summary, op_matrix, use_cases, report_path)
    files.append(report_path)

    # 变更说明与校验清单
    change_log = REPORT_DIR / "version_refined_script_change_log.md"
    change_log.write_text(
        f"""# 版本专项脚本重写说明

脚本版本：`{SCRIPT_VERSION}`

这不是旧 `07_analyze_versions.py` 的小修，而是一个新脚本：`scripts/09_analyze_versions_refined.py`。

关键变化：

1. `final_12_version_update_timeline.png` 不再画全年时间线，不再贴满版本号；改为按下载观察点分面，只展示观察窗口附近节点。
2. 新增 `version_log_text_units.csv`：把版本日志拆成动作单元。
3. 新增 `version_analysis_use_cases.csv`：说明每类版本动作后续如何接评论、关键词、下载趋势。
4. 新增 `version_four_source_candidate_nodes.csv`：专门给四源整合用。
5. 新增 `version_output_verification_manifest.csv`：记录输出文件 sha256，方便确认脚本真的重跑。

表达边界：版本日志只能作为公开版本动作背景，不写强因果。
""",
        encoding="utf-8",
    )
    files.append(change_log)

    manifest_path = TABLE_DIR / "version_output_verification_manifest.csv"
    files.append(Path(__file__).resolve())
    write_manifest(files, manifest_path)

    print("版本节奏专项分析完成。")
    print(f"SCRIPT_VERSION = {SCRIPT_VERSION}")
    print(f"输入文件：{input_path}")
    print(f"输出目录：{ROOT / 'outputs'}")
    print(f"校验清单：{manifest_path}")


if __name__ == "__main__":
    main()