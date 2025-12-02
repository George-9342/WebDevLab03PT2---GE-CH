import streamlit as st
import creativeApi            
import creativeAPI_llm        
import creativeAPI_chatbot  

st.title("Web Development Lab03")

st.header("CS 1301")
st.subheader("Team 17, Web Development - Section E")
st.subheader("George Ejike, Chris Hernandez")

st.sidebar.title("Menu")
page = st.sidebar.radio(
    "Go to:",
    ["Home", "API Page (Phase 2)", "LLM Analysis (Phase 3)", "Chatbot (Phase 4)"]
)

if page == "Home":
    st.write("""
    Welcome to our Streamlit Web Development Lab03 app!

    - **API Page (Phase 2)** – Rick and Morty API & graphs  
    - **LLM Analysis (Phase 3)** – Character comparison with Gemini  
    - **Chatbot (Phase 4)** – Rick and Morty conversational assistant  
    """)

elif page == "API Page (Phase 2)":
    creativeApi.dataStuff()

elif page == "LLM Analysis (Phase 3)":
    creativeAPI_llm.dataStuff()

elif page == "Chatbot (Phase 4)":
    creativeAPI_chatbot.dataStuff()
