# ⚙️ Backend Practice

A FastAPI backend built to practice clean architecture, OAuth
authentication, async database access, and automated testing.

## 🧰 Stack

-   **FastAPI** --- API framework
-   **Authlib** --- Google & Discord OAuth
-   **aiosqlite / SQLite** --- async persistence
-   **Pydantic** --- data models and validation
-   **pytest / pytest-asyncio** --- automated testing

## 📁 Structure

-   `routes/` --- HTTP endpoints and request handling
-   `services/` --- application and business logic
-   `db/` --- database queries and connection management
-   `models/` --- Pydantic models
-   `tests/` --- isolated API and backend tests

## 🔐 Features

-   Google & Discord OAuth
-   OAuth account linking
-   Session-based authentication
-   User and admin operations
-   Activity logging
-   SQLite foreign-key enforcement
-   Isolated test databases

## 🚀 Running

Install the project dependencies, configure the required credentials in
`.env`, then start the FastAPI application with Uvicorn.