FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml README.md /app/
COPY tuda /app/tuda

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir .

EXPOSE 8000

CMD ["uvicorn", "tuda.api:app", "--host", "0.0.0.0", "--port", "8000"]
