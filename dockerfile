# Use official Python image
FROM python:3.13-slim

# Set the working directory inside the container
WORKDIR /app

# Copy project files into the container
COPY . .

# Install dependencies
RUN pip install -r requirements.txt

# Command to run the game
CMD ["python", "hangman.py"]
