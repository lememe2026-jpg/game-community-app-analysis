from pathlib import Path
import pandas as pd
import numpy as np


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
CLEANED_DIR = PROJECT_ROOT / "data" / "cleaned"
REPORT_DIR = PROJECT_ROOT / "outputs" / "reports"

CLEANED_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)


def read_csv_safely(file_path: Path) -> pd.DataFrame:
    encodings = ["utf-8-sig", "utf-8", "gbk", "gb18030"]
    last_error = None

    for encoding in encodings:
        try:
            return pd.read_csv(file_path, encoding=encoding)
        except Exception as exc:
            last_error = exc

    raise RuntimeError(f"Failed to read CSV file: {file_path}. Last error: {last_error}")


def clean_numeric_series(series: pd.Series) -> pd.Series:
    """
    Convert messy numeric columns to numeric.
    Handles commas, blanks, '-', and ranking symbols.
    """
    return (
        series.astype(str)
        .str.replace(",", "", regex=False)
        .str.replace("，", "", regex=False)
        .str.replace("-", "", regex=False)
        .str.strip()
        .replace({"": np.nan, "nan": np.nan, "None": np.nan})
        .pipe(pd.to_numeric, errors="coerce")
    )

def clean_chinese_date_series(series: pd.Series) -> pd.Series:
    """
    Convert Chinese date strings like '2026年04月20日' to datetime.
    """
    cleaned = (
        series.astype(str)
        .str.strip()
        .str.replace("年", "-", regex=False)
        .str.replace("月", "-", regex=False)
        .str.replace("日", "", regex=False)
    )

    return pd.to_datetime(cleaned, errors="coerce", format="%Y-%m-%d")

def clean_keywords() -> pd.DataFrame:
    df = read_csv_safely(RAW_DIR / "keywords_comparison.csv").copy()

    df = df.rename(
        columns={
            "关键词": "keyword",
            "搜索指数": "search_index",
            "搜索结果数": "search_result_count",
            "流行度": "popularity",
            "小黑盒 ~ 八千万游戏玩家社区(排名)": "xhh_rank",
            "游民星空~攻略工具资讯一网打尽的游戏社区(排名)": "ym_rank",
        }
    )

    numeric_cols = [
        "search_index",
        "search_result_count",
        "popularity",
        "xhh_rank",
        "ym_rank",
    ]

    for col in numeric_cols:
        df[col] = clean_numeric_series(df[col])

    df["keyword"] = df["keyword"].astype(str).str.strip()
    df = df[df["keyword"].notna() & (df["keyword"] != "")]

    df["xhh_has_rank"] = df["xhh_rank"].notna()
    df["ym_has_rank"] = df["ym_rank"].notna()

    df = df.drop_duplicates(subset=["keyword"])

    return df


def clean_downloads() -> pd.DataFrame:
    files = {
        "xhh": "xhh_downloads.csv",
        "ym": "ym_downloads.csv",
    }

    frames = []

    for app, filename in files.items():
        df = read_csv_safely(RAW_DIR / filename).copy()

        df = df.rename(
            columns={
                "日期": "date",
                "下载量预估~iPhone": "estimated_downloads_iphone",
            }
        )

        df["app"] = app
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df["estimated_downloads_iphone"] = clean_numeric_series(
            df["estimated_downloads_iphone"]
        )

        df = df.dropna(subset=["date"])
        df = df.sort_values("date")

        frames.append(df[["app", "date", "estimated_downloads_iphone"]])

    downloads = pd.concat(frames, ignore_index=True)

    downloads["month"] = downloads["date"].dt.to_period("M").astype(str)
    downloads["week"] = downloads["date"].dt.to_period("W").astype(str)

    downloads = downloads.sort_values(["app", "date"])

    return downloads


def find_review_header_row(raw_df: pd.DataFrame) -> int:
    """
    Qimai review Excel files often contain several description rows before the real header.
    We detect the row that contains both '发表时间' and '评级'.
    """
    for idx, row in raw_df.iterrows():
        values = [str(value) for value in row.tolist()]
        row_text = " ".join(values)

        if "发表时间" in row_text and "评级" in row_text:
            return idx

    # fallback: based on current data observation
    return 2


