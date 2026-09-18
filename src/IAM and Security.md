# IAM and Security

AWS Identity and Access Management (IAM) is the core security service that controls who can access what resources and what actions they can perform. Security in AWS is built on the principle of least privilege—granting only the minimum permissions needed.

## IAM Fundamentals

### IAM Users
- Individual identities representing people or applications
- Each user has a unique name and credentials
- Can have programmatic access (Access Key + Secret Key) or console access (username + password)
- Used for development, individual access, or specific applications
- Root account should never be used for daily operations

### IAM Groups
- Collections of users with shared permissions
- Simplify permission management for teams
- Add/remove users from groups instead of individually managing permissions
- Groups cannot be nested

### IAM Roles
- Temporary identity with specific permissions
- No permanent credentials—assumes role to get temporary credentials
- Can be assumed by:
  - AWS services (Lambda, EC2, etc.)
  - Users (cross-account or same account)
  - External identities (federated users)
- Ideal for service-to-service communication

## IAM Policies

### Policy Structure (JSON)
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::my-bucket/*"
    }
  ]
}
```

### Policy Components
- **Effect**: `Allow` or `Deny`
- **Action**: Specific API action(s) the policy applies to (e.g., `s3:PutObject`, `lambda:InvokeFunction`)
- **Resource**: ARN (Amazon Resource Name) of the resource being accessed
- **Principal**: Who the policy applies to (used in trust policies)
- **Condition**: Optional constraints (IP address, time, MFA requirement, etc.)

### Inline vs Managed Policies
- **Inline Policies**: Directly attached to user/role/group; one-to-one relationship; deleted when principal is deleted
- **Managed Policies**: Standalone policies; can attach to multiple users/roles/groups; version history; easier to reuse

### AWS Managed Policies
- Pre-created by AWS (e.g., `AmazonS3FullAccess`, `AWSLambdaFullAccess`)
- Regularly updated by AWS
- Good for common use cases

## Trust Relationships

### Assume Role Mechanics
Trust relationships define who can assume a role. They use a trust policy (resource-based policy):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

### Principals
- **Service**: AWS services (lambda, ec2, s3, etc.)
- **AWS**: Specific AWS accounts or users
- **Federated**: External identity providers
- Example: `arn:aws:iam::ACCOUNT:role/MyRole`

### Service Assumption
When Lambda executes with a role, it assumes that role and receives temporary credentials:
1. Role has trust relationship allowing Lambda service
2. Role has permission policies defining what Lambda can do
3. Lambda uses credentials for AWS API calls

## Least-Privilege Access

The security principle of granting minimal permissions:

```json
{
  "Effect": "Allow",
  "Action": [
    "s3:GetObject"
  ],
  "Resource": "arn:aws:s3:::my-bucket/logs/*"
}
```

**Instead of:**
```json
{
  "Effect": "Allow",
  "Action": "s3:*",
  "Resource": "*"
}
```

Benefits:
- Reduces blast radius if credentials are compromised
- Prevents accidental harmful actions
- Auditing is easier
- Meets compliance requirements

## Resource-Based Policies

Policies attached to resources (not principals):

```json
{
  "Effect": "Allow",
  "Principal": {
    "AWS": "arn:aws:iam::ACCOUNT:role/LambdaRole"
  },
  "Action": "s3:GetObject",
  "Resource": "arn:aws:s3:::bucket-name/*"
}
```

Common on: S3 buckets, Lambda functions (resource policies), KMS keys, SNS topics

## Cross-Account Access

Enable access to resources in different AWS accounts:

1. **Resource account**: Add resource-based policy allowing principal in other account
2. **User account**: Add policy allowing `sts:AssumeRole` for cross-account role
3. User assumes role in resource account, gets temporary credentials
4. Use cross-account role ARN

```json
{
  "Effect": "Allow",
  "Principal": {
    "AWS": "arn:aws:iam::ACCOUNT-A:role/MyRole"
  },
  "Action": "sts:AssumeRole"
}
```

## Temporary Security Credentials

Provided when assuming a role via AWS STS (Security Token Service):
- **Access Key ID**: Public identifier
- **Secret Access Key**: Private key (never share)
- **Session Token**: Proves credential is temporary
- **Expiration**: Default 1 hour, can be customized (15 min - 12 hours)

More secure than long-term credentials for temporary access.

## Testing Policies

### IAM Policy Simulator
- AWS console tool to test policies without applying them
- Shows which API calls are allowed/denied
- Helps identify permission gaps
- Useful for debugging access issues

### Common Debugging Steps
1. Check principal's attached policies
2. Check resource-based policies
3. Check for explicit Deny statements (Deny overrides Allow)
4. Check Conditions (IP restrictions, time, MFA, etc.)
5. Use Policy Simulator to test

## Common Security Patterns

| Pattern | Use Case |
|---------|----------|
| Lambda execution role | Service accessing S3, DynamoDB, CloudWatch |
| Cross-account role | Organization member accessing shared resources |
| Federated identity | External users via SSO/SAML |
| STS AssumeRole | Temporary elevated permissions |
| Resource policy | Control access to specific service |

## Security Best Practices

- **Use roles, not users**: For service-to-service, use roles
- **MFA for root account**: Prevent unauthorized access
- **Rotate credentials**: Change access keys regularly
- **Use temporary credentials**: Prefer STS AssumeRole over long-term keys
- **Enable CloudTrail**: Audit API calls
- **Apply least privilege**: Only grant necessary permissions
- **Use managed policies**: Easier to maintain and update
- **Regular audits**: Review permissions quarterly
- **Avoid hardcoding credentials**: Use environment variables or Secrets Manager
