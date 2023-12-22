import streamlit as st

# Setting ChatVideo page
st.set_page_config(page_title="Help", layout="wide")
st.title("Help 💁")

if "LANGUAGE" not in st.session_state:
    st.session_state["LANGUAGE"] = "简体中文"


if st.session_state["LANGUAGE"] == "简体中文":
    st.markdown(
        """
        ### 使用说明
        #### 1. 当前摘要总结功能体验感较差的原因
        开发时采用的是免费的OpenAI API Key，官方限速每分钟至多调用三次，(RPM≤3)，因此程序选用循环分段总结。
        #### 2. 当前响应速度较慢的原因
        还是由于开发时RPM速度限制 😅，因此在每次调用OpenAI API后手动睡眠30秒。
        #### 3. Pinecone 向量数据库重复上传的原因
        还没有找到合适的方法解决。
        
        # 总而言之，理解万岁！ 🥹
        """
    )
elif st.session_state["LANGUAGE"] == "English":
    st.markdown(
        """
        ### Note
        #### 1. Reasons for the poor experience of the current summary function
        The development uses the free OpenAI API Key, the official speed limit of up to three calls per minute, (RPM ≤ 3), so the program was designed with a loop segmentation summary.
        #### 2. Reasons for current slow response times
        Still due to RPM speed limitations during development 😅, so manually sleep for 30 seconds after each OpenAI API call.
        #### 3. Reasons for duplicate uploads to the Pinecone vector database
        Haven't found a suitable solution yet.
        
        # All in all, hooray for understanding! 🥹
        """
    )