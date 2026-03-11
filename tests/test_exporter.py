from pathlib import Path

from src.exporter import Exporter


def test_exporter_writes_csv_and_xlsx():
    output_dir = Path("tests/.artifacts")
    output_dir.mkdir(parents=True, exist_ok=True)
    exporter = Exporter(output_dir=output_dir)
    rows = [{"a": 1, "b": "x"}]

    csv_path = exporter.export_csv(rows, "out.csv")
    xlsx_path = exporter.export_xlsx({"sheet": rows}, "out.xlsx")

    assert csv_path.exists()
    assert xlsx_path.exists()
