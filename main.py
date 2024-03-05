from crawler.parse_webpage import WebPageParser
from dotenv import load_dotenv
from preprocessor.process_document import WebPageTextPreprocessor
from vector_db.chroma_db import ChromaDb
from bot.Bot import Bot
from langchain.memory import ChatMessageHistory

if __name__ == '__main__':
    load_dotenv("setup.env")
    blog_url = "https://technibbana.wordpress.com/"
    parser = WebPageParser(blog_url)
    parsed_webpage = parser.parse()
    text_preprocessor = WebPageTextPreprocessor(parsed_webpage)
    doc_chunks = text_preprocessor.process()
    vector_db = ChromaDb()
    vector_db.store_webpage(doc_chunks)
    ai_bot = Bot(blog_name="TechNibbana",
                 contact_info="nitesh@technibbana.com",
                 blog_writer="Nitesh Sinha",
                 blog_url=blog_url)
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
