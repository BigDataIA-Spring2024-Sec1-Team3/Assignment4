# Use the official Python image from the Docker Hub
FROM python:3.9

# Set the working directory inside the container
WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*


# Copy the requirements.txt file into the container at /app
COPY requirements.txt /app/

# Install any dependencies in the requirements.txt
RUN pip install -r requirements.txt

# Copy the frontend code into the container at /app/user-interface
COPY user-interface /app/user-interface

# Make port 8501 available to the world outside this container
EXPOSE 8501

# Define the command to run your app using Streamlit
CMD ["streamlit", "run", "user-interface/app.py"]
