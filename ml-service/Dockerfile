FROM python:3.11.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y build-essential gcc && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir numpy==2.4.3
RUN pip install --no-cache-dir faiss-cpu
RUN pip install --no-cache-dir torch==2.2.0+cpu --extra-index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]