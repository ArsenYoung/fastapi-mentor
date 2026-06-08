FROM python:3.12

WORKDIR /app

RUN pip install poetry

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false
RUN poetry install --without dev

COPY . .

CMD ["uvicorn", "src.application:get_app", "--host", "0.0.0.0", "--port", "8000", "--factory"]
