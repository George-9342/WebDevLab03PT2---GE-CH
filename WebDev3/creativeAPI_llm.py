import streamlit as st
import requests
import pandas as pd
import altair as alt
import google.generativeai as genai

# Gemini API Key
API_KEY = st.secrets["key"]
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

# Rick & Morty API
BASE_URL = "https://rickandmortyapi.com/api/character"

# Getting characters
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


def build_character_summary(c):
    return (
        f"Name: {c['name']}\n"
        f"Status: {c['status']}\n"
        f"Species: {c['species']}\n"
        f"Gender: {c['gender']}\n"
        f"Origin: {c['origin']['name']}\n"
        f"Number of episodes: {len(c['episode'])}\n"
    )

def dataStuff():

    
    st.title("Rick and Morty Character Analyzer (Phase 3)")

    
    col1, col2 = st.columns(2)
    with col1:
        name1 = st.text_input("Character 1", value="Rick Sanchez")
    with col2:
        name2 = st.text_input("Character 2", value="Morty Smith")

    style = st.selectbox(
        "Analysis Style",
        ["Serious analysis", "Funny roast", "In-universe news article"]
    )

    if st.button("Analyze"):

        # Get characters
        char1 = fetch_character(name1)
        char2 = fetch_character(name2)

        if not char1:
            st.error(f"Could not find {name1}")
            return
        if not char2:
            st.error(f"Could not find {name2}")
            return

        # Side by side Comp
        st.subheader("Character Comparison")
        card_col1, card_col2 = st.columns(2)

        with card_col1:
            st.markdown(f"### {char1['name']}")
            st.image(char1["image"], use_container_width=True)
            st.write(f"**Status:** {char1['status']}")
            st.write(f"**Species:** {char1['species']}")
            st.write(f"**Gender:** {char1['gender']}")
            st.write(f"**Origin:** {char1['origin']['name']}")
            st.write(f"**Episodes:** {len(char1['episode'])}")

        with card_col2:
            st.markdown(f"### {char2['name']}")
            st.image(char2["image"], use_container_width=True)
            st.write(f"**Status:** {char2['status']}")
            st.write(f"**Species:** {char2['species']}")
            st.write(f"**Gender:** {char2['gender']}")
            st.write(f"**Origin:** {char2['origin']['name']}")
            st.write(f"**Episodes:** {len(char2['episode'])}")

        # DataFrame
        df = pd.DataFrame({
            "name": [char1["name"], char2["name"]],
            "episode_count": [len(char1["episode"]), len(char2["episode"])]
        })
        st.write("### Episode Counts")
        st.dataframe(df)

        # Chart
        chart = (
            alt.Chart(df)
            .mark_bar()
            .encode(
                x="name:N",
                y="episode_count:Q",
                tooltip=["name", "episode_count"]
            )
            .interactive()
        )
        st.altair_chart(chart, use_container_width=True)

        # Prompt for LLM
        summary1 = build_character_summary(char1)
        summary2 = build_character_summary(char2)

        if style == "Serious analysis":
            tone = "Write an objective comparison using only the data."
        elif style == "Funny roast":
            tone = "Write a humorous roast style comparison."
        else:
            tone = "Write an in-universe Rick and Morty news article comparing them."

        prompt = f"""
Compare these two Rick and Morty characters using only the data.

Character 1:
{summary1}

Character 2:
{summary2}

{tone}
"""

        # Error handling
        st.subheader("LLM-Generated Analysis")
        try:
            response = model.generate_content(prompt)
            st.write(response.text)
        except Exception as e:
            st.error(f"Error calling Gemini: {e}")
