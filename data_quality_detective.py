import os
import json
import requests
import pandas as pd

API_URL = os.getenv("DATA_API_URL", "https://dummyjson.com/products?limit=100")
TIMEOUT = 10


def fetch_data() -> pd.DataFrame:
    """Fetch product data from public REST API with offline fallback handling."""
    print("Fetching dataset from API...")
    try:
        response = requests.get(API_URL, timeout=TIMEOUT)
        response.raise_for_status()
        payload = response.json()
        
        # Handle API payload variants (DummyJSON vs standard list)
        items = payload.get("products", payload) if isinstance(payload, dict) else payload
        df = pd.json_normalize(items)
        print(f"Successfully retrieved {len(df)} records from API.")
        return df

    except (requests.exceptions.RequestException, ValueError) as err:
        print(f"[WARNING] API fetch failed: {err}. Loading fallback data 'sample_products.json'...")
        if os.path.exists("sample_products.json"):
            with open("sample_products.json", "r", encoding="utf-8") as f:
                items = json.load(f)
            return pd.json_normalize(items)
        else:
            raise FileNotFoundError("Neither API nor local fallback file 'sample_products.json' is available.")


def analyze_data_quality(df: pd.DataFrame) -> dict:
    """Detect missing values, duplicates, and out-of-range/suspicious values."""
    metrics = {}
    
    # Total Records & Columns
    metrics["total_rows"] = len(df)
    metrics["total_cols"] = len(df.columns)
    
    # 1. Missing Values
    metrics["missing_per_column"] = df.isnull().sum().to_dict()
    metrics["total_missing_values"] = int(df.isnull().sum().sum())
    
    # 2. Duplicate Entries
    metrics["duplicate_rows"] = int(df.duplicated().sum())
    
    # 3. Suspicious Values (Negative/Zero Prices or Extreme Outliers)
    metrics["negative_prices"] = 0
    metrics["extreme_outliers"] = 0
    
    if "price" in df.columns:
        metrics["negative_prices"] = int((df["price"] <= 0).sum())
        q3 = df["price"].quantile(0.75)
        iqr = q3 - df["price"].quantile(0.25)
        upper_bound = q3 + (3 * iqr)
        metrics["extreme_outliers"] = int((df["price"] > upper_bound).sum())
        
    return metrics


def clean_dataset(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Clean the dataset: drop duplicate rows, fill missing values, and flag or filter invalid prices."""
    cleaned_df = df.copy()
    changes = {}
    
    # 1. Deduplication
    initial_count = len(cleaned_df)
    cleaned_df = cleaned_df.drop_duplicates()
    changes["duplicates_removed"] = initial_count - len(cleaned_df)
    
    # 2. Impute Missing Values
    missing_before = int(cleaned_df.isnull().sum().sum())
    if "price" in cleaned_df.columns:
        median_price = cleaned_df["price"].median()
        cleaned_df["price"] = cleaned_df["price"].fillna(median_price)
    
    cleaned_df = cleaned_df.fillna("Unknown")
    changes["missing_imputed"] = missing_before - int(cleaned_df.isnull().sum().sum())
    
    # 3. Handle Invalid Prices (Replace negative/zero values with column median)
    if "price" in cleaned_df.columns:
        invalid_mask = cleaned_df["price"] <= 0
        changes["invalid_prices_corrected"] = int(invalid_mask.sum())
        median_valid_price = cleaned_df.loc[~invalid_mask, "price"].median()
        cleaned_df.loc[invalid_mask, "price"] = median_valid_price

    return cleaned_df, changes


def generate_markdown_report(metrics: dict, changes: dict, df_raw: pd.DataFrame, df_clean: pd.DataFrame):
    """Generate Markdown report summarizing dataset metrics and findings."""
    report = f"""# 📊 Data Quality Detective Report

## 1. Executive Summary
- **Raw Records Analyzed**: {metrics['total_rows']}
- **Total Columns**: {metrics['total_cols']}
- **Duplicate Rows Detected**: {metrics['duplicate_rows']}
- **Total Missing Values**: {metrics['total_missing_values']}
- **Negative / Zero Price Entries**: {metrics['negative_prices']}
- **Extreme Price Outliers**: {metrics['extreme_outliers']}

---

## 2. Detailed Data Quality Issues
### Missing Values per Column
