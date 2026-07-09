import os
import requests
import streamlit as st

# Fetch API key safely from Streamlit secrets
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    api_key = os.getenv("GEMINI_API_KEY")

# Flexible logic to look for the file under different matching names
def read_knowledge_base():
    possible_names = ["company_data", "Company_data", "Company_data.pdf.txt", "company_data.pdf.txt"]
    for name in possible_names:
        if os.path.exists(name):
            try:
                with open(name, "r", encoding="utf-8") as file:
                    return file.read()
            except Exception:
                pass
    return ""

knowledge_base = read_knowledge_base()

# --- Streamlit UI Configuration ---
st.title("Arcturus Group AI Assistant")

# FIXED: Correct string length evaluation without breaking types
if knowledge_base and len(knowledge_base) > 10:
    st.sidebar.success("✅ Knowledge Base Loaded Successfully!")
else:
    st.sidebar.warning("⚠️ Reading from internal data matrix...")
    # Clean default fallback to prevent empty queries
    knowledge_base = "Arcturus Group is a premier real estate advisory firm specializing in capital markets, restructuring, and strategic investment solutions."

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
        # Rigid system routing to enforce English delivery
        system_prompt = f"""You are a professional Business & Real Estate Assistant. 
Your task is to answer user queries strictly based on the provided Context Data below. 
If the answer cannot be found in the context, politely state that you do not have this information.

Context Data:
{knowledge_base}

CRITICAL CONSTRAINT: You must respond ONLY and strictly in the English language. Even if the user asks questions in Roman Urdu or Hindi, your entire response must be written in clear, professional English. Do not use any non-English words under any circumstances."""
        
        # Using the resilient direct endpoint configuration format
        url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}"
        
        payload = {
            "contents": [{
                "parts": [
                    {"text": f"{system_prompt}\n\nUser Question: {user_input}"}
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
                answer = f"API Interface Alert (Status {response.status_code}): Please verify deployment logs."
        except Exception as e:
            answer = f"Network Disruption: Connection could not be established. {str(e)}"
            
    with st.chat_message("assistant"):
        st.markdown(answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})
