from langchain.chains.base import Chain
from langchain_openai import ChatOpenAI
from langchain.prompts import (ChatPromptTemplate, SystemMessagePromptTemplate,
                               HumanMessagePromptTemplate, PromptTemplate)
from vector_db.chroma_db import ChromaDb
from langchain.chains import ConversationalRetrievalChain

SYSTEM_PROMPT_TEMPLATE = """
You are NibbanaBot, the AI soul behind this blog {blog_name} and so possess all the knowledge from it.
Your task is to answer user queries related to this {blog_name}.
If you do not understand the user's question well, ask them to clarify it.
If the user's query is not answered in {blog_name}, don't try to make up an answer. Instead you say that you don't know 
the answer and suggest the best way forward is to contact {blog_writer}, the human brain behind {blog_name} at {contact_info}. 
Don't be overconfident and don't hallucinate. Please be respectful and polite while answering the questions.
Wherever needed, please provide helpful links to understand more about the query. 

Use the following pieces of context to answer the user's question.

----------------

{context}
{chat_history}

Follow up question:
"""

HUMAN_PROMPT_TEMPLATE = """
{question}
"""

class Bot:
    def __init__(self, blog_name, blog_writer, contact_info):
        self.blog_name = blog_name
        self.blog_writer = blog_writer
        self.contact_info = contact_info

    def get_response(self, question, chat_history=""):
        cur_chain = Bot.make_chain()
        bot_response = cur_chain({
            "question": question,
            "chat_history": chat_history,
            "blog_name": self.blog_name,
            "contact_info": self.contact_info,
            "blog_writer": self.blog_writer
        })
        return bot_response["answer"]

    @classmethod
    def get_prompt(cls) -> ChatPromptTemplate:
        return ChatPromptTemplate(
            input_variables=["context", "chat_history", "question", "blog_name", "contact_info", "blog_writer"],
            messages=[
                SystemMessagePromptTemplate(
                    prompt=PromptTemplate(
                        input_variables=["context", "chat_history", "blog_name", "contact_info", "blog_writer"],
                        template=SYSTEM_PROMPT_TEMPLATE,
                        template_format="f-string",
                        validate_template=True
                    ), additional_kwargs={}
                ),
                HumanMessagePromptTemplate(
                    prompt=PromptTemplate(
                        input_variables=["question"],
                        template=HUMAN_PROMPT_TEMPLATE,
                        template_format="f-string",
                        validate_template=True
                    ), additional_kwargs={}
                )
            ]
        )

    # For every question asked by human, a new chain should get constructed
    @classmethod
    def make_chain(cls) -> Chain:
        model = ChatOpenAI(
            model_name="gpt-3.5-turbo",
            temperature=0.0,
            verbose=True
        )
        model_prompt = Bot.get_prompt()
        vector_db = ChromaDb()
        vector_db_retriever = vector_db.get_retriever()
        # This retrieves the relevant docs from vector store
        # based on input query, then uses them as additional
        # context along with system prompt, chat history and human query
        # to query the ChatGPT model to answer the query
        return ConversationalRetrievalChain.from_llm(
            model,
            retriever=vector_db_retriever,
            return_source_documents=True,
            combine_docs_chain_kwargs=dict(prompt=model_prompt),
            verbose=True,
            rephrase_question=False
        )
