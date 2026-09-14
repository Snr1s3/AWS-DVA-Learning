# AWS Certified Developer - Associate (DVA)

This book contains practical notes and exercises for the AWS Certified Developer - Associate certification.

## Main Topics

### AWS Lambda

Create and deploy serverless functions, configure handlers and runtimes, manage IAM roles, and invoke functions manually or through AWS services.

### Amazon S3

Store and retrieve objects, configure bucket permissions, upload files with the AWS CLI, and use S3 events to trigger Lambda functions.

### IAM and Security

Understand users, groups, roles, policies, trust relationships, and least-privilege permissions. Learn how AWS services assume roles and access other services securely.

### Application Integration

Work with event-driven architectures using Lambda, Amazon SQS, Amazon SNS, and Amazon EventBridge.

### Deployment

Package and deploy applications using the AWS CLI, ZIP files, environment variables, and infrastructure automation tools.

### Monitoring and Troubleshooting

Use Amazon CloudWatch Logs and metrics to monitor applications, diagnose failures, and verify AWS service integrations.

## Example Project

The repository includes an example Lambda workflow:

1. Upload a file to an input S3 bucket.
2. Amazon S3 sends an `ObjectCreated` event.
3. The event invokes a Lambda function.
4. Lambda reads the input object.
5. Lambda writes the processed object to an output bucket.
6. CloudWatch stores the execution logs.

The Lambda execution role requires permission to read from the input bucket and write to the output bucket. The output bucket must not trigger the same Lambda function, otherwise recursive invocations may occur.

## Useful AWS CLI Commands

```bash
aws lambda create-function
aws lambda update-function-code
aws lambda invoke
aws s3 cp
aws s3 ls
aws logs tail
```

## Learning Goal

The goal is to understand how to build, deploy, secure, monitor, and troubleshoot applications on AWS using practical developer workflows.