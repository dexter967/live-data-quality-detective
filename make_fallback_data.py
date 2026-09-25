import json

# Generates sample dataset with synthetic data quality issues (missing values, duplicates, outliers)
sample_data = [
    {"id": i, "title": f"Product {i}", "price": round(10.0 + (i * 2.5), 2), "category": "electronics", "rating": {"rate": 4.1, "count": 100 + i}}
    for i in range(1, 101)
]

# Introduce intentionally messy records for detection
sample_data[5]["price"] = None  # Missing value
sample_data[12]["price"] = -50.0  # Suspicious negative price
sample_data[15]["title"] = None  # Missing title
sample_data.append(sample_data[0].copy())  # Exact duplicate entry
sample_data[45]["price"] = 99999.0  # Outlier price

with open("sample_products.json", "w", encoding="utf-8") as f:
    json.dump(sample_data, f, indent=2)

print("Generated sample_products.json successfully.")
