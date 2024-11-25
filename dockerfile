# Mentioning amd64 specifically cuz on the mac it defaulted to arm64 and failed in the Azure container
FROM --platform=linux/amd64 python:3.11-slim-bookworm

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# Install playwright chromium
RUN playwright install chromium

# otherwise we get the error "host system is missing dependencies to run browsers"
RUN playwright install-deps

# Run main.py when the container launches
CMD ["python3", "main.py"]

# docker build -t customs-er-az-doc-intelli .