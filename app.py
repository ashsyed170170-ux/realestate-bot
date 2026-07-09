import os
import requests
import streamlit as st

# Streamlit secrets se API key uthana
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    api_key = os.getenv("GEMINI_API_KEY")

# Background mein file read karne ka function
def read_knowledge_base(file_path="Company_data.pdf.txt"):
 # Background mein file read karne ka naya aur safe tareeqa
def read_knowledge_base():
    # Yeh un saare naamon ko check karega jo aapki file ke ho sakte hain
    possible_names = ["Company_data.pdf.txt", "company_data.pdf.txt", "Company_data.pdf"]
    for name in possible_names:
        if os.path.exists(name):
            try:
                with open(name, "r", encoding="utf-8") as file:
                    return file.read()
            except Exception:
                pass
    return ""

knowledge_base = read_knowledge_base()

# --- Streamlit UI ---
st.title("Arcturus Group AI Assistant")

# Sidebar status code check
if len(knowledge_base) > 10:  # Agar file mein thoda sa bhi data parha gaya hai
    st.sidebar.success("✅ Knowledge Base Loaded Successfully!")
else:
    # Agar sach mein data bilkul khaali hai
    st.sidebar.warning("⚠️ Warning: Reading from backup memory.")
    # Agar data bilkul nahi mil raha to error na dikhaye agar bot chal raha hai
    knowledge_base = "Arcturus Group is a senior real estate advisory firm..." # Backup context

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if user_input := st.chat_input("Ask anything about Arcturus Group..."):
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    if not api_key:
        answer = "ERROR: GEMINI_API_KEY is missing in Streamlit Secrets!"
    else:
        # Strict English System Prompt
        system_prompt = f"""You are a professional Business & Real Estate Assistant. 
Your task is to answer user queries strictly based on the provided Context Data below. 
If the answer cannot be found in the context, politely state that you do not have this information.

Context Data:
{knowledge_base}

CRITICAL CONSTRAINT: You must respond ONLY and strictly in the English language. Even if the user asks questions in Roman Urdu or Hindi, your entire response must be written in clear, professional English. Do not use any non-English words."""
        
        # FIXED: Using the globally available gemini-1.5-flash endpoint
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        
        full_prompt_text = f"{system_prompt}\n\nUser Question: {user_input}"
        
        payload = {
            "contents": [{
                "parts": [
                    {"text": full_prompt_text}
                ]
            }]
        }
        
        headers = {"Content-Type": "application/json"}
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code == 200:
                res_data = response.json()
                answer = res_data['candidates'][0]['content']['parts'][0]['text']
            else:
                answer = f"API Error (Status {response.status_code}): {response.text}"
        except Exception as e:
            answer = f"Connection Error: Could not connect to Gemini API. {str(e)}"
            
    with st.chat_message("assistant"):
        st.markdown(answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})
