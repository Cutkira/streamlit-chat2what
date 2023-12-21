import streamlit as st

# Setting page with API about OpenAI and Pinecone
st.set_page_config(page_title="Setting", layout="wide")
st.title("Setting ⚙️")

if "LANGUAGE" not in st.session_state:
    st.session_state["LANGUAGE"] = "简体中文"

# set button string
if st.session_state["LANGUAGE"] == "简体中文":
    save_string = "保存"
elif st.session_state["LANGUAGE"] == "English":
    save_string = "Save"

if "switch_page" not in st.session_state:
    st.session_state["switch_page"] = "Setting"

# Setting initialization
if "OPENAI_API_KEY" not in st.session_state:
    st.session_state["OPENAI_API_KEY"] = ""
if "PINECONE_API_KEY" not in st.session_state:
    st.session_state["PINECONE_API_KEY"] = ""
if "PINECONE_ENVIRONMENT" not in st.session_state:
    st.session_state["PINECONE_ENVIRONMENT"] = ""

# OpenAI setting
st.title("OpenAI")
openai_api_key = st.text_input(label="🔑 :violet[API Key]",
                               value=st.session_state["OPENAI_API_KEY"],
                               max_chars=None,
                               type='password')


if st.button(label="🔑 " + save_string):
    with st.spinner("Saving..."):
        st.session_state["OPENAI_API_KEY"] = openai_api_key

# Pinecone setting
st.title("Pinecone")
pinecone_api_key = st.text_input(label="🌲 :violet[API Key]",
                                 value=st.session_state["PINECONE_API_KEY"],
                                 max_chars=None,
                                 type='password')
environment = st.text_input(label="🌲 :violet[Environment]",
                            value=st.session_state["PINECONE_ENVIRONMENT"],
                            max_chars=None,
                            type='password')
if st.button(label="🌲 " + save_string):
    with st.spinner("Saving..."):
        st.session_state["PINECONE_API_KEY"] = pinecone_api_key
        st.session_state["PINECONE_ENVIRONMENT"] = environment

st.session_state["switch_page"] = "Setting"
