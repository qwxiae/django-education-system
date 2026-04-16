# EduPlatform
![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white) ![DRF](https://img.shields.io/badge/DRF-ff1709?style=for-the-badge&logo=django&logoColor=white) ![HTMX](https://img.shields.io/badge/HTMX-36C?style=for-the-badge&logo=htmx&logoColor=white) ![CSS](https://img.shields.io/badge/CSS-1572B6?style=for-the-badge&logo=css3&logoColor=white) ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white) ![Celery](https://img.shields.io/badge/Celery-37814A?style=for-the-badge&logo=celery&logoColor=white) ![RabbitMQ](https://img.shields.io/badge/RabbitMQ-FF6600?style=for-the-badge&logo=rabbitmq&logoColor=white) ![Redis](https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white) ![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white) ![Nginx](https://img.shields.io/badge/Nginx-009639?style=for-the-badge&logo=nginx&logoColor=white)
---
Онлайн образовательная платформа, которая позволяет инструктору создавать курсы, уроки и интерактивные задания. Инструкторам доступны аналитические данные о прохождении их курса. Ученики могут записывться на курсы, отслеживать прогресс и прозодить задания.

## Preview
![demo gif](assets/demo.gif)
<!-- ![описание](assets/screenshot.png) -->

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Django 5, Django REST Framework |
| Frontend | HTMX, vanilla CSS |
| Database | PostgreSQL |
| Async | Celery + RabbitMQ |
| Cache | Redis |
| Editor | TinyMCE |
| Admin | Jazzmin |
| Deployment | Docker + Nginx |


## Features

- **Каталог курсов** — список всех курсов с фильтром по категории и поиском по названию курса
- **Система записи** — возможность записаться на курс / отписаться с курса с использованием HTMX
- **Система уроков** — пошаговая навигация по уроку с использованием HTMX partial updates
- **Типы шагов** — теоретический шаг (текстовый), выбор правильного ответа, ввод данных, задание по программированию
- **Отслеживание прогресса** — каждая запись на курс ослеживает прогресс пользователя
- **Пользовательские профили** — публичные профили с аватарками, созданными пользователем курсами и информацией о самом пользователе
- **Ролевая система** — роли student, instructor, moderator 

---

## Project Structure
```
education_system/
├── apps/
│   ├── users/          # auth, profiles, roles
│   ├── courses/        # courses, modules, enrollments
│   └── lessons/        # lessons, steps, step subtypes
├── config/             # settings, urls, wsgi
├── infra/              # nginx, docker configs
├── static/             # css, js, fonts
└── templates/          # base, includes, partials
```

---

## Local Setup

**Требования:** Python 3.12+, PostgreSQL, Redis, RabbitMQ

```bash
# clone
git clone https://github.com/yourusername/education_system.git
cd education_system

# virtual environment
python -m venv .venv
source .venv/bin/activate      
# windows: .venv\Scripts\activate

# dependencies
pip install -r requirements.txt

# environment variables
cp .env.example .env
# edit .env with your database, redis, rabbitmq credentials

# database
python manage.py migrate

# Optional: seed data
python manage.py seed_data

# static files
python manage.py collectstatic

# run
python manage.py runserver
```

---

## Seed Data

Команды *seed* идемпотентны: можно запускать несколько раз.   
В основном используются для тестирования приложения.

```bash
# student, instructor, moderator
python manage.py seed_roles       
# programming, math, cybersecurity
python manage.py seed_categories  
# test users
python manage.py seed_users       
# courses with modules
python manage.py seed_courses     
# lessons and steps for intro-to-python
python manage.py seed_lessons     
```

---

## Data Model

```
User ──< UserRole >── Role
User ──< Enrollment >── Course
Course ──< Module ──< Lesson ──< Step
                                  ├── TheoryStep      
                                  ├── ChoiceStep      
                                  ├── TextInputStep   
                                  └── ProgrammingStep
```

Ключевые решения:  
- Courses идентифицируются по по слагу: SEO-оптимизированны, стабильны
- Lessons идентифицируются по общедоступному идентификатору: 9-значное случайное число
- Steps используется для **конкретного наследования** — у каждого типа, наследующего Steps, своя таблица
- Прогресс сохраняется в Enrollment в виде количества пройденных уроков, вычисляемого в процентах.

---

## Running Tests

```bash
# all tests
python manage.py test

# specific app
python manage.py test apps.courses
python manage.py test apps.users

# with coverage
coverage run manage.py test
coverage html
open htmlcov/index.html
```

---

## Environment Variables

```env
SECRET_KEY=<your-secret-key-here>
DEBUG=True
DATABASE_URL=postgres://user:password@localhost:5432/eduplatform
REDIS_URL=redis://localhost:6379/0
RABBITMQ_URL=amqp://guest:guest@localhost:5672/
MEDIA_ROOT=media/
```

## Admin Panel

Доступ по адресу `/admin/` — оформление выполнено с иcпользованием Jazzmin.

Для доступа к панели администратора:
```bash
python manage.py createsuperuser
```

---

## Docker
```sh
docker compose up
```

Для установки языков программирования в Piston sandbox:
```sh
# install Python 3.10
curl -X POST http://localhost:2000/api/v2/packages \
  -H "Content-Type: application/json" \
  -d '{"language": "python", "version": "3.10.0"}'

# verify it installed
curl http://localhost:2000/api/v2/runtimes
```