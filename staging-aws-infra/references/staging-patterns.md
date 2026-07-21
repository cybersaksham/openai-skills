# Staging infrastructure patterns

Use these as current staging patterns. Discover all live identifiers during each plan; do not copy project ARNs, image tags, hostnames, secrets, or credentials.

## Shared ingress

- The staging EKS cluster is `newton-core-staging` in `ap-south-1`.
- Public workloads use one shared internet-facing ALB. Each public Kubernetes Service needs its own IP TargetGroupBinding and AWS target group.
- Create target groups with service-specific HTTP health endpoints. Add HTTPS listener rules with exact host conditions and, when needed, path conditions. Create matching Route53 `A` and `AAAA` ALIAS records.
- Find listener rule priorities dynamically. They are shared and cannot be assumed.

## GitOps layout

- Add a project under `clusters/newton-core/staging/<project>/` and include it in the parent staging kustomization.
- Use ClusterIP Services plus `elbv2.k8s.aws/v1beta1` TargetGroupBindings; the AWS Load Balancer Controller registers pod IPs.
- Flux watches `main` and uses pruning. A PR is the delivery artifact; never mutate the cluster directly to bypass it.
- Validate the rendered whole overlay before creating the PR.

## Stateful services

- The established PostgreSQL and Redis patterns run in-cluster, not as RDS or ElastiCache. Persistent volumes use `ebs-csi-gp3` and stateful pods commonly target the existing cluster-manager node group.
- Make state, storage capacity, resource limits, probes, and authentication explicit.

## S3 and AWS credentials

- Prefer a private S3 bucket with block-public-access, server-side encryption, lifecycle rules, and purpose-specific CORS where browser access is required.
- Use a dedicated `<project>-s3-user` and attachable `<project>-s3-access-policy`; never share a credential user or policy between projects.
- Scope the policy to the project's bucket and approved prefixes. Add only S3 actions evidenced by the source. Include bucket-level `s3:GetBucketLocation` or `s3:ListBucket` only when needed, and include `s3:AbortMultipartUpload` when the source aborts multipart uploads.
- Create one active access key after explicit approval. Store its ID and secret only in the private `0600` backend environment draft using the repository's exact environment-key names. Never print the secret, commit it, or edit SOPS; the user performs the SOPS update.

## CloudFront

- Treat CloudFront as optional. Decide from repository evidence whether it serves a static frontend/S3 origin or fronts a public application; never enable it from the project name alone.
- Use Origin Access Control and a distribution-scoped bucket policy for an S3 origin. Keep the bucket private.
- Derive cache behaviors from the application routes. Do not cache authenticated, API, WebSocket, or mutation endpoints by default.
- CloudFront is global. Custom aliases require an ACM certificate in `us-east-1`, even though all normal staging resources remain in `ap-south-1`. Validate the certificate through the approved staging Route53 zone and create `A` and `AAAA` aliases only after approval.

## Secrets

- SOPS-encrypted `secrets.yaml` values are a human-approved operation. Do not decrypt, print, invent, or commit plaintext values.
- It is safe to prepare the expected Secret object names and key names in the plan. Do not apply an incomplete workload as healthy; call out missing secret values as blockers.

## Build and image pins

- Create an ECR repository and project-specific CodeBuild configuration only after confirming the app repo supplies the needed Docker/build files.
- Before creating or updating either resource, inspect the live `samvaad` ECR repository, CodeBuild project, webhook, and service role. New staging projects must use its current build baseline:
  - ECR image tag mutability is `MUTABLE`.
  - CodeBuild uses `LINUX_CONTAINER`, `aws/codebuild/amazonlinux-x86_64-standard:6.0`, `BUILD_GENERAL1_SMALL`, and privileged Docker builds.
  - CodeBuild uses the same discovered staging-core VPC, core-private subnet, and outbound-unlimited security group as Samvaad.
  - Attach exactly the four managed policies currently attached to Samvaad’s CodeBuild role; do not add a project-specific inline policy.
  - The webhook has one `PUSH` filter group whose commit-message regex is `.*[BUILD].*`; pull-request comment approval is `DISABLED`.
- Preserve the project’s source URL, source ref, image repository name, and required non-secret build variables. Do not copy Samvaad secrets, image tags, or application configuration.
- Use full commit SHA revision tags in Kubernetes manifests. Verify the exact tag in ECR before opening the GitOps PR.
- A multi-image project must verify and pin every image it deploys.
