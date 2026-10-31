"""Behavior checks for corpus capture, refresh and mechanism-based retrieval."""

import contextlib
import io
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import collect_omni_review_corpus as collector
import search_omni_review_corpus as searcher


def episode(number, body, path="", author="reviewer", created_at="2026-01-01"):
    return {
        "schema_version": 1, "episode_id": f"org/repo:pr:{number}", "kind": "pr", "number": number,
        "captured_at": created_at,
        "sources": {},
        "raw": {
            "metadata": {"title": "Change", "body": "", "html_url": f"https://github.com/org/repo/pull/{number}"},
            "conversation": [{"id": number, "body": body, "user": {"login": author}}],
            "inline": [{"path": path}] if path else [], "files": [], "reviews": [],
        },
        "completeness": {"endpoint_pagination": "complete"},
    }


class CollectionTests(unittest.TestCase):
    def test_incomplete_changed_file_coverage_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            def get(endpoint):
                return {"changed_files": 1} if endpoint.endswith("pulls/1") else []

            with self.assertRaisesRegex(ValueError, "coverage"):
                collector.collect_episode("org/repo", 1, "pr", Path(directory), get)

    def test_pagination_resumes_after_interruption_without_losing_replies(self):
        with tempfile.TemporaryDirectory() as directory:
            calls = []

            def interrupted(endpoint):
                calls.append(endpoint)
                if "page=2" in endpoint:
                    raise RuntimeError("interrupted")
                return [{"id": number, "body": f"reply {number}"} for number in range(100)]

            with self.assertRaises(RuntimeError):
                collector.fetch_resource("comments", True, Path(directory), interrupted)

            def resumed(endpoint):
                self.assertIn("page=2", endpoint)
                return [{"id": 100, "body": "final author rebuttal"}]

            rows, coverage = collector.fetch_resource("comments", True, Path(directory), resumed)
            self.assertEqual(len(rows), 101)
            self.assertEqual(rows[-1]["body"], "final author rebuttal")
            self.assertEqual(coverage["pages"], 2)
            self.assertTrue(coverage["complete"])

    def test_collect_retains_all_people_revisions_empty_reviews_and_late_replies(self):
        with tempfile.TemporaryDirectory() as directory:
            def get(endpoint):
                if endpoint.endswith("pulls/1"):
                    return {"number": 1, "head": {"sha": "head"}, "changed_files": 0, "commits": 0}
                if "/pulls/1/comments?" in endpoint:
                    return [{"id": number, "in_reply_to_id": 0 if number else None, "commit_id": "old", "body": f"reply {number}", "user": {"login": str(number)}} for number in range(7)]
                if "/reviews?" in endpoint:
                    return [{"body": "", "state": "APPROVED", "commit_id": "new"}]
                return []

            captured = collector.collect_episode("org/repo", 1, "pr", Path(directory), get)
            self.assertEqual(len(captured["raw"]["inline"]), 7)
            self.assertEqual(captured["raw"]["inline"][-1]["commit_id"], "old")
            self.assertEqual(captured["raw"]["reviews"][0]["body"], "")
            self.assertNotIn("outcome", captured)

    def test_refresh_upserts_edited_discussions_and_retains_unselected_episode(self):
        with tempfile.TemporaryDirectory() as directory:
            corpus = Path(directory) / "omni-review-corpus.jsonl.gz"
            original = episode(1, "old comment")
            untouched = episode(2, "other PR")
            collector.publish(corpus, {row["episode_id"]: row for row in (original, untouched)})
            refreshed = episode(1, "edited comment and new author response")
            command = ["collector", "--repo", "org/repo", "--pr", "1", "--corpus", str(corpus), "--state-dir", str(Path(directory) / "new-attempt")]
            with patch.object(sys, "argv", command), patch.object(collector, "collect_episode", return_value={**refreshed, "sources": {}}), contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(collector.main(), 0)
            rows = collector.read_corpus(corpus)
            self.assertEqual(rows[original["episode_id"]]["raw"]["conversation"][0]["body"], "edited comment and new author response")
            self.assertEqual(rows[untouched["episode_id"]], untouched)

    def test_discovery_cap_fails_instead_of_claiming_complete_coverage(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError, "cap"):
                collector.discover("org/repo", "person", None, Path(directory), lambda endpoint: {"total_count": 1001, "incomplete_results": False, "items": []})

    def test_failure_keeps_previous_published_corpus_and_records_gap(self):
        with tempfile.TemporaryDirectory() as directory:
            corpus = Path(directory) / "omni-review-corpus.jsonl.gz"
            original = episode(1, "known raw discussion")
            collector.publish(corpus, {original["episode_id"]: original})
            before = corpus.read_bytes()
            command = ["collector", "--pr", "9", "--corpus", str(corpus), "--state-dir", str(Path(directory) / "attempt")]
            with patch.object(sys, "argv", command), patch.object(collector, "collect_episode", side_effect=RuntimeError("rate limited")), contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(collector.main(), 1)
            self.assertEqual(corpus.read_bytes(), before)
            metadata = json.loads((Path(directory) / "omni-review-corpus.metadata.json").read_text())
            self.assertEqual(metadata["last_attempt"]["status"], "incomplete")

            resumed = {**episode(9, "resumed complete discussion"), "repository": "sgl-project/sglang-omni"}
            with patch.object(sys, "argv", command + ["--resume"]), patch.object(collector, "collect_episode", return_value=resumed), contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(collector.main(), 0)
            metadata = json.loads((Path(directory) / "omni-review-corpus.metadata.json").read_text())
            self.assertEqual(metadata["last_attempt"]["status"], "complete")
            self.assertNotIn("error", metadata["last_attempt"])
            self.assertEqual(len(collector.read_corpus(corpus)), 2)


