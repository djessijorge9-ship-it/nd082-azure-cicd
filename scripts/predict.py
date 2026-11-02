"""Send the supplied example to a local server or an explicit HTTPS deployment."""
import argparse
import json
from pathlib import Path
import time
from urllib.error import URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


def wait_for_deployment(base_url, expected_heading, timeout=180):
    """Require model readiness and the expected release before prediction."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            remaining = max(1, deadline - time.monotonic())
            with urlopen(base_url.rstrip("/") + "/health",
                         timeout=min(15, remaining)) as response:
                health = json.load(response)
            if isinstance(health, dict) and health.get("status") == "ready":
                remaining = max(1, deadline - time.monotonic())
                with urlopen(base_url.rstrip("/") + "/",
                             timeout=min(15, remaining)) as response:
                    homepage = response.read().decode("utf-8")
                if expected_heading in homepage:
                    print("Application health and expected release ready")
                    return
        except (URLError, TimeoutError, ValueError):
            pass
        remaining = deadline - time.monotonic()
        if remaining > 0:
            print("Waiting for application health and expected release", flush=True)
            time.sleep(min(5, remaining))
    raise RuntimeError("Application did not serve the expected ready release within "
                       f"{timeout} seconds")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("base_url", help="http://127.0.0.1:5000 or deployed HTTPS URL")
    parser.add_argument("--wait-for-heading",
                        help="Require this deployed homepage text before predicting")
    args = parser.parse_args()
    target = urlparse(args.base_url)
    if target.scheme != "https" and not (target.scheme == "http" and
                                         target.hostname in ("127.0.0.1", "localhost")):
        parser.error("Use HTTPS for remote deployments")
    if args.wait_for_heading:
        wait_for_deployment(args.base_url, args.wait_for_heading)
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
