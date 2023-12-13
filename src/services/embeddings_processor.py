class EmbeddingsProcessor:
    def __init__(self, embeddings_model, milvus_manager):
        self.embeddings_model = embeddings_model
        self.milvus_manager = milvus_manager

    def process_and_save(self, text):


        embedding_vector = self.embeddings_model.embed_query(text)
        result = self.milvus_manager.insert(
            embedding_vector,
            text,
        )
        return result

    def process_and_search(self, query, top_k=None):
        embedding_vector_list = self.embeddings_model.embed_query(query)
        result = self.milvus_manager.search([embedding_vector_list], top_k)
        return result
