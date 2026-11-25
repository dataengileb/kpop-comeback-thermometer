# Evals

Contracts, the quality gate and the gold data tests check that the data has the right shape and obeys the rules. None of them checks that the pipeline picked the right videos. This page covers that part, in five steps: define the task, build a golden dataset, run automated checks, score with a judge, then interpret and act.

## 1. Define the task

**What is evaluated:** the YouTube title matcher (`match_videos` in [`src/ingest_youtube/handler.py`](../src/ingest_youtube/handler.py)). It is the only step where the pipeline makes a judgment rather than a calculation.

| | |
| --- | --- |
| Input | One upload from a tracked channel: video ID, channel, title |
| Output | Either "not a launch", or a launch with its artist, market (`kr`/`jp`) and video type (`mv`/`visual_clip`) |
| Why it matters | A missed music video breaks no contract and fails no data test. It simply never appears, and every rank for that artist is computed against an incomplete history. A false launch, such as a teaser, gets ranked against real releases. |
| Target | Precision 1.0, recall 1.0 and artist/market/type accuracy 1.0 on the labeled golden rows. The set is small and every case is decided by hand, so any miss is a bug rather than noise. |

The rest of the pipeline is deterministic, and each RFP acceptance criterion already has a check:

| [Acceptance criterion](rfp.md#acceptance-criteria) | Checked by |
| --- | --- |
| 1–2. Day 1, 7, 28 values and their ranks | Gold rules in [ADR 4](adr/0004-gold-iceberg-tables-rebuilt-with-merge.md); `CheckGold` data tests in the state machine |
| 3. Never ranked against another artist or market | Ranking partition in the gold MERGE; **gap:** no golden expected values yet (see step 5) |
| 4. Older videos not ranked | `CheckGold`: "day-N values only for comparable videos", "only comparable originals are ranked" |
| 5. Data date shown, no request to AWS | `site_video` contract on the export; the site reads only `site/data/` |
| 6. Same day processed twice gives the same numbers | `tests/test_quality_gate.py`, MERGE on stable keys |
| 7. The question word for word, EN and ES | Fixed text in `site/app.js` |

## 2. Build the golden dataset

[`evals/golden/youtube_titles.jsonl`](../evals/golden/youtube_titles.jsonl), one upload per line:

```json
{"video_id": "eHHQaoEW30Q", "channel": "@JYPEntertainment", "published_at": "2025-07-11",
 "title": "TWICE \"THIS IS FOR\" M/V",
 "expected": {"artist": "twice", "market": "kr", "video_type": "mv"},
 "status": "labeled", "note": "official full video"}
```

`expected` is `null` for an upload that is not a launch. `status` is `labeled`, or `needs_review` while a row waits for a verdict. `note` gives the reason in a few words.

It was seeded on 2026-11-25 from the bronze snapshot of that day: 7,678 uploads across the four channels, of which 687 are in the set.

- **104 launches.** Every one was checked by hand against the rubric in step 4.
- **577 hard negatives.** These are uploads that name a tracked artist and look like a release but are not one: 136 teasers, 87 performances or stages, 87 alternate versions, 71 short versions, 54 reactions or behind-the-scenes, 43 concept films, 33 audio, lyric or visualizer uploads, 14 promos, 9 special clips and 1 director's cut. There are also 42 music videos by other JYP artists. Some of those contain a tracked name, such as GOT7 "NOT BY THE MOON".
- **6 rows awaiting a verdict**, listed in the eval log.

The launches were seeded from the matcher's own output, so the first score of 1.0 proves only that nothing has regressed. Evidence for recall comes from the sweep: every upload that names a tracked artist and looks like a video is in the set and was judged, so a release the matcher skipped would have shown up as a disagreement.

Rows are never deleted. A changed verdict edits the row and says why in `note`.

## 3. Run automated checks

```bash
python evals/run.py
```

This scores the matcher on every labeled row and prints precision, recall, field accuracy, recall by artist, each disagreement, and the rows awaiting a verdict. It exits 1 on any disagreement. `pytest` runs the same check (`tests/test_evals.py`), so a change to the matcher or to `artists.json` that breaks a golden row fails the tests.

```bash
./scripts/eval_titles.sh
```

This is the weekly sweep, run together with the Monday site refresh. It scores the golden set, downloads the uploads from the latest bronze snapshot and writes `evals/review/<date>.jsonl`, which git ignores. That file holds every upload not yet in the golden set that the matcher took, or that names a tracked artist and looks like a video. Each line is already a golden row with `status: needs_review`.

## 4. Score with a judge

The judge is the project owner, who applies this rubric to each row in the review file.

An upload is a **launch** only if all of these hold:
1. It is the official, full-length video for one song, uploaded to a channel in `artists.json`.
2. It is credited to one tracked act as the lead artist. A collaboration billed to several acts is not a launch for any of them.
3. Its type is in `artists.json`: `mv` for a music video, or `visual_clip` for a tripleS Special Visual Clip of a song.

It is **not a launch** if it is a teaser, trailer or intro; a short or vertical version; a director's cut; an alternate edit (member, stage, choreography or "… Ver." cuts); a performance, stage or live video; a lyric video, audio upload or visualizer; a concept or story film; a reaction or behind-the-scenes video; or a promo.

- **Market:** `jp` if the channel is a Japan channel or the title marks a Japanese version; otherwise `kr`.
- **Duplicate uploads** of the same video are each a launch here. Gold keeps the most-viewed copy ([ADR 4](adr/0004-gold-iceberg-tables-rebuilt-with-merge.md)).
- **An act missing from `artists.json`** is not a launch. If it should be tracked, that is a change request ([SOW §8](sow.md#8-change-control)), not a label.

The verdict is the row's `expected` value and `note`, with `status` set to `labeled`. The judged row is then appended to the golden set.

**Why the judge is a person, not a model.** An LLM judge pays off when outputs are open-ended, such as summaries or answers, and exact match can't score them. Here every case has one right answer, and a person who knows the artists can give it in seconds. A model judge inside the pipeline would also add cost and nondeterminism to an AWS-only, zero-cost batch. A model can draft verdicts offline to speed up a long review file, but the owner signs each one.

## 5. Interpret and act

| Result | Action |
| --- | --- |
| **Missed launch** | Fix the matcher or `artists.json` (`title_names`, `titled_under_parent`, a video-type suffix). Use `extra_mv_ids` only for a one-off title. Keep the row so the miss cannot come back. |
| **False launch** | Tighten the pattern or the suffix. Keep the row as a negative. |
| **Wrong artist, market or type** | Fix the prefix rules or `market_of`, and check every row for that artist. |
| **New format seen in the sweep** | Add a few examples as golden rows before changing the code. |
| **Act not in `artists.json`** | Note it in the eval log. Track it only through a change request. |

Never change a golden label to make a test pass. If the label is wrong, fix it with a reason in `note`, and say so in the pull request.

**Next eval: the gold rules.** Criteria 1–3 have invariant checks but no expected values. The next step is a small synthetic silver fixture, with known day 1, 7 and 28 values and known ranks, run through the same MERGE in Athena.

### Eval log

| Date | Golden rows | Precision | Recall | Field accuracy | Findings and actions |
| --- | --- | --- | --- | --- | --- |
| 2026-11-25 | 687 (6 awaiting a verdict) | 1.000 | 1.000 | 1.000 | Seeded. Awaiting the owner's verdict: tripleS 「やがてそれは、夏だった」 Special Visual Clip (song title first, so the matcher skips it); three uploads of "tripleS AAA Generation : M/V Ver."; the JYP collaboration "Like Magic" (J.Y. Park, Stray Kids, ITZY, NMIXX); tripleS Acid Eyes "Cherry Gene" Visualizer (Acid Eyes is not in `artists.json`). |
