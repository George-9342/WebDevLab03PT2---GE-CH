import streamlit as st
import requests
import pandas as pd
import google.generativeai as genai

# LLM setup
API_KEY = st.secrets["key"]
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

BASE_URL = "https://rickandmortyapi.com/api/character"


def get_character(name):
    if name.strip() == "":
        return None
    resp = requests.get(f"{BASE_URL}/?name={name}")
    if resp.status_code != 200:
        return None
    data = resp.json().get("results", [])
    if len(data) == 0:
        return None
    return data[0]


def get_top_characters(limit=10):
    resp = requests.get(BASE_URL)
    if resp.status_code != 200:
        return pd.DataFrame()

    data = resp.json().get("results", [])
    if not data:
        return pd.DataFrame()

    df = pd.DataFrame(data)
    df["episode_count"] = df["episode"].apply(len)

    origin_names = []
    for o in df["origin"]:
        if isinstance(o, dict) and "name" in o:
            origin_names.append(o["name"])
        else:
            origin_names.append("Unknown")

    df["origin_name"] = origin_names
    df = df[["name", "status", "species", "origin_name", "episode_count"]]

    df = df.sort_values("episode_count", ascending=False).head(limit)
    return df


def build_context_text(df, focus_char):
    lines = []
    for _, row in df.iterrows():
        lines.append(
            f"{row['name']} — status: {row['status']}, species: {row['species']}, "
            f"origin: {row['origin_name']}, episodes: {row['episode_count']}"
        )

    context = "\n".join(lines)

    focus_text = ""
    if focus_char is not None:
        focus_text = (
            f"\n\nFocused character:\n"
            f"Name: {focus_char['name']}\n"
            f"Status: {focus_char['status']}\n"
            f"Species: {focus_char['species']}\n"
            f"Origin: {focus_char['origin']['name']}\n"
            f"Episodes: {len(focus_char['episode'])}\n"
        )

    return context + focus_text



def dataStuff():

    st.title("🧪 Rick and Morty Chatbot")
    st.markdown(
        "Talk to a chatbot that uses **live Rick and Morty API data** to answer questions."
    )
    st.write("---")

    # Chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Layout
    chat_col, data_col = st.columns([2, 1])

    with data_col:
        st.subheader("⚙️ API Context Settings")

        top_n = st.slider("Number of top characters to include", 3, 20, 8)

        focus_name = st.text_input(
            "Optional focus character", 
            value="Rick Sanchez",
            help="Adds extra detail to the chatbot."
        )

        df = get_top_characters(top_n)

        focus_char = None
        if focus_name.strip() != "":
            focus_char = get_character(focus_name)

        if focus_char is not None:
            st.markdown("**Focused Character:**")
            st.write(f"**{focus_char['name']}**")
            st.write(f"Status: {focus_char['status']}")
            st.write(f"Species: {focus_char['species']}")
            st.write(f"Origin: {focus_char['origin']['name']}")
            st.write(f"Episodes: {len(focus_char['episode'])}")
        else:
            st.caption("No valid focus character found.")

        st.markdown("**Characters sent to the LLM:**")
        if not df.empty:
            st.dataframe(df, height=260)
        else:
            st.warning("Could not load character data.")

    with chat_col:
        st.subheader("💬 Chat")

        user_msg = st.text_area(
            "Ask a question:", 
            height=100,
            placeholder="e.g., Who appears in more episodes?"
        )

        if st.button("Send"):
            if user_msg.strip() == "":
                st.warning("Type a message first.")
            else:
                context_text = build_context_text(df, focus_char)

                history_text = ""
                for role, text in st.session_state.chat_history:
                    history_text += f"{role.upper()}: {text}\n"

                prompt = f"""
You are a helpful assistant that knows about Rick and Morty.

Here is API data:
{context_text}

Prior conversation:
{history_text}

Answer the user's question using API data when possible.

USER QUESTION: {user_msg}
"""

                try:
                    response = model.generate_content(prompt)
                    bot_reply = response.text
                except Exception as e:
                    st.error(f"Error calling Gemini: {e}")
                    return

                st.session_state.chat_history.append(("user", user_msg))
                st.session_state.chat_history.append(("bot", bot_reply))

        # display chat history
        for role, text in st.session_state.chat_history:
            if role == "user":
                st.markdown(f"**🧑 You:** {text}")
            else:
                st.markdown(f"**🤖 Bot:** {text}")
