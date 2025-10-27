# Use an official Python runtime as a parent image
FROM python:3.12.4-slim


# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install argcomplete and activate global completion
RUN pip install argcomplete

# Copy the rest of the working directory contents into the container at /app
COPY . .

# Register the script for auto-completion
RUN echo 'eval "$(register-python-argcomplete structkit)"' >> /etc/bash.bashrc

# Run your script when the container launches
ENTRYPOINT ["python", "structkit/main.py"]
