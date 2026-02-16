FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libgomp1

RUN pip install poetry==2.3.1
RUN poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root --without dev

COPY . .

EXPOSE 8000

CMD ["uvicorn", "src.main:fastapi_app", "--host", "0.0.0.0", "--port", "8000"]