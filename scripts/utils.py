from pathlib import Path

base = Path(__file__).resolve().parents[1]
data_path = base/"data"
if not data_path.exists():
    data_path.mkdir(parents=True)