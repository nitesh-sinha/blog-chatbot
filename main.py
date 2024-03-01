from crawler.parse_webpage import WebPageParser
from dotenv import load_dotenv
from preprocessor.process_document import WebPageTextPreprocessor
from vector_db.chroma_db import ChromaDb
from bot.Bot import Bot
from langchain.memory import ChatMessageHistory

if __name__ == '__main__':
    load_dotenv("setup.env")
    parser = WebPageParser("https://technibbana.wordpress.com/")
    parsed_webpage = parser.parse()
    text_preprocessor = WebPageTextPreprocessor(parsed_webpage)
    doc_chunks = text_preprocessor.process()
    vector_db = ChromaDb()
    vector_db.store_webpage(doc_chunks)
    nibbana_bot = Bot(blog_name="TechNibbana",
                      contact_info="nitesh@technibbana.com",
                      blog_writer="Nitesh Sinha")
    chat_history = ChatMessageHistory()
    while True:
        user_query = input("Hey there! What do you want to know about today? ")
        answer = nibbana_bot.get_response(question=user_query, chat_history=chat_history.messages)
        print(answer)
        chat_history.add_user_message(user_query)
        chat_history.add_ai_message(answer)
