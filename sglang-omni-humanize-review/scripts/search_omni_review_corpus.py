#!/usr/bin/env python3
"""Recall historical candidates by union of component, mechanism and condition routes."""

import argparse
import gzip
import hashlib
import json
from pathlib import Path

REFERENCES = Path(__file__).resolve().parents[1] / "references"


def load_episodes(path):
    metadata_path = path.with_name("omni-review-corpus.metadata.json")
    if metadata_path.exists():
        metadata = json.loads(metadata_path.read_text())
        expected = metadata.get("corpus_sha256")
        if expected and hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError("Corpus/metadata hash mismatch; refresh or resume capture before using historical evidence")
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def load_annotations(path):
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def search(episodes, annotations, paths=(), symbols=(), mechanisms=(), conditions=(), exclude_prs=()):
    matches = []
    eligible = 0
    for episode in episodes:
        if episode["kind"] == "pr" and episode["number"] in exclude_prs:
            continue
        eligible += 1
        notes = [note for note in annotations if note["episode_id"] == episode["episode_id"]]
        raw = episode["raw"]
        bodies = [raw["metadata"].get("title", ""), raw["metadata"].get("body") or ""]
        for name in ("conversation", "inline", "reviews"):
            bodies.extend(row.get("body") or "" for row in raw.get(name, []))
        text = "\n".join(bodies).lower()
        path_text = "\n".join([row.get("path", "") for row in raw.get("inline", [])] + [row["filename"] for row in raw.get("files", [])]).lower()
        component_text = text + "\n" + path_text + "\n" + "\n".join(row.get("patch", "") for row in raw.get("files", [])) + "\n" + "\n".join(row.get("diff_hunk", "") for row in raw.get("inline", []))
        component_text = component_text.lower()
        interpreted = json.dumps(notes, ensure_ascii=False).lower()
        routes = {
            "component": sorted({term for term in paths if term.lower() in path_text} | {term for term in symbols if term.lower() in component_text}),
            "mechanism": sorted({term for term in mechanisms if term.lower() in text or term.lower() in interpreted}),
            "condition": sorted({term for term in conditions if term.lower() in text or term.lower() in interpreted}),
        }
        if not any(routes.values()):
            continue
        matches.append({
            "episode_id": episode["episode_id"], "url": raw["metadata"]["html_url"],
            "title": raw["metadata"]["title"], "routes": routes,
            "rank": [len(routes["mechanism"]), len(routes["condition"]), len(routes["component"])],
            "pagination": episode["completeness"]["endpoint_pagination"],
            "navigation_only": True,
            "discussion_counts": {name: len(raw.get(name, [])) for name in ("conversation", "inline", "reviews")},
            "annotation_summaries": [{"annotation_id": note.get("annotation_id"), "concern": note.get("concern"), "tags": note.get("tags")} for note in notes],
        })
    matches.sort(key=lambda row: (tuple(-count for count in row["rank"]), row["episode_id"]))
    return {"scanned": len(episodes), "eligible": eligible, "excluded_prs": sorted(set(exclude_prs)), "matched": len(matches), "matches": matches}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", type=Path, default=REFERENCES / "omni-review-corpus.jsonl.gz")
    parser.add_argument("--annotations", type=Path, default=REFERENCES / "omni-review-corpus.annotations.jsonl")
    parser.add_argument("--path", action="append", default=[])
    parser.add_argument("--symbol", action="append", default=[])
    parser.add_argument("--mechanism", action="append", default=[])
    parser.add_argument("--condition", action="append", default=[])
    parser.add_argument("--exclude-pr", type=int, action="append", default=[])
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--expand", help="Print the entire raw episode plus separate annotations, with no comment truncation")
    args = parser.parse_args()
    episodes = load_episodes(args.corpus)
    annotations = load_annotations(args.annotations)
    if args.expand:
        rows = [row for row in episodes if row["episode_id"] == args.expand and not (row["kind"] == "pr" and row["number"] in args.exclude_pr)]
        if not rows:
            parser.error("episode not found or excluded")
        print(json.dumps({"episode": rows[0], "interpretations": [note for note in annotations if note["episode_id"] == args.expand]}, ensure_ascii=False, indent=2))
        return 0
    if args.limit < 1 or not any((args.path, args.symbol, args.mechanism, args.condition)):
        parser.error("supply at least one route term and a positive --limit")
    result = search(episodes, annotations, args.path, args.symbol, args.mechanism, args.condition, args.exclude_pr)
    result["matches"] = result["matches"][:args.limit]
    result["ranking"] = "Lexical mechanism, condition, component hits; no reviewer identity or recency boost. Navigation only; applicability requires current-code analysis."
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
