# Data Profile - 42-station weather CSV

This file documents the expected CSV schema used by the project and gives quick data-profiling guidance.

If you have the original CSV `42-station-meteo-toulouse-parc-compans-cafarelli.csv`, it is expected to contain station-level and observation-level fields. If your dataset differs, adapt the column names in the retriever or the `DataCleaner`.

## Expected columns (suggested schema)

- `station_id`: unique station identifier (string)
- `station_name`: human readable name (string)
- `latitude`: station latitude (float)
- `longitude`: station longitude (float)
- `altitude`: station altitude (float, meters)
- `timestamp`: observation timestamp (ISO 8601 string)
- `temperature_c`: air temperature in °C (float)
- `humidity_pct`: relative humidity in % (float)
- `pressure_hpa`: atmospheric pressure in hPa (float)
- `wind_speed_ms`: wind speed in m/s (float)
- `wind_dir_deg`: wind direction in degrees (int)
- `precip_mm`: precipitation in millimeters (float)

Fields are case-insensitive by default; the project's `DataCleaner` normalizes columns to snake_case.

## Quick profiling steps (pandas)

```python
import pandas as pd

df = pd.read_csv('42-station-meteo-toulouse-parc-compans-cafarelli.csv')
print(df.head())
print(df.dtypes)
print(df.isnull().sum())
print(df.describe(include='all'))
```

## Missing data handling suggestions

- Timestamps: drop or impute if missing; parse with `pd.to_datetime` and set timezone.
- Numerical values: consider filling with sentinel (e.g., NaN) and interpolate or forward-fill where appropriate.
- Station metadata: ensure `station_id` and coordinates exist for spatial joins.

## Example header (synthetic)

```
station_id,station_name,latitude,longitude,altitude,timestamp,temperature_c,humidity_pct,pressure_hpa,wind_speed_ms,wind_dir_deg,precip_mm
PARC_COMPANS,Parc Compans Cafarelli,43.610,-1.443,146,2024-01-01T00:00:00Z,8.2,82,1013.2,3.4,180,0.0
```

## Where to put the file

Place the CSV in the project root or pass its path to the CLI: `python -m projet csv path/to/file.csv`.

## Notes

- If your CSV has different column names, update the mapping in `projet/cleaner.py`.
- For large files, use chunked reading with `pd.read_csv(chunk_size=...)` and process in batches.
