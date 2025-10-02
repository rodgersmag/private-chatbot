FROM ubuntu:20.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive

# Install necessary packages
RUN apt-get update && \
    apt-get install -y curl && \
    apt-get clean

# Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# Set the working directory
WORKDIR /app

# Copy the run-model.sh script
COPY scripts/run-model.sh /app/run-model.sh

# Make the script executable
RUN chmod +x /app/run-model.sh

# Command to run the script
CMD ["/app/run-model.sh"]