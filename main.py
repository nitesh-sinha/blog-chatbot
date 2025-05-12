import time
import argparse
import os
from crawler.parse_webpage import WebPageParser
from crawler.crawl_blog import BlogCrawler
from dotenv import load_dotenv
from preprocessor.process_document import WebPageTextPreprocessor
from vector_db.chroma_db import ChromaDb
from bot.Bot import Bot
from blog import Blog
from langchain_community.chat_message_histories import RedisChatMessageHistory
from tqdm import tqdm
import random


def create_blog_text_embeddings(loc_tags, vector_db):
    for loc_tag in tqdm(loc_tags):
        # Add wait to fix OpenAI's Embedding API rate limits
        # TODO: Make it more sophisticated by sending more
        #  tokens per API call using tiktoken token counter
        #  and keeping it under the max token limit for the
        #  model(150,000 TPM for text-embedding-ada-002 model)
        # time.sleep(20)
        if loc_tag.text.endswith((".jpg", ".png", ".jpeg")):
            # TODO: Remove img links while parsing sitemap
            continue
        print(f"Now processing {loc_tag.text}")
        parser = WebPageParser(loc_tag.text)
        parsed_webpage = parser.parse()
        text_preprocessor = WebPageTextPreprocessor(parsed_webpage)
        doc_chunks = text_preprocessor.process()
        vector_db.store_webpage(doc_chunks)


def parse_arguments():
    parser = argparse.ArgumentParser(description='Blog chatbot application')
    parser.add_argument('--blog-name', type=str, help='Name of the blog', required=True)
    parser.add_argument('--blog-owner', type=str, help='Owner of the blog', required=True)
    parser.add_argument('--blog-url', type=str, help='URL of the blog', required=True)
    parser.add_argument('--blog-contact', type=str, help='Contact email for the blog', required=True)
    parser.add_argument('--redis-url', type=str, default="redis://localhost:6379/0", 
                        help='Redis URL for chat history storage')
    parser.add_argument('--update-embeddings', action='store_true', 
                        help='Update vector embeddings for the blog content')
    return parser.parse_args()


if __name__ == '__main__':
    # Load environment variables
    env_file = "setup.env"
    if os.path.exists(env_file):
        load_dotenv(env_file)
    else:
        print(f"Warning: {env_file} not found. Make sure environment variables are set.")

    # Parse command-line arguments
    args = parse_arguments()
    
    # Generate session ID for user
    session_id = random.randint(10000, 99999)
    print(f"User session id: {session_id}")
    
    # Set up Redis connection
    redis_url = args.redis_url
    user_session_id = f"SESSION_{session_id}"
    
    # Create blog instance with parameters from command-line
    blog = Blog(
        blog_name=args.blog_name,
        blog_owner=args.blog_owner,
        blog_url=args.blog_url,
        blog_contact=args.blog_contact
    )
    
    # Crawl the blog for content
    crawler = BlogCrawler(blog.blog_url)
    loc_tags = crawler.crawl()
    
    # Create or update vector embeddings if requested
    if args.update_embeddings:
        print("Updating vector embeddings for blog content...")
        vector_db = ChromaDb()
        create_blog_text_embeddings(loc_tags, vector_db)
    
    # Initialize the bot
    ai_bot = Bot(blog_name=blog.blog_name,
                 contact_info=blog.blog_contact,
                 blog_writer=blog.blog_owner,
                 blog_url=blog.blog_url)
    
    # Set up chat history
    chat_history = RedisChatMessageHistory(url=redis_url, session_id=user_session_id)
    
    print(f"\nWelcome to the {blog.blog_name} chatbot!")
    print(f"This bot will help you find information about {blog.blog_name}.")
    print("Type 'exit' or 'quit' to end the session.\n")
    
    # Start chat loop
    while True:
        user_query = input("Hey there! What do you want to know about today? ")
        
        # Check if user wants to exit
        if user_query.lower() in ['exit', 'quit']:
            print("Thank you for using the chatbot. Goodbye!")
            break
            
        answer = ai_bot.get_response(question=user_query, chat_history=chat_history.messages)
        print(answer)
        
        # Store chat history
        chat_history.add_user_message(user_query)
        chat_history.add_ai_message(answer)
