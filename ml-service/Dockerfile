FROM python:3.11.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir numpy==2.4.3
RUN pip install --no-cache-dir faiss-cpu
RUN pip install --no-cache-dir torch==2.2.0+cpu --extra-index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Step 2 — Create `ml-service/requirements.txt`:**
```
fastapi==0.115.0
uvicorn==0.30.0
pandas==2.3.0
scikit-learn==1.6.1
xgboost==2.1.0
shap==0.51.0
sentence-transformers==5.3.0
groq==0.13.0
httpx==0.27.0
python-dotenv==1.0.0
pydantic==2.6.0
requests==2.32.5
keybert==0.9.0