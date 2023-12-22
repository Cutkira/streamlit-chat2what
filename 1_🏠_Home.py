import streamlit as st

# Homepage with no any feature
st.set_page_config(page_title="Home", layout="wide")
st.title("Welcome 🏠")

if "LANGUAGE" not in st.session_state:
    st.session_state["LANGUAGE"] = "简体中文"
    language_index = 0
elif st.session_state["LANGUAGE"]:
    if st.session_state["LANGUAGE"] == "简体中文":
        language_index = 0
    elif st.session_state["LANGUAGE"] == "English":
        language_index = 1

st.session_state["LANGUAGE"] = st.radio("语言 / Language",
                                        ["简体中文", "English"],
                                        index=language_index,
                                        horizontal=True)

if "switch_page" not in st.session_state:
    st.session_state["switch_page"] = "Home"

if st.session_state["LANGUAGE"] == "简体中文":
    st.markdown(
        """
        ### 欢迎，这里是基于Streamlit前端，OpenAI和Pinecone为后端搭建的课程设计。
        #### 你能够...
        - 解析PDF，翻译PDF文字，对PDF内容总结，提问。
        - 解析视频，得到视频文字稿，对视频内容进行总结，提问。
        - 和ChatGPT聊天。
        #### 你需要...
        - 准备魔法节点，最好设置全局，tun模式。（非必须，取决于你的网络环境）
        - 准备OpenAI API Key。
        - 准备Pinecone API Key。（如果你需要用到Q&A功能）
        #### 如果你...
        - 碰到BUG，理解万岁！
        - 有二次开发的想法，请到GitHub链接中下载源码！
        #### 开源链接
        https://github.com/Cutkira/streamlit-chat2what.git
        """
    )
elif st.session_state["LANGUAGE"] == "English":
    st.markdown(
        """
        ### Welcome, here's a course design based on Streamlit built as the front-end and OpenAI and Pinecone built as the back-end.
        #### You can...
        - Parsing PDF files, translating PDF text, summarizing PDF content, asking questions.
        - Parse the video content, get a transcript of the video, summarize the video content, ask questions.
        - Chat with ChatGPT.
        #### You need...
        - Set VPN if necessary, better turn on global and tun mode.
        - Prepare OpenAI API.
        - Prepare Pinecone API, if you need to use the Q&A feature.
        #### If you...
        - Run into bugs, long live understanding.
        - Have any ideas for secondary development, go to the GitHub link and download the source code!
        #### Open Source Link
        https://github.com/Cutkira/streamlit-chat2what.git
        """
    )

st.session_state["switch_page"] = "Home"
