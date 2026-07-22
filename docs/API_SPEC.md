# API Specification

# Enterprise Agent Lab

Version: 1.0

Author: Param Patel

Status: Approved

Last Updated: July 2026

---

# Table of Contents

1. API Principles
2. Authentication
3. Standard Response Format
4. Error Format
5. World APIs
6. Document APIs
7. Task APIs
8. Execution APIs
9. Evaluation APIs
10. Leaderboard APIs
11. Analytics APIs
12. Settings APIs
13. Health APIs
14. Future APIs

---

# 1. API Principles

Architecture Style

REST

Data Format

JSON

Authentication

JWT (Future)

Current MVP

Development Authentication

API Version

/api/v1

Content-Type

application/json

File Uploads

multipart/form-data

---

# 2. Standard Success Response

{
    "success": true,
    "message": "World created successfully.",
    "data": {}
}

---

# 3. Standard Error Response

{
    "success": false,
    "error": {
        "code": "WORLD_NOT_FOUND",
        "message": "Requested world does not exist."
    }
}

---

# 4. World APIs

Base Route

/api/v1/worlds

---

## Create World

POST /worlds

Request

{
    "name": "TechNova",
    "description": "Enterprise Finance Company",
    "industry": "Finance"
}

Response

201 Created

{
    "success": true,
    "data": {
        "id": "...",
        "name": "TechNova"
    }
}

---

## List Worlds

GET /worlds

Response

200 OK

[
    {
        "id": "...",
        "name": "...",
        "documents": 12,
        "tasks": 8
    }
]

---

## Get World

GET /worlds/{world_id}

---

## Update World

PATCH /worlds/{world_id}

---

## Delete World

DELETE /worlds/{world_id}

---

# 5. Document APIs

Base Route

/api/v1/documents

---

## Upload Documents

POST /documents/upload

Form Data

world_id

files[]

Response

{
    "uploaded": 5,
    "status": "processing"
}

---

## List Documents

GET /documents?world_id={id}

---

## Get Document

GET /documents/{document_id}

---

## Delete Document

DELETE /documents/{document_id}

---

## Trigger Indexing

POST /documents/{document_id}/index

---

## Search Documents

POST /documents/search

Request

{
    "world_id":"...",
    "query":"Find the vendor contract.",
    "top_k":5
}

Response

[
    {
        "chunk":"...",
        "score":0.92,
        "document":"contract.pdf",
        "page":8
    }
]

---

# 6. Task APIs

Base Route

/api/v1/tasks

---

## Create Task

POST /tasks

Request

{
    "world_id":"...",
    "title":"Approve Invoice",
    "description":"Determine if invoice should be approved.",
    "difficulty":"Hard",
    "ground_truth":"Reject",
    "rubric":"..."
}

---

## List Tasks

GET /tasks?world_id={id}

---

## Get Task

GET /tasks/{task_id}

---

## Update Task

PATCH /tasks/{task_id}

---

## Delete Task

DELETE /tasks/{task_id}

---

# 7. Execution APIs

Base Route

/api/v1/executions

---

## Execute Task

POST /executions/run

Request

{
    "world_id":"...",
    "task_id":"...",
    "model":"gpt-5",
    "prompt_version":"v1"
}

Response

{
    "execution_id":"..."
}

---

## Execution Status

GET /executions/{execution_id}

---

## Execution Trace

GET /executions/{execution_id}/trace

Response

{
    "steps":[]
}

---

## Tool Calls

GET /executions/{execution_id}/tools

---

## Retrieved Chunks

GET /executions/{execution_id}/retrieval

---

## Final Answer

GET /executions/{execution_id}/answer

---

# 8. Evaluation APIs

Base Route

/api/v1/evaluations

---

## Evaluate Execution

POST /evaluations/{execution_id}

---

## Get Evaluation

GET /evaluations/{execution_id}

Response

{
    "accuracy":94,
    "groundedness":91,
    "citation_score":98,
    "retrieval_score":90,
    "hallucination_score":4,
    "overall_score":94
}

---

# 9. Leaderboard APIs

Base Route

/api/v1/leaderboard

---

## Global Leaderboard

GET /leaderboard

---

## World Leaderboard

GET /leaderboard/world/{world_id}

---

## Task Leaderboard

GET /leaderboard/task/{task_id}

---

## Compare Models

POST /leaderboard/compare

Request

{
    "models":[
        "gpt-5",
        "claude-sonnet",
        "gemini-pro"
    ],
    "task_id":"..."
}

---

# 10. Analytics APIs

Base Route

/api/v1/analytics

---

## Dashboard

GET /analytics/dashboard

Returns

Runs

Average Accuracy

Average Cost

Average Latency

Total Documents

Total Worlds

---

## Execution History

GET /analytics/history

---

## Recent Runs

GET /analytics/recent

---

## Cost Analysis

GET /analytics/cost

---

## Latency Analysis

GET /analytics/latency

---

## Accuracy Trends

GET /analytics/accuracy

---

# 11. Settings APIs

GET /settings

PATCH /settings

---

# 12. Health APIs

GET /health

Returns

{
    "status":"healthy"
}

---

GET /health/database

---

GET /health/vectorstore

---

GET /health/providers

Checks

OpenAI

Anthropic

Gemini

Ollama

---

# 13. Future APIs

Prompt Registry

/api/v1/prompts

Model Registry

/api/v1/models

Experiments

/api/v1/experiments

Benchmarks

/api/v1/benchmarks

Human Review

/api/v1/reviews

Approval Queue

/api/v1/approvals

Workflow Builder

/api/v1/workflows

Knowledge Graph

/api/v1/knowledge

Plugins

/api/v1/plugins

Enterprise Connectors

/api/v1/connectors

Slack

Salesforce

Notion

Confluence

SharePoint

---

# HTTP Status Codes

200 OK

201 Created

202 Accepted

204 No Content

400 Bad Request

401 Unauthorized

403 Forbidden

404 Not Found

409 Conflict

422 Validation Error

429 Too Many Requests

500 Internal Server Error

---

# Pagination

All list APIs use

?page=1

&limit=20

Example

GET /worlds?page=1&limit=20

Response

{
    "items":[],
    "page":1,
    "limit":20,
    "total":124
}

---

# Filtering

Supported Query Parameters

search

sort

order

department

difficulty

model

world_id

Example

GET /tasks?difficulty=Hard&department=Finance

---

# API Rules

1. Every endpoint returns JSON.

2. Routes never contain business logic.

3. Validation uses Pydantic schemas.

4. Every resource uses UUIDs.

5. Every endpoint returns consistent response structures.

6. PATCH is used for partial updates.

7. DELETE performs soft delete where applicable.

8. Long-running operations (indexing, execution, evaluation) return immediately and are processed asynchronously.

9. Every endpoint must be documented with OpenAPI (Swagger).

10. Every new API version is introduced under `/api/v2` without breaking `/api/v1`.