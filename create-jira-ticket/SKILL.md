---
name: create-jira-ticket
description: Create Jira issues through Jira MCP only. Use when Codex needs to file a Jira ticket from conversation context, a PR summary, a bug report, a task request, meeting notes, or an implementation plan, including deriving the summary, description, issue type, assignee, reporter, and supported optional Jira fields.
---

# Create Jira Ticket

## Overview

Create Jira issues from explicit user input plus surrounding context. Infer the summary, description, and issue type when needed, while keeping reporter and assignee defaults pinned to Saksham unless the user overrides them.

## Mandatory Tooling

- Use Jira MCP only.
- If Jira MCP is unavailable, inaccessible, or unauthenticated, stop immediately and report that the skill cannot proceed without Jira MCP.
- Do not fall back to web browsing, manual instructions, curl, or any non-Jira-MCP path.
- Resolve the Jira site with `mcp__jira_mcp__getAccessibleAtlassianResources` when `cloudId` is not already known.
- Resolve reporter and assignee emails with `mcp__jira_mcp__lookupJiraAccountId`.
- Create the issue with `mcp__jira_mcp__createJiraIssue`.
- Inspect project issue types and field metadata with:
  - `mcp__jira_mcp__getVisibleJiraProjects`
  - `mcp__jira_mcp__getJiraProjectIssueTypesMetadata`
  - `mcp__jira_mcp__getJiraIssueTypeMetaWithFields`

## Required Inputs

- Determine these values before creating the issue:
  - `cloudId`
  - project key
- Default the project key to `NS`.
- Override `NS` only when the user explicitly and unambiguously specifies a different Jira project key.
- Do not infer a different project key from loose context, nearby ticket references, or project names alone.
- If the user gives conflicting project-key signals, ask for clarification instead of guessing.

## Resolve Issue Content

### Summary

- Use the explicit title when the user provides one.
- Otherwise derive a concise summary from the current task or surrounding context.
- Keep the summary specific and action-oriented.

### Description

- Unless the user explicitly says not to add a description, always add one.
- Build a detailed Markdown description from the available context.
- When the request is tied to a PR, include the best available detail about:
  - problem or motivation
  - change summary
  - impact or risk
  - testing or validation
  - follow-up work
- When no PR exists, still include the strongest available context such as background, expected outcome, constraints, acceptance notes, dependencies, and links.
- Do not invent facts. Omit unknown sections instead of fabricating content.

### Issue Type

- Use the explicit issue type when provided.
- Otherwise infer it from context.
- Prefer:
  - `Bug` for defects, regressions, broken flows, incidents, and unexpected behavior
  - `Story` for user-facing feature work or product-scoped functionality
  - `Task` for engineering chores, internal work, cleanup, documentation, or ambiguous requests
- Validate the chosen type against the project's available issue types.
- If the inferred type is unavailable, use the closest available type and report the fallback.

## Resolve People

- Default reporter email to `saksham.bindal@newtonschool.co`.
- Default assignee email to `saksham.bindal@newtonschool.co`.
- If the user provides reporter or assignee email, use the provided value instead.
- Resolve each email to an Atlassian account ID with `mcp__jira_mcp__lookupJiraAccountId`.
- If an email cannot be resolved, stop and report which value failed.

## Apply Optional Fields

- Only set labels, story points, due date, or sprint when the user explicitly provides them.
- Leave those fields empty when they are not provided.
- Use issue-type field metadata to map provided values to the correct Jira fields.
- Apply:
  - labels through the native `labels` field when supported
  - due date through `duedate` or the project's equivalent field
  - story points only through the exact Jira field named `Story Points`
  - never use `Story point estimate`, `Story point estimation`, or any similarly named fallback field for story points
  - if metadata exposes multiple story-point-like fields, select only the exact `Story Points` field
  - sprint only when the sprint field is clearly identified in metadata
- If the user provided an optional field but the project does not expose a matching field, create the issue without that field and report the omission.

## Creation Workflow

1. Resolve `cloudId`.
2. Use project key `NS` unless the user explicitly provided a different key.
3. Fetch project issue types and field metadata.
4. Determine summary, description, and issue type from explicit input first, then context.
5. Resolve reporter and assignee account IDs from emails, defaulting to Saksham.
6. Build `additional_fields` only for optional values that were explicitly provided and are supported by the project.
   For story points, populate only the exact `Story Points` field when it exists.
7. Call `mcp__jira_mcp__createJiraIssue`.
8. Return the created issue key or URL and summarize the final values used.

## Output Expectations

- Report the created issue key.
- Report the issue URL when Jira returns one.
- Report the project key and issue type used.
- Report the reporter and assignee that were applied.
- Report which optional fields were applied, skipped because they were absent, or skipped because the project did not support them.
- If creation fails, report the concrete blocker directly.
