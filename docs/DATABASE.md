# Database Design

# Enterprise Agent Lab

Version: 1.0

Author: Param Patel

Status: Approved

Last Updated: July 2026

---

# Table of Contents

1. Database Philosophy
2. Design Principles
3. Database Overview
4. Entity Relationship
5. Table Specifications
6. Relationships
7. Indexing Strategy
8. Vector Storage
9. Audit Strategy
10. Future Tables

---

# 1. Database Philosophy

The database is designed around one core concept:

**Every execution must be reproducible.**

Given an execution ID, the platform should reconstruct:

- World
- Task
- Prompt
- Retrieved Documents
- Tool Calls
- Model
- Output
- Evaluation

Nothing should be lost.

---

# 2. Design Principles

- UUID primary keys
- Immutable execution history
- Soft delete where appropriate
- Provider agnostic
- Normalized schema
- Metadata stored as JSON when flexible
- Full traceability
- Version everything important

---

# 3. Database Overview

Core Tables

Users

↓

Worlds

↓

Documents

↓

Chunks

↓

Tasks

↓

Executions

↓

Execution Steps

↓

Tool Calls

↓

Evaluations

↓

Leaderboard Entries

Supporting Tables

Models

Prompt Versions

Reports

Settings

---

# 4. Entity Relationship Diagram

User

│

├── Worlds

│      │

│      ├── Documents

│      │       │

│      │       └── Chunks

│      │

│      ├── Tasks

│      │

│      └── Executions

│               │

│               ├── Execution Steps

│               ├── Tool Calls

│               ├── Retrieved Chunks

│               └── Evaluation

│

└── Reports

---

# 5. Table Specifications

---

## users

Purpose

Platform users.

Columns

id (UUID)

name

email

password_hash

role

created_at

updated_at

Indexes

email UNIQUE

---

## worlds

Purpose

Represents a simulated enterprise.

Examples

TechNova

LegalCorp

RetailHub

Columns

id

owner_id

name

description

industry

status

metadata (JSON)

created_at

updated_at

Relationships

One World

↓

Many Documents

Many Tasks

Many Executions

---

## documents

Purpose

Uploaded enterprise files.

Columns

id

world_id

filename

document_type

department

storage_path

file_size

checksum

metadata (JSON)

created_at

Indexes

world_id

document_type

department

---

## chunks

Purpose

Searchable document fragments.

Columns

id

document_id

chunk_number

text

token_count

page_number

embedding_id

metadata

Relationships

One Document

↓

Many Chunks

---

## embeddings

Purpose

Vector storage metadata.

(The actual vector lives in pgvector.)

Columns

id

chunk_id

embedding_model

embedding_dimension

created_at

---

## tasks

Purpose

Business problems.

Columns

id

world_id

title

description

difficulty

department

ground_truth

rubric

expected_output

metadata

created_at

Indexes

world_id

difficulty

department

---

## executions

Purpose

One model solving one task.

Columns

id

task_id

world_id

model_id

prompt_version_id

status

started_at

completed_at

duration_ms

token_input

token_output

cost

final_answer

error_message

Relationships

One Execution

↓

Many Steps

Many Tool Calls

Many Retrieved Chunks

One Evaluation

---

## execution_steps

Purpose

Replayable execution timeline.

Columns

id

execution_id

step_number

step_type

description

input

output

latency_ms

created_at

Example

Search

↓

Retrieve

↓

Tool

↓

Reason

↓

Answer

---

## tool_calls

Purpose

Every tool invocation.

Columns

id

execution_id

tool_name

arguments

response

success

latency_ms

created_at

---

## retrieved_chunks

Purpose

Documents used by execution.

Columns

id

execution_id

chunk_id

similarity_score

retrieval_rank

Indexes

execution_id

chunk_id

---

## evaluations

Purpose

Execution quality.

Columns

id

execution_id

accuracy

groundedness

citation_score

retrieval_score

hallucination_score

tool_success

latency_score

overall_score

feedback

created_at

---

## models

Purpose

Supported LLM providers.

Columns

id

provider

model_name

context_window

max_output_tokens

supports_tools

supports_json

metadata

Examples

GPT-5

Claude Sonnet

Gemini 2.5 Pro

Llama 3

---

## prompt_versions

Purpose

Version prompts.

Columns

id

name

version

system_prompt

description

created_at

Allows experiments.

---

## reports

Purpose

Export benchmark reports.

Columns

id

world_id

execution_id

report_type

storage_path

created_at

---

## settings

Purpose

Global configuration.

Columns

id

key

value

updated_at

---

# 6. Relationships

User

1:N

World

World

1:N

Document

Document

1:N

Chunk

World

1:N

Task

Task

1:N

Execution

Execution

1:N

Execution Step

Execution

1:N

Tool Call

Execution

1:N

Retrieved Chunk

Execution

1:1

Evaluation

---

# 7. Indexing Strategy

Indexes

users.email

documents.world_id

documents.document_type

chunks.document_id

tasks.world_id

executions.task_id

executions.world_id

evaluations.execution_id

retrieved_chunks.execution_id

---

Composite Indexes

(world_id, document_type)

(task_id, model_id)

(world_id, department)

---

# 8. Vector Storage

Vectors are NOT stored inside normal SQL columns.

pgvector stores

embedding VECTOR(3072)

Associated metadata remains in SQL.

Search

Question

↓

Embedding

↓

Vector Search

↓

Chunk IDs

↓

Chunk Metadata

↓

LLM Context

---

# 9. Audit Strategy

Every important action creates an immutable record.

Tracked Events

World Created

Document Uploaded

Task Created

Execution Started

Tool Called

Execution Completed

Evaluation Generated

No execution should ever be modified after completion.

Corrections create new records.

---

# 10. Future Tables

agent_versions

benchmark_runs

workflow_templates

tool_registry

approval_queue

human_reviews

connectors

organizations

api_keys

model_gateways

telemetry

experiment_runs

prompt_experiments

dataset_versions

feature_flags

plugin_registry

knowledge_graph_nodes

knowledge_graph_edges

---

# Naming Conventions

Tables

snake_case plural

Columns

snake_case

Primary Keys

id UUID

Foreign Keys

<entity>_id

JSON

metadata

Timestamps

created_at

updated_at

deleted_at

---

# Database Rules

1. Every execution is immutable.

2. Every entity uses UUID.

3. Never store embeddings as JSON.

4. Every execution references exactly one task.

5. Every task belongs to exactly one world.

6. Every chunk belongs to one document.

7. Tool calls must be replayable.

8. Evaluations cannot exist without executions.

9. Documents never directly reference tasks.

10. Every important entity includes metadata for extensibility.