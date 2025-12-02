import streamlit as st
import requests
import pandas as pd
import google.generativeai as genai

# LLM setup
API_KEY = st.secrets["key"]  
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

BASE_URL = "https://rickandmortyapi.com/api/character"


def fetch_character(name):
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
            f"{row['name']} — status: {row['status']}, "
            f"species: {row['species']}, origin: {row['origin_name']}, "
            f"episodes: {row['episode_count']}"
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
        """
        Talk to a chatbot that uses **live Rick and Morty API data** to answer questions  
        about characters, their status, origins, and episode appearances.
        """
    )
    st.write("---")

    # Chat History 
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Layout
    chat_col, data_col = st.columns([2, 1])

    with data_col:
        st.subheader("⚙️ API Context Settings")

        top_n = st.slider("Number of top characters to include", 3, 20, 8)
        focus_name = st.text_input(
            "Optional focus character", value="Rick Sanchez", help="Used to give the LLM extra detail."
        )

        df = get_top_characters(top_n)

        focus_char = None
        if focus_name.strip() != "":
            focus_char = fetch_character(focus_name)

        if focus_char is not None:
            st.markdown("**Focused Character**")
            with st.container():
                st.write(f"**{focus_char['name']}**")
                st.write(f"Status: {focus_char['status']}")
                st.write(f"Species: {focus_char['species']}")
                st.write(f"Origin: {focus_char['origin']['name']}")
                st.write(f"Episodes: {len(focus_char['episode'])}")
        else:
            st.caption("No valid focus character found.")

        st.markdown("**Characters sent to the LLM:**")
        if not df.empty:
            st.dataframe(df, use_container_width=True, height=260)
        else:
            st.warning("Could not load character data from the API.")

    with chat_col:
        st.subheader("💬 Chat")

        user_msg = st.text_area(
            "Ask me a question Why don'tya:",
            height=100,
            placeholder="e.g., Who appears in more episodes, and why?"
        )

        send = st.button("Send")

        if send:
            if user_msg.strip() == "":
                st.warning("Type a question before sending.")
            else:
                context_text = build_context_text(df, focus_char)

                history_text = ""
                for role, text in st.session_state.chat_history:
                    history_text += f"{role.upper()}: {text}\n"

                prompt = f"""
You are a helpful assistant that knows about the TV show Rick and Morty.

Here is data from the Rick and Morty API about some characters:
{context_text}

Here is the previous conversation:
{history_text}

The user will now ask a new question.
Answer using the API data above when possible. If something is not in the data,
you can still answer based on general knowledge of the show, or to the best of your ability generally.

USER QUESTION: {user_msg}
"""

                try:
                    response = model.generate_content(prompt)
                    bot_reply = response.text
                except Exception as e:
                    st.error(f"Error calling Gemini: {e}")
                    return

                st.session_state.chat_history.append(("you", user_msg))
                st.session_state.chat_history.append(("bot", bot_reply))

        # Chat History Display
        if st.session_state.chat_history:
            st.markdown("----")
            for role, text in st.session_state.chat_history:
                if role == "you":
                    st.markdown(f"**🧑 You:** {text}")
                else:
                    st.markdown(f"**🤖 Bot:** {text}")
        else:
            st.caption("No messages yet. Ask something to start the conversation!")
