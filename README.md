#Distributed Job Processor
A high-performance, resilient distributed job processing system built with FastAPI, RabbitMQ (with Delayed Message Plugin), and PostgreSQL. This system supports job scheduling, priority-based execution, and exponential backoff retries.

##🏗 Architecture Overview
The system is designed as a decoupled producer-consumer architecture:

**API Service (Producer)**: A FastAPI application that receives job requests, persists them to PostgreSQL, and publishes them to RabbitMQ.

**Redis Cache**: Help to use storing the idempotency_key for each new job submited, and rechecking it for existing idempotency_key, with TTL of 24 hours

**RabbitMQ (Message Broker)**: Uses the x-delayed-message exchange to handle scheduled jobs and a Priority Queue to manage job urgency.

**Processor Service (Consumer)**: A scalable worker service that consumes jobs, executes the logic (e.g., Webhooks, Emails), and updates the job status in the database. It features a Graceful Shutdown mechanism to ensure in-flight jobs finish during deployments.

##🚀 How to Run the Project
Prerequisites
Docker and Docker Compose

Windows Users: PowerShell (to run automation scripts)

**Setup & Start**
Clone the repository:

Bash
git clone <https://github.com/Imanuel1/de_assignment_processor>
cd de_assignment_processor

PowerShell
#at the start just run everything on the docker-compose
`docker-compose up -d --build`

#if some of the services isn't running :
# 1. try to run play on it from the docker desktop
# 2. if 1 option isn't working run this command to build again your specifc service:
`docker-compose up -d --build service_name` (for example - service_name= api_service)

This will start the API, PostgreSQL, RabbitMQ, and three instances of the Processor service.

##🧪 How to Run TestsThe project includes an automated test suite and a custom runner script to simulate failures and verify retry logic
.1. Enable Script Execution (Windows Only)If you are on Windows, you may need to enable script execution for the current session:
`PowerShellSet-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process` 
2. Run the Automated Test SuiteRun the custom PowerShell script. This script automatically sets the environment to a 0% success rate to test retries, runs pytest, and then restores the environment.PowerShell
`./tests/run_tests.ps1`
3. Run ManuallyTo run tests without the automation script:Bash
`docker-compose exec api_service pytest tests/`

##📩 How to Submit a Test Job
You can submit jobs via POST requests to the API.

Example: Webhook Job with schedule_time Delay
Bash
curl -X 'POST' \
 'http://localhost:8000/jobs' \
 -H 'Content-Type: application/json' \
 -d '{
"idempotency_key": "unique_test_key_001",
"job_type": "webhook",
"priority": 3,
"payload": {
"url": "[http://example.com/webhook](http://example.com/webhook)",
"method": "POST"
},
"scheduled_time": "2026-04-09T14:00:00Z"
}'

Example: Email Job (Immediate)
Bash
curl -X 'POST' \
 'http://localhost:8000/jobs' \
 -H 'Content-Type: application/json' \
 -d '{
"idempotency_key": "email_task_101",
"job_type": "email",
"priority": 2,
"payload": {
"to": "user@example.com",
"subject": "Hello",
"body": "Your job is complete!"
}
}'

##📊 Monitoring
API Health: http://localhost:8000/
PROCESSOR Health: http://localhost:8081/
SERVICES HEALTH: http://localhost:8000/health

RabbitMQ Management: http://localhost:15672 (guest/guest)
