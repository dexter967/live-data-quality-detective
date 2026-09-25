import os

# Primary API endpoint (DummyJSON products endpoint returns 100 items by default)
API_URL = os.getenv("DATA_API_URL", "https://dummyjson.com/products?limit=100")

# HTTP timeout limit in seconds
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "10"))

# File path settings
RAW_DATASET_PATH = os.getenv("RAW_DATASET_PATH", "raw_dataset.csv")
CLEANED_DATASET_PATH = os.getenv("CLEANED_DATASET_PATH", "cleaned_dataset.csv")
FALLBACK_DATA_PATH = os.getenv("FALLBACK_DATA_PATH", "sample_products.json")
REPORT_PATH = os.getenv("REPORT_PATH", "quality_report.md")
