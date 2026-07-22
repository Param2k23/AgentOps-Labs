# CODING_STANDARDS.md

# Enterprise Agent Lab

Version: 1.0

Status: Approved

Author: Param Patel

---

# Table of Contents

1. Philosophy
2. General Rules
3. Repository Structure
4. Python Standards
5. FastAPI Standards
6. Database Standards
7. Frontend Standards
8. API Standards
9. AI Runtime Standards
10. Error Handling
11. Logging
12. Testing
13. Documentation
14. Git Workflow
15. Performance
16. Security
17. AI Coding Rules
18. Code Review Checklist
19. Definition of Done

---

# 1. Philosophy

Enterprise Agent Lab should feel like software built by a professional engineering team.

Priorities

Correctness

↓

Maintainability

↓

Readability

↓

Performance

↓

Optimization

Never optimize code before correctness.

Every module should be easy to understand by another engineer.

---

# 2. General Rules

✓ Use descriptive names.

✓ Keep functions small.

✓ Avoid duplicate logic.

✓ Prefer composition over inheritance.

✓ Write type hints everywhere.

✓ Prefer explicit code over clever code.

✓ Every feature must have tests.

✓ Every public method must have documentation.

✓ Every commit should leave the project in a working state.

---

# 3. Repository Structure

backend/

api/

core/

config/

middleware/

repositories/

services/

execution/

retrieval/

agents/

evaluation/

analytics/

workers/

models/

schemas/

utils/

frontend/

app/

components/

features/

hooks/

lib/

types/

styles/

tests/

docs/

docker/

scripts/

sample_worlds/

---

# 4. Python Standards

Python Version

3.12

Formatting

Black

Linting

Ruff

Type Checking

MyPy

Dependency Management

Poetry

Rules

Use dataclasses only when appropriate.

Prefer Pydantic models for validation.

Prefer async functions for I/O.

Never use wildcard imports.

Never ignore exceptions.

Avoid global variables.

No business logic in __init__.py.

Every function must have type hints.

---

Naming

snake_case

Classes

PascalCase

Constants

UPPER_CASE

Private Members

_prefix

---

Function Rules

Maximum 40 lines

Maximum 3 nested levels

Single Responsibility

No duplicated code

Return early

Avoid long if/else chains

---

# 5. FastAPI Standards

Routes

Only receive requests.

Validate input.

Call services.

Return responses.

Nothing else.

Business logic belongs only in services.

Repositories never return HTTP responses.

Dependency Injection should be used everywhere.

Use APIRouter for every module.

Each feature has its own router.

Never access the database directly from routes.

---

# 6. Database Standards

ORM

SQLAlchemy 2

Migrations

Alembic

Primary Keys

UUID

Relationships

Explicit

Indexes

Every frequently queried column

Soft Delete

Use deleted_at where appropriate

Rules

No raw SQL unless justified.

Repositories own database access.

Transactions handled in services.

Never commit inside repositories.

---

# 7. Frontend Standards

Framework

Next.js

Language

TypeScript

Styling

Tailwind CSS

Components

shadcn/ui

Data Fetching

TanStack Query

Forms

React Hook Form

Validation

Zod

---

Component Rules

Reusable

Typed

Pure whenever possible

Maximum 200 lines

No API logic inside components

No business logic inside pages

Feature-based organization

---

Naming

PascalCase Components

camelCase Hooks

camelCase Variables

---

# 8. API Standards

REST only

Versioned

/api/v1

JSON responses only

Consistent error format

Pagination

Filtering

Sorting

Validation

Use Pydantic

Never return ORM models directly.

Always return response schemas.

---

# 9. AI Runtime Standards

Model access only through LiteLLM.

Never call providers directly.

Every execution produces

Execution ID

Prompt

Retrieved Chunks

Tool Calls

Timing

Tokens

Cost

Final Response

Every execution is immutable.

Every execution is replayable.

Every execution is evaluable.

---

# 10. Error Handling

Every exception must be handled.

Create custom exceptions.

Examples

DocumentNotFound

WorldNotFound

ExecutionFailed

EvaluationFailed

ValidationError

Errors returned to users

should never expose stack traces.

---

# 11. Logging

Every request

INFO

Execution start

INFO

Tool Call

DEBUG

Evaluation

INFO

Failures

ERROR

Unexpected Errors

CRITICAL

Use structured logging.

Never log secrets.

Never log API keys.

Never log embeddings.

---

# 12. Testing

Framework

Pytest

Coverage

Minimum 90%

Test Types

Unit

Integration

API

End-to-End

Performance

Mock external APIs.

Never depend on live LLM providers.

Every bug fix requires a regression test.

---

# 13. Documentation

Every module needs

README (if complex)

Docstrings

Type hints

Comments only when necessary

Document WHY

not WHAT.

Public classes require documentation.

Public methods require documentation.

---

# 14. Git Workflow

Branch Names

feature/world-management

feature/rag

feature/evaluation

bugfix/search-ranking

docs/api-spec

Commits

Use Conventional Commits.

Examples

feat:

fix:

docs:

refactor:

test:

perf:

style:

chore:

Every milestone ends with a commit.

---

# 15. Performance

Background jobs for

Indexing

Evaluation

Large uploads

Target Metrics

Search

<500 ms

Dashboard

<2 sec

API

<300 ms

Avoid unnecessary database queries.

Prefer batch operations.

Cache expensive computations.

---

# 16. Security

Validate every request.

Validate uploads.

Parameterized queries only.

Secrets in .env

No credentials in code.

Limit upload size.

Sanitize filenames.

Validate MIME types.

Prepare for RBAC.

---

# 17. AI Coding Rules

These rules apply to all AI-generated code.

AI must never

Invent architecture

Change folder structure

Rename modules

Break existing APIs

Duplicate functionality

Modify unrelated files

Ignore typing

Skip tests

Generate placeholder implementations

AI must

Follow PROJECT_SPEC.md

Follow SRS.md

Follow ARCHITECTURE.md

Follow DATABASE.md

Follow API_SPEC.md

Follow UI_SPEC.md

Follow ROADMAP.md

Follow this document

Only implement the requested milestone.

Stop after completion.

---

# 18. Code Review Checklist

Before merging code

✓ Builds successfully

✓ Lint passes

✓ Tests pass

✓ Documentation updated

✓ No duplicated code

✓ Uses dependency injection

✓ Uses repository pattern

✓ Uses service layer

✓ Uses type hints

✓ Uses logging

✓ Uses validation

✓ Handles errors

✓ No hardcoded values

✓ No TODOs

✓ No commented code

✓ No debug prints

✓ No secrets

---

# 19. Definition of Done

A feature is complete only when

✓ Code compiles

✓ Tests pass

✓ Documentation updated

✓ APIs documented

✓ UI implemented

✓ Docker works

✓ Logs added

✓ Errors handled

✓ Code reviewed

✓ Performance acceptable

✓ Feature demonstrated

Otherwise

The feature is NOT complete.