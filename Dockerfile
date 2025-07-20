# Use Python 3.10.9 base image
FROM python:3.10.9

# Set working directory
WORKDIR /app

# Copy requirements.txt and install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy the rest of your code
COPY . .

# Run your app (change this if needed)
CMD ["python", "app.py"]
