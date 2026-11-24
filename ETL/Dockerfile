FROM python:3.12-slim

WORKDIR /app

# Install the Python libraries first (Docker caches this step, so rebuilds are faster)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the 8 CSVs into /app/data, the same folder CSV_FOLDER points to in your script
COPY *.csv /app/data/

# Copy the ETL script
COPY etl_pipeline.py .

# Run the script when the container starts
CMD ["python", "etl_pipeline.py"]