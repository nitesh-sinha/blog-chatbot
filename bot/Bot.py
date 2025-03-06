from langchain.chains.base import Chain
from langchain_openai import ChatOpenAI
from langchain.prompts import (ChatPromptTemplate, SystemMessagePromptTemplate,
                               HumanMessagePromptTemplate, PromptTemplate)
from vector_db.chroma_db import ChromaDb
from langchain.chains import ConversationalRetrievalChain, LLMChain
import chainlit as cl
from typing import Any

SYSTEM_PROMPT_TEMPLATE = """
You are the AI soul behind this blog {blog_name} and so possess all the knowledge from it.
The blog is hosted at {blog_url}. Your task is to answer user queries related to this blog {blog_name}.
If you do not understand the user's question well, ask them to clarify it.
If the user's query is not answered in {blog_name}, don't try to make up an answer. Instead say that you don't know 
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

QUESTION_GENERATOR_TEMPLATE = """
Combine the chat history and followup question into a standalone question.
Chat history: {chat_history}
Followup question: {question}
"""


class Bot:
    def __init__(self, blog_name, blog_writer, blog_url, contact_info):
        self.blog_name = blog_name
        self.blog_writer = blog_writer
        self.blog_url = blog_url
        self.contact_info = contact_info
        self.model = ChatOpenAI(
            model_name="gpt-3.5-turbo",
            temperature=0.0,
            verbose=True
        )

    # Summarizes the user query based on the chat history
    # and current query.
    def summarize_question(self, chat_history: list[Any], question: str) -> str:
        question_prompt = PromptTemplate(
            input_variables=["chat_history", "question"],
            template=QUESTION_GENERATOR_TEMPLATE
        )
        question_summ_chain = LLMChain(llm=self.model, prompt=question_prompt)
        return question_summ_chain.run({
            "chat_history": chat_history,
            "question": question
        })

    def get_response(self, question, chat_history: list[Any]):
        # summarize the question
        question_summary = self.summarize_question(chat_history, question)

        # Feed this summary_question in the next call to QA model
        cur_chain = self.make_chain()
        bot_response = cur_chain({
            "question": question_summary,
            "chat_history": "",  # ConversationalRetrievalChain uses chat_history internally in a prompt
            "blog_name": self.blog_name,
            "contact_info": self.contact_info,
            "blog_url": self.blog_url,
            "blog_writer": self.blog_writer
        })
        return bot_response["answer"]

    # For every question asked by human, a new chain should get constructed
    def make_chain(self) -> Chain:
        model_prompt = Bot.get_prompt()
        vector_db = ChromaDb()
        vector_db_retriever = vector_db.get_retriever()
        # This retrieves the relevant docs from vector store
        # based on input query, then uses them as additional
        # context along with system prompt, chat history and human query
        # to query the ChatGPT model to answer the query
        return ConversationalRetrievalChain.from_llm(
            self.model,
            retriever=vector_db_retriever,
            return_source_documents=True,
            combine_docs_chain_kwargs=dict(prompt=model_prompt),
            verbose=True,
            rephrase_question=False
        )

    @classmethod
    def get_prompt(cls) -> ChatPromptTemplate:
        return ChatPromptTemplate(
            input_variables=["context", "chat_history", "question", "blog_name",
                             "contact_info", "blog_writer", "blog_url"],
            messages=[
                SystemMessagePromptTemplate(
                    prompt=PromptTemplate(
                        input_variables=["context", "chat_history", "blog_name",
                                         "contact_info", "blog_writer", "blog_url"],
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
