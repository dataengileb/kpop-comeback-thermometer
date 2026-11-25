"""Evaluate the YouTube title matcher against the golden dataset, or list new uploads to judge.

    python evals/run.py                      # score the matcher on evals/golden/youtube_titles.jsonl
    python evals/run.py --bronze DIR         # list uploads in a bronze snapshot that need a verdict

Golden mode exits 1 if any labeled row disagrees with the matcher. Rows marked "needs_review"
are reported but not scored: they wait for a verdict (see docs/evals.md).
"""

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from ingest_youtube.handler import match_videos  # noqa: E402

GOLDEN = ROOT / "evals" / "golden" / "youtube_titles.jsonl"
CONFIG = ROOT / "src" / "config" / "artists.json"
FIELDS = ("artist", "market", "video_type")


def load_config() -> dict:
    return json.loads(CONFIG.read_text(encoding="utf-8"))


def load_golden(path: Path = GOLDEN) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def predict(uploads: list[dict], config: dict) -> dict[str, dict | None]:
    """Run the production matcher on uploads ({video_id, channel, title}) as one page per channel."""
    by_channel = defaultdict(list)
    for u in uploads:
        by_channel[u["channel"]].append(
            {"snippet": {"title": u["title"], "resourceId": {"videoId": u["video_id"]}}})
    markets = {c["handle"]: c["market"] for c in config["channels"]}
    predictions = {u["video_id"]: None for u in uploads}
    for handle, items in by_channel.items():
        artists = [a for a in config["artists"] if handle in a["channels"]]
        found = match_videos([{"items": items}], artists, markets[handle], config["video_types"], config["artists"])
        for video_id, match in found.items():
            predictions[video_id] = {f: match[f] for f in FIELDS}
    return predictions


def score(rows: list[dict], predictions: dict) -> dict:
    """Counts for launch detection, plus rows whose artist, market or type is wrong."""
    counts = Counter()
    errors = []
    for row in rows:
        if row["status"] != "labeled":
            continue
        expected, got = row["expected"], predictions[row["video_id"]]
        if expected and got:
            counts["tp"] += 1
            wrong = [f for f in FIELDS if expected[f] != got[f]]
            if wrong:
                counts["wrong_fields"] += 1
                errors.append(("wrong " + ", ".join(wrong), row, got))
        elif expected:
            counts["fn"] += 1
            errors.append(("missed", row, got))
        elif got:
            counts["fp"] += 1
            errors.append(("false launch", row, got))
        else:
            counts["tn"] += 1
    tp, fp, fn = counts["tp"], counts["fp"], counts["fn"]
    return {
        "counts": dict(counts),
        "precision": tp / (tp + fp) if tp + fp else 1.0,
        "recall": tp / (tp + fn) if tp + fn else 1.0,
        "field_accuracy": (tp - counts["wrong_fields"]) / tp if tp else 1.0,
        "errors": errors,
    }


def recall_by_artist(rows: list[dict], predictions: dict) -> dict[str, str]:
    hits, totals = Counter(), Counter()
    for row in rows:
        if row["status"] == "labeled" and row["expected"]:
            artist = row["expected"]["artist"]
            totals[artist] += 1
            hits[artist] += predictions[row["video_id"]] is not None
    return {a: f"{hits[a]}/{totals[a]}" for a in sorted(totals)}


def golden_report() -> int:
    rows, config = load_golden(), load_config()
    predictions = predict(rows, config)
    result = score(rows, predictions)
    pending = [r for r in rows if r["status"] == "needs_review"]
    c = result["counts"]
    print(f"Golden rows: {len(rows)} ({len(rows) - len(pending)} labeled, {len(pending)} awaiting a verdict)")
    print(f"Launches found {c.get('tp', 0)}, missed {c.get('fn', 0)}, false {c.get('fp', 0)}, "
          f"correct non-launches {c.get('tn', 0)}")
    print(f"Precision {result['precision']:.3f} · recall {result['recall']:.3f} · "
          f"artist/market/type accuracy {result['field_accuracy']:.3f}")
    print("Recall by artist: " + ", ".join(f"{a} {v}" for a, v in recall_by_artist(rows, predictions).items()))
    for kind, row, got in result["errors"]:
        print(f"  {kind}: {row['video_id']} {row['title']!r} expected={row['expected']} got={got}")
    for row in pending:
        print(f"  awaiting verdict: {row['video_id']} {row['title']!r} matcher says {predictions[row['video_id']]}")
    return 1 if result["errors"] else 0


def review_candidates(bronze: Path) -> int:
    """Uploads not yet in the golden set that the matcher took, or that name a tracked artist and
    look like a video release. Each line is a golden row with status "needs_review"."""
    config, known = load_config(), {r["video_id"] for r in load_golden()}
    names = {n for a in config["artists"] for n in [a["name"], *(a.get("title_names") or [])] if len(n) > 3}
    mentions = re.compile("|".join(re.escape(n) for n in sorted(names, key=len, reverse=True)), re.IGNORECASE)
    looks_like_video = re.compile(r"M/?V|Music\s*Video|Visual|Clip|Film|Ver\.", re.IGNORECASE)
    uploads = []
    for channel in config["channels"]:
        path = bronze / f"uploads_{channel['handle'].lstrip('@').lower()}.json"
        for page in json.loads(path.read_text(encoding="utf-8")):
            for item in page.get("items") or []:
                s = item["snippet"]
                if s["resourceId"]["videoId"] not in known:
                    uploads.append({"video_id": s["resourceId"]["videoId"], "channel": channel["handle"],
                                    "published_at": s["publishedAt"][:10], "title": s["title"]})
    uploads = list({u["video_id"]: u for u in uploads}.values())
    predictions = predict(uploads, config)
    count = 0
    for u in sorted(uploads, key=lambda u: u["published_at"], reverse=True):
        got = predictions[u["video_id"]]
        if got or (mentions.search(u["title"]) and looks_like_video.search(u["title"])):
            print(json.dumps({**u, "expected": got, "status": "needs_review",
                              "note": "matcher took it" if got else "names a tracked artist; matcher skipped it"},
                             ensure_ascii=False))
            count += 1
    print(f"{count} uploads to judge", file=sys.stderr)
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--bronze", type=Path, help="folder with a day's bronze uploads_<channel>.json files")
    args = parser.parse_args()
    sys.exit(review_candidates(args.bronze) if args.bronze else golden_report())
