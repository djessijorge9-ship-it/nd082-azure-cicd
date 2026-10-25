FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt
COPY app.py startup.txt ./
COPY Housing_price_model/LinearRegression.joblib ./Housing_price_model/
RUN useradd --create-home appuser
USER appuser
EXPOSE 8000
CMD ["gunicorn", "--bind=0.0.0.0:8000", "--workers=2", "--timeout=120", "--access-logfile=-", "--error-logfile=-", "app:app"]
