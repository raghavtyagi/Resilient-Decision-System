# Resilient Decision System

## Overview

This project implements a configurable workflow decision platform that processes structured requests, evaluates rules dynamically, executes workflows, and maintains full audit logs. The system is designed to be resilient, explainable, and adaptable to changing business requirements.

## Features

* Config-driven rules and workflows (no hardcoding)
* Workflow execution with branching (APPROVED, MANUAL_REVIEW, RETRY)
* Full audit logging with explanations
* Idempotent request handling
* Failure handling with retry mechanism
* State lifecycle tracking

## Tech Stack

* Python
* FastAPI
* Pytest

## Setup Instructions

### 1. Install dependencies

pip install -r requirements.txt

### 2. Run the server

uvicorn main:app --reload

### 3. Open API docs

http://127.0.0.1:8000/docs

## API Endpoints

### Create Request

POST /request

### Get Status

GET /request/{id}

### Retry Request

POST /request/{id}/retry

### Get Audit Log

GET /audit/{id}

## Sample Request

{
"request_id": "123",
"type": "loan_application",
"data": {
"income": 50000,
"credit_score": 700
}
}

## Configuration

Rules and workflows are defined in config.json.

Example:

{
"rules": {
"income_check": {
"field": "income",
"operator": ">",
"value": 30000
}
}
}

You can modify thresholds or add rules without changing code.

## Running Tests

pytest test_system.py

## Design Highlights

* Modular architecture with separation of concerns
* Configurable rule engine
* Explainable decision-making
* Robust failure handling


