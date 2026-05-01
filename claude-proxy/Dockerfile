FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir fastapi uvicorn[standard] pydantic

COPY proxy.py .

EXPOSE 5000

CMD ["uvicorn", "proxy:app", "--host", "0.0.0.0", "--port", "5000"]
