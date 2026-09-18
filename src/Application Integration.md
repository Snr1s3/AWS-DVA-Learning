# Application Integration

Application Integration in AWS focuses on how different applications, services, and components communicate asynchronously with each other.

## Core Concepts

### Event-Driven Architecture
- Applications communicate through events rather than direct calls
- Decouples producers and consumers
- Enables scalability and resilience

## Key AWS Services

### Amazon SQS (Simple Queue Service)
- Message queue service for asynchronous communication
- **Delivery guarantees**: At least once delivery (can have duplicates)
- **Standard queues**: Unlimited throughput
- **FIFO queues**: Guaranteed ordering and exactly-once delivery
- Messages can sit in queue for up to 14 days
- Workflow: Producers put messages → Consumers poll for messages

### Amazon SNS (Simple Notification Service)
- Pub/Sub messaging service for broadcasting
- **Topics**: Channels where messages are published
- **Subscriptions**: Endpoints that receive messages (SQS, Lambda, HTTP, email, etc.)
- Fan-out pattern: One message published to multiple subscribers
- Push-based delivery model

### AWS Lambda
- Serverless compute service for event processing
- Can be triggered by SQS, SNS, EventBridge, S3, and other services
- Executes code in response to events
- Scales automatically

### Amazon EventBridge
- Event routing and transformation service
- Routes events from sources to targets based on rules
- Supports event filtering before routing
- Supports CloudEvents standard format
- Enables complex event workflows

## Design Patterns

### Fan-Out Pattern (SNS + SQS)
- Publish message to SNS topic
- Multiple SQS queues subscribe to the topic
- Each queue receives a copy → multiple consumers process independently
- Enables parallel processing with guaranteed delivery to each queue

### Dead-Letter Queues (DLQ)
- Capture messages that fail processing after max retries
- Separate queue for investigation and debugging
- Prevents poison messages from blocking the system
- Critical for system reliability

### Event Filtering & Transformation
- EventBridge can filter events before routing to targets
- Transform event structure for compatibility with target services
- Reduces unnecessary processing and costs

## When to Use What

| Use Case | Service |
|----------|---------|
| Direct queue-based communication | SQS |
| Worker pools and buffering | SQS |
| Broadcasting to multiple subscribers | SNS |
| Notifications and alerts | SNS |
| Complex routing rules | EventBridge |
| Event transformation | EventBridge |
| Multiple event sources | EventBridge |
| Serverless event processing | Lambda |
