import time
from crawler.parse_webpage import WebPageParser
from crawler.crawl_blog import BlogCrawler
from dotenv import load_dotenv
from preprocessor.process_document import WebPageTextPreprocessor
from vector_db.chroma_db import ChromaDb
from bot.Bot import Bot
from blog import Blog
from langchain.memory import ChatMessageHistory
from tqdm import tqdm

if __name__ == '__main__':
    load_dotenv("setup.env")
    blog = Blog(
        blog_name="TechNibbana",
        blog_owner="Nitesh Sinha",
        blog_url="https://technibbana.wordpress.com/",
        blog_contact="nitesh@technibbana.com"
    )
    crawler = BlogCrawler(blog.blog_url)
    loc_tags = crawler.crawl()
    vector_db = ChromaDb()
    for loc_tag in tqdm(loc_tags):
        # Add wait to fix Embedding API rate limits
        # TODO: Make it more sophisticated by sending more
        #  tokens per API call using tiktoken token counter
        #  and keeping it under the max token limit for the
        #  model(150,000 TPM for text-embedding-ada-002 model)
        time.sleep(20)
        if loc_tag.text.endswith((".jpg", ".png", ".jpeg")):
            # TODO: Remove img links while parsing sitemap
            continue
        print(f"Now processing {loc_tag.text}")
        parser = WebPageParser(loc_tag.text)
        parsed_webpage = parser.parse()
        text_preprocessor = WebPageTextPreprocessor(parsed_webpage)
        doc_chunks = text_preprocessor.process()
        vector_db.store_webpage(doc_chunks)
    ai_bot = Bot(blog_name=blog.blog_name,
                 contact_info=blog.blog_contact,
                 blog_writer=blog.blog_owner,
                 blog_url=blog.blog_url)
    chat_history = ChatMessageHistory()
    while True:
        user_query = input("Hey there! What do you want to know about today? ")
        answer = ai_bot.get_response(question=user_query, chat_history=chat_history.messages)
        print(answer)
        # Chat history will be summarized later.
        # TODO: Can be trimmed to last N messages if
        #  latency observed during longer chats
        chat_history.add_user_message(user_query)
        chat_history.add_ai_message(answer)
