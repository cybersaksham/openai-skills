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
- Prefer IRSA: create a narrowly scoped IAM role and policy, then annotate a project ServiceAccount with that role ARN. This supplies short-lived credentials to pods.
- Never place static AWS access keys in a Kubernetes Secret.

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
- Use immutable full commit SHA image tags in Kubernetes manifests. Verify the exact tag in ECR before opening the GitOps PR.
- A multi-image project must verify and pin every image it deploys.
