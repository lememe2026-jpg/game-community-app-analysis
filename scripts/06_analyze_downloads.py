# -*- coding: utf-8 -*-
"""
下载趋势分析专项脚本

项目：游戏社区 App 运营分析：以小黑盒与游民星空为例
定位：下载趋势 = 结果表现背景

注意：
- 七麦下载量为第三方预估值，只能用于趋势观察，不能等同于官方真实下载量。
- 本脚本不证明版本、活动、热门游戏或运营动作导致下载变化。
- 本脚本只输出下载趋势专项所需的表格、图表和摘要报告。

默认输入：data/cleaned/cleaned_downloads.csv
默认输出：outputs/tables、outputs/charts、outputs/reports

建议脚本路径：scripts/06_analyze_downloads.py
原因：按当前项目最新编号，下载专项为 06，版本专项为 07，总图表脚本为 08。
"""

from __future__ import annotations

import argparse
import csv
import math
import os
from collections import Counter, defaultdict, deque
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import matplotlib.pyplot as plt
from matplotlib import font_manager


TARGET_APPS = ["小黑盒", "游民星空"]
APP_ALIAS = {
    "xhh": "小黑盒",
    "小黑盒": "小黑盒",
    "xiaoheihe": "小黑盒",
    "xiao hei he": "小黑盒",
    "xiao-hei-he": "小黑盒",
    "ym": "游民星空",
    "游民星空": "游民星空",
    "游民": "游民星空",
    "youmin": "游民星空",
    "gamersky": "游民星空",
    "gamer sky": "游民星空",
}

DATE_CANDIDATES = ["date", "日期", "download_date", "stat_date", "day", "数据日期"]
APP_CANDIDATES = ["app", "app_name", "product", "product_name", "产品", "产品名", "应用", "应用名称", "name"]
DOWNLOAD_CANDIDATES = [
    "estimated_downloads_iphone",
    "estimated_downloads",
    "downloads",
    "download",
    "daily_downloads",
    "新增下载量",
    "每日新增下载量预估",
    "下载量预估",
    "iphone_downloads",
]


@dataclass
class DownloadRow:
    app_raw: str
    app: str
    date: date
    downloads: int
    month: str
    week: str
    ma7: Optional[float] = None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="下载趋势分析专项：生成下载趋势表格、图表与摘要报告。")
    default_root = Path(__file__).resolve().parents[1] if "__file__" in globals() else Path.cwd()
    parser.add_argument("--project-root", default=str(default_root), help="项目根目录，默认取 scripts/ 的上一级。")
    parser.add_argument("--input", default=None, help="输入 CSV 路径；默认 data/cleaned/cleaned_downloads.csv。")
    parser.add_argument("--date-col", default=None, help="日期字段名；默认自动识别。")
    parser.add_argument("--app-col", default=None, help="产品 / App 字段名；默认自动识别。")
    parser.add_argument("--downloads-col", default=None, help="每日新增下载量预估字段名；默认自动识别。")
    return parser.parse_args()


def ensure_dirs(root: Path) -> Dict[str, Path]:
    dirs = {
        "tables": root / "outputs" / "tables",
        "charts": root / "outputs" / "charts",
        "reports": root / "outputs" / "reports",
    }
    for d in dirs.values():
        d.mkdir(parents=True, exist_ok=True)
    return dirs


def norm_text(value: object) -> str:
    return str(value).strip().replace("\ufeff", "")


def normalize_app(value: object) -> Optional[str]:
    raw = norm_text(value)
    key = raw.lower().replace("_", " ").strip()
    if raw in APP_ALIAS:
        return APP_ALIAS[raw]
    if key in APP_ALIAS:
        return APP_ALIAS[key]
    compact = key.replace(" ", "").replace("-", "")
    if compact in APP_ALIAS:
        return APP_ALIAS[compact]
    if "小黑盒" in raw or "xiaoheihe" in compact or compact == "xhh":
        return "小黑盒"
    if "游民" in raw or "gamersky" in compact or compact == "ym":
        return "游民星空"
    return None