class SearchTests(unittest.TestCase):
    def test_modified_corpus_is_rejected_when_metadata_hash_disagrees(self):
        with tempfile.TemporaryDirectory() as directory:
            corpus = Path(directory) / "corpus.gz"
            row = episode(1, "body")
            collector.publish(corpus, {row["episode_id"]: row})
            (Path(directory) / "omni-review-corpus.metadata.json").write_text(json.dumps({"corpus_sha256": "wrong"}))
            with self.assertRaisesRegex(ValueError, "hash mismatch"):
                searcher.load_episodes(corpus)

    def test_bundled_raw_snapshot_and_interpretation_provenance(self):
        references = Path(searcher.REFERENCES)
        corpus = references / "omni-review-corpus.jsonl.gz"
        metadata = json.loads((references / "omni-review-corpus.metadata.json").read_text())
        self.assertEqual(metadata["corpus_sha256"], hashlib.sha256(corpus.read_bytes()).hexdigest())
        episodes = {row["episode_id"]: row for row in searcher.load_episodes(corpus)}
        self.assertEqual(len(episodes), metadata["episode_count"])
        for row in episodes.values():
            self.assertTrue(all(source["complete"] for source in row["sources"].values()))
        for note in searcher.load_annotations(references / "omni-review-corpus.annotations.jsonl"):
            raw = episodes[note["episode_id"]]["raw"]
            urls = {raw["metadata"]["html_url"]}
            for channel in ("conversation", "inline", "reviews"):
                urls.update(row["html_url"] for row in raw.get(channel, []))
            for field in ("tags", "background", "code_revision", "concern", "trigger_invariant", "requested_evidence", "response", "outcome", "applicability"):
                statement = note[field]
                self.assertIn(statement["status"], {"observed", "inferred", "author_report", "unknown"})
                self.assertTrue(set(statement["source_urls"]).issubset(urls))
                if statement["status"] != "unknown":
                    self.assertTrue(statement["source_urls"])

    def test_union_recalls_pathless_mechanism_and_condition_discussions(self):
        rows = [episode(1, "exactly-once release after abort"), episode(2, "unrelated", "scheduler.py"), episode(3, "MLX lazy execution")]
        result = searcher.search(rows, [], paths=["scheduler"], mechanisms=["exactly-once release"], conditions=["MLX"])
        self.assertEqual({row["episode_id"] for row in result["matches"]}, {row["episode_id"] for row in rows})
        self.assertEqual(result["matches"][0]["episode_id"], rows[0]["episode_id"])

    def test_ranking_has_no_identity_or_recency_preference(self):
        rows = [episode(1, "slot reuse", author="unknown", created_at="2020-01-01"), episode(2, "slot reuse", author="zhaochenyang20", created_at="2030-01-01")]
        result = searcher.search(rows, [], mechanisms=["slot reuse"])
        self.assertEqual(result["matches"][0]["episode_id"], rows[0]["episode_id"])
        self.assertEqual(result["matches"][0]["rank"], result["matches"][1]["rank"])

    def test_annotation_recall_stays_separate_and_evaluation_pr_is_excluded(self):
        rows = [episode(1, "public request check"), episode(2, "public request check")]
        note = {"episode_id": rows[0]["episode_id"], "mechanism": {"value": "capability mismatch", "status": "inferred", "source_urls": ["url"]}}
        result = searcher.search(rows, [note], mechanisms=["capability mismatch"])
        self.assertEqual(result["matched"], 1)
        self.assertNotIn("mechanism", rows[0])
        self.assertEqual(searcher.search(rows, [note], mechanisms=["capability mismatch"], exclude_prs=[1])["matched"], 0)

    def test_expand_keeps_final_rebuttal_and_does_not_truncate_to_four_comments(self):
        with tempfile.TemporaryDirectory() as directory:
            row = episode(1, "first objection")
            row["raw"]["conversation"] += [{"body": f"reply {number}"} for number in range(8)]
            row["raw"]["conversation"].append({"body": "concern withdrawn with counterexample"})
            corpus = Path(directory) / "corpus.gz"
            collector.publish(corpus, {row["episode_id"]: row})
            result = subprocess.run([sys.executable, str(Path(searcher.__file__)), "--corpus", str(corpus), "--annotations", str(Path(directory) / "none"), "--expand", row["episode_id"]], capture_output=True, text=True, check=True)
            expanded = json.loads(result.stdout)
            self.assertEqual(expanded["episode"]["raw"]["conversation"][-1]["body"], "concern withdrawn with counterexample")
            self.assertEqual(len(expanded["episode"]["raw"]["conversation"]), 10)


if __name__ == "__main__":
    unittest.main()
