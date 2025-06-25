FROM python:3.11-slim

WORKDIR /app

COPY rotation.py .

RUN pip install --no-cache-dir flask ibm-cloud-sdk-core ibm-secrets-manager-sdk ibm-code-engine-sdk

EXPOSE 8080

ENV PYTHONUNBUFFERED=1

CMD ["python", "rotation.py"]