import os
import glob
from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import Docx2txtLoader
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

def process_docx_to_vector_store(docx_folder_path: str, vector_store_path: str):
    model_name = "Qwen/Qwen3-Embedding-0.6B"
    model = SentenceTransformer(model_name)
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000,
        chunk_overlap=200,
        length_function=len,
        separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
    )

    embeddings = HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )

    if os.path.exists(os.path.join(vector_store_path, "index.faiss")):
        vector_store = FAISS.load_local(vector_store_path, embeddings, allow_dangerous_deserialization=True)
        print("Vector store đã được nạp.")

        existing_sources = set(
            doc.metadata["source_file"]
            for doc in vector_store.docstore._dict.values()
            if "source_file" in doc.metadata
        )
    else:
        vector_store = FAISS.from_texts([], embedding=embeddings)
        existing_sources = set()
        print("Tạo mới vector store.")

    docx_files = glob.glob(os.path.join(docx_folder_path, "*.docx"))
    new_chunks = []

    for docx_file in docx_files:
        filename = os.path.basename(docx_file)
        if filename in existing_sources:
            print(f"Đã tồn tại: {filename}, bỏ qua.")
            continue

        print(f"Đang xử lý: {filename}")
        loader = Docx2txtLoader(docx_file)
        documents = loader.load()
        chunks = text_splitter.split_documents(documents)

        for i, chunk in enumerate(chunks):
            chunk.metadata['source_file'] = filename
            chunk.metadata['chunk_id'] = i
            chunk.metadata['chunk_size'] = len(chunk.page_content)

        new_chunks.extend(chunks)

    if new_chunks:
        texts = [chunk.page_content for chunk in new_chunks]
        metadatas = [chunk.metadata for chunk in new_chunks]

        vector_store.add_texts(
            texts=texts,
            metadatas=metadatas
        )

        vector_store.save_local(vector_store_path)
        print(f"Đã thêm {len(new_chunks)} đoạn mới vào vector store.")
    else:
        print("Không có tài liệu mới để thêm.")

    return vector_store


if __name__ == "__main__":
    DOCX_FOLDER = "data/"
    VECTOR_STORE_PATH = "vector_store/"
    vector_store = process_docx_to_vector_store(DOCX_FOLDER, VECTOR_STORE_PATH)