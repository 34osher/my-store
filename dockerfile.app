FROM python:3.8-slim

WORKDIR /usr/src/app

# Copy the current directory contents into the container
COPY . .



# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 5000 available outside this container
EXPOSE 8000

# Define environment variable
ENV FLASK_ENV dev

# Run app.py when the container launches
CMD ["python", "app.py"]
