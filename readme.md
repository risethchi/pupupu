# TeamFinder (вариант 1)

**TeamFinder** — это платформа для поиска единомышленников для совместной работы над IT-проектами.  
Пользователи могут создавать проекты, приглашать участников, добавлять проекты в избранное и фильтровать участников по различным критериям.

### Используемые технологии

- **Python 3.10**
- **Django 5.2**
- **PostgreSQL 16**
- **Docker & Docker Compose**
- **Pillow** (генерация аватаров)

---

## Запуск в Docker (рекомендуется для ревью)

### 1. Подготовьте `.env`

Скопируйте пример и отредактируйте при необходимости:

```bash
cp .env_example .env
Минимально важное для варианта 1:

    TASK_VERSION=1

    POSTGRES_HOST=db

    POSTGRES_PORT=5432

Пример содержимого .env:

  DJANGO_SECRET_KEY=your-secret-key-here
  DJANGO_DEBUG=True

  POSTGRES_DB=team_finder
  POSTGRES_USER=team_finder
  POSTGRES_PASSWORD=team_finder
  POSTGRES_HOST=db
  POSTGRES_PORT=5432

  TASK_VERSION=1

2. Запустите проект

  docker compose up --build

После сборки откройте в браузере: http://localhost:8000/projects/list 

3. Остановка
  docker compose down

Данные Postgres сохраняются в Docker volume postgres_data и не теряются после перезапуска контейнеров.    

Проверка работоспособности (вариант 1)
Базовые сценарии

    Главная – /projects/list

        проекты отсортированы по дате (новые сверху)

        для авторизованного пользователя видна кнопка «Создать проект» и иконка «Добавить в избранное»

    Регистрация – /users/register/

    Вход – /users/login/

    Профиль пользователя – /users/<id>

        для владельца доступны кнопки «Редактировать профиль» и «Добавить проект»

    Редактирование профиля – /users/edit-profile

        валидация телефона (формат 8XXXXXXXXXX или +7XXXXXXXXXX)

        валидация GitHub-ссылки (должна вести на github.com)

    Список участников – /users/list

        доступны фильтры для авторизованных пользователей

    Страница проекта – /projects/<id>

        кнопка «Участвовать/Отказаться» – для авторизованных

        кнопка «Завершить проект» – только для владельца

    Избранное – /projects/favorites (доступно только авторизованным)

        добавление/удаление из избранного через сердечко на карточке проекта

Админка

Создать суперпользователя:

  docker compose exec web python manage.py createsuperuser

Админ-панель: http://localhost:8000/admin

Создание тестовых данных

После запуска проекта создайте несколько пользователей и проектов для проверки функционала.

Способ 1. Через веб-интерфейс

    Зарегистрируйте двух-трёх пользователей через /users/register/.

    Войдите под каждым и создайте по одному-двум проектам через кнопку «Создать проект».

    Добавьте проекты в избранное, участвуйте в чужих проектах.

Способ 2. Через Django shell

  docker compose exec web python manage.py shell

Затем выполните:

  from users.models import User
  from projects.models import Project

  # Создаём пользователей
  user1 = User.objects.create_user(
      email='alice@example.com',
      first_name='Алиса',
      last_name='Иванова',
      password='alice123'
  )
  user2 = User.objects.create_user(
      email='bob@example.com',
      first_name='Боб',
      last_name='Петров',
      password='bob123'
  )

  # Создаём проекты от имени user1
  project1 = Project.objects.create(
      name='Чат-бот для Telegram',
      description='Бот с интеграцией OpenAI',
      owner=user1,
      status=Project.Status.OPEN
  )
  project2 = Project.objects.create(
      name='Мобильное приложение для спорта',
      description='Трекер тренировок',
      owner=user1,
      status=Project.Status.OPEN
  )

  # Добавляем user2 в участники project1
  project1.participants.add(user2)

  # Добавляем project2 в избранное user2
  user2.favorites.add(project2)

Способ 3. Загрузка фикстур (если подготовлены)

  docker compose exec web python manage.py loaddata users/fixtures/users.json
  docker compose exec web python manage.py loaddata projects/fixtures/projects.json

Локальный запуск без Docker (опционально)
1. Виртуальное окружение

  python3 -m venv venv
  source venv/bin/activate        # Linux/Mac
  # или venv\Scripts\activate     # Windows

2. Установка зависимостей

  pip install -r requirements.txt

3. Настройка .env

Скопируйте .env_example в .env и отредактируйте:

  cp .env_example .env

Убедитесь, что POSTGRES_HOST=localhost (если PostgreSQL запущен отдельно).
4. Запуск PostgreSQL (локально или через Docker)

Если используете Docker только для БД:

  docker run --name teamfinder-db -e POSTGRES_PASSWORD=teamfinder -e POSTGRES_USER=teamfinder -e POSTGRES_DB=teamfinder -p 5432:5432 -d postgres:16

5. Миграции и запуск

  python manage.py migrate
  python manage.py runserver

Проект будет доступен по адресу http://localhost:8000
Дополнительная информация

    При регистрации автоматически генерируется аватар с первой буквой имени на случайном цветном фоне.

    При смене аватара старый файл удаляется (через сигнал pre_save).

    Телефоны нормализуются к формату +7XXXXXXXXXX и проверяются на уникальность независимо от исходного формата (8 или +7).

    GitHub-ссылки валидируются: домен должен оканчиваться на github.com.

