# AviatorBot

A Django-based backend for predicting crash game multipliers. It integrates machine learning models (TensorFlow/Keras) with a Telegram bot and WebSocket connections to provide real-time predictions to customers.

> **IMPORTANT DISCLAIMER - EDUCATIONAL PURPOSE ONLY**
>
> This project was created **exclusively for educational and learning purposes**. It is intended to demonstrate programming concepts, software architecture, browser automation, and GUI development with Python.
>
> **This software is NOT intended for real gambling or commercial use.** The author does not encourage, promote, or endorse gambling in any form. The author assumes no responsibility for any use of this software, whether legal or illegal, and expressly disclaims any liability for financial losses, legal consequences, or any other damages arising from its use.
>
> **By using this software, you acknowledge that you do so at your own risk and accept full responsibility for any consequences.**


## Table of Contents

- [Overview](#overview)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
  - [Django Apps](#django-apps)
  - [ML Prediction Layer](#ml-prediction-layer)
  - [Telegram Bot](#telegram-bot)
  - [WebSocket Layer](#websocket-layer)
- [API Endpoints](#api-endpoints)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Environment Variables](#environment-variables)
  - [Development Setup](#development-setup)
- [Development Commands](#development-commands)
  - [Docker Commands](#docker-commands)
  - [Database Commands](#database-commands)
  - [ML Model Management](#ml-model-management)
  - [Celery Commands](#celery-commands)
  - [Testing](#testing)
- [Code Style](#code-style)
- [Deployment](#deployment)
- [Disclaimer](#disclaimer)

## Overview

AviatorBot is a prediction system designed for crash games. It uses machine learning models to predict multiplier outcomes and delivers these predictions to customers through multiple channels:

- **REST API**: Django REST Framework endpoints for authentication and data access
- **Telegram Bot**: Real-time notifications and interactions via Telegram
- **WebSocket**: Live data streaming for connected clients

The system categorizes multipliers into three categories for classification-based predictions, enabling customers to make informed decisions.

## Tech Stack

| Component | Technology |
|-----------|------------|
| **Backend Framework** | Django 4.2.5 |
| **API** | Django REST Framework 3.14.0 |
| **Database** | PostgreSQL 13 |
| **Cache/Message Broker** | Redis |
| **Task Queue** | Celery 5.2.7 |
| **Machine Learning** | TensorFlow 2.12.0, Keras 2.12.0, scikit-learn 1.2.2 |
| **Telegram Integration** | Telethon 1.27.0 |
| **Authentication** | django-rest-knox 4.2.0 |
| **Cloud Storage** | AWS S3 (boto3, django-storages) |
| **Monitoring** | Sentry SDK |
| **Containerization** | Docker, Docker Compose |

## Architecture

### Project Structure

```
aviatorbot/
├── aviator_bot_backend/     # Django configuration
│   ├── settings/
│   │   ├── common.py        # Base settings
│   │   ├── development.py   # Development settings
│   │   └── production.py    # Production settings
│   ├── celery.py            # Celery configuration
│   └── urls.py              # Main URL routing
│
├── apps/
│   ├── django_projects/     # Django apps (service pattern)
│   │   ├── auth/            # Authentication (Knox)
│   │   ├── core/            # Base entities
│   │   ├── customers/       # Customers and subscriptions
│   │   ├── bets/            # Betting system
│   │   └── predictions/     # ML models and bots
│   │
│   ├── prediction/          # ML engine
│   │   └── models/          # Keras implementations
│   │
│   ├── telegram_bot/        # Telegram bot
│   ├── sockets/             # WebSocket consumers
│   └── utils/               # Shared utilities
│
├── models_created/          # Trained models (.h5)
├── fixtures/                # Initial data
└── tests/                   # Tests
```

### Service Layer Pattern

Each Django app in `apps/django_projects/` follows a service-layer pattern:

```
app/
  ├── models.py      # Django ORM models
  ├── services.py    # Business logic
  ├── selectors.py   # Query logic (read operations)
  ├── views.py       # DRF API views
  └── urls.py        # URL routing
```

### Django Apps

| App | Description |
|-----|-------------|
| `core` | Base entities: CrashGame, HomeBet, HomeBetGame, Multiplier, Plan |
| `customers` | Customer, CustomerBalance, CustomerPlan, CustomerSession |
| `bets` | Betting logic with Telegram bot integration |
| `predictions` | ModelHomeBetGame, Bot, BotCondition (trading bot configuration) |
| `auth` | Knox token authentication |

### ML Prediction Layer

Located in `apps/prediction/`, this layer handles all machine learning operations:

- `models/base.py` - AbstractBaseModel defining train/predict/evaluate interface
- `models/sequential_model.py` - Sequential Keras model implementation
- `models/gru_model.py` - GRU-based Keras model implementation

**Key Features:**
- Models are stored in AWS S3 and downloaded to local `models_created/` directory
- Multipliers are categorized (Category 1, 2, 3) for classification predictions
- Configurable minimum probability threshold via `MIN_PROBABILITY_TO_EVALUATE_MODEL`

### Telegram Bot

Located in `apps/telegram_bot/`:

- Uses Telethon library for Telegram API integration
- Implements singleton pattern for bot instance management
- `channel_listeners.py` handles incoming channel messages
- Provides real-time prediction notifications to customers

### WebSocket Layer

Located in `apps/sockets/`:

- Built with Django Channels and Redis backend
- `BotConsumer` manages user connections and multiplier data streaming
- Tracks which user is authorized to save multipliers per home_bet
- Enables real-time bidirectional communication

## API Endpoints

### Authentication (`/api/auth/`)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `login/` | POST | Login with username/password |
| `verify/` | GET | Verify token |
| `logout/` | POST | Logout current session |
| `logoutall/` | POST | Logout all sessions |

### Customers (`/api/customers/`)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `me/` | GET | Get customer data and plan |
| `balance/` | GET | Get balance |
| `balance/` | PATCH | Update balance |
| `live/` | POST | Create/update session |

### Bets (`/api/bets/`)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | List bets |
| `/` | POST | Create bets |

### Core (`/api/`)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `health/` | GET | Health check |
| `home-bet/` | GET | Betting platforms |
| `home-bet/multiplier/` | POST | Save multipliers |

### Predictions (`/api/predictions/`)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `predict/` | POST | Get AI prediction |
| `models/` | GET | List ML models |
| `models/evaluate/` | GET | Evaluate model |
| `bots/` | GET | Bot configuration |
| `positions/` | GET | Position analysis |

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Python 3.11 (for local development without Docker)
- AWS account (for S3 model storage)
- Telegram API credentials

### Environment Variables

Create a `.envrc` file in the project root with the following variables:

```bash
# =============================================================================
# DJANGO SETTINGS
# =============================================================================
DJANGO_SETTINGS_MODULE=aviator_bot_backend.settings.development  # Django settings module path (development/production)
ALLOWED_HOSTS=*                      # Comma-separated list of allowed hosts (* for all in development)
ENVIRONMENT=dev                      # Environment identifier: dev, staging, or prod

# =============================================================================
# DATABASE CONFIGURATION
# =============================================================================
DATABASE_HOST=postgres               # PostgreSQL server hostname
DATABASE_NAME=aviatorbot             # Database name
DATABASE_USER=postgres               # Database user
DATABASE_PASSWORD=your_password      # Database password
DATABASE_PORT=5432                   # Database port

# =============================================================================
# TEST DATABASE CONFIGURATION
# =============================================================================
TEST_DATABASE_HOST=postgres          # Test database hostname
TEST_DATABASE_NAME=aviator_db_test   # Test database name
TEST_DATABASE_USER=postgres          # Test database user
TEST_DATABASE_PASSWORD=postgres      # Test database password
TEST_DATABASE_PORT=5432              # Test database port

# =============================================================================
# REDIS CONFIGURATION
# =============================================================================
REDIS_HOSTNAME=redis                 # Redis server hostname
REDIS_PORT=6379                      # Redis server port

# =============================================================================
# TELEGRAM CONFIGURATION
# =============================================================================
TELEGRAM_API_ID=your_api_id          # Telegram API ID from my.telegram.org
TELEGRAM_API_HASH=your_api_hash      # Telegram API hash from my.telegram.org
TELEGRAM_PHONE_NUMBER=your_phone     # Phone number associated with Telegram account
TELEGRAM_CHANNEL_ID=your_channel_id  # Telegram channel ID for listening to multiplier data
TELEGRAM_BOT_TOKEN=your_bot_token    # Telegram Bot token from @BotFather

# =============================================================================
# AWS CONFIGURATION
# =============================================================================
AWS_ACCESS_KEY_ID=your_access_key              # AWS IAM access key ID
AWS_SECRET_ACCESS_KEY=your_secret_key          # AWS IAM secret access key
AWS_STORAGE_BUCKET_NAME=your_bucket_name       # S3 bucket for general storage
S3_BUCKET_MODELS=bucket-models                 # S3 bucket for storing trained ML models

# =============================================================================
# ML MODEL CONFIGURATION
# =============================================================================
DEFAULT_SEQ_LEN=15                             # Default sequence length for model input
GENERATE_AUTOMATIC_MODEL_TYPES=sequential_lstm # Comma-separated model types to auto-generate (sequential_lstm, sequential)
EPOCHS_SEQUENTIAL_LSTM=1000                    # Training epochs for Sequential LSTM model
EPOCHS_SEQUENTIAL=1000                         # Training epochs for Sequential model

# =============================================================================
# MODEL EVALUATION & PREDICTION
# =============================================================================
MIN_PROBABILITY_TO_EVALUATE_MODEL=0.5          # Minimum probability threshold for model evaluation (0.0-1.0)
PERCENTAGE_ACCEPTABLE=0.7                      # Minimum acceptable accuracy percentage for model predictions
PERCENTAGE_MODEL_TO_INACTIVE=0.65              # Accuracy threshold below which a model is marked inactive
DIFF_MULTIPLIERS_TO_GENERATE_NEW_MODEL=50      # Number of new multipliers required to trigger new model generation
NUMBER_OF_MODELS_TO_PREDICT=1                  # Number of models to use for ensemble predictions
NUMBER_OF_MULTIPLIERS_TO_EVALUATE_MODEL=200    # Number of multipliers used to evaluate model performance

# =============================================================================
# MONITORING (OPTIONAL)
# =============================================================================
# SENTRY_URL=https://xxx@xxx.ingest.sentry.io/xxx  # Sentry DSN for error tracking (optional)
```

### Development Setup

1. Clone the repository:
   ```bash
   git clone git@github.com:bikerlfh/aviatorbot.git
   cd aviatorbot
   ```

2. Copy the environment template and configure:
   ```bash
   cp .envrc.example .envrc
   # Edit .envrc with your configuration
   ```

3. Build and start the Docker containers:
   ```bash
   make build
   make up
   ```

4. Run database migrations:
   ```bash
   make migrate
   ```

5. Create a superuser:
   ```bash
   make create-superuser
   ```

6. (Optional) Load fixtures:
   ```bash
   make load-fixtures
   ```

## Development Commands

### Docker Commands

| Command | Description |
|---------|-------------|
| `make build` | Build Docker containers |
| `make up` | Start all services |
| `make up-d` | Start all services in detached mode |
| `make down` | Stop services and remove orphans |
| `make shell` | Open Django shell_plus |
| `make run ARGS="command"` | Run a command in the worker container |

### Database Commands

| Command | Description |
|---------|-------------|
| `make makemigrations` | Create Django migrations |
| `make migrate` | Apply migrations |
| `make reset-db` | Reset the database (use with caution) |
| `make load-fixtures` | Load all fixtures |
| `make load-bot-fixtures` | Load bot-specific fixtures |
| `make clear-cache` | Invalidate all cache |

### ML Model Management

| Command | Description |
|---------|-------------|
| `make create-model home_bet_game_id=1 model_type=sequential seq_len=10` | Create a new ML model |
| `make generate-category-result` | Generate category results for all models |
| `make download-models-from-s3` | Download trained models from S3 |
| `make export-multipliers-to-csv is_production_data=true` | Export multipliers to CSV |

**Model Types:**
- `sequential` - Sequential neural network model
- `gru` - GRU (Gated Recurrent Unit) model

### Celery Commands

| Command | Description |
|---------|-------------|
| `make celery` | Run Celery worker |
| `make beat` | Run Celery beat scheduler |
| `make exec-celery` | Execute Celery in running container |

### Testing

Run the test suite:
```bash
make run-tests
```

Run specific tests:
```bash
make run-tests ARGS="-k test_name"
```

## Code Style

This project enforces code style through pre-commit hooks:

- **Black**: Code formatter with line-length=79, excludes migrations
- **isort**: Import sorting
- **flake8**: Linting

Run Black manually:
```bash
make black
```

Pre-commit hooks prevent direct commits to `main`, `master`, and `dev` branches.

## Deployment

The application deploys to AWS Elastic Beanstalk (Virginia region) with Python 3.11.

### AWS Services Used

| Service | Purpose |
|---------|---------|
| Elastic Beanstalk | Application hosting |
| RDS PostgreSQL | Database |
| ElastiCache Redis | Caching and message broker |
| S3 | ML model storage |

### Deployment Commands

```bash
# Initialize Elastic Beanstalk
eb init -v

# Create a new environment
eb create -i t3a.small -v

# Deploy to existing environment
eb deploy -v
```

### Process Configuration

The `Procfile` defines the following processes:

```
web: gunicorn --bind 127.0.0.1:8000 --workers=1 --threads=15 aviator_bot_backend.wsgi:application
celery-worker: celery -A aviator_bot_backend.celery worker -l info
celery-beat: celery -A aviator_bot_backend.celery beat -l info
```

## Disclaimer

**This project is for educational and demonstration purposes only.**

- This software is **NOT** intended for real gambling or commercial use
- The predictions generated by the ML models do not guarantee any outcomes
- Gambling involves financial risk and can lead to addiction
- The authors are not responsible for any financial losses or legal consequences arising from the use of this software
- Users must comply with all applicable laws and regulations in their jurisdiction regarding online gambling

By using this software, you acknowledge that you understand these terms and assume full responsibility for your actions.
