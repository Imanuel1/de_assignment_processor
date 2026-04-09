# Design Decisions

## 1. Job Pickup Strategy

Approach chosen: [Using RabbitMQ and aio-pika creating custom retry stratgy for failed job ]
Why: [Using RabbitMq is build for background job processing, and creating custom retry logic in order to create an Exponential retry delay]
Trade-offs: [The implementation of it a litle bigger, need to define the publish instead of using the build in requeue, but this way i can controll the delay the way i need and not constant retry delay]

## 2. Worker Crash Recovery

Approach chosen: [Explicit ack with a Graceful Shutdown Lifespan]
Why: [i used a message.process() context manager which only sends an ack to RabbitMQ after the Python code successfully finishes or defined as failure job]
What happens if worker crashes mid-job: [If the worker (processor service) is crushes, first i drop the RabbitM connection, so new message will stop comming to the consumer then i implemented an active_tasks tracker in the FastAPI lifespan that waits for active processing job to finish and then the DB updates to finish job before allowing the service to exit]

## 3. Priority Queue Implementation

Approach chosen: [RabbitMQ Priority Queue x-max-priority]
Why: [i used a single jobs queue configured with a priority range (1–10). This allows the RabbitMQ broker to reorder the internal buffer so that a higher priority job is delivered to the next available worker before a lowwer priority job, even if the low priority job arrived earlier]

## 4. Retries and Delay Strategy

Approach chosen: [Exponential Delay with RabbitMQ x-delayed-message plugin]
Timing: [CONSTANT_DELAY * times 2^{attempt}, the CONSTANT_DELAY is defined as an ENV so it can be dynamicly change, default is 1 ]

## 5. One Thing I Would Do Differently With More Time

- use authentication with Token for the api service requests
- reorganize the code more, add router file api service