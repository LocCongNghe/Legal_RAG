import streamlit as st
from typing import Tuple, List, Dict, Optional
from llm import ask_gpt, grade_documents, gpt_generate_answer_text
from web_search import web_search

def process_question(question: str) -> Tuple[Optional[str], Optional[str], Optional[List[Dict]]]:
    try:
        # Tạo lịch sử cho context
        if st.session_state.chat_history:
            history_text = "\n".join([
                f"Q: {item['question']}\nA: {item['answer']}" 
                for item in st.session_state.chat_history
            ])
            docs_history = [{"content": history_text, "metadata": {}}]
        else:
            docs_history = []

        # Sinh answer text từ câu hỏi
        answer_text = gpt_generate_answer_text(
            question, 
            docs_history, 
            st.session_state.config['api_key'],
            st.session_state.config['base_url'],
            st.session_state.config['app_code']
        )

        # Tìm kiếm trong vector store
        docs_from_vector = st.session_state.retriever.basic_retrieve(answer_text, k=3)

        # Đánh giá chất lượng tài liệu
        grade = grade_documents(
            question, 
            docs_from_vector,
            st.session_state.config['api_key'],
            st.session_state.config['base_url'],
            st.session_state.config['app_code']
        )

        # Tìm kiếm web nếu cần
        docs_web = []
        if grade == "no" or grade == "ambiguous":
            web_doc = web_search(question)
            if web_doc:
                docs_web = [{"content": web_doc.page_content, "metadata": {}}]

        # Xác định nguồn tài liệu cuối cùng
        if grade == "yes":
            docs_final = docs_from_vector
            source_info = "Dựa trên tài liệu từ Vector Store"
        elif grade == "no":
            docs_final = docs_web
            source_info = "Dựa trên tài liệu từ Internet"
        elif grade == "ambiguous":
            docs_final = docs_from_vector + docs_web
            source_info = "Dựa trên tài liệu từ Vector Store và Internet"
        else:
            docs_final = docs_from_vector
            source_info = "Dựa trên tài liệu từ Vector Store"

        # Tạo câu trả lời cuối cùng
        final_answer = ask_gpt(
            question, 
            docs_final,
            st.session_state.config['api_key'],
            st.session_state.config['base_url'],
            st.session_state.config['app_code']
        )

        return final_answer, source_info, docs_final

    except Exception as e:
        st.error(f"Lỗi khi xử lý câu hỏi: {e}")
        return None, None, None