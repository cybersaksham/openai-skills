---
name: raise-pr-and-send-to-slack
description: Use when the user asks to create a GitHub pull request and post a Slack review-request message with the PR link. Includes Jira-aware PR title formatting, defaults Slack posting to the `#development` channel when no channel is specified, and requires strict Slack bot-token usage.
---

# Raise PR and Send to Slack

Use this skill when the user asks to:

- raise/create/open a PR, and
- send a Slack message with that PR link for review.

## Mandatory Tooling

- Use **GitHub MCP** for PR creation (`mcp__github__create_pull_request`).
- Use **Slack Web API** (`curl`) for Slack posting.
- For Slack auth, use **only** `SLACK_BOT_TOKEN`.
  - Never use `SLACK_USER_TOKEN`.
  - Never use `SLACK_TOKEN` fallback.
  - Never use any other Slack token or token alias in any case.
  - If `SLACK_BOT_TOKEN` is missing, stop and ask the user to set it.

## Workflow

1. Prepare branch and changes

- Ensure intended files are committed.
- Push the branch to origin.

2. Build PR title

- Start from a clear human title.
- If Jira ticket is involved in the conversation, prefix PR title as:
  - `NS-<id>: <title>`
- Jira involvement rules:
  - Detect any `NS-<digits>` in user conversation/context.
  - If multiple IDs are present, use the latest user-mentioned ID unless user specifies one.

3. Create PR with GitHub MCP

- Use `mcp__github__create_pull_request`.
- Capture returned PR URL.

4. Send Slack message via Slack Web API

- If no Slack channel is specified by the user, use `#development`.
- Resolve target channel name to channel ID using `conversations.list`.
- Resolve `@core-dev` as usergroup mention using `usergroups.list`.
- Post message using `chat.postMessage`.
- Message format must be exactly:

```text
@core-dev Please review and merge
<pr_link>
```

- Prefer rich-text entities for mentions/links and include plain-text fallback.

## Slack API Requirements

- Token env key: `SLACK_BOT_TOKEN` only.
- Required scopes: `chat:write`, `channels:read`, `groups:read`, `users:read`, `usergroups:read`.
- Use API calls:
  - `conversations.list`
  - `usergroups.list`
  - `chat.postMessage`

## Output Expectations

After posting:

- Report PR URL.
- Report Slack post result: `ok`, `channel`, `ts`.
- Explicitly report token env key used: `SLACK_BOT_TOKEN`.

If anything fails:

- Show exact API error (`missing_scope`, `channel_not_found`, etc.).
- Stop and ask only for the missing prerequisite.
