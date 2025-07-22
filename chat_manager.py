import os
import csv
import datetime
from typing import List, Dict

def save_chat_history(chat_history: List[Dict]):
    """Lưu lịch sử chat vào file CSV"""
    if chat_history:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        filename = "all_chat_sessions.csv"
        file_exists = os.path.isfile(filename)
        
        history_text = "\n".join([
            f"Q: {item['question']}\nA: {item['answer']}" 
            for item in chat_history
        ])
        
        with open(filename, "a", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["timestamp", "history"])
            if not file_exists:
                writer.writeheader()
            writer.writerow({
                "timestamp": timestamp,
                "history": history_text
            })

def load_chat_sessions() -> List[Dict]:
    """Tải các phiên chat đã lưu"""
    filename = "all_chat_sessions.csv"
    if os.path.isfile(filename):
        with open(filename, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return list(reader)
    return []

def parse_chat_history(history_text: str) -> List[Dict]:
    """Phân tích lịch sử chat từ text, thu thập toàn bộ câu trả lời nhiều dòng"""
    chat_history = []
    lines = history_text.split("\n")
    i = 0
    while i < len(lines):
        if lines[i].startswith("Q: "):
            question = lines[i][3:]
            answer_lines = []
            i += 1
            if i < len(lines) and lines[i].startswith("A: "):
                # Lấy phần còn lại của dòng bắt đầu với "A: "
                answer_lines.append(lines[i][3:])
                i += 1
                # Thu thập các dòng tiếp theo cho đến khi gặp "Q: " mới hoặc hết file
                while i < len(lines) and not lines[i].startswith("Q: "):
                    answer_lines.append(lines[i])
                    i += 1
                answer = "\n".join(answer_lines).rstrip()
                chat_history.append({"question": question, "answer": answer})
            else:
                continue
        else:
            i += 1
    return chat_history