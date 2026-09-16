# AWS Lambda

## Important Research Topics

### Core Concepts
- **Serverless Computing**: Execute code without managing servers
  - Pay-per-use model (charged per millisecond of execution)
  - Automatic scaling and high availability
  - AWS manages infrastructure, patching, and scaling
- **Functions**: Self-contained units of compute
  - Handler: Entry point to your function
  - Runtime: Execution environment (Python, Node.js, Java, Go, C#, etc.)
  - Maximum execution time: 15 minutes
  - Memory allocation: 128 MB to 10,240 MB (CPU scales with memory)

### Function Configuration
- **Runtimes and Handlers**: Supported languages and entry points
  - Python 3.x (python3.11, python3.12, etc.) - handler format: `lambda_function.lambda_handler`
  - Node.js (18.x, 20.x) - handler format: `index.handler`
  - Java 11, 17, 21 - handler format: `package.ClassName::methodName`
  - Go 1.x - handler format: `bootstrap` (custom runtime)
  - C# (.NET 6, .NET 8) - handler format: `Assembly::Namespace.ClassName::MethodName`
  - Ruby (3.x) - handler format: `lambda_function.lambda_handler`
- **Layers**: Reusable code, libraries, and dependencies
  - Package common code and share across functions
  - Up to 5 layers per function
  - Maximum uncompressed size: 250 MB
  - Useful for libraries, shared utilities, Lambda extensions
- **Environment Variables**: Configuration without code changes
  - Key-value pairs passed to function at runtime
  - Accessible via environment variable API
  - Not encrypted by default (use Lambda Secrets Manager for sensitive data)
- **Memory and CPU Configuration**
  - Memory: 128 MB to 10,240 MB (1 vCPU equivalent at 1,769 MB)
  - CPU scales proportionally with memory allocation
  - Affects execution speed and billing
  - Higher memory = faster execution = potentially lower cost

### IAM and Security
- **Execution Roles**: Service role for Lambda permissions
  - Trust relationship allowing Lambda service to assume role
  - Attached policies grant permissions to access AWS services
  - Every Lambda must have an execution role
- **Lambda Resource Policies**: Control who can invoke the function
  - Principal-based (who can invoke)
  - Condition-based (source service, AWS account)
  - Examples: Allow S3 to invoke, Allow API Gateway to invoke
- **Secrets Management**: Secure credential storage
  - Use AWS Secrets Manager or Systems Manager Parameter Store
  - Reference in environment variables or code
  - Never hardcode sensitive data
- **VPC Integration**: Run Lambda within VPC
  - Access private resources (RDS, ElastiCache)
  - Requires VPC configuration (subnets, security groups)
  - Cold start impact (Lambda creates ENI)
  - Alternative: VPC endpoints for AWS services

### Function Invocation
- **Synchronous Invocation** (wait for response)
  - Caller waits for function to complete
  - Response includes execution result or error
  - Examples: API Gateway, Cognito, ALB
  - Maximum payload: 6 MB
- **Asynchronous Invocation** (fire and forget)
  - Lambda returns immediately (queued for processing)
  - Caller doesn't wait for result
  - Built-in retries (up to 2 additional attempts)
  - Dead Letter Queue (DLQ) for failed invocations
  - Examples: S3 events, SNS, SQS
- **Event Source Mappings**: Lambda polls AWS services
  - Lambda reads from stream/queue (SQS, DynamoDB Streams, Kinesis)
  - Automatically invokes function on new records
  - Batch processing of multiple records per invocation
  - Error handling with batch item failures

### Event Sources and Triggers
- **AWS Services that trigger Lambda**:
  - **S3**: ObjectCreated, ObjectDeleted, ObjectRestored events
  - **SQS**: Standard or FIFO queue records
  - **SNS**: Topic notifications
  - **DynamoDB Streams**: Item modifications (INSERT, UPDATE, DELETE)
  - **Kinesis**: Stream records
  - **EventBridge**: Custom rules and schedules (cron expressions)
  - **API Gateway**: HTTP requests
  - **ALB**: HTTP requests to target group
  - **CloudWatch Events/Logs**: Log patterns and scheduled events
  - **Cognito**: User pool events (signup, signin, custom messages)
  - **CloudFormation**: Stack lifecycle events
  - **Alexa**: Voice request handling

### Error Handling and Resilience
- **Timeout Configuration**:
  - Default: 3 seconds, Maximum: 900 seconds (15 minutes)
  - Function stops and throws timeout error if exceeded
  - Set based on expected execution time + buffer
- **Retry Policies**:
  - Synchronous: No automatic retries (handled by caller)
  - Asynchronous: 2 automatic retries (total 3 attempts over 6 hours)
  - Event source mappings: Configurable retry behavior
- **Dead Letter Queues (DLQ)**:
  - SQS or SNS destination for failed invocations (async only)
  - Capture failed events for debugging and reprocessing
  - Essential for production event-driven architecture
- **Error Handling Best Practices**:
  - Catch exceptions in function code
  - Return structured error responses
  - Log errors with context
  - Use custom metrics for failure tracking
  - Consider exponential backoff for external API calls

### Performance Optimization
- **Cold Starts**: Initial setup time for function execution
  - First invocation: ~500ms - 2s depending on package size
  - Provisioned Concurrency: Pay to keep functions "warm"
  - Container reuse: Subsequent invocations faster
  - Dependency initialization: Keep lightweight
- **Concurrency Limits**:
  - Default: 1,000 concurrent executions per account/region
  - Reserved concurrency: Guarantee capacity for critical functions
  - Provisioned concurrency: Eliminate cold starts
- **Package Optimization**:
  - Minimize deployment package size
  - Use Lambda Layers for shared dependencies
  - Remove unnecessary files and dependencies
  - Consider Lambda Extensions for external integrations

### Monitoring and Troubleshooting
- **CloudWatch Metrics**: Built-in monitoring
  - Invocations, Duration, Errors, Throttles, ConcurrentExecutions
  - Dead Letter Queue destination metrics
- **CloudWatch Logs**: Automatic log generation
  - Each invocation logs to `/aws/lambda/function-name`
  - Print statements appear in logs
  - Use structured logging for better analysis
- **X-Ray Tracing**: Request tracing across services
  - Visualize call chains and timing
  - Identify bottlenecks and failures
  - Requires X-Ray write access in IAM role
- **Lambda Insights**: Enhanced monitoring
  - Real-time performance metrics
  - Memory utilization, duration distribution
  - Anomaly detection
  - Available via CloudWatch Logs agent

## Practical Examples

### Scenario 1: Event-Driven Image Processing with S3
- User uploads image to S3 bucket (ObjectCreated event)
- S3 triggers Lambda asynchronously with event payload
- Lambda downloads image, applies filters/transformations
- Stores processed image to output bucket with "processed-" prefix
- Uses DLQ to capture failed processing jobs
- CloudWatch Logs track execution details

### Scenario 2: API Gateway → Lambda → DynamoDB
- API Gateway receives HTTP POST request (synchronous)
- Triggers Lambda with request body and headers
- Lambda validates input, parses JSON
- Queries/updates DynamoDB table
- Returns structured JSON response to client
- API Gateway returns HTTP response (status code + body)

### Scenario 3: Scheduled Lambda with EventBridge
- EventBridge rule triggers Lambda on schedule (cron: 0 2 * * ? = 2 AM daily)
- Lambda connects to external API or database
- Fetches data, processes, stores results to S3
- Sends SNS notification on completion or failure
- CloudWatch alarms monitor execution success rate

### Scenario 4: Lambda with SQS for Decoupled Processing
- Application sends messages to SQS queue
- Lambda reads from queue via event source mapping (batch of 10 messages)
- Process each message independently
- Report batch item failures for failed records
- Failed records return to queue for retry
- DLQ captures messages after max retries (default 3)

### Scenario 5: Lambda Authorizer for API Security
- API Gateway request → Lambda authorizer function (synchronous)
- Validates authorization header (JWT, custom logic)
- Returns policy document (Allow/Deny)
- API Gateway caches authorization result
- Routes to actual API handler if authorized

## Key CLI Commands Reference

```bash
# Create function
aws lambda create-function \
  --function-name my-function \
  --runtime python3.12 \
  --role arn:aws:iam::ACCOUNT:role/lambda-execution-role \
  --handler lambda_function.lambda_handler \
  --zip-file fileb://function.zip

# Update function code
aws lambda update-function-code \
  --function-name my-function \
  --zip-file fileb://function.zip

# Update function configuration
aws lambda update-function-configuration \
  --function-name my-function \
  --memory-size 512 \
  --timeout 60 \
  --environment Variables={KEY1=value1,KEY2=value2}

# Invoke function synchronously
aws lambda invoke \
  --function-name my-function \
  --payload '{"key": "value"}' \
  response.json

# Invoke function asynchronously
aws lambda invoke \
  --function-name my-function \
  --invocation-type Event \
  --payload '{"key": "value"}' \
  response.json

# List functions
aws lambda list-functions
aws lambda get-function --function-name my-function

# Create function URL (public endpoint)
aws lambda create-function-url-config \
  --function-name my-function \
  --auth-type NONE

# Publish version and alias
aws lambda publish-version --function-name my-function
aws lambda create-alias \
  --function-name my-function \
  --name prod \
  --function-version 1

# Add event source mapping (SQS, DynamoDB, Kinesis)
aws lambda create-event-source-mapping \
  --event-source-arn arn:aws:sqs:region:account:queue \
  --function-name my-function \
  --batch-size 10 \
  --enabled

# Add resource policy (allow S3 to invoke)
aws lambda add-permission \
  --function-name my-function \
  --statement-id AllowS3Invoke \
  --action lambda:InvokeFunction \
  --principal s3.amazonaws.com \
  --source-arn arn:aws:s3:::bucket-name

# View logs
aws logs tail /aws/lambda/my-function --follow
aws logs filter-log-events \
  --log-group-name /aws/lambda/my-function \
  --filter-pattern ERROR
```

## Best Practices

- ✅ Keep functions small and focused (single responsibility)
- ✅ Minimize deployment package size
- ✅ Use Lambda Layers for shared dependencies
- ✅ Configure appropriate timeout (default 3s is too low for most)
- ✅ Use environment variables for configuration
- ✅ Store secrets in Secrets Manager or Parameter Store
- ✅ Always configure Dead Letter Queue (DLQ) for async invocations
- ✅ Enable X-Ray tracing for debugging distributed systems
- ✅ Use CloudWatch Insights for log analysis
- ✅ Set reserved concurrency for critical functions
- ✅ Use provisioned concurrency to eliminate cold starts if needed
- ✅ Implement proper error handling and logging
- ✅ Initialize external connections outside handler (connection pooling)
- ✅ Use Lambda versions and aliases for deployment
- ✅ Test locally with SAM CLI or Lambda runtime images
- ✅ Monitor memory utilization and optimize allocation
- ✅ Use structured logging (JSON) for better searchability
- ✅ Implement idempotency for event-driven functions
- ✅ Use VPC only when necessary (cold start penalty)
- ✅ Implement least-privilege IAM policies

## Common Exam Tips

- **Lambda charges by millisecond**: 1 ms = smallest unit billed
- **Default timeout**: 3 seconds (often too short, set explicitly)
- **Maximum execution time**: 900 seconds (15 minutes)
- **Synchronous vs Asynchronous**: Async has built-in retries; sync doesn't
- **Cold start**: First invocation ~500ms-2s, subsequent faster (container reuse)
- **Concurrency limit**: Default 1,000 per region/account
- **Dead Letter Queue**: Only for asynchronous invocations
- **Event source mapping**: Lambda polls (doesn't get pushed) from SQS/Kinesis/DynamoDB
- **S3 event notifications**: Use EventBridge or S3 → SNS/SQS → Lambda for filtering
- **Lambda Layers**: Up to 5 per function, total size limit 250 MB
- **Environment variables**: NOT encrypted by default (use Secrets Manager for sensitive)
- **Memory**: 128 MB to 10,240 MB; CPU scales with memory (1 vCPU at ~1,769 MB)
- **Payload size**: Synchronous 6 MB, asynchronous 256 KB
- **Versions**: Immutable snapshots; aliases point to versions
- **Handler format**: Varies by runtime (Python: `file.function`, Node: `file.handler`)
- **Execution role**: Every function MUST have one
- **Resource policy**: Controls who can invoke (Principal-based)
- **VPC Lambda**: Creates ENI in subnet (causes cold start delay)
- **Provisioned Concurrency**: Pre-initialized executions (costs money)
- **Reserved Concurrency**: Guaranteed capacity without pre-initialization
- **Retries for async**: 2 additional attempts (3 total) over 6 hours
