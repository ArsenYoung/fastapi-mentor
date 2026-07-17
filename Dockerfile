FROM python:3.12.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

ARG POETRY_VERSION=2.4.0
RUN pip install --no-cache-dir "poetry==$POETRY_VERSION"

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false \
    && poetry install --without dev --no-interaction --no-ansi

EXPOSE 8000
COPY . .

CMD ["uvicorn", "src.application:get_app", "--host", "0.0.0.0", "--port", "8000", "--factory"]
