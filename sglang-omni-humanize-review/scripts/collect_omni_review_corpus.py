#!/usr/bin/env python3
"""Collect complete public GitHub discussion snapshots with resumable pagination."""

import argparse
import datetime
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import urllib.parse
import uuid

VERSION = 1
DEFAULT_CORPUS = Path(__file__).resolve().parents[1] / "references/omni-review-corpus.jsonl.gz"


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def write_json(path, value):
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")
    temporary.replace(path)


def github_get(endpoint):
    result = subprocess.run(["gh", "api", endpoint], capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(f"GitHub read failed for {endpoint}: {result.stderr.strip()}")
    return json.loads(result.stdout)


def fetch_resource(endpoint, paginated, state_directory, get=github_get):
    cache = state_directory / (hashlib.sha256(endpoint.encode()).hexdigest() + ".json")
    if cache.exists():
        state = json.loads(cache.read_text())
    else:
        state = {"endpoint": endpoint, "pages": [], "complete": False, "started_at": now()}
    if not state["complete"]:
        while True:
            page = len(state["pages"]) + 1
            separator = "&" if "?" in endpoint else "?"
            url = f"{endpoint}{separator}per_page=100&page={page}" if paginated else endpoint
            payload = get(url)
            if paginated and not isinstance(payload, list):
                raise ValueError(f"Expected a list from {url}")
            state["pages"].append(payload)
            state["complete"] = not paginated or len(payload) < 100
            state["finished_at"] = now()
            write_json(cache, state)
            if state["complete"]:
                break
    payload = [row for page in state["pages"] for row in page] if paginated else state["pages"][0]
    provenance = {key: state[key] for key in ("endpoint", "complete", "started_at", "finished_at")}
    provenance["pages"] = len(state["pages"])
    provenance["count"] = len(payload) if paginated else 1
    return payload, provenance


def collect_episode(repository, number, kind, state_directory, get=github_get):
    base = f"repos/{repository}"
    resource = f"{base}/pulls/{number}" if kind == "pr" else f"{base}/issues/{number}"
    metadata, metadata_source = fetch_resource(resource, False, state_directory, get)
    if kind == "issue" and "pull_request" in metadata:
        raise ValueError(f"#{number} is a PR; select it with --pr")
    endpoints = {"conversation": f"{base}/issues/{number}/comments"}
    if kind == "pr":
        endpoints.update({
            "inline": f"{base}/pulls/{number}/comments",
            "reviews": f"{base}/pulls/{number}/reviews",
            "commits": f"{base}/pulls/{number}/commits",
            "files": f"{base}/pulls/{number}/files",
        })
    raw = {"metadata": metadata}
    sources = {"metadata": metadata_source}
    for name, endpoint in endpoints.items():
        raw[name], sources[name] = fetch_resource(endpoint, True, state_directory, get)
    if kind == "pr" and len(raw["files"]) != metadata["changed_files"]:
        raise ValueError(f"#{number} changed-file coverage differs from PR metadata (API cap or concurrent edit); refresh with a fresh state directory")
    if kind == "pr" and len(raw["commits"]) != metadata["commits"]:
        raise ValueError(f"#{number} commit coverage differs from PR metadata (API cap or concurrent edit); use a narrower explicit source scope")
    return {
        "schema_version": VERSION,
        "episode_id": f"{repository}:{kind}:{number}",
        "repository": repository, "kind": kind, "number": number,
        "captured_at": now(), "sources": sources, "raw": raw,
        "completeness": {
            "endpoint_pagination": "complete",
            "scope": "whole PR or issue discussion, not a single interpreted concern",
            "limitations": [
                "Point-in-time REST snapshot; deleted comments and earlier edits are unavailable.",
                "Top-level comments/reviews may not identify the revision being discussed.",
                "Thread resolved/outdated state is not certified by REST; published inline replies retain in_reply_to_id.",
                "Endpoint reads are not an atomic GitHub snapshot; cross-PR links are not expanded.",
            ],
        },
    }


def discover(repository, participant, since, state_directory, get=github_get):
    selected = set()
    coverage = []
    for qualifier in ("commenter", "reviewed-by"):
        query = f"repo:{repository} is:pr {qualifier}:{participant}"
        if since:
            query += f" updated:>={since}"
        pages = []
        for page in range(1, 11):
            endpoint = f"search/issues?q={urllib.parse.quote(query)}&per_page=100&page={page}"
            result, _ = fetch_resource(endpoint, False, state_directory, get)
            if result.get("incomplete_results") or result["total_count"] > 1000:
                raise ValueError("Discovery is incomplete or exceeds GitHub's 1,000-result cap; narrow --since or use explicit --pr selections")
            pages.append(len(result["items"]))
            selected.update(row["number"] for row in result["items"])
            if len(result["items"]) < 100:
                break
        coverage.append({"query": query, "pages": pages, "total_count": result["total_count"]})
    return selected, coverage


def read_corpus(path):
    if not path.exists():
        return {}
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        return {row["episode_id"]: row for row in map(json.loads, handle) if row}


def publish(path, episodes):
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("wb") as output:
        with gzip.GzipFile(fileobj=output, mode="wb", mtime=0) as compressed:
            for identifier in sorted(episodes):
                compressed.write((json.dumps(episodes[identifier], ensure_ascii=False, sort_keys=True) + "\n").encode())
    temporary.replace(path)


def export_run(run):
    exported = {**run, "selection": {key: value for key, value in run["selection"].items() if key != "corpus"}}
    return exported


def event_range(episodes):
    timestamps = []
    for episode in episodes.values():
        raw = episode["raw"]
        for row in [raw["metadata"]] + raw.get("conversation", []) + raw.get("inline", []) + raw.get("reviews", []):
            timestamps.extend(row[key] for key in ("created_at", "updated_at", "submitted_at") if row.get(key))
    return {"earliest": min(timestamps) if timestamps else None, "latest": max(timestamps) if timestamps else None}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default="sgl-project/sglang-omni")
    parser.add_argument("--pr", type=int, action="append", default=[])
    parser.add_argument("--issue", type=int, action="append", default=[])
    parser.add_argument("--participant", help="Discover PRs by commenter/reviewed-by; identity does not affect retrieval ranking")
    parser.add_argument("--since", help="Optional updated-date lower bound for candidate discovery")
    parser.add_argument("--corpus", type=Path, default=DEFAULT_CORPUS)
    parser.add_argument("--state-dir", type=Path, required=True, help="Separate writable checkpoint directory; use a fresh directory for each refresh")
    parser.add_argument("--resume", action="store_true", help="Resume this interrupted attempt; completed endpoint pages are reused")
    args = parser.parse_args()
    if not (args.pr or args.issue or args.participant):
        parser.error("select --pr, --issue, or --participant")
    args.state_dir.mkdir(parents=True, exist_ok=True)
    args.corpus.parent.mkdir(parents=True, exist_ok=True)
    run_path = args.state_dir / "run.json"
    selection = {"repo": args.repo, "pr": sorted(set(args.pr)), "issue": sorted(set(args.issue)), "participant": args.participant, "since": args.since, "corpus": str(args.corpus.resolve())}
    if args.resume:
        run = json.loads(run_path.read_text())
        if run["selection"] != selection or run["status"] == "complete":
            parser.error("resume requires the same selection and an unfinished attempt")
        run.update(status="running")
        run.pop("error", None)
        run.pop("failed_at", None)
    else:
        if any(args.state_dir.iterdir()):
            parser.error("state directory is not empty; use --resume or a fresh directory")
        run = {"collector_version": VERSION, "run_id": str(uuid.uuid4()), "selection": selection, "started_at": now(), "status": "running"}
    write_json(run_path, run)
    metadata_path = args.corpus.with_name("omni-review-corpus.metadata.json")
    previous_metadata = json.loads(metadata_path.read_text()) if metadata_path.exists() else {}
    try:
        episodes = read_corpus(args.corpus)
        candidates = set(args.pr)
        if args.participant:
            discovered, run["discovery"] = discover(args.repo, args.participant, args.since, args.state_dir)
            candidates.update(discovered)
        run["selected"] = {"pr": sorted(candidates), "issue": sorted(set(args.issue))}
        write_json(run_path, run)
        for kind, numbers in (("pr", sorted(candidates)), ("issue", sorted(set(args.issue)))):
            for number in numbers:
                episode = collect_episode(args.repo, number, kind, args.state_dir)
                episodes[episode["episode_id"]] = episode
                print(f"Captured {episode['episode_id']}", file=sys.stderr)
        publish(args.corpus, episodes)
        run.update(status="complete", finished_at=now())
        metadata = {
            "schema_version": VERSION, "collector_version": VERSION,
            "collector_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "corpus_sha256": hashlib.sha256(args.corpus.read_bytes()).hexdigest(),
            "discussion_event_range": event_range(episodes),
            "episode_count": len(episodes),
            "episodes": [{"episode_id": row["episode_id"], "captured_at": row["captured_at"], "sources": row["sources"]} for row in episodes.values()],
            "last_attempt": export_run(run),
            "coverage": "Bounded selected discussions; completeness applies to listed REST endpoints, not all repository history or per-concern resolution.",
            "filtering": "No comment, participant, language, or bot filtering; raw context is retained. Participant queries select candidates only.",
            "refresh_policy": "Upsert selected whole episodes, retain unselected snapshots, refetch every selected endpoint on a new attempt to capture edited/deleted visible comments.",
            "missing": ["Deleted/private/inaccessible history; earlier comment/body revisions; unselected or undiscovered discussions; GraphQL thread resolution."],
        }
        write_json(metadata_path, metadata)
    except (OSError, ValueError, RuntimeError) as error:
        run.update(status="incomplete", failed_at=now(), error=str(error))
        previous_metadata["last_attempt"] = export_run(run)
        write_json(metadata_path, previous_metadata)
        print(f"Incomplete attempt; check recorded corpus hash before use. Resume from {args.state_dir}: {error}", file=sys.stderr)
        return 1
    finally:
        write_json(run_path, run)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
