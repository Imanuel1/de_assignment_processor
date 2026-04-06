FROM python:3.11.9-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=True
COPY apps/api/requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

COPY apps/api /app/

RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser
RUN chown -R appuser:appgroup /app

USER appuser

EXPOSE 8080

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port 8080"]