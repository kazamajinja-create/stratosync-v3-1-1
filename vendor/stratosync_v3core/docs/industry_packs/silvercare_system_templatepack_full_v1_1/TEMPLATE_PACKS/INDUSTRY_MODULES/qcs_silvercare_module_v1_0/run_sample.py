import json
from pathlib import Path

def main():
    root = Path(__file__).resolve().parent
    sample = json.loads((root / "sample_silvercare_data.json").read_text(encoding="utf-8"))
    print("Loaded sample entity:", sample.get("entity",{}).get("name"))
    print("KPI keys:", list(sample.get("kpi",{}).keys()))

if __name__ == "__main__":
    main()
