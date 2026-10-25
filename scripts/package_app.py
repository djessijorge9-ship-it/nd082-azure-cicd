"""Build a small App Service source archive with a strict file allowlist."""
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]
FILES = ("app.py", "requirements.txt", "startup.txt",
         "Housing_price_model/LinearRegression.joblib")


def main():
    output = ROOT / "dist" / "app.zip"
    output.parent.mkdir(exist_ok=True)
    with ZipFile(output, "w", ZIP_DEFLATED) as archive:
        for relative in FILES:
            archive.write(ROOT / relative, relative)
    print(f"Created {output} ({output.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
