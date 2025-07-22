import os
import streamlit as st
from retriever import LegalDocumentRetriever

def initialize_retriever() -> bool:
    vector_store_path = "vector_store/"
    if os.path.exists(vector_store_path):
        try:
            retriever = LegalDocumentRetriever(vector_store_path)
            st.session_state.retriever = retriever
            return True
        except Exception as e:
            st.error(f"Lỗi khi khởi tạo retriever: {e}")
            return False
    else:
        st.error("Không tìm thấy vector store. Vui lòng chạy embedding.py trước.")
        return False