#!/usr/bin/env bash
# Read-only preflight for the staging-aws-infra skill. It intentionally has no
# apply mode and must complete before any AWS or Git write is considered.
set -euo pipefail

EXPECTED_ACCOUNT="552623333554"
EXPECTED_REGION="ap-south-1"
PROJECT=""
GITHUB_REPO=""
INFRA_REPO=""
ENVIRONMENT="staging"

usage() {
  cat <<'EOF'
Usage: preflight-plan.sh --project <dns-safe-slug> --github-repo <owner/repository> --infra-repo <path> [--environment staging]

Perform read-only staging identity, collision, and GitHub repository checks. The
script refuses any environment other than staging and never changes AWS or Git state.
EOF
}

fail() {
  echo "preflight failed: $*" >&2
  exit 1
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --project) PROJECT="${2:-}"; shift 2 ;;
    --github-repo) GITHUB_REPO="${2:-}"; shift 2 ;;
    --infra-repo) INFRA_REPO="${2:-}"; shift 2 ;;
    --environment) ENVIRONMENT="${2:-}"; shift 2 ;;
    --help|-h) usage; exit 0 ;;
    *) fail "unknown argument: $1" ;;
  esac
done

[ "$ENVIRONMENT" = "staging" ] || fail "this skill supports staging only"
[ -n "$PROJECT" ] || fail "--project is required"
[ -n "$GITHUB_REPO" ] || fail "--github-repo is required"
[ -n "$INFRA_REPO" ] || fail "--infra-repo is required"
printf '%s' "$PROJECT" | grep -Eq '^[a-z][a-z0-9-]{1,47}$' || fail "project must be a lower-case DNS-safe slug"
printf '%s' "$GITHUB_REPO" | grep -Eq '^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$' || fail "github repo must be OWNER/REPOSITORY"
[ "${AWS_PROFILE:-}" = "staging" ] || fail "AWS_PROFILE must be exactly staging; it will not be changed automatically"
[ -d "$INFRA_REPO/.git" ] || fail "infra repo is not a Git checkout: $INFRA_REPO"

ACCOUNT="$(aws sts get-caller-identity --query Account --output text)" || fail "cannot resolve the active AWS identity"
[ "$ACCOUNT" = "$EXPECTED_ACCOUNT" ] || fail "active AWS account $ACCOUNT is not the staging account"

REGION="${AWS_REGION:-${AWS_DEFAULT_REGION:-$(aws configure get region)}}"
[ "$REGION" = "$EXPECTED_REGION" ] || fail "active AWS region must be $EXPECTED_REGION, got ${REGION:-unset}"

echo "Safety gates passed"
echo "  environment: $ENVIRONMENT"
echo "  aws_profile: $AWS_PROFILE"
echo "  account: $ACCOUNT"
echo "  region: $REGION"
echo "  project: $PROJECT"
echo "  github_repo: $GITHUB_REPO"

command -v gh >/dev/null 2>&1 || fail "GitHub CLI is required to verify the application repository"
GITHUB_METADATA="$(gh repo view "$GITHUB_REPO" --json nameWithOwner,url,defaultBranchRef,isPrivate)" \
  || fail "cannot access GitHub repository $GITHUB_REPO"
echo "  github_metadata: $GITHUB_METADATA"

echo
echo "Existing AWS resources (read-only)"
aws ecr describe-repositories --repository-names "$PROJECT" --region "$REGION" \
  --query 'repositories[*].{name:repositoryName,uri:repositoryUri}' --output table 2>/dev/null \
  || echo "  ECR repository: not found"
aws codebuild batch-get-projects --names "$PROJECT" --region "$REGION" \
  --query 'projects[*].{name:name,source:source.location,webhook:webhook.status}' --output table 2>/dev/null \
  || echo "  CodeBuild project: not found"
TARGET_GROUPS="$(aws elbv2 describe-target-groups --region "$REGION" \
  --query "TargetGroups[?starts_with(TargetGroupName, \`$PROJECT\`)].{name:TargetGroupName,arn:TargetGroupArn}" \
  --output table)"
if [ -n "$TARGET_GROUPS" ]; then
  printf '%s\n' "$TARGET_GROUPS"
else
  echo "  Project-prefixed target groups: not found"
fi

echo
echo "Infra repository state (read-only)"
git -C "$INFRA_REPO" status --short --branch
git -C "$INFRA_REPO" remote get-url origin
git -C "$INFRA_REPO" show-ref --verify --quiet refs/remotes/origin/main \
  && echo "  origin/main: available" \
  || echo "  origin/main: fetch required before apply"

echo
echo "Plan preflight is complete. No AWS or Git write was performed."
