# Monitoring and Troubleshooting

Monitoring and troubleshooting are critical for maintaining reliable serverless applications. AWS provides CloudWatch and X-Ray to track performance, errors, and system behavior.

## Amazon CloudWatch Logs

### Overview
- Centralized log storage for AWS services
- Lambda automatically sends logs to CloudWatch Logs
- Log groups organize logs by application/service
- Log streams contain logs from individual executions
- Logs are searchable and queryable

### Viewing Lambda Logs
- **Console**: Lambda function → Monitor tab → Logs
- **CloudWatch Logs console**: View log groups and streams directly
- **AWS CLI**: `aws logs tail /aws/lambda/my-function --follow`
- Each execution gets a unique stream with timestamp and request ID

### Log Format
```
START RequestId: abc-123 Version: $LATEST
[timestamp] DEBUG: Processing event
[timestamp] INFO: Result: success
END RequestId: abc-123
REPORT RequestId: abc-123 Duration: 45.23 ms Billed Duration: 100 ms Memory Used: 64 MB
```

### Log Retention
- Default: Never expire
- Set retention policies: 1 day → 10 years
- Cost optimization: Delete old logs automatically
- Complies with data retention requirements

## CloudWatch Logs Insights

### Query Language
SQL-like language for searching logs:

```
fields @timestamp, @message, @duration
| filter @duration > 1000
| stats count() as error_count by @message
```

### Common Queries
**Find all errors:**
```
fields @timestamp, @message
| filter @message like /ERROR|Exception/
```

**Calculate average duration:**
```
stats avg(@duration) as avg_duration
```

**Count invocations by status:**
```
stats count() as invocation_count by @message
```

### Insights Benefits
- Fast querying across large log volumes
- Pattern recognition
- Aggregation and statistics
- Export results to S3

## CloudWatch Metrics

### Lambda Metrics
- **Invocations**: Total number of function invocations
- **Duration**: Time function takes to execute (milliseconds)
- **Errors**: Number of failed invocations
- **Throttles**: Invocations rejected due to concurrency limit
- **ConcurrentExecutions**: Current concurrent invocations
- **UnreservedConcurrentExecutions**: Execution using unreserved capacity

### Custom Metrics
Publish custom metrics from Lambda code:

```python
import boto3

cloudwatch = boto3.client('cloudwatch')
cloudwatch.put_metric_data(
    Namespace='MyApp',
    MetricData=[
        {
            'MetricName': 'ProcessingTime',
            'Value': 150,
            'Unit': 'Milliseconds'
        }
    ]
)
```

### Dashboards
- Visual representation of metrics
- Real-time or historical data
- Combine metrics from multiple services
- Share dashboards across team
- Create custom visualizations

## Alarms and Notifications

### Setting Up Alarms
```bash
aws cloudwatch put-metric-alarm \
  --alarm-name high-lambda-errors \
  --metric-name Errors \
  --namespace AWS/Lambda \
  --statistic Sum \
  --period 300 \
  --threshold 10 \
  --comparison-operator GreaterThanThreshold
```

### Alarm States
- **OK**: Metric within threshold
- **ALARM**: Metric exceeded threshold
- **INSUFFICIENT_DATA**: Not enough data to evaluate

### Notifications
- SNS topics trigger notifications
- Email, SMS, Slack integration via SNS
- CloudWatch → SNS → Notification channel
- Create runbooks for alarm responses

## Lambda Error Diagnosis

### Common Error Types

| Error | Cause | Solution |
|-------|-------|----------|
| **TimeoutException** | Execution took > timeout | Increase timeout or optimize code |
| **OutOfMemory** | Memory limit exceeded | Increase memory allocation |
| **UnrecognizedCreditExpression** | IAM permission denied | Check execution role policies |
| **ResourceNotFound** | S3 bucket, DB doesn't exist | Verify resource names and region |
| **ConfigurationError** | Invalid handler or runtime | Check function configuration |
| **ThrottlingException** | Concurrent execution limit hit | Request limit increase or optimize |

### Debugging Steps
1. **Check logs**: CloudWatch Logs for error messages
2. **Check metrics**: Monitor errors, duration, throttles
3. **Test locally**: Replicate issue in development
4. **Check IAM**: Verify execution role has needed permissions
5. **Check service**: Is dependent service available?
6. **Review code**: Look for logic errors or edge cases

## X-Ray Tracing

### Overview
- Distributed tracing service for end-to-end visibility
- Traces Lambda invocation and service dependencies
- Shows latency bottlenecks and failures
- Creates service map showing inter-service communication

### Enabling X-Ray
1. Add X-Ray write access to Lambda execution role
2. Import X-Ray SDK in code
3. X-Ray automatically traces AWS service calls

### X-Ray Example (Python)
```python
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.ext.flask.middleware import XRayMiddleware

@xray_recorder.capture('lambda_handler')
def lambda_handler(event, context):
    # Code here is traced
    response = s3.get_object(...)
    return response
```

### Service Map
- Visual representation of service communication
- Shows latency and error rates
- Identifies slow services
- Tracks requests through multiple services

### Traces
- End-to-end request journey
- Breaks down into segments (individual service calls)
- Shows duration of each segment
- Identifies where time is spent

## Log Retention and Cleanup

### Cost Optimization
- CloudWatch Logs storage costs money
- Set retention on log groups to prevent unlimited growth
- Reduce verbosity: Log only necessary information
- Archive old logs to S3 for compliance

### Retention Examples
```bash
aws logs put-retention-policy \
  --log-group-name /aws/lambda/my-function \
  --retention-in-days 30
```

## Verifying Service Integrations

### Test Checklist
- [ ] Lambda can invoke target service
- [ ] Target service responds correctly
- [ ] Permissions are correct (IAM role)
- [ ] Network connectivity works (VPC/subnets if applicable)
- [ ] API endpoints are correct
- [ ] Resource exists and is accessible

### Integration Testing
```python
def test_s3_integration():
    s3 = boto3.client('s3')
    s3.head_bucket(Bucket='my-bucket')  # Verify bucket exists
    
def test_dynamodb_integration():
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('my-table')
    table.scan(Limit=1)  # Verify table exists and accessible
```

## Monitoring Best Practices

- **Alert on SLOs**: Set alerts based on service level objectives
- **Log strategically**: Log important state changes, not every line
- **Use structured logging**: JSON format for easy parsing
- **Set retention policies**: Balance compliance and cost
- **Create dashboards**: At-a-glance view of system health
- **Tag resources**: Track costs and ownership
- **Automate remediation**: Auto-scale, restart, or notify on issues
- **Review metrics regularly**: Catch trends early
- **Test alerting**: Verify notifications work before production
- **Document runbooks**: Provide clear steps for each alarm
