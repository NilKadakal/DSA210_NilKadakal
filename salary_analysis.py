import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import f_oneway, ttest_ind, spearmanr


RAW_DIR = "data/raw"
PROCESSED_DIR = "data/processed"
FIGURES_DIR = "outputs/figures"
TABLES_DIR = "outputs/tables"


def ensure_directories() -> None:
    """Create required output directories."""
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    os.makedirs(FIGURES_DIR, exist_ok=True)
    os.makedirs(TABLES_DIR, exist_ok=True)


def normalize_language_name(lang: str) -> str:
    """Standardize language names so Stack Overflow and TIOBE can be merged."""
    if pd.isna(lang):
        return lang

    lang = str(lang).strip()

    mapping = {
        "Bash/Shell (all shells)": "Bash",
        "Visual Basic (.Net)": "Visual Basic (.Net)",
        "HTML/CSS": "HTML/CSS",
        "Assembly": "Assembly",
        "Cobol": "Cobol",
        "Delphi": "Delphi",
        "Lisp": "Lisp",
        "MATLAB": "MATLAB",
        "Objective-C": "Objective-C",
        "PHP": "PHP",
        "Python": "Python",
        "JavaScript": "JavaScript",
        "TypeScript": "TypeScript",
        "C": "C",
        "C#": "C#",
        "C++": "C++",
        "Java": "Java",
        "Go": "Go",
        "Rust": "Rust",
        "Ruby": "Ruby",
        "Swift": "Swift",
        "Kotlin": "Kotlin",
        "Scala": "Scala",
        "R": "R",
        "Dart": "Dart",
        "Fortran": "Fortran",
        "Lua": "Lua",
        "Ada": "Ada",
        "Julia": "Julia",
        "Perl": "Perl",
        "Prolog": "Prolog",
        "Haskell": "Haskell",
        "SQL": "SQL",
    }

    return mapping.get(lang, lang)


def load_stackoverflow_data() -> pd.DataFrame:
    """Load the main Stack Overflow 2024 survey file."""
    path = os.path.join(RAW_DIR, "survey_results_public.csv")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Missing file: {path}")
    return pd.read_csv(path)


def load_tiobe_data() -> pd.DataFrame:
    """Load yearly averaged TIOBE data."""
    path = os.path.join(PROCESSED_DIR, "tiobe_2024_avg.csv")
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Missing processed TIOBE file: {path}. "
            "Run src/prepare_tiobe.py first."
        )
    return pd.read_csv(path)


