FROM python:3.10-slim

# Create the folder structure that the Paths.py function expects
WORKDIR /app/full-project/backend

# Copy requirements first
COPY requirements.txt /app/full-project/backend/requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Now copy the backend code into the correct path
COPY . /app/full-project/backend/

# Expose FastAPI port
EXPOSE 8000

# Run the app (note the full path)
CMD ["uvicorn", "app.app:app", "--host", "0.0.0.0", "--port", "8000"]
