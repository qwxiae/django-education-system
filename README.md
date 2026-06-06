# EduPlatform
![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white) ![DRF](https://img.shields.io/badge/DRF-ff1709?style=for-the-badge&logo=django&logoColor=white) ![HTMX](https://img.shields.io/badge/HTMX-36C?style=for-the-badge&logo=htmx&logoColor=white) ![CSS](https://img.shields.io/badge/CSS-1572B6?style=for-the-badge&logo=css3&logoColor=white) ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white) ![Celery](https://img.shields.io/badge/Celery-37814A?style=for-the-badge&logo=celery&logoColor=white) ![RabbitMQ](https://img.shields.io/badge/RabbitMQ-FF6600?style=for-the-badge&logo=rabbitmq&logoColor=white) ![Redis](https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white) ![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white) ![Nginx](https://img.shields.io/badge/Nginx-009639?style=for-the-badge&logo=nginx&logoColor=white)
---
Онлайн образовательная платформа, которая позволяет инструктору создавать курсы, уроки и интерактивные задания. Инструкторам доступны аналитические данные о прохождении их курса. Ученики могут записывться на курсы, отслеживать прогресс и проходить задания.

## Preview
![demo gif](assets/demo.gif)

## Features

**For students:**
- Поиск и фильтрация каталога по категории и названию
- Запись на курс и отслеживание прогресса
- Теоретические задания, задания на выбор и ввод правильного ответа, задания по программированию 

**For instructors:**
- Полное управление своими курсами – создание и обновление курса, уроков, заданий со встроенным редактором текстовых данных TinyMCE 
- Аналитическая панель для каждого курса: данные о записи, прохождении и самые неудачные задания
- Учительская панель со всеми курсами пользователя

**System:**
- Ролевая система доступа (student, instructor)
- Асинхронное выполнение кода вместе с celery и изолированным FastAPI микросервисом
- Redis кэширование
- Django админ стилизирован с помощью Jazzmin
- Разворотка с помощью Docker Compose + Nginx

---

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

---

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

---

## Seed Commands

Каждая команда идемпотента, может запускаться несколько раз.

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
- [ ] Only Python supported in programming steps

