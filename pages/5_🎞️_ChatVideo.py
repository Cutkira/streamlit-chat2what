import streamlit as st
import pinecone
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Pinecone
from langchain.document_loaders import BiliBiliLoader, YoutubeLoader
from langchain_core.messages import HumanMessage, AIMessage

from openai import OpenAI
from langchain.llms import OpenAI as LLM_OpenAI

from utils.utils import extract_text_from_video, split_content_into_chunks, translate_into_chinese, summary_from_texts, \
    save_chunks_into_vectorstore, search_from_content

# Initialize llm, embedding model and vectorstore Object
speech_to_text_llm = None
openai_llm = None
embedding_model = None
qa_chain = None

# Setting ChatVideo page
st.set_page_config(page_title="ChatVideo", layout="wide")
st.title("ChatVideo 🎞️")

if "LANGUAGE" not in st.session_state:
    st.session_state["LANGUAGE"] = "简体中文"

if st.session_state["LANGUAGE"] == "简体中文":
    file_uploader_string = "上传视频或音频文件，点击‘提交并处理’"
    submit_button_string = "提交并处理"
    submit_button_spinner_string = "稍等..."
    tab_translation_string = "翻译"
    tab_summarization_string = "总结"
    translate_button_string = "翻译！"
    translate_button_spinner_string = "翻译中..."
    summary_button_string = "总结！"
    summary_button_spinner_string = "总结中..."
    chat_input_string = "问点儿什么吧..."
    qa_warning_string = "哎呀！ 如果你想测试 Q&A 功能，请先设置Pinecone API Key 和提交PDF文件"
    openai_error_string = "哎呀！你好像没设置OpenAI API Key。"
elif st.session_state["LANGUAGE"] == "English":
    file_uploader_string = "Upload PDF file, click 'Submit and Process'"
    submit_button_string = "Submit and Process"
    submit_button_spinner_string = "Waiting..."
    tab_translation_string = "Translation"
    tab_summarization_string = "Summarization"
    translate_button_string = "Translate"
    translate_button_spinner_string = "Translating..."
    summary_button_string = "Summary"
    summary_button_spinner_string = "Summarizing..."
    chat_input_string = "Ask something..."
    qa_warning_string = "Oops! If you want to test Q&A, set valid Pinecone API Key and submit PDF file first."
    openai_error_string = "Oops! It seems the OpenAI API Key is invalid."

# switch page
if "switch_page" not in st.session_state:
    st.session_state["switch_page"] = "ChatVideo"

# Setting initialization
if "OPENAI_API_KEY" not in st.session_state:
    st.session_state["OPENAI_API_KEY"] = ""
elif st.session_state["OPENAI_API_KEY"] != "":
    speech_to_text_llm = OpenAI(api_key=st.session_state["OPENAI_API_KEY"])  # speech-to-text model
    # openai_llm = LLM_OpenAI(api_key=st.session_state["OPENAI_API_KEY"])
    openai_llm = ChatOpenAI(openai_api_key=st.session_state["OPENAI_API_KEY"])
    embedding_model = OpenAIEmbeddings(openai_api_key=st.session_state["OPENAI_API_KEY"])

if "video_files" not in st.session_state:
    st.session_state["video_files"] = []
if "video_texts" not in st.session_state:
    st.session_state["video_texts"] = []
if "video_content_chunks" not in st.session_state:
    st.session_state["video_content_chunks"] = []

if "PINECONE_API_KEY" not in st.session_state:
    st.session_state["PINECONE_API_KEY"] = ""
if "PINECONE_ENVIRONMENT" not in st.session_state:
    st.session_state["PINECONE_ENVIRONMENT"] = ""

if "video_messages" not in st.session_state:
    st.session_state["video_messages"] = []

# if page switch, reset all video channel
if st.session_state["switch_page"] != "ChatVideo":
    st.session_state["video_files"] = []
    st.session_state["video_texts"] = []
    st.session_state["video_content_chunks"] = []
    st.session_state["video_messages"] = []

# Initialize texts and content_chunks Object
raw_transcript = st.session_state["video_texts"]
chunks_transcript = st.session_state["video_content_chunks"]

# TODO:main
if speech_to_text_llm and openai_llm:
    files = st.file_uploader(file_uploader_string,
                             accept_multiple_files=False)
    files_type = "Video"
    submit_button = st.button(submit_button_string)
    if submit_button:
        with st.spinner(submit_button_spinner_string):
            st.session_state["video_files"] = files
            # 1. get text from video
            raw_transcript = extract_text_from_video(speech_to_text_llm, files)
            st.session_state["video_texts"] = raw_transcript
            # 2. split text into chunks
            chunks_transcript = split_content_into_chunks(raw_transcript, files_type)
            st.session_state["video_content_chunks"] = chunks_transcript

    tab1, tab2 = st.tabs([tab_translation_string, tab_summarization_string])
    # Option 1: translation
    with tab1:
        if st.button(translate_button_string):
            with st.spinner(translate_button_spinner_string):
                translate_into_chinese(chunks_transcript, openai_llm, files_type)

    # Option 2: summarization
    with tab2:
        if st.button(summary_button_string):
            with st.spinner(summary_button_spinner_string):
                summary_from_texts(chunks_transcript, openai_llm, files_type)

    # Option 3: Q&A, ensure submit 1 doc 1 time
    if submit_button and st.session_state["PINECONE_API_KEY"] != "" and st.session_state["PINECONE_ENVIRONMENT"] != "":
        # Initialize and save chunks into vector store.
        namespace = "video"
        st.session_state["vector_store"] = save_chunks_into_vectorstore(chunks_transcript, embedding_model, namespace,
                                                                        files_type)

    if st.session_state["vector_store"]:

        for message in st.session_state["video_messages"]:
            if isinstance(message, HumanMessage):
                with st.chat_message("user"):
                    st.markdown(message.content)
            elif isinstance(message, AIMessage):
                with st.chat_message("assistant"):
                    st.markdown(message.content)

        prompt = st.chat_input(placeholder=chat_input_string)
        search_from_content(openai_llm, st.session_state["vector_store"], prompt, files_type)

    else:
        st.warning(qa_warning_string)

else:
    with st.container():
        st.error(openai_error_string)

st.session_state["switch_page"] = "ChatVideo"
