# AI_DEVELOPER_GUIDE.md

# Enterprise Agent Lab

Version: 1.0

Author: Param Patel

Status: REQUIRED READING

---

# Purpose

This document defines how AI coding assistants should contribute to
Enterprise Agent Lab.

It exists to ensure all generated code follows the same architecture,
coding style, quality standards, and project vision.

Before writing ANY code, the AI assistant MUST read this document together
with all project documentation.

This document has higher priority than ad-hoc implementation requests unless
explicitly overridden by the project owner.

---

# Project Vision

Enterprise Agent Lab is NOT an AI chatbot.

It is NOT another RAG demo.

It is NOT an LLM wrapper.

Enterprise Agent Lab is an open platform for

• Building enterprise environments

• Executing AI agents

• Benchmarking models

• Evaluating AI systems

• Observing execution behavior

Every feature should support one of those goals.

If a requested implementation does not align with this vision,
the AI should explain why before proceeding.

---

# Required Reading Order

Before implementing anything, read the following files.

1. PROJECT_SPEC.md

2. SRS.md

3. ARCHITECTURE.md

4. DATABASE.md

5. API_SPEC.md

6. UI_SPEC.md

7. ROADMAP.md

8. CODING_STANDARDS.md

9. This document

Implementation must follow those documents.

Never invent architecture.

---

# Core Principles

Enterprise Agent Lab is designed around

Control Plane

↓

Execution Plane

↓

Observability Plane

Every implementation must respect this separation.

---

Control Plane

Responsible for

Configuration

Worlds

Tasks

Prompt Versions

Models

Settings

Experiments

Never execute AI here.

---

Execution Plane

Responsible for

Retrieval

Planning

Tool Calling

LLM Inference

Execution

Tracing

Never perform evaluation here.

---

Observability Plane

Responsible for

Evaluation

Analytics

Reports

Leaderboard

Benchmarking

Never execute models here.

---

# Development Philosophy

Always optimize for

Maintainability

↓

Correctness

↓

Readability

↓

Extensibility

↓

Performance

Never optimize prematurely.

---

# Implementation Rules

Only implement what was requested.

Never continue into future milestones.

Never add "nice to have" features.

Never modify unrelated modules.

Never rename existing APIs.

Never change folder structure.

Never redesign architecture.

Never remove tests.

Never remove logging.

---

# Milestone Workflow

Every implementation follows this sequence.

Understand milestone

↓

Read related documentation

↓

Review existing code

↓

Design implementation

↓

Implement

↓

Write tests

↓

Run static checks

↓

Review code

↓

Stop

Never continue to the next milestone automatically.

---

# Before Writing Code

The AI assistant should ask itself

Do I understand this milestone?

Have I read the relevant documents?

Will this implementation violate architecture?

Will this break existing APIs?

Can I reuse existing modules?

Can this feature be independently tested?

If any answer is "No"

STOP

Explain the issue.

---

# Coding Rules

Every function

• Small

• Typed

• Documented

Every class

• Single responsibility

Every module

• Independent

Every API

• Validated

Every database operation

• Repository pattern

Every business rule

• Service layer

---

# Architecture Rules

Routes

↓

Services

↓

Repositories

↓

Database

Never skip layers.

Never access the database inside routes.

Never call repositories from frontend.

Never place business logic in React components.

---

# AI Provider Rules

All models are accessed ONLY through LiteLLM.

Never import

OpenAI

Anthropic

Gemini

directly inside business logic.

Only the provider abstraction layer may communicate with LLM APIs.

---

# RAG Rules

Documents

↓

Extraction

↓

Chunking

↓

Embeddings

↓

Vector Search

↓

Context Builder

↓

LLM

↓

Evaluation

Never bypass retrieval.

Never send full documents directly to the model.

Always preserve metadata.

Always preserve citations.

---

# Database Rules

Every entity

UUID

Every execution

Immutable

Soft delete where appropriate.

Repositories own persistence.

Services own transactions.

Never commit inside repositories.

---

# API Rules

REST

Versioned

Validated

Typed

Documented

Every response

Uses standard response schema.

Every error

Uses standard error schema.

---

# Frontend Rules

Feature-first organization.

Reusable components.

Strong typing.

No API logic inside components.

No business logic inside pages.

All API calls go through a centralized client.

---

# Logging Rules

Every major action should log

Execution Started

Execution Completed

Evaluation Generated

Background Job Started

Background Job Finished

Unexpected Errors

Never log

Secrets

Passwords

API Keys

Embeddings

Personal data

---

# Testing Rules

Every new feature requires

Unit Tests

Integration Tests

API Tests (if applicable)

Regression Tests (when fixing bugs)

Never merge untested code.

---

# Performance Rules

Avoid unnecessary queries.

Avoid repeated embeddings.

Cache expensive operations.

Batch inserts.

Background process long-running tasks.

Target Metrics

API

<300ms

Search

<500ms

Dashboard

<2 seconds

---

# Documentation Rules

Every public class

Docstring

Every public method

Docstring

Every module

Purpose at top

Every complex algorithm

Explanation

Document WHY

not WHAT.

---

# Git Rules

One milestone

↓

One commit

Commit messages

feat:

fix:

refactor:

docs:

test:

perf:

style:

chore:

Never mix unrelated work.

---

# Code Review Checklist

Before returning code, verify

✓ Builds successfully

✓ Lint passes

✓ Type checking passes

✓ Tests pass

✓ Documentation updated

✓ Uses dependency injection

✓ Uses repository pattern

✓ Uses service layer

✓ Uses logging

✓ Uses validation

✓ Handles failures

✓ No duplicated code

✓ No TODO comments

✓ No commented code

✓ No debug statements

✓ No hardcoded secrets

If any item fails

Fix it before responding.

---

# Response Format

When implementing a milestone, respond in the following order.

1. Summary

Explain what was implemented.

2. Files Changed

List every modified file.

3. Design Decisions

Explain important architectural decisions.

4. Code

Provide implementation.

5. Tests

Provide tests.

6. Manual Testing Steps

Explain how to verify.

7. Possible Improvements

List future work.

Stop after completing the requested milestone.

---

# Forbidden Changes

Never

Change architecture

Change APIs

Change folder structure

Change database schema

Change response formats

Rename modules

Invent new services

Skip repository layer

Skip service layer

Use different libraries

Ignore coding standards

Implement future milestones

Unless explicitly instructed.

---

# If Requirements Are Ambiguous

Do NOT guess.

Instead

Explain the ambiguity.

List assumptions.

Recommend the best solution.

Wait for confirmation if the ambiguity affects architecture.

---

# If Existing Code Conflicts with Documentation

Documentation is the source of truth.

Do not silently modify architecture.

Explain the conflict.

Recommend the smallest possible change.

Wait for approval before proceeding.

---

# Definition of Success

The implementation is successful only if

✓ It satisfies the requested milestone.

✓ It follows every architecture rule.

✓ It passes all tests.

✓ It introduces no breaking changes.

✓ It is production-ready.

✓ Another engineer can understand it without additional explanation.

Quality is more important than speed.

Enterprise Agent Lab should feel like software developed by a senior engineering team—not a collection of AI-generated files.