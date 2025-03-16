from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import Chroma

class ChromaDb:
    def get_client(self) -> Chroma:
        client = Chroma(
            collection_name="blog_data",
            embedding_function=OllamaEmbeddings(model="mistral"),
            persist_directory="chroma/datastore"

        )
        return client

    '''
    Takes chunks of a doc as input and stores them
    in vector database. While storing those docs, the
    chroma client creates the embeddings using embedding 
    function on the doc_chunks and then persists those
    embeddings of the doc_chunks
    '''
    def store_webpage(self, doc_chunks):
        chroma_client = self.get_client()
        chroma_client.add_documents(doc_chunks)
        chroma_client.persist()

    def search_k_nearest_neighbors(self, k):
        pass

    def get_retriever(self):
        chroma_client = self.get_client()
        return chroma_client.as_retriever(search_type="mmr", verbose=True)
                                          # TODO: Uncomment this for k nearest search - search_kwargs={"k": 1})