def pick_column(fieldnames: Sequence[str], candidates: Sequence[str], user_value: Optional[str], label: str) -> str:
    if user_value:
        if user_value not in fieldnames:
            raise ValueError(f"手动指定的{label}字段不存在：{user_value}；现有字段：{fieldnames}")
        return user_value
    lower_map = {f.lower().strip(): f for f in fieldnames}
    for c in candidates:
        if c in fieldnames:
            return c
        if c.lower().strip() in lower_map:
            return lower_map[c.lower().strip()]
    raise ValueError(f"未能自动识别{label}字段。现有字段：{fieldnames}；可用参数手动指定。")


def parse_date(value: object) -> date:
    s = norm_text(value)
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%Y.%m.%d", "%Y年%m月%d日"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            pass
    try:
        return datetime.fromisoformat(s).date()
    except ValueError as exc:
        raise ValueError(f"无法解析日期：{s}") from exc


def parse_int(value: object) -> int:
    s = norm_text(value).replace(",", "")
    if s == "":
        return 0
    return int(round(float(s)))


def read_downloads(input_path: Path, args: argparse.Namespace) -> Tuple[List[DownloadRow], Dict[str, object]]:
    if not input_path.exists():
        raise FileNotFoundError(f"未找到输入文件：{input_path}")
    with input_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []
        if not fieldnames:
            raise ValueError("CSV 没有表头，无法分析。")
        date_col = pick_column(fieldnames, DATE_CANDIDATES, args.date_col, "日期")
        app_col = pick_column(fieldnames, APP_CANDIDATES, args.app_col, "产品名")
        downloads_col = pick_column(fieldnames, DOWNLOAD_CANDIDATES, args.downloads_col, "每日新增下载量预估")
        rows: List[DownloadRow] = []
        raw_apps = Counter()
        unrecognized_apps = Counter()
        for raw in reader:
            app_raw = norm_text(raw.get(app_col, ""))
            raw_apps[app_raw] += 1
            app = normalize_app(app_raw)
            if app is None:
                unrecognized_apps[app_raw] += 1
                continue
            d = parse_date(raw.get(date_col, ""))
            downloads = parse_int(raw.get(downloads_col, "0"))
            month = norm_text(raw.get("month", "")) or d.strftime("%Y-%m")
            week = norm_text(raw.get("week", ""))
            rows.append(DownloadRow(app_raw=app_raw, app=app, date=d, downloads=downloads, month=month, week=week))
    if not rows:
        raise ValueError("没有识别到小黑盒或游民星空的下载数据，请检查产品字段取值或别名。")
    rows.sort(key=lambda r: (r.app, r.date))
    meta = {
        "fieldnames": fieldnames,
        "date_col": date_col,
        "app_col": app_col,
        "downloads_col": downloads_col,
        "raw_apps": dict(raw_apps),
        "unrecognized_apps": dict(unrecognized_apps),
    }
    return rows, meta


def add_rolling_ma(rows: List[DownloadRow], window: int = 7) -> None:
    by_app: Dict[str, List[DownloadRow]] = defaultdict(list)
    for r in rows:
        by_app[r.app].append(r)
    for app_rows in by_app.values():
        app_rows.sort(key=lambda r: r.date)
        q: deque[int] = deque()
        s = 0
        for r in app_rows:
            q.append(r.downloads)
            s += r.downloads
            if len(q) > window:
                s -= q.popleft()
            r.ma7 = s / len(q)


def percentile(values: Sequence[float], p: float) -> float:
    if not values:
        return float("nan")
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    k = (len(ordered) - 1) * p / 100
    lo = math.floor(k)
    hi = math.ceil(k)
    if lo == hi:
        return ordered[lo]
    return ordered[lo] * (hi - k) + ordered[hi] * (k - lo)


def days_in_month(ym: str) -> int:
    y, m = [int(x) for x in ym.split("-")]
    if m == 12:
        next_month = date(y + 1, 1, 1)
    else:
        next_month = date(y, m + 1, 1)
    return (next_month - date(y, m, 1)).days


