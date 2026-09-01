# sglang-omni-release-note

Reusable skill for producing evidence-based SGLang-Omni release highlights and concise Chinese WeChat announcements.

## Install

Copy the skill directory into the repository's Claude skill folder:

```bash
mkdir -p .claude/skills
cp -R sglang-omni-release-note .claude/skills/
```

Expected layout:

```text
.claude/skills/sglang-omni-release-note/
├── SKILL.md
├── README.md
├── examples/
│   └── v0.1.1-to-current-wechat.md
└── references/
    ├── editorial-rules.md
    ├── evidence-workflow.md
    └── output-templates.md
```

## Example Prompts

```text
Use the sglang-omni-release-note skill. Summarize the major changes from v0.1.1 to current main for a Chinese WeChat post. GitHub will auto-generate the detailed PR list, so return only the four-pillar human summary.
```

```text
Use the sglang-omni-release-note skill. Create an expanded Chinese announcement for v0.1.2.post1. Verify merged PRs against the release cutoff, retain opt-in/experimental qualifiers, and use no more than three headline metrics.
```

```text
Use the sglang-omni-release-note skill. Produce only the editorial intro and four highlights that will appear above GitHub's automatically generated release notes.
```
