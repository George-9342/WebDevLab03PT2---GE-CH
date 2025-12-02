import streamlit as st
import requests
import pandas as pd
import altair as alt # for my data

def dataStuff():

    st.title("Rick and Morty API Explorer")

    st.header("Character Search")

    char_name = st.text_input("Search for a character:")

    if char_name.strip() != "":
        url = f"https://rickandmortyapi.com/api/character/?name={char_name}"
        resp = requests.get(url)

        if resp.status_code != 200:
            st.error("Character not found.")
            return

        data = resp.json().get("results", [])
        if len(data) == 0:
            st.warning("No match found.")
            return

        c = data[0]

        st.subheader(c["name"])
        st.image(c["image"], width=200)
        st.write(f"**Status:** {c['status']}")
        st.write(f"**Species:** {c['species']}")
        st.write(f"**Gender:** {c['gender']}")
        st.write(f"**Origin:** {c['origin']['name']}")
        st.write(f"**Appears in:** {len(c['episode'])} episodes")

        ep_df = pd.DataFrame({
            "stat": ["Episode Appearances"],
            "value": [len(c["episode"])]
        })

        st.subheader("Character Episode Count")

        chart = (
            alt.Chart(ep_df)
            .mark_bar()
            .encode(
                x="stat:N",
                y="value:Q",
                tooltip=["stat", "value"]
            )
            .interactive()
        )

        st.altair_chart(chart, use_container_width=True)

    st.write("---")

    st.header("Top Characters by Episode Count")

    count_limit = st.slider("How many characters should be shown?", 3, 20, 5)

    url = "https://rickandmortyapi.com/api/character"
    first_page = requests.get(url).json()

    df = pd.DataFrame(first_page["results"])
    df["episode_count"] = df["episode"].apply(len)

    top_chars = df.sort_values("episode_count", ascending=False).head(count_limit)[
        ["name", "episode_count"]
    ]

    chart2 = (
        alt.Chart(top_chars)
        .mark_bar()
        .encode(
            x="name:N",
            y="episode_count:Q",
            tooltip=["name", "episode_count"]
        )
        .interactive()
    )

    st.altair_chart(chart2, use_container_width=True)
    st.dataframe(top_chars)
