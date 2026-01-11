import json
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path

# Ensure data directory exists
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

# Generate synthetic call-level data
base = datetime(2026, 1, 10, 14, 0)

rows = []
for i in range(50):
    rows.append({
        "call_id": f"call_{i}",
        "client_id": "bank_01" if i < 30 else "bank_02",
        "start_time": (base + timedelta(minutes=i)).isoformat(),
        "duration_sec": 60 + i * 3,
        "status": "completed" if i % 5 != 0 else "dropped",
        "resolution": (
            "promise_to_pay"
            if i % 4 == 0
            else "paid"
            if i % 7 == 0
            else "none"
        ),
        "llm_latency_ms": 280 + (i % 10) * 15
    })

df = pd.DataFrame(rows)

# Write CSV
csv_path = DATA_DIR / "calls.csv"
df.to_csv(csv_path, index=False)

# Write JSON (array format)
json_path = DATA_DIR / "calls.json"
with open(json_path, "w") as f:
    json.dump(rows, f, indent=2)

print(f"Created {csv_path}")
print(f"Created {json_path}")