def clean_single_review_file(filename: str, app: str) -> pd.DataFrame:
    file_path = RAW_DIR / filename
    raw = pd.read_excel(file_path, header=None)

    header_row = find_review_header_row(raw)

    columns = raw.iloc[header_row].tolist()
    df = raw.iloc[header_row + 1 :].copy()
    df.columns = columns

    expected_columns = {
        "发表时间": "published_at",
        "作者": "author",
        "评级": "rating",
        "标题": "title",
        "内容": "content",
    }

    df = df.rename(columns=expected_columns)

    keep_cols = ["published_at", "author", "rating", "title", "content"]
    existing_keep_cols = [col for col in keep_cols if col in df.columns]
    df = df[existing_keep_cols].copy()

    df["app"] = app

    df["published_at"] = pd.to_datetime(df["published_at"], errors="coerce")
    df["rating"] = clean_numeric_series(df["rating"])

    for col in ["author", "title", "content"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
            df[col] = df[col].replace({"nan": np.nan, "None": np.nan, "": np.nan})

    df = df.dropna(subset=["published_at", "rating"])

    df["rating"] = df["rating"].astype(int)
    df["month"] = df["published_at"].dt.to_period("M").astype(str)

    df["content_length"] = df["content"].fillna("").astype(str).str.len()

    df["sentiment_group"] = pd.cut(
        df["rating"],
        bins=[0, 2, 3, 5],
        labels=["negative", "neutral", "positive"],
        include_lowest=True,
    )

    return df


def clean_reviews() -> pd.DataFrame:
    xhh = clean_single_review_file("xhh_reviews.xlsx", "xhh")
    ym = clean_single_review_file("ym_reviews.xlsx", "ym")

    reviews = pd.concat([xhh, ym], ignore_index=True)

    reviews = reviews.sort_values(["app", "published_at"])
    reviews = reviews.drop_duplicates(
        subset=["app", "published_at", "author", "rating", "title", "content"]
    )

    return reviews


def clean_versions() -> pd.DataFrame:
    files = {
        "xhh": "xhh_versions.csv",
        "ym": "ym_versions.csv",
    }

    frames = []

    for app, filename in files.items():
        df = read_csv_safely(RAW_DIR / filename).copy()

        df = df.rename(
            columns={
                "版本号": "version",
                "版本更新日期": "update_date",
                "更新日志": "update_log",
                "应用描述": "app_description",
                "应用标题": "app_title",
                "应用副标题": "app_subtitle",
            }
        )

        df["app"] = app
        df["update_date"] = clean_chinese_date_series(df["update_date"])

        keep_cols = [
            "app",
            "version",
            "update_date",
            "app_title",
            "app_subtitle",
            "update_log",
            "app_description",
        ]

        existing_keep_cols = [col for col in keep_cols if col in df.columns]
        df = df[existing_keep_cols].copy()

        for col in ["version", "app_title", "app_subtitle", "update_log", "app_description"]:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip()
                df[col] = df[col].replace({"nan": np.nan, "None": np.nan, "": np.nan})

        df = df.dropna(subset=["update_date"])
        df["month"] = df["update_date"].dt.to_period("M").astype(str)

        frames.append(df)

    versions = pd.concat(frames, ignore_index=True)
    versions = versions.sort_values(["app", "update_date"])

    return versions


def write_cleaning_report(
    keywords: pd.DataFrame,
    downloads: pd.DataFrame,
    reviews: pd.DataFrame,
    versions: pd.DataFrame,
) -> None:
    lines = []

    lines.append("# Cleaning Report")
    lines.append("")
    lines.append("This report summarizes the cleaned datasets generated from Qimai exported files.")
    lines.append("")

    datasets = {
        "cleaned_keywords": keywords,
        "cleaned_downloads": downloads,
        "cleaned_reviews": reviews,
        "cleaned_versions": versions,
    }

    for name, df in datasets.items():
        lines.append(f"## {name}")
        lines.append("")
        lines.append(f"- rows: {len(df)}")
        lines.append(f"- columns: {len(df.columns)}")
        lines.append("")
        lines.append("### Columns")
        lines.append("")
        for col in df.columns:
            lines.append(f"- {col}")
        lines.append("")

        lines.append("### Missing values")
        lines.append("")
        for col, count in df.isna().sum().items():
            lines.append(f"- {col}: {count}")
        lines.append("")
        lines.append("---")
        lines.append("")

    lines.append("## Notes")
    lines.append("")
    lines.append("- Qimai download data is an estimate and should only be used for trend observation.")
    lines.append("- Review volume differs significantly between XHH and YM, so comparison should be descriptive rather than causal.")
    lines.append("- Version logs are used as supporting context only, not as strong causal evidence.")
    lines.append("")

    report_path = REPORT_DIR / "cleaning_report.md"
    report_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    print("Cleaning keywords ...")
    keywords = clean_keywords()

    print("Cleaning downloads ...")
    downloads = clean_downloads()

    print("Cleaning reviews ...")
    reviews = clean_reviews()

    print("Cleaning versions ...")
    versions = clean_versions()

    keywords.to_csv(CLEANED_DIR / "cleaned_keywords.csv", index=False, encoding="utf-8-sig")
    downloads.to_csv(CLEANED_DIR / "cleaned_downloads.csv", index=False, encoding="utf-8-sig")
    reviews.to_csv(CLEANED_DIR / "cleaned_reviews.csv", index=False, encoding="utf-8-sig")
    versions.to_csv(CLEANED_DIR / "cleaned_versions.csv", index=False, encoding="utf-8-sig")

    write_cleaning_report(keywords, downloads, reviews, versions)

    print("")
    print("Done.")
    print(f"Cleaned data saved to: {CLEANED_DIR}")
    print(f"Cleaning report saved to: {REPORT_DIR / 'cleaning_report.md'}")


if __name__ == "__main__":
    main()