from langchain.docstore.document import Document
from langchain.text_splitter import MarkdownTextSplitter
from crawler.webpage import WebPage


class WebPageTextPreprocessor:
    def __init__(self, page: WebPage):
        self.doc_text = page.text
        self.doc_metadata = page.metadata

    def process(self) -> list[Document]:
        self._clean_text()
        return self._chunk_docs()

    def remove_extra_spaces(self) -> str:
        return ' '.join(self.doc_text.split())

    def _clean_text(self):
        for cleaning_fn in [self.remove_extra_spaces()]:
            self.doc_text = cleaning_fn

    def _chunk_docs(self) -> list[Document]:
        text_splitter = MarkdownTextSplitter(chunk_size=1000, chunk_overlap=200)
        text_chunks = text_splitter.split_text(self.doc_text)
        doc_chunks = [Document(page_content=text_chunk, metadata=self.doc_metadata) for text_chunk in text_chunks]
        return doc_chunks
