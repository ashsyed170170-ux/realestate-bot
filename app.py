import streamlit as st
import google.generativeai as genai
import os

# 1. SETUP: Direct API Key configuration taake Secrets ki zaroorat na rahe 🔴
GEMINI_API_KEY = "AQ.Ab8RN6L_8afZufZ5B0d47WQmTXUtc9uQhxhCC_jzYhaiOJuvNA"
genai.configure(api_key=GEMINI_API_KEY)

# 2. DATA LOAD: Direct variables me data daal diya taake ghalti ka chance na ho
properties_data = """
Available Properties:
1. DHA Phase 6 - 500 Sq Yards Luxury House. Price: 8 Crore PKR. 4 Bedrooms, Attached Baths, Beautiful Lawn, Modular Kitchen.
2. Clifton Block 5 - 3 Bedroom Apartment with Sea View. Price: 3.5 Crore PKR. Standby Generator, Dedicated Parking, 24/7 Security.
3. Bahria Town Precinct 10 - 250 Sq Yards Brand New House. Price: 2.2 Crore PKR. 3 Bedrooms, Double Story, Ready to move in.
4. Gulshan-e-Iqbal Block 13D - 120 Sq Yards Residential Plot. Price: 1.8 Crore PKR. West Open, Boundary Wall Project.

Company Name: Elite Real Estate Karachi
Contact Email: info@eliterealestate.com
Process: If a client is interested in any property or wants to visit, you MUST politely ask for their Name and Phone Number so our human agent can call them back. Do not give any property location details outside of this list.
"""

# 3. INTERFACE: Streamlit ki screen design
st.set_page_config(page_title="Elite Real Estate Bot", page_icon="🏡")
st.title("🏡 Elite Real Estate AI Assistant")
st.write("Welcome! Main aapko Karachi ki behtareen properties dhoondne me madad karunga.")

# 4. BOT BRAIN: System Instructions jo bot ko unka role samjhayengi
system_instruction = f"""
Aap Elite Real Estate Karachi ke ek professional, smart aur friendly sales agent hain. 
Aapka kaam sirf neeche diye gaye 'Properties Data' se parh kar client ko jawab dena hai. 
Agar data me koi property na ho, to politely mazuurat kar lein.
Jab bhi client kisi property me thoda sa bhi interest show kare, to aapne har haal me unka Name aur Phone Number mangna hai taake hamari team unse rabta kar sake.
Jawab hamesha short, professional aur Roman Urdu ya English me dein.

Properties Data:
{properties_data}
"""

# Gemini Model initialize karna
try:
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",  # Fast and free model
        system_instruction=system_instruction
    )
    
    # 5. CHAT HISTORY: Puraani baatein yaad rakhne ke liye
    if "chat" not in st.session_state:
        st.session_state.chat = model.start_chat(history=[])
except Exception as e:
    st.error(f"Model initialization me masla hai: {e}")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Purani chat screen par dikhana
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 6. USER INPUT: User se message lena aur bot ka jawab dikhana
if user_input := st.chat_input("DHA, Clifton ya Bahria me ghar chahiye?"):
    # User ka message screen par dikhana
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Gemini se response lena aur screen par dikhana
    with st.chat_message("assistant"):
        try:
            response = st.session_state.chat.send_message(user_input)
            answer = response.text
            st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
        except Exception as e:
            st.error(f"Error: {e}. Agar yeh authentication error hai, to please check karein ke API key valid hai ya nahi.")
