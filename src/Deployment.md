# Deployment

Deployment in AWS focuses on packaging, managing, and deploying applications—particularly Lambda functions—to production environments using various tools and patterns.

## Application Packaging

### Structure and ZIP Files
- Lambda functions are deployed as ZIP files containing code and dependencies
- ZIP structure: Function handler at root, dependencies in `lib/`, `node_modules/`, or `site-packages/`
- Python: Code files + `python/` directory for dependencies
- Node.js: Code files + `node_modules/` directory
- Must include all required libraries for execution

### Deployment Package Size
- Maximum unzipped size: 250 MB (soft limit)
- Maximum ZIP file size: 50 MB (direct upload)
- Larger packages use S3 bucket upload

## AWS CLI Deployment Commands

### Creating Functions
```bash
aws lambda create-function \
  --function-name my-function \
  --runtime python3.11 \
  --role arn:aws:iam::ACCOUNT:role/ROLE \
  --handler lambda_function.lambda_handler \
  --zip-file fileb://function.zip
```

### Updating Function Code
```bash
aws lambda update-function-code \
  --function-name my-function \
  --zip-file fileb://updated-function.zip
```

### Updating Configuration
```bash
aws lambda update-function-configuration \
  --function-name my-function \
  --timeout 60 \
  --memory-size 256
```

## Environment Configuration

### Environment Variables
- Key-value pairs stored in Lambda function configuration
- Accessed in code: `os.environ['KEY']` (Python), `process.env.KEY` (Node.js)
- Used for configuration without changing code
- Support string values only

### Configuration Management
- Store non-sensitive configs in environment variables
- Use AWS Secrets Manager for sensitive data (API keys, passwords, DB credentials)
- Reference secrets: `aws secretsmanager get-secret-value`
- Separate configs per environment (dev, staging, prod)

## Infrastructure as Code (IaC)

### CloudFormation
- AWS's native IaC service
- YAML/JSON templates define resources
- Entire stack deployment in one operation
- **Stacks**: Collections of AWS resources managed together
- Version control templates for reproducibility
- Rollback capability on failure

### AWS SAM (Serverless Application Model)
- Simplified CloudFormation syntax for serverless apps
- YAML template format
- Simpler than raw CloudFormation for Lambda deployments
- Resources: `AWS::Serverless::Function`, `AWS::Serverless::Api`, `AWS::Serverless::SimpleTable`
- Transforms into standard CloudFormation during deployment
- Supports local testing and packaging

### SAM Template Example
```yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31

Resources:
  MyFunction:
    Type: AWS::Serverless::Function
    Properties:
      Runtime: python3.11
      Handler: index.handler
      CodeUri: ./src
      Environment:
        Variables:
          TABLE_NAME: my-table
```

## Deployment Automation

### CI/CD Integration
- Integrate deployments with GitHub Actions, GitLab CI, Jenkins, etc.
- Automated testing on code commits
- Automated deployment to AWS on merge/tag
- Environment promotion: dev → staging → production

### Deployment Pipeline
1. Code commit to repository
2. Run tests and linting
3. Build deployment package
4. Deploy to dev/staging environment
5. Run integration tests
6. Deploy to production on approval

## Versioning and Aliases

### Function Versions
- AWS Lambda maintains immutable versions of functions
- `$LATEST`: Development version (always mutable)
- Numbered versions (1, 2, 3...): Snapshots after publishing
- Create version: `aws lambda publish-version`
- Each version is immutable and independent

### Aliases
- Pointers to specific versions
- Mutable, can point to different versions
- Enable traffic shifting and blue-green deployments
- Common aliases: `prod`, `staging`, `dev`
- Example: Alias `prod` points to version 5, can update to version 6

### Canary Deployment
- Route small percentage of traffic to new version
- Gradually increase traffic if metrics are good
- Rollback quickly if issues detected
- Minimize blast radius of issues

## Deployment Best Practices

| Practice | Benefit |
|----------|---------|
| Use SAM for serverless apps | Simpler templates, faster development |
| Version control templates | Track infrastructure changes, easy rollback |
| Separate configs from code | Reuse same code across environments |
| Use Secrets Manager for sensitive data | Secure credential management |
| Implement CI/CD pipeline | Automated testing and deployment |
| Use aliases for traffic control | Enable blue-green and canary deployments |
| Monitor deployments | Catch issues early, quick rollback |
| Test in staging first | Prevent production issues |
