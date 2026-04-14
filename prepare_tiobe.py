import glob
import os
import re
import pandas as pd


RAW_DIR = "data/raw"
PROCESSED_DIR = "data/processed"


def ensure_directories() -> None:
    """Create output directory if it does not exist."""
    os.makedirs(PROCESSED_DIR, exist_ok=True)


def normalize_language_name(lang: str) -> str:
    """Standardize language names for consistent merging."""
    if pd.isna(lang):
        return lang

    lang = str(lang).strip()

    mapping = {
        "C#": "C#",
        "C++": "C++",
        "C": "C",
        "Java": "Java",
        "JavaScript": "JavaScript",
        "TypeScript": "TypeScript",
        "Python": "Python",
        "Go": "Go",
        "PHP": "PHP",
        "R": "R",
        "Ruby": "Ruby",
        "Rust": "Rust",
        "Swift": "Swift",
        "Kotlin": "Kotlin",
        "MATLAB": "MATLAB",
        "Delphi/Object Pascal": "Delphi",
        "Visual Basic": "Visual Basic (.Net)",
        "Perl": "Perl",
        "Scala": "Scala",
        "Dart": "Dart",
        "Assembly language": "Assembly",
        "SQL": "SQL",
        "Objective-C": "Objective-C",
        "Fortran": "Fortran",
        "Lua": "Lua",
        "Ada": "Ada",
        "Julia": "Julia",
        "COBOL": "Cobol",
        "Lisp": "Lisp",
        "Prolog": "Prolog",
        "Haskell": "Haskell",
        "SAS": "SAS",
        "Scratch": "Scratch",
        "Scractch": "Scratch",
        "Rustlang": "Rust",
    }

    return mapping.get(lang, lang)


def extract_month_name(filename: str) -> str:
    """Extract month from filename like tiobe_index_january2024.csv."""
    base = os.path.basename(filename).lower()
    match = re.search(r"tiobe_index_([a-z]+)2024\.csv", base)
    return match.group(1) if match else "unknown"


def read_single_tiobe_file(file_path: str) -> pd.DataFrame:
    """Read and standardize a single monthly TIOBE file."""
    df = pd.read_csv(file_path)
    df.columns = [col.strip() for col in df.columns]

    language_col = None
    rating_col = None
    rank_col = None

    for col in df.columns:
        col_lower = col.lower()
        if "programming language" in col_lower:
            language_col = col
        elif "ratings" in col_lower:
            rating_col = col
        elif "rank" in col_lower and "2024" in col_lower:
            rank_col = col

    if language_col is None or rating_col is None:
        raise ValueError(
            f"Could not detect required columns in {file_path}. "
            f"Found columns: {df.columns.tolist()}"
        )

    out = df[[language_col, rating_col]].copy()
    out.columns = ["Language", "TIOBE_Rating"]

    if rank_col is not None:
        out["TIOBE_Rank_2024"] = df[rank_col]
    else:
        out["TIOBE_Rank_2024"] = pd.NA

    out["Month"] = extract_month_name(file_path)

    out["Language"] = out["Language"].astype(str).str.strip().apply(normalize_language_name)
    out["TIOBE_Rating"] = (
        out["TIOBE_Rating"]
        .astype(str)
        .str.replace("%", "", regex=False)
        .str.strip()
    )
    out["TIOBE_Rating"] = pd.to_numeric(out["TIOBE_Rating"], errors="coerce")
    out["TIOBE_Rank_2024"] = pd.to_numeric(out["TIOBE_Rank_2024"], errors="coerce")

    out = out.dropna(subset=["Language", "TIOBE_Rating"])

    return out


def build_yearly_average() -> pd.DataFrame:
    """Aggregate all monthly TIOBE files into yearly averages."""
    files = sorted(glob.glob(os.path.join(RAW_DIR, "tiobe_index_*2024.csv")))

    if not files:
        raise FileNotFoundError(
            "No TIOBE monthly files found in data/raw/. "
            "Expected files like tiobe_index_january2024.csv"
        )

    monthly_frames = []
    for file_path in files:
        monthly_df = read_single_tiobe_file(file_path)
        monthly_frames.append(monthly_df)

    all_months = pd.concat(monthly_frames, ignore_index=True)

    yearly = (
        all_months.groupby("Language", as_index=False)
        .agg(
            Avg_TIOBE_Rating=("TIOBE_Rating", "mean"),
            Avg_TIOBE_Rank=("TIOBE_Rank_2024", "mean"),
            Months_Observed=("Month", "nunique"),
        )
        .sort_values("Avg_TIOBE_Rating", ascending=False)
        .reset_index(drop=True)
    )

    yearly["Avg_TIOBE_Rank"] = yearly["Avg_TIOBE_Rank"].round(2)
    yearly["Avg_TIOBE_Rating"] = yearly["Avg_TIOBE_Rating"].round(4)

    return yearly


def main() -> None:
    ensure_directories()
    yearly = build_yearly_average()
    output_path = os.path.join(PROCESSED_DIR, "tiobe_2024_avg.csv")
    yearly.to_csv(output_path, index=False)
    print(f"Saved yearly TIOBE averages to: {output_path}")
    print(yearly.head(15))


if __name__ == "__main__":
    main()
