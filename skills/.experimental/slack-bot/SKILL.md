---
name: "slack-bot"
description: "Use when the user needs to post Slack messages as a bot or user using environment tokens, choose a bot by name, resolve channel names and @mentions to IDs, and send rich-text messages via Slack Web API calls (curl/PowerShell) without a bundled script."
---

# Slack Bot Posting (API-Only)

## Workflow

Use direct Slack Web API calls (`curl` on macOS/Linux, `curl.exe` or `Invoke-RestMethod` on Windows). Do not rely on bundled scripts.

1. Select token from environment using actor + optional bot name.
2. Resolve channel name to channel ID (unless input is already `C...`/`G...`/`D...`).
3. Resolve plain `@mentions` to Slack user IDs.
4. Build rich-text blocks that use user and broadcast elements.
5. Call `chat.postMessage`.

## Inputs

- `actor`: `bot` or `user`
- `bot_name`: optional; valid only for `actor=bot`
- `channel`: `#name`, `name`, or channel ID
- `message`: text content that may include mentions

## Token selection rules

- Never ask users to paste raw tokens in chat. Ask them to set env vars locally.
- For `actor=bot` with `bot_name`, normalize bot name to env suffix: uppercase + non-alnum to `_`.
  - Example: `release-bot` -> `SLACK_BOT_TOKEN_RELEASE_BOT`
- Resolution order:
  - Bot + bot_name: `SLACK_BOT_TOKEN_<NORMALIZED_NAME>` -> `SLACK_BOT_TOKEN` -> `SLACK_TOKEN`
  - Bot without bot_name: `SLACK_BOT_TOKEN` -> `SLACK_TOKEN`
  - User: `SLACK_USER_TOKEN` -> `SLACK_TOKEN`
- If `bot_name` is provided and named token is missing but fallback token exists, ask for confirmation before fallback.
- If fallback is not approved, stop and ask the user to set the named token.

## Required API scopes

- `chat:write`
- `users:read`
- `channels:read` for public channels
- `groups:read` for private channels

## API calls

### 1) Resolve channel

If channel input is not an ID, call `conversations.list` with pagination and match by name (case-insensitive):

```bash
curl -sS -H "Authorization: Bearer $SLACK_TOKEN_IN_USE" \
  "https://slack.com/api/conversations.list?exclude_archived=true&limit=1000&types=public_channel,private_channel,mpim,im"
```

Use `response_metadata.next_cursor` until found or exhausted.

### 2) Resolve mentions

Parse message mentions:

- Existing `<@U...>`: keep as explicit user mention.
- Existing `<!here>`, `<!channel>`, `<!everyone>`: keep as broadcast mention.
- Plain `@alias`: resolve through `users.list` (with pagination), matching alias against:
  - `name`
  - `profile.display_name`
  - `profile.display_name_normalized`
  - `profile.real_name`
  - `profile.real_name_normalized`
- If alias maps to multiple users, treat as ambiguous and ask user to disambiguate.
- If alias maps to no users, ask user to provide explicit `<@U...>` mention.

Get users:

```bash
curl -sS -H "Authorization: Bearer $SLACK_TOKEN_IN_USE" \
  "https://slack.com/api/users.list?limit=1000"
```

### 3) Post rich text

Construct `blocks` with `rich_text` and `rich_text_section` elements.

- User mention element: `{"type":"user","user_id":"U123..."}`
- Broadcast element: `{"type":"broadcast","range":"here|channel|everyone"}`
- Text element: `{"type":"text","text":"..."}`

Then post:

```bash
curl -sS -X POST "https://slack.com/api/chat.postMessage" \
  -H "Authorization: Bearer $SLACK_TOKEN_IN_USE" \
  -H "Content-Type: application/json; charset=utf-8" \
  -d @payload.json
```

`payload.json` must include:

- `channel`: resolved channel ID
- `text`: fallback plain-text string (with `<@U...>` / `<!here>` forms)
- `blocks`: rich text blocks

## Windows note

On Windows, prefer `curl.exe` (not PowerShell alias) or `Invoke-RestMethod` with equivalent headers/body.

## Output expectations

- Show final API result with `ok`, `channel`, and `ts`.
- Also report which token env key was used (for example `SLACK_BOT_TOKEN_RELEASE_BOT`).
- If mention resolution fails or is ambiguous, do not post until the user confirms/disambiguates.
