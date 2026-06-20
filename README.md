🌍 Languages: [🇬🇧 English](README.md) | [🇷🇺 Русский](README.ru.md)

# EduPlatform
![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white) [![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](#) ![CSS](https://img.shields.io/badge/CSS-1572B6?style=for-the-badge&logo=css3&logoColor=white) ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white) ![Celery](https://img.shields.io/badge/Celery-37814A?style=for-the-badge&logo=celery&logoColor=white) ![RabbitMQ](https://img.shields.io/badge/RabbitMQ-FF6600?style=for-the-badge&logo=rabbitmq&logoColor=white) ![Redis](https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white) ![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white) ![Nginx](https://img.shields.io/badge/Nginx-009639?style=for-the-badge&logo=nginx&logoColor=white)

## Preview
![demo gif](assets/demo.gif)
---
An online educational platform that allows instructors to create courses, lessons, and interactive assignments. Instructors have access to analytics data about course completion. Students can enroll in courses, track their progress, and complete assignments.

## Features

**For students:**:
- Search and filter the catalog by category and name
- Enroll in courses and track progress
- Theoretical tasks, multiple-choice tasks, text input tasks with correct answers, and programming tasks

**For instructors:**
- Full management of courses — creating and updating courses, lessons, and assignments using the built-in TinyMCE rich text editor
- Analytics dashboard for each course: enrollment data, completion statistics, and most frequently failed tasks
- Instructor panel with all user-created courses

**System:**
- Role-based access system (student, instructor)
- Asynchronous code execution using Celery and an isolated FastAPI microservice
- Redis caching
- Django admin customized with Jazzmin
- Deployment using Docker Compose + Nginx

## Tech Stack
| Layer | Technology |
|---|---|
| Backend | Django 5, Gunicorn |
| Frontend | Django Templates, HTMX, Chart.js, CodeMirror 5 |
| Database | PostgreSQL 14 |
| Cache | Redis 7 |
| Task queue | Celery + RabbitMQ |
| Code execution | FastAPI microservice (Python 3.11-slim) |
| Web server | Nginx |
| Admin | Jazzmin + TinyMCE |
| Containerisation | Docker, Docker Compose |

## Project Structure

```
education_system/
├── apps/
│   ├── users/          # auth, profiles, roles, signals
│   ├── courses/        # courses, modules, enrollment, progress
│   ├── lessons/        # lessons, steps (theory/choice/text/code)
│   ├── submissions/    # submissions, results, celery tasks
│   └── core/           # cache keys, shared utilities
├── config/             # settings, urls, celery, wsgi
├── infra/
│   ├── docker/         # Dockerfile (main app)
│   ├── executor/       # FastAPI code execution microservice
│   └── nginx/          # nginx.conf
├── static/             # css, fonts, htmx
├── templates/          # all Django templates
├── media/              # user uploads 
└── docker-compose.yml
```

## Quick Start

**Requirements:** Docker, Docker Compose

```bash
# 1. clone
git clone https://github.com/yourusername/education_system.git
cd education_system

# 2. environment
cp env.example .env

# 3. start
docker-compose up --build

# 4. seed data (optional)
docker-compose exec web python manage.py seed_submissions

# 5. create admin user
docker-compose exec web python manage.py createsuperuser

# 6. open
http://localhost        # main app via Nginx
http://localhost/admin/ # admin panel
```

## Environment Variables

```dotenv
# Django
ENVIRONMENT=production
DEBUG=False
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1

# PostgreSQL
POSTGRES_HOST=db
POSTGRES_DB=eduplatform
POSTGRES_USER=dbuser
POSTGRES_PASSWORD=password

# Redis
REDIS_PASSWORD=redispassword
REDIS_URL=redis://:redispassword@redis:6379/0

# RabbitMQ
RABBITMQ_USER=guest
RABBITMQ_PASSWORD=guest
RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672//

# Executor microservice
EXECUTOR_URL=http://executor:8080
```

## Seed Commands

The commands are idempotent
```bash
python manage.py seed_roles        # student, instructor, moderator roles
python manage.py seed_categories   # programming, math, science...
python manage.py seed_users        # user accounts
python manage.py seed_courses      # courses with modules
python manage.py seed_lessons      # lessons for courses
python manage.py seed_lessons      # submissions for lessons
```

## Running Tests

```bash
# all tests
docker-compose exec web python manage.py test

# specific app
docker-compose exec web python manage.py test apps.courses
docker-compose exec web python manage.py test apps.users

# with coverage
docker-compose exec web coverage run manage.py test
docker-compose exec web coverage html
```

## Known Limitations / Future Work

- [ ] No OAuth (Google/GitHub login)
- [ ] No email verification or password reset
- [ ] Code execution sandbox uses subprocess inside Docker
- [ ] Only Python is supported in programming tasks
