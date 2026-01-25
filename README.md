# Async Task Queue System (FastAPI + RabbitMQ + MySQL)
## Project Overview
### This project implements a robust asynchronous task processing backend system using a message queue architecture. Instead of processing long-running tasks synchronously inside an API request, tasks are queued and processed asynchronously by a dedicated worker service.
### The system demonstrates real-world backend design patterns used in scalable, distributed systems such as:
- Message queues (RabbitMQ)
- Producer–consumer architecture
- Asynchronous background processing
- Decoupled microservices
- Reliable task state persistence
- Docker-based service orchestration

## Objective
### To design and implement a backend system that:
- Accepts task submissions via a REST API
- Stores task metadata persistently
- Publishes tasks to a message queue
- Processes tasks asynchronously using a worker
- Updates task status reliably
- Allows clients to query task status at any time

## Architecture Overview
```
Client
  |
  |  POST /api/tasks
  v
API Service (FastAPI)
  |
  |  Publish message
  v
RabbitMQ Queue
  |
  |  Consume message
  v
Worker Service
  |
  |  Update status
  v
MySQL Database
```
### Key Design Decisions
- Decoupling: API never performs heavy work directly.
- Scalability: Worker service can be horizontally scaled.
- Reliability: Tasks are persisted before publishing.
- Asynchronous Processing: Ensures fast API response times.
- Durability: RabbitMQ acknowledgements prevent message loss.

## Technology Stack

| Component        | Technology              |
|------------------|-------------------------|
| API Framework    | FastAPI (Python)        |
| Worker           | Python                  |
| Message Queue    | RabbitMQ                |
| Database         | MySQL 8                 |
| ORM              | SQLAlchemy              |
| Containerization | Docker                  |
| Orchestration    | Docker Compose          |
| Testing          | Pytest                  |
| API Docs         | OpenAPI / Swagger       |


## Project Structure
```
async-task-queue-system
├── api-service/
│   ├── src/
│   │   ├── main.py
│   │   ├── api/
│   │   │   └── tasks.py
│   │   ├── db/
│   │   ├── models/
│   │   └── services/
│   ├── tests/
│   │   ├── test_unit_tasks.py
│   │   └── test_integration_flow.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── worker-service/
│   ├── src/
│   │   └── main.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── db/
│   └── init.sql
│
├── docker-compose.yml
├── .env.example
└── README.md
```

## Database Schema
### The database schema is initialized automatically using db/init.sql.
```
CREATE TABLE tasks (
    id VARCHAR(36) PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    status ENUM('PENDING','PROCESSING','COMPLETED','FAILED')
        NOT NULL DEFAULT 'PENDING',
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL
);
```

## API Endpoints
- Submit a Task
### POST /api/tasks
- Request Body
```
{
  "title": "Sample Task",
  "description": "Process something",
  "metadata": {
    "priority": "high"
  }
}
```
- Response (202 Accepted)
```
{
  "task_id": "uuid",
  "message": "Task submitted successfully"
}
```
- Get Task Status
  ### GET /api/tasks/{task_id}
Response
```
{
  "task_id": "uuid",
  "title": "Sample Task",
  "description": "Process something",
  "status": "COMPLETED",
  "metadata": {
    "priority": "high"
  },
  "created_at": "2026-01-23T04:17:34",
  "updated_at": "2026-01-23T04:17:39",
  "completed_at": "2026-01-23T04:17:39"
}
```

### Error Responses
- 400 – Invalid request
- 404 – Task not found
- 500 – Internal server error

## Worker Service Logic
- Listens continuously to RabbitMQ queue
- Consumes task messages
- Marks task as PROCESSING
- Simulates work (sleep)
- Marks task as COMPLETED
- Updates completed_at timestamp
- Acknowledges message only after success
This ensures idempotency and reliability.

## Docker Setup
- Configure environment variables
```
cp .env.example .env
```
- Start all services
```
docker compose up --build
```
Services started:
- API → http://localhost:8000
- Swagger UI → http://localhost:8000/docs
- RabbitMQ UI → http://localhost:15672
- MySQL → localhost:3306

## Port Exposure Design Decision
### Not all services in this project expose ports to the host machine. This is an intentional architectural decision.
### Why some ports are removed:
- Internal-only services (MySQL, Worker, RabbitMQ AMQP) are accessed only by other Docker containers via the Docker network.
- Exposing unnecessary ports increases:
  - Security risk
  - Configuration complexity
  - Chance of port conflicts on the host

### What is exposed and why:
- API Service (8000)
Exposed so clients can submit tasks and query task status.
- RabbitMQ Management UI (15672)
Exposed only for monitoring and debugging.

### What is NOT exposed:
- Worker Service
No HTTP interface; it only consumes messages from RabbitMQ.
- MySQL Database
Accessed internally by API and Worker via Docker networking.
- RabbitMQ AMQP Port (5672)
Used only for internal message passing.

### Benefits of this approach:
- Follows least privilege principle
- Improves security
- Matches production-grade Docker deployments
- Keeps the system clean and maintainable

## Testing
Automated Tests Implemented
- Unit Tests
  - Input validation
  - Task creation logic
  - Error handling

- Integration Tests
  - Full async flow:
    - Submit task
    - Worker processes task
    - Status changes to COMPLETED

## Run Tests
```
docker compose exec api_service pytest
```
### Sample Output
```
4 passed, 1 warning in 6.68s
```
## Error Handling & Validation
- Pydantic input validation
- Standardized JSON error responses
- Proper HTTP status codes
- Database and queue failure handling
- Safe message acknowledgements (ACK/NACK)

## Scalability & Reliability
- Worker service can be scaled independently
- RabbitMQ ensures message durability
- API remains responsive under load
- No tight coupling between services


