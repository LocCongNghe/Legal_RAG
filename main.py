import streamlit as st
from config import PAGE_CONFIG, CUSTOM_CSS, initialize_session_state
from ui_components import (
    render_header, render_sidebar, render_chat_history, 
    render_question_form, render_system_info, render_answer_display
)
from question_processor import process_question

def main():

    st.set_page_config(**PAGE_CONFIG)
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    initialize_session_state()
    render_header()
    render_sidebar()
    col1, col2 = st.columns([3, 1])
    
    with col1:
        render_chat_history()
        submit_button, question = render_question_form()
        
        if submit_button and question.strip():
            if not st.session_state.retriever:
                st.error("Vui lòng khởi tạo Vector Store trước khi sử dụng!")
            else:
                with st.spinner("🔍 Đang tìm kiếm và xử lý..."):
                    answer, source_info, docs = process_question(question.strip())
                    
                    if answer:
                        st.session_state.chat_history.append({
                            "question": question.strip(),
                            "answer": answer
                        })
                        render_answer_display(answer, source_info, docs)
                        st.rerun()
                    else:
                        st.error("Không thể tạo câu trả lời. Vui lòng thử lại!")
    
    with col2:
        render_system_info()

if __name__ == "__main__":
    main()