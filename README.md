# Створення Django 6.0 додатку та розгортання в Azure App Services

---

## Передумови

Перед початком переконайтеся, що маєте:
- Обліковий запис **GitHub**
- Обліковий запис **Microsoft Azure**
- Базові знання Python та Django

---

## Етап 1: Налаштування GitHub Codespace

### Крок 1.1: Створення нового репозиторію

1. Відкрийте [github.com](https://github.com)
2. Натисніть **"New repository"**
3. Заповніть параметри:

```
Repository name: my-django-azure-app
Description: Django 6.0 app deployed to Azure
Visibility: Public або Private
✅ Add a README file
✅ Add .gitignore → Python
```

4. Натисніть **"Create repository"**

---

### Крок 1.2: Запуск GitHub Codespace

1. У репозиторії натисніть **"Code"**
2. Виберіть вкладку **"Codespaces"**
3. Натисніть **"Create codespace on main"**
4. Зачекайте поки середовище завантажиться (1-2 хвилини)

---

### Крок 1.3: Налаштування середовища у Codespace

```bash
# Перевірте версію Python
python --version
# Має бути Python 3.11+

# Оновіть pip
pip install --upgrade pip

# Створіть віртуальне середовище
python -m venv venv

# Активуйте віртуальне середовище
source venv/bin/activate

# Переконайтеся що venv активовано
which python
# Має показати: /workspaces/my-django-azure-app/venv/bin/python
```

---

## Етап 2: Встановлення Django 6.0 та створення проєкту

### Крок 2.1: Встановлення залежностей

```bash
# Встановлення Django 6.0
pip install django==6.0

# Встановлення додаткових пакетів для Azure
pip install gunicorn
pip install whitenoise
pip install python-dotenv
pip install psycopg2-binary

# Перевірка встановлення
django-admin --version
# Має показати: 6.0
```

---

### Крок 2.2: Створення Django проєкту

```bash
# Створення проєкту (з підкресленнями, без дефісів!)
django-admin startproject myapp .

# Перевірте структуру проєкту
ls -la
```

Структура має виглядати так:
```
my-django-azure-app/
├── myapp/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── venv/
├── manage.py
├── .gitignore
└── README.md
```

---

### Крок 2.3: Створення першого додатку

```bash
# Створення додатку
python manage.py startapp core

# Перевірте структуру
ls -la core/
```

---

## Етап 3: Налаштування проєкту

### Крок 3.1: Створення файлу змінних середовища

```bash
# Створіть файл .env
touch .env
```

Додайте до `.env`:
```env
SECRET_KEY=your-super-secret-key-here-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,.azurewebsites.net
DATABASE_URL=sqlite:///db.sqlite3
```

Переконайтеся, що `.env` є у `.gitignore`:
```bash
echo ".env" >> .gitignore
echo "venv/" >> .gitignore
echo "__pycache__/" >> .gitignore
echo "*.pyc" >> .gitignore
echo "db.sqlite3" >> .gitignore
```

---

### Крок 3.2: Налаштування settings.py

Відкрийте `myapp/settings.py` та замініть вміст:

```python
import os
from pathlib import Path
from dotenv import load_dotenv

# Завантаження змінних середовища
load_dotenv()

# Базова директорія
BASE_DIR = Path(__file__).resolve().parent.parent

# Безпека
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-dev-key-change-in-production')
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost').split(',')

# Додатки
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',  # Наш додаток
]

# Middleware з WhiteNoise для статичних файлів
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # WhiteNoise
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'myapp.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'myapp.wsgi.application'

# База даних
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Валідація паролів
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Інтернаціоналізація
LANGUAGE_CODE = 'uk'
TIME_ZONE = 'Europe/Kyiv'
USE_I18N = True
USE_TZ = True

# Статичні файли
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Медіафайли
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Тип первинного ключа за замовчуванням
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
```

---

### Крок 3.3: Створення базового View та URL

Відкрийте `core/views.py`:
```python
from django.shortcuts import render
from django.http import HttpResponse


def home(request):
    """Головна сторінка"""
    context = {
        'title': 'Django 6.0 на Azure',
        'message': 'Вітаємо! Ваш Django додаток працює успішно!',
    }
    return render(request, 'core/home.html', context)


def health_check(request):
    """Перевірка стану для Azure"""
    return HttpResponse("OK", status=200)
```

Створіть `core/urls.py`:
```python
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('health/', views.health_check, name='health_check'),
]
```

Оновіть `myapp/urls.py`:
```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
]
```

---

### Крок 3.4: Створення шаблонів

```bash
# Створення директорій для шаблонів
mkdir -p templates/core
mkdir -p templates/base
```

Створіть `templates/base/base.html`:
```html
<!DOCTYPE html>
<html lang="uk">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Django Azure App{% endblock %}</title>
    {% load static %}
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 { color: #0078d4; }
        .badge {
            background: #0078d4;
            color: white;
            padding: 5px 10px;
            border-radius: 5px;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="container">
        {% block content %}{% endblock %}
    </div>
</body>
</html>
```

Створіть `templates/core/home.html`:
```html
{% extends 'base/base.html' %}

{% block title %}{{ title }}{% endblock %}

{% block content %}
    <h1>🚀 {{ title }}</h1>
    <p>{{ message }}</p>
    <p><span class="badge">Django 6.0</span> 
       <span class="badge">Azure App Service</span></p>
    <hr>
    <p>✅ Сервер працює коректно</p>
    <p>✅ Статичні файли налаштовано</p>
    <p>✅ Шаблони підключено</p>
{% endblock %}
```

---

### Крок 3.5: Перевірка локальної роботи

```bash
# Застосування міграцій
python manage.py migrate

# Збір статичних файлів
python manage.py collectstatic --noinput

# Запуск сервера
python manage.py runserver
```

Відкрийте браузер та перевірте `http://127.0.0.1:8000/`

---

## Етап 4: Підготовка до розгортання в Azure

### Крок 4.1: Створення requirements.txt

```bash
pip freeze > requirements.txt
```

Переконайтеся що `requirements.txt` містить:
```text
Django==6.0
gunicorn==21.2.0
whitenoise==6.6.0
python-dotenv==1.0.0
psycopg2-binary==2.9.9
```

---

### Крок 4.2: Створення файлу startup.sh

```bash
touch startup.sh
chmod +x startup.sh
```

Додайте до `startup.sh`:
```bash
#!/bin/bash

# Активація міграцій
python manage.py migrate --noinput

# Збір статичних файлів
python manage.py collectstatic --noinput

# Запуск Gunicorn
gunicorn myapp.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --timeout 120 \
    --access-logfile '-' \
    --error-logfile '-'
```

---

### Крок 4.3: Створення .azure/config (необов'язково)

```bash
mkdir -p .azure
touch .azure/config
```

---

### Крок 4.4: Фінальна структура проєкту

```
my-django-azure-app/
├── .azure/
├── core/
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── urls.py
│   └── views.py
├── myapp/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── templates/
│   ├── base/
│   │   └── base.html
│   └── core/
│       └── home.html
├── staticfiles/
├── venv/
├── .env
├── .gitignore
├── manage.py
├── requirements.txt
├── startup.sh
└── README.md
```

---

### Крок 4.5: Збереження змін у GitHub

```bash
# Додайте всі файли
git add .

# Перевірте що додається
git status

# Зробіть коміт
git commit -m "Initial Django 6.0 project setup"

# Відправте на GitHub
git push origin main
```

---

## Етап 5: Розгортання в Azure App Services

### Крок 5.1: Встановлення Azure CLI у Codespace

```bash
# Встановлення Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Перевірка встановлення
az --version

# Авторизація в Azure
az login --use-device-code
```

---

### Крок 5.2: Створення ресурсів Azure

```bash
# Змінні для зручності
RESOURCE_GROUP="my-django-rg"
LOCATION="eastus"
APP_NAME="my-django-app-$(date +%s)"  # Унікальна назва
APP_PLAN="my-django-plan"

# Створення групи ресурсів
az group create \
    --name $RESOURCE_GROUP \
    --location $LOCATION

# Створення плану App Service (безкоштовний рівень F1)
az appservice plan create \
    --name $APP_PLAN \
    --resource-group $RESOURCE_GROUP \
    --sku F1 \
    --is-linux

# Створення Web App
az webapp create \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --plan $APP_PLAN \
    --runtime "PYTHON:3.11"

# Збережіть назву додатку
echo "App name: $APP_NAME"
echo "URL: https://$APP_NAME.azurewebsites.net"
```

---

### Крок 5.3: Налаштування змінних середовища в Azure

```bash
# Генерація нового SECRET_KEY
SECRET_KEY=$(python -c "
import secrets
import string
chars = string.ascii_letters + string.digits + '!@#$%^&*()'
print(''.join(secrets.choice(chars) for _ in range(50)))
")

# Встановлення змінних середовища в Azure
az webapp config appsettings set \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --settings \
        SECRET_KEY="$SECRET_KEY" \
        DEBUG="False" \
        ALLOWED_HOSTS="$APP_NAME.azurewebsites.net" \
        SCM_DO_BUILD_DURING_DEPLOYMENT="true" \
        WEBSITE_HTTPLOGGING_RETENTION_DAYS="3"
```

---

### Крок 5.4: Налаштування команди запуску

```bash
# Встановлення startup команди
az webapp config set \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --startup-file "startup.sh"
```

---

### Крок 5.5: Розгортання через GitHub Actions (Рекомендований спосіб)

#### Отримання профілю публікації:
```bash
az webapp deployment list-publishing-profiles \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --xml > publish_profile.xml

cat publish_profile.xml
```

#### Додавання секрету до GitHub:
1. Відкрийте ваш репозиторій на GitHub
2. Перейдіть до **Settings → Secrets and variables → Actions**
3. Натисніть **"New repository secret"**
4. Назва: `AZURE_WEBAPP_PUBLISH_PROFILE`
5. Значення: вміст файлу `publish_profile.xml`

#### Створення GitHub Actions workflow:
```bash
mkdir -p .github/workflows
touch .github/workflows/deploy.yml
```

Додайте до `.github/workflows/deploy.yml`:
```yaml
name: Deploy Django to Azure App Service

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    
    steps:
    # Крок 1: Отримання коду
    - name: Checkout code
      uses: actions/checkout@v4

    # Крок 2: Налаштування Python
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    # Крок 3: Встановлення залежностей
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt

    # Крок 4: Збір статичних файлів
    - name: Collect static files
      run: |
        python manage.py collectstatic --noinput
      env:
        SECRET_KEY: ${{ secrets.SECRET_KEY }}
        DEBUG: 'False'
        ALLOWED_HOSTS: 'localhost'

    # Крок 5: Розгортання в Azure
    - name: Deploy to Azure Web App
      uses: azure/webapps-deploy@v2
      with:
        app-name: ${{ secrets.AZURE_WEBAPP_NAME }}
        publish-profile: ${{ secrets.AZURE_WEBAPP_PUBLISH_PROFILE }}
        package: .
```

---

### Крок 5.6: Додавання секретів GitHub Actions

У GitHub репозиторії додайте ще два секрети:

| Назва секрету | Значення |
|---|---|
| `AZURE_WEBAPP_NAME` | Назва вашого додатку (значення $APP_NAME) |
| `AZURE_WEBAPP_PUBLISH_PROFILE` | Вміст publish_profile.xml |
| `SECRET_KEY` | Згенерований SECRET_KEY |

---

### Крок 5.7: Запуск розгортання

```bash
# Збережіть workflow файл та відправте на GitHub
git add .
git commit -m "Add Azure deployment configuration"
git push origin main
```

GitHub Actions автоматично розпочне розгортання.

---

## Етап 6: Перевірка розгортання

### Крок 6.1: Моніторинг GitHub Actions

1. Відкрийте репозиторій на GitHub
2. Перейдіть до вкладки **"Actions"**
3. Перегляньте прогрес розгортання
4. Переконайтеся що всі кроки завершились успішно ✅

---

### Крок 6.2: Перевірка роботи додатку

```bash
# Перевірка через curl
curl https://$APP_NAME.azurewebsites.net/health/

# Має повернути: OK
```

Відкрийте браузер та перейдіть до:
```
https://[your-app-name].azurewebsites.net
```

---

### Крок 6.3: Перегляд логів Azure

```bash
# Перегляд логів у реальному часі
az webapp log tail \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP
```

---

## Підсумкова схема розгортання

```
GitHub Codespace
      │
      │ git push
      ▼
GitHub Repository
      │
      │ GitHub Actions trigger
      ▼
GitHub Actions Runner
  ├── Встановлення Python
  ├── Встановлення залежностей
  ├── Збір статичних файлів
  └── Розгортання в Azure
            │
            ▼
    Azure App Service
    ├── Python 3.11
    ├── Django 6.0
    ├── Gunicorn
    └── WhiteNoise (статичні файли)
            │
            ▼
    https://your-app.azurewebsites.net
```

---

## Очищення ресурсів Azure

Після завершення роботи видаліть ресурси щоб уникнути зайвих витрат:

```bash
az group delete \
    --name $RESOURCE_GROUP \
    --yes \
    --no-wait
```

---

## Поширені помилки та їх вирішення

| Помилка | Причина | Вирішення |
|---|---|---|
| `ModuleNotFoundError` | Невірна назва модуля | Перевірте назви без дефісів |
| `DisallowedHost` | Хост не в ALLOWED_HOSTS | Додайте `.azurewebsites.net` |
| `Static files 404` | WhiteNoise не налаштовано | Перевірте MIDDLEWARE |
| `Application Error` | Помилка Gunicorn | Перегляньте логи Azure |
| `Migration errors` | Міграції не застосовані | Додайте migrate до startup.sh |