def write_csv(path: Path, fieldnames: Sequence[str], records: Sequence[Dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for rec in records:
            writer.writerow({k: rec.get(k, "") for k in fieldnames})


def build_monthly_summary(rows: List[DownloadRow]) -> List[Dict[str, object]]:
    grouped: Dict[Tuple[str, str], List[DownloadRow]] = defaultdict(list)
    for r in rows:
        grouped[(r.app, r.month)].append(r)
    records: List[Dict[str, object]] = []
    for app in TARGET_APPS:
        app_months = sorted([m for (a, m) in grouped if a == app])
        prev_total: Optional[int] = None
        monthly_rows: List[Dict[str, object]] = []
        for month in app_months:
            rs = grouped[(app, month)]
            total = sum(r.downloads for r in rs)
            observed_days = len({r.date for r in rs})
            full_days = days_in_month(month)
            avg = total / observed_days if observed_days else 0
            if prev_total is None:
                mom_change = ""
                mom_pct = ""
            else:
                mom_change_value = total - prev_total
                mom_change = mom_change_value
                mom_pct = round(mom_change_value / prev_total * 100, 2) if prev_total else ""
            monthly_rows.append({
                "app": app,
                "month": month,
                "estimated_downloads": total,
                "observed_days": observed_days,
                "calendar_days": full_days,
                "is_full_month": "是" if observed_days == full_days else "否",
                "daily_avg": round(avg, 2),
                "mom_change": mom_change,
                "mom_change_pct": mom_pct,
            })
            prev_total = total
        # rank separately after all months are built
        totals_rank = {rec["month"]: i + 1 for i, rec in enumerate(sorted(monthly_rows, key=lambda x: int(x["estimated_downloads"]), reverse=True))}
        for rec in monthly_rows:
            rec["month_rank_desc"] = totals_rank[rec["month"]]
        records.extend(monthly_rows)
    return records


def build_trend_detail(rows: List[DownloadRow]) -> List[Dict[str, object]]:
    records: List[Dict[str, object]] = []
    medians = {app: percentile([r.downloads for r in rows if r.app == app], 50) for app in TARGET_APPS}
    for r in sorted(rows, key=lambda x: (x.date, x.app)):
        med = medians.get(r.app, 0) or 0
        ratio = r.downloads / med if med else ""
        records.append({
            "app": r.app,
            "app_raw": r.app_raw,
            "date": r.date.isoformat(),
            "month": r.month,
            "week": r.week,
            "estimated_downloads": r.downloads,
            "downloads_7d_ma": round(r.ma7, 2) if r.ma7 is not None else "",
            "vs_app_median_ratio": round(ratio, 3) if ratio != "" else "",
        })
    return records


def build_peak_dates(rows: List[DownloadRow], top_n: int = 10) -> List[Dict[str, object]]:
    records: List[Dict[str, object]] = []
    for app in TARGET_APPS:
        app_rows = [r for r in rows if r.app == app]
        vals = [r.downloads for r in app_rows]
        med = percentile(vals, 50)
        p95 = percentile(vals, 95)
        top = sorted(app_rows, key=lambda r: r.downloads, reverse=True)[:top_n]
        for rank, r in enumerate(top, 1):
            records.append({
                "app": app,
                "rank": rank,
                "date": r.date.isoformat(),
                "month": r.month,
                "estimated_downloads": r.downloads,
                "downloads_7d_ma": round(r.ma7, 2) if r.ma7 is not None else "",
                "vs_app_median_ratio": round(r.downloads / med, 3) if med else "",
                "above_p95": "是" if r.downloads >= p95 else "否",
                "interpretation_boundary": "仅表示第三方预估下载波动，不证明运营动作效果或因果关系",
            })
    return records


def cluster_dates(dates: Sequence[date], max_gap_days: int = 1) -> List[Tuple[date, date]]:
    if not dates:
        return []
    ordered = sorted(set(dates))
    clusters: List[Tuple[date, date]] = []
    start = prev = ordered[0]
    for d in ordered[1:]:
        if (d - prev).days <= max_gap_days:
            prev = d
        else:
            clusters.append((start, prev))
            start = prev = d
    clusters.append((start, prev))
    return clusters


def build_observation_points(rows: List[DownloadRow], monthly: List[Dict[str, object]]) -> List[Dict[str, object]]:
    records: List[Dict[str, object]] = []
    by_app = defaultdict(list)
    for r in rows:
        by_app[r.app].append(r)
    for app in TARGET_APPS:
        app_rows = sorted(by_app.get(app, []), key=lambda r: r.date)
        if not app_rows:
            continue
        vals = [r.downloads for r in app_rows]
        ma_vals = [r.ma7 for r in app_rows if r.ma7 is not None]
        med = percentile(vals, 50)
        p95 = percentile(vals, 95)
        ma90 = percentile(ma_vals, 90)
        candidate_dates = [r.date for r in app_rows if r.downloads >= p95 or (r.ma7 is not None and r.ma7 >= ma90)]
        clusters = cluster_dates(candidate_dates)
        cluster_summaries = []
        for start, end in clusters:
            in_range = [r for r in app_rows if start <= r.date <= end]
            peak = max(in_range, key=lambda r: r.downloads)
            total = sum(r.downloads for r in in_range)
            cluster_summaries.append((peak.downloads, start, end, peak, total, len(in_range)))
        # 保留峰值更明显的区间，避免输出过多探索点。
        for peak_value, start, end, peak, total, days in sorted(cluster_summaries, reverse=True)[:6]:
            if peak.downloads >= med * 1.5 or days >= 3:
                strength = "高" if peak.downloads >= med * 2 or days >= 5 else "中"
                records.append({
                    "app": app,
                    "observation_type": "下载峰值 / 高位区间",
                    "start_date": start.isoformat(),
                    "end_date": end.isoformat(),
                    "days": days,
                    "peak_date": peak.date.isoformat(),
                    "peak_estimated_downloads": peak.downloads,
                    "estimated_downloads_sum": total,
                    "basis": f"单日达到该 App P95 阈值（约 {round(p95, 2)}）或 7日均线达到 P90 阈值（约 {round(ma90, 2)}）",
                    "followup_value": "适合后续与版本、评论、关键词、热门游戏节点做时间对齐观察",
                    "portfolio_usage": "可作为辅助观察；不单独作为核心结论",
                    "caution": "不能写成版本/活动/热门游戏导致下载增长",
                    "strength": strength,
                })
        # 月度层面观察，优先完整月份。
        app_monthly = [m for m in monthly if m["app"] == app and m["is_full_month"] == "是"]
        for rec in sorted(app_monthly, key=lambda x: int(x["estimated_downloads"]), reverse=True)[:3]:
            records.append({
                "app": app,
                "observation_type": "月度高位月份",
                "start_date": f"{rec['month']}-01",
                "end_date": f"{rec['month']}-{days_in_month(str(rec['month'])):02d}",
                "days": rec["observed_days"],
                "peak_date": "",
                "peak_estimated_downloads": "",
                "estimated_downloads_sum": rec["estimated_downloads"],
                "basis": f"完整月份中月度预估下载排名第 {rec['month_rank_desc']}，月度合计 {rec['estimated_downloads']}",
                "followup_value": "适合与评论/关键词/版本专项做月份级对齐",
                "portfolio_usage": "适合作为月度波动背景进入作品集",
                "caution": "不能据此判断真实用户规模或运营能力",
                "strength": "中",
            })
    records.sort(key=lambda x: (x["app"], x["observation_type"], str(x["start_date"])))
    return records


def has_cjk_font() -> bool:
    wanted = {"Microsoft YaHei", "SimHei", "Noto Sans CJK SC", "Arial Unicode MS", "Source Han Sans SC", "WenQuanYi Micro Hei"}
    names = {f.name for f in font_manager.fontManager.ttflist}
    return any(name in names for name in wanted)


def setup_matplotlib() -> bool:
    plt.rcParams["font.sans-serif"] = [
        "Microsoft YaHei",
        "SimHei",
        "Noto Sans CJK SC",
        "Source Han Sans SC",
        "WenQuanYi Micro Hei",
        "Arial Unicode MS",
        "DejaVu Sans",
    ]
    plt.rcParams["axes.unicode_minus"] = False
    plt.rcParams["figure.dpi"] = 150
    return has_cjk_font()


def plot_daily_trend(rows: List[DownloadRow], path: Path) -> None:
    use_cn = setup_matplotlib()
    label_map = {"小黑盒": "小黑盒" if use_cn else "Xiaoheihe", "游民星空": "游民星空" if use_cn else "Gamersky"}
    plt.figure(figsize=(13, 6))
    for app in TARGET_APPS:
        rs = sorted([r for r in rows if r.app == app], key=lambda r: r.date)
        plt.plot([r.date for r in rs], [r.downloads for r in rs], linewidth=1.2, label=label_map[app])
    plt.title("小黑盒 vs 游民星空：每日新增下载量预估趋势（七麦 iPhone 预估）" if use_cn else "Daily Estimated Downloads Trend (Qimai iPhone Estimate)")
    plt.xlabel("日期" if use_cn else "Date")
    plt.ylabel("每日新增下载量预估" if use_cn else "Daily estimated downloads")
    plt.legend()
    plt.grid(alpha=0.25)
    plt.tight_layout()
    plt.savefig(path, bbox_inches="tight")
    plt.close()


def plot_monthly_compare(monthly: List[Dict[str, object]], path: Path) -> None:
    use_cn = setup_matplotlib()
    label_map = {"小黑盒": "小黑盒" if use_cn else "Xiaoheihe", "游民星空": "游民星空" if use_cn else "Gamersky"}
    months = sorted({str(m["month"]) for m in monthly})
    x = list(range(len(months)))
    width = 0.38
    plt.figure(figsize=(13, 6))
    for offset, app in [(-width / 2, "小黑盒"), (width / 2, "游民星空")]:
        lookup = {str(m["month"]): int(m["estimated_downloads"]) for m in monthly if m["app"] == app}
        vals = [lookup.get(m, 0) for m in months]
        plt.bar([i + offset for i in x], vals, width=width, label=label_map[app])
    plt.title("小黑盒 vs 游民星空：月度新增下载量预估对比（七麦 iPhone 预估）" if use_cn else "Monthly Estimated Downloads Comparison (Qimai iPhone Estimate)")
    plt.xlabel("月份" if use_cn else "Month")
    plt.ylabel("月度新增下载量预估" if use_cn else "Monthly estimated downloads")
    plt.xticks(x, months, rotation=45, ha="right")
    plt.legend()
    plt.grid(axis="y", alpha=0.25)
    plt.tight_layout()
    plt.savefig(path, bbox_inches="tight")
    plt.close()


def plot_7d_ma(rows: List[DownloadRow], path: Path) -> None:
    use_cn = setup_matplotlib()
    label_map = {"小黑盒": "小黑盒" if use_cn else "Xiaoheihe", "游民星空": "游民星空" if use_cn else "Gamersky"}
    plt.figure(figsize=(13, 6))
    for app in TARGET_APPS:
        rs = sorted([r for r in rows if r.app == app], key=lambda r: r.date)
        plt.plot([r.date for r in rs], [r.ma7 for r in rs], linewidth=1.6, label=label_map[app])
    plt.title("小黑盒 vs 游民星空：7日移动平均下载趋势（七麦 iPhone 预估）" if use_cn else "7-Day Moving Average Downloads Trend (Qimai iPhone Estimate)")
    plt.xlabel("日期" if use_cn else "Date")
    plt.ylabel("7日移动平均新增下载量预估" if use_cn else "7-day moving average downloads")
    plt.legend()
    plt.grid(alpha=0.25)
    plt.tight_layout()
    plt.savefig(path, bbox_inches="tight")
    plt.close()


def fmt_int(n: object) -> str:
    try:
        return f"{int(float(n)):,}"
    except Exception:
        return str(n)


def report_month_sentence(app: str, monthly: List[Dict[str, object]], full_only: bool = True) -> str:
    app_monthly = [m for m in monthly if m["app"] == app]
    if full_only:
        app_monthly = [m for m in app_monthly if m["is_full_month"] == "是"]
    top = sorted(app_monthly, key=lambda x: int(x["estimated_downloads"]), reverse=True)[:3]
    low = sorted(app_monthly, key=lambda x: int(x["estimated_downloads"]))[:3]
    return f"高位月份为 {', '.join([str(t['month']) + '（' + fmt_int(t['estimated_downloads']) + '）' for t in top])}；低位月份为 {', '.join([str(t['month']) + '（' + fmt_int(t['estimated_downloads']) + '）' for t in low])}。"


def write_report(
    path: Path,
    rows: List[DownloadRow],
    meta: Dict[str, object],
    monthly: List[Dict[str, object]],
    peaks: List[Dict[str, object]],
    observations: List[Dict[str, object]],
    output_paths: Dict[str, Path],
) -> None:
    total_rows = len(rows)
    min_date = min(r.date for r in rows)
    max_date = max(r.date for r in rows)
    app_counts = Counter(r.app for r in rows)
    app_totals = {app: sum(r.downloads for r in rows if r.app == app) for app in TARGET_APPS}
    app_medians = {app: percentile([r.downloads for r in rows if r.app == app], 50) for app in TARGET_APPS}
    top_peaks = {app: [p for p in peaks if p["app"] == app and p["rank"] == 1][0] for app in TARGET_APPS if any(p["app"] == app and p["rank"] == 1 for p in peaks)}

    lines: List[str] = []
    lines.append("# 下载趋势分析摘要")
    lines.append("")
    lines.append("## 1. 数据说明")
    lines.append("")
    lines.append("- 数据来源：`data/cleaned/cleaned_downloads.csv`。")
    lines.append(f"- 样本范围：{min_date.isoformat()} 至 {max_date.isoformat()}，共 {total_rows} 行记录。")
    lines.append(f"- 产品样本：小黑盒 {app_counts.get('小黑盒', 0)} 天，游民星空 {app_counts.get('游民星空', 0)} 天。")
    lines.append(f"- 字段识别：日期字段 `{meta['date_col']}`，产品字段 `{meta['app_col']}`，每日新增下载量预估字段 `{meta['downloads_col']}`。")
    lines.append(f"- 原始产品取值：{meta['raw_apps']}。脚本已将 `xhh` 归一为小黑盒，将 `ym` 归一为游民星空。")
    lines.append("- 七麦下载量为第三方预估值，只能用于趋势观察，不能等同于官方真实下载量，也不能单独证明运营动作效果。")
    lines.append("")
    lines.append("## 2. 整体下载趋势")
    lines.append("")
    lines.append(f"- 小黑盒在样本期内的七麦 iPhone 新增下载预估合计为 {fmt_int(app_totals.get('小黑盒', 0))}，日中位数约为 {fmt_int(round(app_medians.get('小黑盒', 0)))}。这只能说明该数据源中的预估下载量级更高，不代表真实用户规模或运营能力。")
    lines.append(f"- 游民星空在样本期内的七麦 iPhone 新增下载预估合计为 {fmt_int(app_totals.get('游民星空', 0))}，日中位数约为 {fmt_int(round(app_medians.get('游民星空', 0)))}。整体波动较小，但仍存在局部高点。")
    lines.append("- 每日趋势图适合作为结果表现背景，用于提示后续版本、评论、关键词专项关注哪些时间段；不适合单独解释波动原因。")
    lines.append("")
    lines.append("## 3. 月度下载量观察")
    lines.append("")
    lines.append(f"- 小黑盒：{report_month_sentence('小黑盒', monthly)}")
    lines.append(f"- 游民星空：{report_month_sentence('游民星空', monthly)}")
    lines.append("- 由于 2025-04 与 2026-04 为样本截断月份，不建议直接与完整月份做强比较。")
    lines.append("- 月度对比图适合作品集展示，因为它可以用较低噪声呈现两款 App 的月份级波动背景。")
    lines.append("")
    lines.append("## 4. 7 日移动平均观察")
    lines.append("")
    lines.append("- 7 日移动平均可以削弱单日波动，更适合观察连续高位或下降区间。")
    lines.append("- 小黑盒在 2025-12 中旬附近出现明显的连续高位区间；该区间值得后续与版本节点、评论异常、关键词需求变化做时间对齐观察。")
    lines.append("- 游民星空的 7 日均线高位相对分散，主要用于辅助定位局部波动，不建议单独作为正文核心图。")
    lines.append("")
    lines.append("## 5. 下载峰值日期与峰值区间")
    lines.append("")
    for app in TARGET_APPS:
        if app in top_peaks:
            p = top_peaks[app]
            lines.append(f"- {app}单日峰值：{p['date']}，七麦 iPhone 新增下载预估为 {fmt_int(p['estimated_downloads'])}，约为该 App 日中位数的 {p['vs_app_median_ratio']} 倍。")
    lines.append("- 峰值日期只能作为后续排查线索：需要结合版本专项、评论专项、关键词专项以及外部热门游戏节点判断是否存在时间接近关系。")
    lines.append("- 当前不能写成某版本、某活动或某热门游戏导致下载增长。")
    lines.append("")
    lines.append("## 6. 与评论专项的关系")
    lines.append("")
    lines.append("- 下载趋势可与负向评论集中期做时间接近观察，例如查看峰值前后是否出现功能体验、客服处理、交易信任等负向评论集中。")
    lines.append("- 表述边界：只能写“时间接近，值得后续排查”，不能写“负向评论导致下载变化”或“下载峰值证明满意度变化”。")
    lines.append("")
    lines.append("## 7. 与关键词专项的关系")
    lines.append("")
    lines.append("- 下载趋势可辅助理解热门游戏、平台生态、内容需求等关键词线索是否与结果波动发生在相近时间段。")
    lines.append("- 关键词是主动需求，下载是结果表现背景；不能说关键词搜索导致下载变化。")
    lines.append("")
    lines.append("## 8. 对六类运营问题的辅助价值")
    lines.append("")
    six_points = [
        ("社区氛围与治理", "辅助价值较弱。下载趋势不能直接证明社区氛围变化，只能作为评论治理问题集中期附近的结果波动背景。"),
        ("用户反馈与客服处理", "辅助价值中等。可观察反馈集中期或客服相关负评高发期附近是否有下载波动，但不能证明客服处理影响下载。"),
        ("内容供给与热门游戏话题", "辅助价值相对较强。热门游戏话题可能对应外部流量与内容需求，但需要关键词和版本专项继续验证。"),
        ("工具服务与功能体验", "辅助价值中等。若版本专项发现工具功能更新，可观察更新前后下载趋势是否有波动，但不能证明功能带来增长。"),
        ("交易 / 库存 / 消费信任", "辅助价值较弱。该问题更依赖评论与具体功能证据，下载趋势只能提供结果背景。"),
        ("活动福利与存量用户体验", "辅助价值中等。可观察活动期附近是否有下载高点，但必须避免写成活动效果证明。"),
    ]
    for i, (name, desc) in enumerate(six_points, 1):
        lines.append(f"{i}. {name}：{desc}")
    lines.append("")
    lines.append("## 9. 可进入作品集的内容")
    lines.append("")
    lines.append("- 推荐图表：`final_09_download_monthly_compare.png`，用于展示月份级下载预估波动。")
    lines.append("- 推荐图表：`final_08_download_daily_trend.png`，用于展示整体波动背景。")
    lines.append("- 谨慎使用：`final_10_download_7d_moving_average.png`，可作为探索图或放入附录，除非后续四源证据链能解释其高位区间。")
    lines.append("- 推荐表述：下载预估趋势显示、可作为结果波动背景、与某时间节点接近，值得后续结合版本和评论进一步排查。")
    lines.append("")
    lines.append("## 10. 不建议进入正文的内容")
    lines.append("")
    lines.append("- 不建议把单日峰值直接解释为版本、活动或热门游戏带来的增长。")
    lines.append("- 不建议用七麦预估下载量判断真实用户规模、运营能力或用户满意度。")
    lines.append("- 不建议把解释力不足、无法与评论/关键词/版本形成呼应的局部波动放入正文。")
    lines.append("")
    lines.append("## 11. 需要版本节奏专项继续验证的问题")
    lines.append("")
    lines.append("- 小黑盒 2025-12 中旬下载高位区间是否与版本更新、活动上线、热门游戏节点或外部流量变化时间接近。")
    lines.append("- 游民星空 2025-06、2025-07、2025-11 附近局部高点是否对应版本日志、内容节点或其他外部因素。")
    lines.append("- 月度高位月份是否能与评论专项和关键词专项形成“结果表现背景 + 被动反馈 + 主动需求 + 版本节奏”的四源证据链。")
    lines.append("")
    lines.append("## 输出文件")
    lines.append("")
    for label, p in output_paths.items():
        lines.append(f"- {label}：`{p.as_posix()}`")
    lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    args = parse_args()
    root = Path(args.project_root).resolve()
    input_path = Path(args.input).resolve() if args.input else root / "data" / "cleaned" / "cleaned_downloads.csv"
    dirs = ensure_dirs(root)

    rows, meta = read_downloads(input_path, args)
    add_rolling_ma(rows, window=7)
    monthly = build_monthly_summary(rows)
    detail = build_trend_detail(rows)
    peaks = build_peak_dates(rows, top_n=10)
    observations = build_observation_points(rows, monthly)

    monthly_path = dirs["tables"] / "download_monthly_summary.csv"
    peaks_path = dirs["tables"] / "download_peak_dates.csv"
    detail_path = dirs["tables"] / "download_trend_detail.csv"
    observation_path = dirs["tables"] / "download_observation_points.csv"
    daily_chart_path = dirs["charts"] / "final_08_download_daily_trend.png"
    monthly_chart_path = dirs["charts"] / "final_09_download_monthly_compare.png"
    ma_chart_path = dirs["charts"] / "final_10_download_7d_moving_average.png"
    report_path = dirs["reports"] / "download_analysis_summary.md"

    write_csv(monthly_path, [
        "app", "month", "estimated_downloads", "observed_days", "calendar_days", "is_full_month",
        "daily_avg", "mom_change", "mom_change_pct", "month_rank_desc",
    ], monthly)
    write_csv(peaks_path, [
        "app", "rank", "date", "month", "estimated_downloads", "downloads_7d_ma",
        "vs_app_median_ratio", "above_p95", "interpretation_boundary",
    ], peaks)
    write_csv(detail_path, [
        "app", "app_raw", "date", "month", "week", "estimated_downloads", "downloads_7d_ma", "vs_app_median_ratio",
    ], detail)
    write_csv(observation_path, [
        "app", "observation_type", "start_date", "end_date", "days", "peak_date", "peak_estimated_downloads",
        "estimated_downloads_sum", "basis", "followup_value", "portfolio_usage", "caution", "strength",
    ], observations)

    plot_daily_trend(rows, daily_chart_path)
    plot_monthly_compare(monthly, monthly_chart_path)
    plot_7d_ma(rows, ma_chart_path)

    output_paths = {
        "月度汇总表": monthly_path.relative_to(root),
        "峰值日期表": peaks_path.relative_to(root),
        "趋势明细表": detail_path.relative_to(root),
        "观察点表": observation_path.relative_to(root),
        "每日趋势图": daily_chart_path.relative_to(root),
        "月度对比图": monthly_chart_path.relative_to(root),
        "7日均线图": ma_chart_path.relative_to(root),
        "摘要报告": report_path.relative_to(root),
    }
    write_report(report_path, rows, meta, monthly, peaks, observations, output_paths)

    missing_apps = [app for app in TARGET_APPS if not any(r.app == app for r in rows)]
    script_path = Path(__file__).resolve() if "__file__" in globals() else Path("scripts/06_analyze_downloads.py")

    print("[OK] 下载趋势分析专项已完成。")
    print(f"脚本路径：{script_path.as_posix()}")
    print("字段识别：")
    print(f"- 日期字段：{meta['date_col']}")
    print(f"- 产品字段：{meta['app_col']}")
    print(f"- 每日新增下载量预估字段：{meta['downloads_col']}")
    print("产品识别：")
    print(f"- 原始产品取值：{meta['raw_apps']}")
    if missing_apps:
        print(f"- 以下目标产品未在数据中识别到：{'、'.join(missing_apps)}。请检查产品名字段或别名。")
    else:
        print("- 已识别：小黑盒、游民星空。")
    print("表格输出：")
    for p in [monthly_path, peaks_path, detail_path, observation_path]:
        print(f"- {p.as_posix()}")
    print("图表输出：")
    for p in [daily_chart_path, monthly_chart_path, ma_chart_path]:
        print(f"- {p.as_posix()}")
    print("报告输出：")
    print(f"- {report_path.as_posix()}")
    print("处理提示：")
    print("- 七麦下载量为第三方预估值，只用于趋势观察，不等同于官方真实下载量。")
    print("- 本脚本不做版本、活动、热门游戏与下载变化之间的强因果判断。")
    print("- 当前项目编号口径：06=下载专项，07=版本专项，08=最终图表脚本。")


if __name__ == "__main__":
    main()