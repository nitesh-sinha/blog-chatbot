# Blog Chatbot

A generic AI chatbot/assistant for websites and blogs that can crawl your content and answer questions based on that content.

## Features

- Crawls your website/blog to gather content
- Creates vector embeddings for semantic search
- Interactive chat interface to query blog content
- Maintains conversation history using Redis
- Containerized with Docker for easy deployment
- Customizable for any website or blog

## Quick Start with Docker

### Prerequisites

- Docker and Docker Compose installed
- OpenAI API key (for embeddings and chat completion)
- Ollama installed and running on your host machine

### Setup

1. Clone this repository:
   ```bash
   git clone https://github.com/nitesh-sinha/blog-chatbot.git
   cd blog-chatbot
   ```

2. Create a `.env` file based on the example:
   ```bash
   cp .env.example .env
   ```

3. Edit the `.env` file and add your API keys and blog information:
   ```
   BLOG_NAME=Your Blog Name
   BLOG_OWNER=Your Name
   BLOG_URL=https://yourblog.com/
   BLOG_CONTACT=your-email@example.com
   ```

4. Download an AI model and run locally using Ollama. This code was tested using `mistral` model.

   ```bash
   ollama run mistral:latest
   ```

5. Start the application with Docker Compose:
   ```bash
   docker-compose run chatbot
   ```

   To update embeddings when starting (e.g., if running this for first time or blog content has changed since prior run):
   ```bash
   UPDATE_EMBEDDINGS=true docker-compose run chatbot
   ```

6. Interact with the chatbot through the stdin of the docker chatbot container.

## Running Without Docker

If you prefer not to use Docker, you can run the application directly:

1. Install Redis on your system
2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   cp sample-setup.env setup.env
   # Edit setup.env with your API keys
   source setup.env
   ```

4. Download an AI model and run locally using Ollama. This code was tested using `mistral` model.

   ```bash
   ollama run mistral:latest
   ```

5. Run the application:
   ```bash
   python main.py --blog-name "Your Blog Name" --blog-owner "Your Name" \
                 --blog-url "https://yourblog.com/" --blog-contact "your-email@example.com" \
                 --update-embeddings  # Optional: Add this flag to update embeddings
   ```

## Customization

You can customize the chatbot by modifying the source files:

- `bot/Bot.py`: Customize the bot's behavior and responses
- `crawler/crawl_blog.py`: Customize the crawling behavior
- `vector_db/chroma_db.py`: Customize the vector database configuration

## Publishing to Docker Hub

To publish your own version of the chatbot to Docker Hub:

1. Build the Docker image:
   ```bash
   docker build -t <yourusername>/blog-chatbot:latest .
   ```

2. Log in to Docker Hub:
   ```bash
   docker login
   ```

3. Push the image to Docker Hub:
   ```bash
   docker push <yourusername>/blog-chatbot:latest
   ```

Note: The chatbot image(without Redis) is published as `niteshks/blog-chatbot:latest` on Dockerhub.

## Redis CLI to view chat history

```bash
# To view all the keys
redis-cli KEYS "*"

# Check message type stored against a specific key
redis-cli Type message_store:SESSION_60035

# Check message content against a specific key
redis-cli LRANGE message_store:SESSION_60035 0 -1
```

## License

[MIT License](LICENSE)