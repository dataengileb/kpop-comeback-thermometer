"""Small JSON-over-HTTP client with retries. Stdlib only, so the Lambdas need no layers."""

import json
import time
import urllib.error
import urllib.parse
import urllib.request

USER_AGENT = "comeback-thermometer/0.1 (+https://github.com/dataengileb)"
RETRYABLE = {429, 500, 502, 503, 504}


def get_json(url: str, params: dict | None = None, retries: int = 4, backoff: float = 1.5) -> dict:
    if params:
        url = f"{url}?{urllib.parse.urlencode(params)}"
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                return json.loads(response.read())
        except urllib.error.HTTPError as err:
            if err.code not in RETRYABLE or attempt == retries:
                raise
        except urllib.error.URLError:
            if attempt == retries:
                raise
        time.sleep(backoff ** attempt)
    raise RuntimeError("unreachable")
