# Social Media API with FastAPI

This project is a REST API for a social media application built with **FastAPI**, designed to handle user management, posts, and authentication. It follows a clean and modern architecture, including testing and automatic documentation.

## Features

- User registration and authentication (JWT).
- Full CRUD for posts.
- Follower management.
- Validation and serialization with Pydantic.
- Relational database support (SQLite or configurable).
- Middleware for error handling and logging.

## Technologies

- **FastAPI**
- **SQLAlchemy**
- **Alembic** (migrations)
- **JWT** (authentication)
- **Pydantic**
- **Pytest** (testing)

## Installation

1. Clone the repository:

```bash
git clone https://github.com/rubjmnz93/social-media-fastapi.git
cd social-media-fastapi
```

2. Install dependencies (virtualenv recommended):

```bash
pip install -r requirements.txt
```

3. Initialize the database:

```bash
alembic upgrade head
```

4. Run the server:

```bash
uvicorn app.main:app --reload
```

Access the automatic docs at: [http://localhost:8000/docs](http://localhost:8000/docs)

## Running Tests

```bash
pytest
```

## Project Structure

```
├── socialmediaapi
│   ├── libs
│   ├── models
│   ├── ruters
│   ├── tests
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── logging_conf.py
│   ├── security.py
│   ├── tasks.py
│   └── utils.py
├── requirements.txt
├── requirements-dev.txt
└── README.md
```

## TODOs / Improvements

- Implement pagination for listings.
- Add more test coverage.
- Integrate CI/CD.