def clean_main_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and filter developer salary data."""
    required_columns = [
        "ConvertedCompYearly",
        "YearsCodePro",
        "EdLevel",
        "RemoteWork",
        "DevType",
        "Country",
        "LanguageHaveWorkedWith",
        "Employment",
    ]

    missing_cols = [col for col in required_columns if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns in survey dataset: {missing_cols}")

    df = df.copy()

    df = df[df["Employment"].fillna("").str.contains("Employed", na=False)]

    df["ConvertedCompYearly"] = pd.to_numeric(df["ConvertedCompYearly"], errors="coerce")
    df = df.dropna(subset=["ConvertedCompYearly"])
    df = df[df["ConvertedCompYearly"] > 0]

    lower = df["ConvertedCompYearly"].quantile(0.01)
    upper = df["ConvertedCompYearly"].quantile(0.99)
    df = df[(df["ConvertedCompYearly"] >= lower) & (df["ConvertedCompYearly"] <= upper)]

    df["YearsCodePro"] = df["YearsCodePro"].replace({
        "Less than 1 year": 0.5,
        "More than 50 years": 50,
    })
    df["YearsCodePro"] = pd.to_numeric(df["YearsCodePro"], errors="coerce")
    df = df.dropna(subset=["YearsCodePro"])

    df = df.dropna(subset=["EdLevel", "RemoteWork", "LanguageHaveWorkedWith"])
    df["LogSalary"] = np.log(df["ConvertedCompYearly"])

    return df


def build_language_level_dataset(df: pd.DataFrame, tiobe: pd.DataFrame) -> pd.DataFrame:
    """Explode multi-language responses into one row per language and merge TIOBE."""
    lang_df = df.copy()

    lang_df["Language"] = lang_df["LanguageHaveWorkedWith"].str.split(";")
    lang_df = lang_df.explode("Language")
    lang_df["Language"] = lang_df["Language"].astype(str).str.strip()
    lang_df = lang_df.dropna(subset=["Language"])
    lang_df = lang_df[lang_df["Language"] != ""]

    lang_df["Language"] = lang_df["Language"].apply(normalize_language_name)
    tiobe["Language"] = tiobe["Language"].apply(normalize_language_name)

    merged = lang_df.merge(tiobe, on="Language", how="left")
    return merged


def save_basic_tables(df: pd.DataFrame, lang_df: pd.DataFrame) -> None:
    summary = df[["ConvertedCompYearly", "LogSalary", "YearsCodePro"]].describe()
    summary.to_csv(os.path.join(TABLES_DIR, "numeric_summary.csv"))

    edlevel_summary = (
        df.groupby("EdLevel")["ConvertedCompYearly"]
        .agg(["count", "median", "mean"])
        .sort_values("median", ascending=False)
    )
    edlevel_summary.to_csv(os.path.join(TABLES_DIR, "salary_by_education.csv"))

    remote_summary = (
        df.groupby("RemoteWork")["ConvertedCompYearly"]
        .agg(["count", "median", "mean"])
        .sort_values("median", ascending=False)
    )
    remote_summary.to_csv(os.path.join(TABLES_DIR, "salary_by_remote_work.csv"))

    language_summary = (
        lang_df.groupby("Language")
        .agg(
            count=("ConvertedCompYearly", "count"),
            median_salary=("ConvertedCompYearly", "median"),
            mean_salary=("ConvertedCompYearly", "mean"),
            avg_tiobe_rating=("Avg_TIOBE_Rating", "mean"),
        )
        .sort_values("count", ascending=False)
    )
    language_summary.to_csv(os.path.join(TABLES_DIR, "salary_by_language.csv"))


def make_figures(df: pd.DataFrame, lang_df: pd.DataFrame) -> None:
    plt.figure(figsize=(8, 5))
    plt.hist(df["ConvertedCompYearly"], bins=40)
    plt.xlabel("Annual Salary")
    plt.ylabel("Frequency")
    plt.title("Distribution of Annual Salary")
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "salary_distribution.png"))
    plt.close()

    plt.figure(figsize=(8, 5))
    plt.hist(df["LogSalary"], bins=40)
    plt.xlabel("Log Annual Salary")
    plt.ylabel("Frequency")
    plt.title("Distribution of Log Annual Salary")
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "log_salary_distribution.png"))
    plt.close()

    plt.figure(figsize=(8, 5))
    plt.scatter(df["YearsCodePro"], df["ConvertedCompYearly"], alpha=0.2)
    plt.xlabel("Years of Professional Coding")
    plt.ylabel("Annual Salary")
    plt.title("Experience vs Salary")
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "experience_vs_salary.png"))
    plt.close()

    remote_order = (
        df.groupby("RemoteWork")["ConvertedCompYearly"]
        .median()
        .sort_values(ascending=False)
        .index
    )
    remote_medians = df.groupby("RemoteWork")["ConvertedCompYearly"].median().loc[remote_order]

    plt.figure(figsize=(8, 5))
    plt.bar(remote_medians.index, remote_medians.values)
    plt.xticks(rotation=20)
    plt.ylabel("Median Salary")
    plt.title("Median Salary by Work Modality")
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "median_salary_by_remote_work.png"))
    plt.close()

    top_langs = lang_df["Language"].value_counts().head(15).index
    top_lang_df = lang_df[lang_df["Language"].isin(top_langs)]

    top_lang_medians = (
        top_lang_df.groupby("Language")["ConvertedCompYearly"]
        .median()
        .sort_values(ascending=False)
    )

    plt.figure(figsize=(10, 6))
    plt.bar(top_lang_medians.index, top_lang_medians.values)
    plt.xticks(rotation=45, ha="right")
    plt.ylabel("Median Salary")
    plt.title("Median Salary for Top Languages")
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "median_salary_top_languages.png"))
    plt.close()

    corr_df = (
        lang_df.groupby("Language", as_index=False)
        .agg(
            median_salary=("ConvertedCompYearly", "median"),
            avg_tiobe=("Avg_TIOBE_Rating", "mean"),
            n=("ConvertedCompYearly", "count"),
        )
        .dropna(subset=["avg_tiobe"])
    )

    plt.figure(figsize=(8, 5))
    plt.scatter(corr_df["avg_tiobe"], corr_df["median_salary"])
    plt.xlabel("Average TIOBE Rating")
    plt.ylabel("Median Salary")
    plt.title("Language Popularity vs Median Salary")
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "tiobe_vs_median_salary.png"))
    plt.close()


def run_hypothesis_tests(df: pd.DataFrame, lang_df: pd.DataFrame) -> pd.DataFrame:
    results = []

    language_counts = lang_df["Language"].value_counts()
    eligible_languages = language_counts[language_counts >= 100].index.tolist()

    anova_groups = []
    used_languages = []

    for lang in eligible_languages:
        group = lang_df.loc[lang_df["Language"] == lang, "LogSalary"].dropna()
        if len(group) >= 30:
            anova_groups.append(group)
            used_languages.append(lang)

    if len(anova_groups) >= 2:
        f_stat, p_val = f_oneway(*anova_groups)
        results.append({
            "Test": "ANOVA_LogSalary_Across_Languages",
            "Statistic": f_stat,
            "P_Value": p_val,
            "Details": f"Languages included: {', '.join(used_languages[:15])}"
        })
    else:
        results.append({
            "Test": "ANOVA_LogSalary_Across_Languages",
            "Statistic": np.nan,
            "P_Value": np.nan,
            "Details": "Not enough eligible language groups"
        })

    remote_group = df.loc[df["RemoteWork"] == "Remote", "LogSalary"].dropna()
    onsite_group = df.loc[df["RemoteWork"] == "In-person", "LogSalary"].dropna()

    if len(remote_group) >= 30 and len(onsite_group) >= 30:
        t_stat, p_val = ttest_ind(remote_group, onsite_group, equal_var=False)
        results.append({
            "Test": "Welch_TTest_LogSalary_Remote_vs_InPerson",
            "Statistic": t_stat,
            "P_Value": p_val,
            "Details": f"Remote n={len(remote_group)}, In-person n={len(onsite_group)}"
        })
    else:
        results.append({
            "Test": "Welch_TTest_LogSalary_Remote_vs_InPerson",
            "Statistic": np.nan,
            "P_Value": np.nan,
            "Details": "Insufficient sample size in one or both groups"
        })

    corr_df = (
        lang_df.groupby("Language", as_index=False)
        .agg(
            median_salary=("ConvertedCompYearly", "median"),
            avg_tiobe=("Avg_TIOBE_Rating", "mean"),
            n=("ConvertedCompYearly", "count"),
        )
        .dropna(subset=["avg_tiobe"])
    )

    corr_df = corr_df[corr_df["n"] >= 30]

    if len(corr_df) >= 3:
        rho, p_val = spearmanr(corr_df["avg_tiobe"], corr_df["median_salary"])
        results.append({
            "Test": "Spearman_TIOBE_vs_MedianSalary",
            "Statistic": rho,
            "P_Value": p_val,
            "Details": f"Languages included: {len(corr_df)}"
        })
    else:
        results.append({
            "Test": "Spearman_TIOBE_vs_MedianSalary",
            "Statistic": np.nan,
            "P_Value": np.nan,
            "Details": "Not enough languages with TIOBE data"
        })

    results_df = pd.DataFrame(results)
    results_df.to_csv(os.path.join(TABLES_DIR, "hypothesis_test_results.csv"), index=False)
    return results_df


def main() -> None:
    ensure_directories()

    survey_df = load_stackoverflow_data()
    tiobe_df = load_tiobe_data()

    clean_df = clean_main_dataset(survey_df)
    lang_df = build_language_level_dataset(clean_df, tiobe_df)

    clean_df.to_csv(os.path.join(PROCESSED_DIR, "analysis_dataset.csv"), index=False)
    lang_df.to_csv(os.path.join(PROCESSED_DIR, "language_salary_with_tiobe.csv"), index=False)

    save_basic_tables(clean_df, lang_df)
    make_figures(clean_df, lang_df)
    results_df = run_hypothesis_tests(clean_df, lang_df)

    print("Analysis completed.")
    print("\nHypothesis test results:")
    print(results_df)


if __name__ == "__main__":
    main()
