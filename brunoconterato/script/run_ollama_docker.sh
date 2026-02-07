#!/bin/bash

# 1. Load variables from .env file
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
else
    echo "Error: .env file not found!"
    exit 1
fi

# Set defaults if .env is missing values
MODEL=${OLLAMA_MODEL:-llama3}
PORT=${OLLAMA_PORT:-11434}
CONTAINER_NAME="ollama-local"

echo "--- Configuration ---"
echo "Model: $MODEL"
echo "Port:  $PORT"
echo "---------------------"

# 2. Check if container is already running and remove it
#    (This ensures port changes in .env take effect)
if [ "$(docker ps -aq -f name=$CONTAINER_NAME)" ]; then
    echo "Stopping and removing old container..."
    docker rm -f $CONTAINER_NAME > /dev/null
fi

# 3. Start the Docker Container
#    -d: Detached mode
#    -v ollama_data: Persist models so you don't download them every time
#    --gpus all: Uncomment if you have an NVIDIA GPU
echo "Starting Docker container..."

docker run -d \
  --name $CONTAINER_NAME \
  -p $PORT:11434 \
  -v ollama_data:/root/.ollama \
  --restart always \
  ollama/ollama

# Optional: Add '--gpus all' above line 38 if you have Nvidia drivers installed

# 4. Wait for the server to initialize
echo "Waiting for Ollama API to start..."
sleep 3

# 5. Pull the model
#    We use 'docker exec' to run the pull command INSIDE the container.
#    If the model is already downloaded, Ollama will verify checksums and skip quickly.
echo "Checking/Pulling model: $MODEL..."
docker exec -it $CONTAINER_NAME ollama pull $MODEL

echo "------------------------------------------------"
echo "✅ Success! Ollama is running."
echo "🔗 API Available at: http://localhost:$PORT"
echo "🧠 Model loaded: $MODEL"
echo "------------------------------------------------"