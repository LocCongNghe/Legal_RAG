from openai import OpenAI
from retriever import LegalDocumentRetriever

def build_prompt(question, docs, prompt_template_path="prompt.txt"):
    with open(prompt_template_path, "r", encoding="utf-8") as f:
        template = f.read()
    docs_text = "\n\n".join([f"- {doc['content']}" for doc in docs])
    return template.format(question=question, documents=docs_text)

def gpt_generate_answer_text(question, docs, api_key, base_url, app_code,prompt_template_path="templates/hyde_prompt.txt", model_name="gpt-4.1-mini"):
    client = OpenAI(
        base_url=base_url,
        api_key=api_key,
        default_headers={"App-Code": app_code}
    )

    prompt = build_prompt(question, docs, prompt_template_path)
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=4096,
            top_p=0.8,
            extra_body={
                "service": "legal"
            }
        )
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        print(f"Lỗi khi gọi GPT để sinh đoạn văn: {e}")
        return None
    
def grade_documents(question, docs, api_key, base_url, app_code, prompt_template_path="templates/grade_prompt.txt", model_name="gpt-4.1-mini"):
    client = OpenAI(
        base_url=base_url,
        api_key=api_key,
        default_headers={"App-Code": app_code}
    )

    prompt = build_prompt(question, docs, prompt_template_path)

    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=4096,
            top_p=0.8,
            extra_body={
                "service": "legal"
            }
        )
        answer = response.choices[0].message.content.strip()

        if "yes" in answer.lower():    
            return "yes"
        elif "ambiguous" in answer.lower():
            return "ambiguous"
        else:
            return "no"
    
    except Exception as e:
        print(f"Lỗi khi gọi GPT để sinh đoạn văn: {e}")
        return None
   
def ask_gpt(question, docs, api_key, base_url,app_code, prompt_template_path="templates/rag_prompt.txt", model_name="gpt-4.1-mini"):
    client = OpenAI(
        base_url=base_url,
        api_key=api_key,
        default_headers={
            "App-Code": app_code
        }
    )
    
    prompt = build_prompt(question, docs, prompt_template_path)
    
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=4096,
            top_p=0.8,
            extra_body={
                "service": "legal"
            }
        )
        
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        print(f"Lỗi khi gọi OpenAI API: {e}")
        return None



