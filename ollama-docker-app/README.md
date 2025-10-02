# Ollama Docker App

## Overview
This project provides a Dockerized environment to run the Ollama model using the `qwen3:1.7b` version. It includes all necessary configurations and scripts to set up and execute the model seamlessly.

## Project Structure
```
ollama-docker-app
├── Dockerfile
├── docker-compose.yml
├── scripts
│   └── run-model.sh
└── README.md
```

## Prerequisites
- Docker installed on your machine.
- Docker Compose installed on your machine.

## Getting Started

### Building the Docker Image
To build the Docker image for the application, navigate to the project directory and run the following command:

```bash
docker-compose build
```

### Running the Docker Container
After building the image, you can run the container using:

```bash
docker-compose up
```

This command will start the Ollama service and execute the model.

### Running the Model
The model can be executed by running the script located in the `scripts` directory:

```bash
bash scripts/run-model.sh
```

This script will install Ollama and run the specified model.

## Additional Information
- Ensure that you have sufficient resources allocated to Docker to run the model effectively.
- For more information on the Ollama model and its capabilities, refer to the official documentation at [Ollama](https://ollama.com).