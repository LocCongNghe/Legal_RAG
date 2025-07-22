import os
import re
from typing import List, Dict, Tuple, Optional
from sentence_transformers import SentenceTransformer
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document

class LegalDocumentRetriever:
    def __init__(self, vector_store_path: str, model_name: str = "Qwen/Qwen3-Embedding-0.6B"):
        self.model_name = model_name
        self.vector_store_path = vector_store_path
        self.vector_store = self._load_vector_store()
        
    def _load_vector_store(self):
        embeddings = HuggingFaceEmbeddings(
            model_name=self.model_name,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        vector_store = FAISS.load_local(
            self.vector_store_path, 
            embeddings, 
            allow_dangerous_deserialization=True  # Thêm dòng này
        )
       
        return vector_store
    
    def preprocess_query(self, query: str) -> str:
 
        query = re.sub(r'\s+', ' ', query)
        query = re.sub(r'[^\w\s\.\,\?\!\-]', '', query)
        query = query.lower().strip()
        return query
    
    def basic_retrieve(self, query: str, k: int = 5) -> List[Dict]:
        processed_query = self.preprocess_query(query)
        
        results = self.vector_store.similarity_search_with_score(processed_query, k=k)
        
        retrieved_docs = []
        for doc, score in results:
            retrieved_docs.append({
                'content': doc.page_content,
                'metadata': doc.metadata,
                'similarity_score': score,
                'source_file': doc.metadata.get('source_file', 'Unknown'),
                'chunk_id': doc.metadata.get('chunk_id', 0)
            })
        
        return retrieved_docs
    

# if __name__ == "__main__":
#     retriever = LegalDocumentRetriever("vector_store/")
    
#     query = "Các biện pháp can thiệp giảm tác hại trong dự phòng lây nhiễm HIV"
    
#     results = retriever.basic_retrieve(query, k=1)

#     for i, doc in enumerate(results, 1):
#         print(f"Kết quả {i}:")
#         print(f"File: {doc['source_file']}")
#         print(f"Score: {doc['similarity_score']:.4f}")
#         print(f"Content: {doc['content'][:2000]}...")
#         print("-" * 50)