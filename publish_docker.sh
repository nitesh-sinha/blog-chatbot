#!/bin/bash
# Script to build and publish the Docker image to Docker Hub

# Variables
IMAGE_NAME="blog-chatbot"
DOCKER_HUB_USERNAME=""
VERSION="1.0.0"

# Check if Docker Hub username is provided
if [ -z "$1" ]; then
  echo "Usage: $0 <docker_hub_username>"
  echo "Example: $0 yourusername"
  exit 1
else
  DOCKER_HUB_USERNAME="$1"
fi

# Full image name
FULL_IMAGE_NAME="$DOCKER_HUB_USERNAME/$IMAGE_NAME:$VERSION"
LATEST_IMAGE_NAME="$DOCKER_HUB_USERNAME/$IMAGE_NAME:latest"

echo "Building Docker image: $FULL_IMAGE_NAME"
docker build -t "$FULL_IMAGE_NAME" .
docker tag "$FULL_IMAGE_NAME" "$LATEST_IMAGE_NAME"

echo "Logging in to Docker Hub..."
docker login

echo "Pushing image to Docker Hub..."
docker push "$FULL_IMAGE_NAME"
docker push "$LATEST_IMAGE_NAME"

echo "Image successfully published to Docker Hub as $FULL_IMAGE_NAME and $LATEST_IMAGE_NAME" 