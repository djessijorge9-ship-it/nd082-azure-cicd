"""Send the supplied example to a local server or an explicit HTTPS deployment."""
import argparse
import json
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("base_url", help="http://127.0.0.1:5000 or deployed HTTPS URL")
    args = parser.parse_args()
    target = urlparse(args.base_url)
    if target.scheme != "https" and not (target.scheme == "http" and
                                         target.hostname in ("127.0.0.1", "localhost")):
        parser.error("Use HTTPS for remote deployments")
    payload = Path(__file__).resolve().parents[1] / "sample-payload.json"
    request = Request(args.base_url.rstrip("/") + "/predict", data=payload.read_bytes(),
                      headers={"Content-Type": "application/json"}, method="POST")
    with urlopen(request, timeout=30) as response:  # nosec: validated explicit destination
        result = json.load(response)
    if not isinstance(result.get("prediction"), list) or len(result["prediction"]) != 1:
        raise ValueError("Deployment returned an unexpected prediction response")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
