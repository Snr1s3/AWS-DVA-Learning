# Amazon S3 (Simple Storage Service)

## Important Research Topics

### Core Concepts
- Object storage concepts and best practices
- **Buckets**: Containers for objects with unique naming conventions
  - Bucket naming rules (3-63 characters, lowercase, no underscores)
  - Region-specific bucket creation
- **Objects**: Data units stored within buckets
  - Object key (filename/path)
  - Object metadata and tags
  - Maximum object size (5TB)

### Storage Management
- **Storage Classes**: Cost optimization with trade-offs
  - Standard (frequent access, highest cost)
  - Intelligent-Tiering (automatic tier transitions)
  - Infrequent Access (IA, minimum 30-day storage)
  - Glacier (archive, retrieval times in hours)
  - Deep Glacier (long-term archive, retrieval in 12 hours)
- S3 bucket versioning and lifecycle policies
  - Versioning enables object recovery
  - Lifecycle rules automate storage class transitions
  - Transition and expiration policies

### Security & Access Control
- **Data Protection**: Encryption at rest and in transit
  - Server-Side Encryption (SSE-S3, SSE-KMS, SSE-C)
  - Client-side encryption before upload
  - SSL/TLS for data in transit
- **Access Control**: IAM policies and resource-based permissions
  - IAM user policies for access
  - Bucket policies for cross-account access
  - Resource-based policies vs principal-based
- Bucket permissions and access control (ACLs, bucket policies)
  - Public Read, Public Read/Write, Private ACLs
  - Bucket policy conditions (IP restrictions, VPC endpoints)
- Public vs private bucket access
  - Block Public Access settings
  - Presigned URLs for temporary access
- **Auditing**: Access logs, CloudTrail action-based logging, and alarms
  - S3 access logging to another bucket
  - CloudTrail for API calls
  - Setting up monitoring alerts
- **Infrastructure Security**: Built on top of AWS Cloud infrastructure
  - VPC endpoints for private S3 access
  - MFA Delete protection

### Operations & Events
- AWS CLI commands for S3 operations
  - `aws s3 cp` for copying objects
  - `aws s3 ls` for listing buckets/objects
  - `aws s3 mb` for creating buckets
  - `aws s3 rm` for deleting objects
  - `aws s3 sync` for synchronizing directories
- S3 events (ObjectCreated, ObjectDeleted, ObjectRestored)
  - Event notification types
  - Event filtering by prefix/suffix
- S3 event notifications and Lambda integration
  - S3 → SQS, SNS, Lambda, EventBridge
  - Event structure and payload
  - Handling duplicate events

### Advanced Features
- Cross-region replication
  - Replication rules and filters
  - Replication status and monitoring
  - Same-region replication (SRR) vs Cross-region replication (CRR)
- S3 Transfer Acceleration for faster uploads
- S3 Batch Operations for bulk processing
- S3 Select for querying object data
- Multipart upload for large files
- Object lock for compliance and governance

## Practical Examples

### Scenario 1: Event-Driven Lambda with S3
- Enable versioning on input bucket
- Create Lambda execution role with S3 read permissions
- Configure S3 event notification → Lambda
- Lambda reads object, processes, writes to output bucket
- Output bucket has different prefix to avoid recursive invocation

### Scenario 2: Cost Optimization with Lifecycle
- Create bucket with standard storage class
- Set lifecycle rule: 30 days → Infrequent Access, 90 days → Glacier
- Archive old data automatically
- Monitor storage class metrics

### Scenario 3: Secure Cross-Account Access
- Account A creates bucket with policy allowing Account B
- Account B creates role with S3 permissions
- Use presigned URLs for temporary access
- Enable CloudTrail for audit trail

## Key CLI Commands Reference
```bash
# Create and manage buckets
aws s3 mb s3://bucket-name
aws s3 ls
aws s3api list-buckets

# Upload/Download objects
aws s3 cp file.txt s3://bucket-name/
aws s3 cp s3://bucket-name/file.txt .
aws s3 sync ./local-dir s3://bucket-name/

# Delete operations
aws s3 rm s3://bucket-name/file.txt
aws s3 rm s3://bucket-name/ --recursive

# View bucket properties
aws s3api get-bucket-versioning --bucket bucket-name
aws s3api get-bucket-encryption --bucket bucket-name
aws s3api get-bucket-acl --bucket bucket-name
```

## Best Practices
- ✅ Enable versioning on critical buckets
- ✅ Use lifecycle policies to manage costs
- ✅ Enable Block Public Access by default
- ✅ Use presigned URLs instead of public ACLs
- ✅ Encrypt sensitive data (SSE-KMS or SSE-S3)
- ✅ Enable MFA Delete for compliance buckets
- ✅ Log all S3 access to separate bucket
- ✅ Enable CloudTrail for API audit
- ✅ Use bucket policies instead of ACLs (modern approach)
- ✅ Implement least-privilege IAM policies
- ✅ Use VPC endpoints for private access
- ✅ Monitor replication status regularly

## Common Exam Tips
- S3 is **eventually consistent** for new objects, but **read-after-write consistent**
- Bucket names are **globally unique** across all AWS accounts
- Default bucket region is **us-east-1** unless specified
- S3 events can trigger **Lambda, SQS, SNS, or EventBridge**
- **Versioning** cannot be disabled, only suspended
- Objects in versioning-enabled buckets have **version IDs**
- **Block Public Access** overrides bucket policies and ACLs
- **Presigned URLs** inherit the permissions of the user creating them
- Lifecycle rules need **at least 30 days** for Infrequent Access transition
- **Multipart upload** recommended for objects > 100MB
- Replication requires **versioning enabled** on both buckets
- Cross-region replication has **latency**; monitor replication metrics
