import streamlit as st
from chat_manager import load_chat_sessions, parse_chat_history, save_chat_history
from retriever_manager import initialize_retriever
import time
from typing import Generator

def render_header():
    """Hiển thị header chính"""
    st.markdown(
        '<div style="text-align: left; width: 100%;">'
        '<h1 style="color: #1f77b4; font-size: 2.5rem; margin-left: 400px; ">⚖️ Legal Chatbot</h1>'
        '</div>', 
        unsafe_allow_html=True
    )

def render_sidebar():
    """Hiển thị sidebar với các chức năng điều khiển"""
    with st.sidebar:
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.header("🔧 Cài đặt")
        
        # Nút tạo phiên chat mới
        if st.button("🆕 Tạo phiên chat mới"):
            st.session_state.chat_history = []
            st.success("Đã tạo phiên chat mới!")
            st.rerun()
        
        # Khởi tạo retriever
        if st.button("🔄 Khởi tạo Vector Store"):
            with st.spinner("Đang khởi tạo..."):
                if initialize_retriever():
                    st.success("Khởi tạo thành công!")
                    
        # Hiển thị trạng thái
        if st.session_state.retriever:
            st.success("✅ Vector Store đã sẵn sàng")
        else:
            st.warning("⚠️ Vector Store chưa được khởi tạo")
            
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Quản lý phiên chat
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.header("💬 Quản lý Chat")
        
        # Tải phiên chat cũ
        sessions = load_chat_sessions()
        if sessions:
            st.subheader("📋 Phiên chat đã lưu")
            session_options = [f"{s['timestamp']}" for s in sessions]
            selected_session = st.selectbox("Chọn phiên:", [""] + session_options)
            
            if selected_session and st.button("📂 Tải phiên"):
                selected_index = session_options.index(selected_session)
                history_text = sessions[selected_index]['history']
                st.session_state.chat_history = parse_chat_history(history_text)
                st.success(f"Đã tải phiên chat lúc {selected_session}")
                st.rerun()
        
        # Xóa lịch sử
        if st.button("🗑️ Xóa lịch sử hiện tại"):
            st.session_state.chat_history = []
            st.rerun()
            
        # Lưu phiên hiện tại
        if st.session_state.chat_history and st.button("💾 Lưu phiên hiện tại"):
            save_chat_history(st.session_state.chat_history)
            st.success("Đã lưu phiên chat!")
            
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Thống kê
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.header("📊 Thống kê")
        st.metric("Số câu hỏi", len(st.session_state.chat_history))
        st.metric("Tổng phiên đã lưu", len(sessions))
        st.markdown('</div>', unsafe_allow_html=True)

def render_chat_history():
    """Hiển thị lịch sử chat"""
    if st.session_state.chat_history:
        st.subheader("💬 Lịch sử hội thoại")
        for i, item in enumerate(st.session_state.chat_history):
            # Câu hỏi
            st.markdown(f"""
            <div class="chat-message user-message">
                <strong>🙋‍♂️ Bạn:</strong> {item['question']}
            </div>
            """, unsafe_allow_html=True)
            
            # Câu trả lời
            st.markdown(f"""
            <div class="chat-message assistant-message">
                <strong>🤖 Assistant:</strong><br>
                {item['answer']}
            </div>
            """, unsafe_allow_html=True)

def render_question_form():
    """Hiển thị form nhập câu hỏi"""
    st.subheader("❓ Đặt câu hỏi")
    
    with st.form("question_form"):
        question = st.text_area(
            "Nhập câu hỏi của bạn:",
            height=100,
            placeholder="Ví dụ: Quy định về hợp đồng lao động là gì?"
        )
        
        col_submit, col_clear = st.columns([1, 1])
        with col_submit:
            submit_button = st.form_submit_button("🚀 Gửi câu hỏi", use_container_width=True)
        with col_clear:
            clear_button = st.form_submit_button("🧹 Xóa", use_container_width=True)
        
        if clear_button:
            st.rerun()
    
    return submit_button, question

def render_system_info():
    """Hiển thị thông tin hệ thống"""
    st.subheader("ℹ️ Thông tin hệ thống")
    st.info("""
    **Legal Chatbot** sử dụng:
    - 🔍 RAG (Retrieval-Augmented Generation)
    - 📚 Vector Store với FAISS
    - 🌐 Web Search với Tavily
    - 🤖 GPT-4.1 Mini
    - 📊 Embedding Qwen3-0.6B
    """)
    
    # Hướng dẫn sử dụng
    st.subheader("📖 Hướng dẫn")
    st.markdown("""
    1. **Khởi tạo**: Nhấn "Khởi tạo Vector Store"
    2. **Đặt câu hỏi**: Nhập câu hỏi vào ô bên trái
    3. **Xem kết quả**: Hệ thống sẽ tìm kiếm và trả lời
    4. **Lưu phiên**: Nhấn "Lưu phiên hiện tại" để lưu
    5. **Tải phiên cũ**: Chọn từ danh sách phiên đã lưu
    """)

def render_answer_display(answer_generator: Generator[str, None, None], 
                          source_info: str, 
                          docs: list,
                          delay: float = 0.01):

    answer_placeholder = st.empty()
    accumulated_answer = ""
    
    # Container cho toàn bộ message
    with answer_placeholder.container():
        # Hiển thị header
        st.markdown("**🤖 Assistant:**")
        
        # Placeholder cho nội dung streaming
        content_placeholder = st.empty()
        
        # Stream từng phần câu trả lời
        for chunk in answer_generator:
            accumulated_answer += chunk
            
            # Cập nhật nội dung với cursor nhấp nháy
            content_placeholder.markdown(f"""
            <div class="chat-message assistant-message">
                {accumulated_answer}<span class="cursor">|</span>
            </div>
            """, unsafe_allow_html=True)
            
            time.sleep(delay)
        
        # Hiển thị câu trả lời hoàn chỉnh
        content_placeholder.markdown(f"""
        <div class="chat-message assistant-message">
            {accumulated_answer}
            <div class="source-info">
                <strong>📚 Nguồn:</strong> {source_info}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    if docs:
        with st.expander("📄 Tài liệu tham khảo"):
            for i, doc in enumerate(docs[:3]):
                st.markdown(f"**Tài liệu {i+1}:**")
                if 'source_file' in doc.get('metadata', {}):
                    st.markdown(f"*Nguồn: {doc['metadata']['source_file']}*")
                st.markdown(f"```\n{doc['content'][:500]}...\n```")
                st.markdown("---")