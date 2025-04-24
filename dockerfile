# Use official Python image
FROM python:3.13-slim

# Set the working directory inside the container
WORKDIR /app

# Copy project files into the container
COPY . .

# Install dependencies
RUN pip install -r requirements.txt

# Expose the port your app will run on
EXPOSE 5000

# Command to run your web app (assuming you're using Flask)
CMD ["python", "hangman.py"]
