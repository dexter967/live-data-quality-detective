# Obstacle Log: Data Quality Detective

### Obstacle 1: Flattening Nested JSON Responses
- **Issue**: Public e-commerce APIs like DummyJSON return deeply nested JSON structures (e.g., nested `dimensions` or `meta` sub-dictionaries). Direct loading into pandas DataFrame resulted in unparsed dict objects within DataFrame cells.
- **Resolution**: Utilized `pd.json_normalize()` on the records payload to automatically flatten nested keys into discrete dot-notated columns (e.g., `dimensions.width`), enabling proper scalar analysis.

### Obstacle 2: Heterogeneous Payload Key Enclosures
- **Issue**: Different public REST APIs structure list responses under distinct top-level keys (e.g., standard lists vs object responses like `{"products": [...]}`).
- **Resolution**: Implemented defensive payload extraction inspecting payload types dynamically before DataFrame conversion (`payload.get("products", payload)`).

### Obstacle 3: Safe Outlier and Missing Value Detection
- **Issue**: Direct application of interquartile range (IQR) calculation failed when data types were inferred improperly as objects due to `None` values.
- **Resolution**: Cast numerical columns explicitly after imputation step and applied conditional filtering using `.isnull()` before calculating percentile metrics.
