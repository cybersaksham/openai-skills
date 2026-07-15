---
name: staging-aws-infra
description: Plan and provision AWS-backed Kubernetes infrastructure for a new project in Newton School staging only. Use when Codex needs to create or review staging ECR, CodeBuild, shared-ALB routing, Route53, optional S3/IRSA, and a Kubernetes-cluster-infra pull request. Always run a read-only plan first and wait for explicit user confirmation before any write.
---

# Staging AWS Infra

Create new-project infrastructure in two strictly separated phases. This skill is staging-only: never create, modify, inspect for implementation, or suggest applying production infrastructure.

## Mandatory phase gate

1. Start every request in `plan` mode, including requests that say “create”, “apply”, or “deploy”.
2. In plan mode, use only read-only commands. Run `scripts/preflight-plan.sh` before discovery.
3. Present the resource plan, exact assumptions, unresolved inputs, collision results, and the GitOps files that would change.
4. Stop and ask for explicit confirmation using the generated plan. Do not treat “looks good”, “continue”, or silence as confirmation.
5. Enter `apply` mode only after the user expressly confirms the named staging plan, for example: `Apply the staging plan for <project>.`
6. Re-run the safety preflight immediately before the first write. If account, profile, region, project slug, hosts, or selected options differ from the approved plan, return to plan mode.

## Absolute safety rules

- Reject a production request outright, even if AWS credentials happen to be staging credentials. Do not offer a production fallback.
- Require `AWS_PROFILE=staging`; never set, export, or override it for the user.
- Run `aws sts get-caller-identity` without `--profile` and require account `552623333554`.
- Require `ap-south-1`. Fail rather than choose another region.
- Use AWS CLI for all AWS discovery and writes. Do not use a console/browser route for AWS operations.
- Work only in the Kubernetes infra repository supplied by the user. Read its `AGENTS.md` and local runbooks before applying.
- Create a new branch from current `origin/main` only when the user has explicitly confirmed the apply plan. Never push to `main`, merge the PR, or edit `prod/`.
- Do not delete or rename files under `clusters/`; Flux uses `prune: true`.
- Do not decrypt, print, commit plaintext, or invent secret values. Treat SOPS secret values as a human-approved input gate.
- Do not automatically delete partially created AWS resources on failure. Report the exact resources created and a safe rollback plan.

## Inputs to resolve in plan mode

Require or explicitly mark as unresolved:

1. Project slug and GitHub repository.
2. Public hostnames and optional path routes.
3. Workload topology: frontend, API, WebSocket API, workers, migration job, scheduled jobs, and ports/health endpoints.
4. Initial immutable image tag(s), image build instructions, and source SHA.
5. Resource requests/limits, replicas, and stateful node-placement needs.
6. Dependencies: PostgreSQL, Redis, S3, and AWS integrations such as SES.
7. Required secret-key names and the approved source of each value.

Use a lower-case DNS-safe slug. Check ECR repository names, target-group names, bucket names, IAM-role names, listener-rule priorities, hostnames, and Kubernetes namespaces for collisions before proposing writes.

## Plan mode

1. Run `scripts/preflight-plan.sh --project <slug> --infra-repo <path>`.
2. Discover, rather than hard-code, the staging EKS cluster, VPC, shared ALB, HTTPS listener, Route53 hosted zone, existing listener rules, existing project resources, and cluster capabilities.
3. Read `references/staging-patterns.md` and the current repository runbooks. Use a recent project only as a pattern, not as a copy source for secrets, names, ARNs, or image tags.
4. Inspect the application repository for Docker/build configuration, health endpoints, ports, migration requirements, and required environment-key names. Do not alter the app repository in this phase.
5. Produce a plan containing:
   - AWS creates, updates, or collisions;
   - target group health checks and ALB host/path rules;
   - DNS records;
   - optional database, Redis, S3, IRSA, and IAM choices;
   - Kubernetes manifests and image pins;
   - secret-key names only, with unresolved values called out;
   - validation commands and rollback steps.
6. Explicitly state that no write has occurred and ask for confirmation of that exact plan.

## Apply mode

Execute only the approved plan and preserve the requested scope.

### AWS build and routing

1. Create or verify the ECR repository with safe project-specific settings.
2. Create or verify the CodeBuild project and least-privilege service role. Match the project’s build requirements; use privileged mode only for Docker builds. Configure the approved GitHub webhook behavior and verify the initial immutable image tags exist in ECR before pinning them in GitOps.
3. For every public Service, create a distinct IP target group in the discovered staging VPC with the approved HTTP port and health path.
4. Add collision-free HTTPS listener rules to the discovered shared ALB. Use host and path conditions exactly as approved; never change another project’s rule.
5. Create approved Route53 `A` and `AAAA` aliases to the shared ALB. Verify records resolve to the intended ALB.

### Optional dependencies

1. PostgreSQL: use the existing staging in-cluster StatefulSet/Flux Helm pattern with `ebs-csi-gp3` persistent storage unless the approved plan explicitly selects another supported design. Add only SOPS-encrypted credential references.
2. Redis: use the existing in-cluster standalone Redis pattern. Make authentication and persistence explicit; schedule stateful workloads on the appropriate existing node group.
3. S3: create a private encrypted bucket with block-public-access and scoped lifecycle/CORS settings. Prefer a project ServiceAccount plus IRSA and least-privilege bucket/prefix policy; do not use static AWS credentials in application secrets.
4. AWS service access: extend the project IRSA role only with approved actions and resource ARNs.

### GitOps pull request

1. Fetch `origin/main`, create a new branch from it, and keep all work in that branch.
2. Create `clusters/newton-core/staging/<project>/` with only the approved resources: namespace, project kustomization, workloads, Services, TargetGroupBindings, optional ServiceAccount/IRSA, ConfigMaps, database/Redis manifests, and SOPS secret references.
3. Add the project directory to `clusters/newton-core/staging/kustomization.yaml` without altering unrelated entries.
4. Use immutable full-SHA ECR image tags, health probes, resource requests/limits, and migration ordering appropriate to the app.
5. Validate the whole staging overlay with:

   ```bash
   kubectl kustomize --load-restrictor LoadRestrictionsNone clusters/newton-core/staging
   ```

6. Commit, push the new branch, and open a pull request. Do not merge it.
7. Report the PR URL, AWS resource IDs/ARNs, image tags, secret values still required, and post-merge verification commands.

## After merge

Only when the user asks to verify a merged PR:

1. Confirm Flux observes the merged revision.
2. Check Kubernetes rollout status and target-group health.
3. Test approved public hosts and health endpoints.
4. Verify optional PostgreSQL, Redis, S3, and IRSA behavior without exposing credentials.
