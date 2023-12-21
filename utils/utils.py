import time

from langchain.callbacks import get_openai_callback
from langchain.chains.question_answering import load_qa_chain
from langchain.chains.summarize import load_summarize_chain
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Pinecone
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain, LLMChain
import pinecone
import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import PromptTemplate

from PyPDF2 import PdfReader

import tempfile


def extract_text_from_PDF(files):
    # single PDF file
    if files is not None:
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(files.read())
            pdf_path = temp_file.name
            loader = PyPDFLoader(pdf_path)
            document = loader.load()
            return document

    # # 加载多个PDF文件
    # text = ""
    # for pdf in files:
    #     pdf_reader = PdfReader(pdf)
    #     for page in pdf_reader.pages:
    #         text += page.extract_text()
    # return text


def split_content_into_chunks(text, files_type):
    if files_type == "PDF":
        text_spliter = CharacterTextSplitter(separator="\n",
                                             chunk_size=1100,
                                             chunk_overlap=0)
        chunks = text_spliter.split_documents(text)
    elif files_type == "Video":
        text_spliter = CharacterTextSplitter(separator=" ",
                                             chunk_size=1100,
                                             chunk_overlap=0,
                                             length_function=len)
        chunks = text_spliter.split_text(text)

    chunks_num = len(chunks)
    st.markdown(f"""Your content has been split into {chunks_num} parts""")
    return chunks


def translate_into_chinese(chunks, llm, files_type):
    template = "请将下面的内容翻译中文：{chunks}"
    prompt = PromptTemplate(
        input_variables=["chunks"],
        template=template,
    )

    for i, split_pdf in enumerate(chunks):
        # there are too many \n in the original text
        if files_type == "PDF":
            cleaned_text = split_pdf.page_content
        elif files_type == "Video":
            cleaned_text = split_pdf

        with get_openai_callback() as cb:
            chain = LLMChain(llm=llm, prompt=prompt)
            translated_text = chain.run(cleaned_text)
            time.sleep(30)
            cleaned_text_label = "Original texts" + f'{i + 1}'
            translated_text_label = "Translated texts" + f'{i + 1}'
            st.markdown(f"""---Part.{i + 1}---\n""")
            with st.expander(cleaned_text_label):
                st.markdown(cleaned_text)
            with st.expander(translated_text_label):
                st.markdown(translated_text)


def summary_from_texts(chunks, llm, files_type):
    template = "总结以下内容,不要胡编乱造：{chunks}"
    prompt = PromptTemplate(
        input_variables=["chunks"],
        template=template,
    )

    # if len(chunks) <= 2:
    #     chain_type = "stuff"
    # else:
    #     chain_type = "map_reduce"

    # summary_chain = load_summarize_chain(llm=llm,
    #                                      chain_type=chain_type)
    # with get_openai_callback() as cb:
    #     summary_texts = summary_chain.run(chunks)
    #     st.markdown(f'{summary_texts}')
    #     time.sleep(30)

    # prevent reaching OpenAI API RPM, manually implementing the map_reduce method
    total_summarization = ""

    for i, text in enumerate(chunks):
        chain = LLMChain(llm=llm, prompt=prompt)
        if files_type == "PDF":
            original_text = text.page_content
        elif files_type == "Video":
            original_text = text

        summarization_text = chain.run(original_text)

        total_summarization = total_summarization + summarization_text
        before_text_label = "Original texts" + f'{i + 1}'
        summarization_text_label = "Summarization texts" + f'{i + 1}'
        st.markdown(f"""---Part.{i + 1}---\n""")

        with st.expander(before_text_label):
            st.markdown(original_text)
        with st.expander(summarization_text_label):
            st.markdown(summarization_text)
        time.sleep(30)

    chain = LLMChain(llm=llm, prompt=prompt)
    result = chain.run(total_summarization)
    with st.expander(f"""Final Summarization"""):
        st.markdown(result)


def save_chunks_into_vectorstore(content_chunks, embedding_model, namespace, files_type):
    # 初始化
    pinecone.init(api_key=st.session_state["PINECONE_API_KEY"],
                  environment=st.session_state["PINECONE_ENVIRONMENT"])
    # 创建索引
    index_name = "pinecone-chatbot-demo"
    # 检查索引是否存在，如果不存在，则创建
    if index_name not in pinecone.list_indexes():
        pinecone.create_index(name=index_name,
                              metric="cosine",
                              dimension=1536)
    if files_type == "PDF":
        vectorstore = Pinecone.from_documents(documents=content_chunks,
                                              embedding=embedding_model,
                                              index_name=index_name,
                                              namespace=namespace)
    elif files_type == "Video":
        vectorstore = Pinecone.from_texts(texts=content_chunks,
                                          embedding=embedding_model,
                                          index_name=index_name,
                                          namespace=namespace)
    return vectorstore


def search_from_content(llm, vectorstore, prompt, files_type):
    channel_name = None
    if prompt:
        qa_chain = load_qa_chain(llm=llm, chain_type="stuff")

        if files_type == "PDF":
            channel_name = "pdf_messages"
        elif files_type == "Video":
            channel_name = "video_messages"

        # process prompt, user message
        st.session_state[channel_name].append(HumanMessage(content=prompt))
        with st.chat_message("user"):
            st.markdown(prompt)

        # get response from OpenAI, its type is AImessage now.
        docs = vectorstore.similarity_search(prompt)
        ai_message = qa_chain.run(input_documents=docs, question=prompt)
        st.session_state[channel_name].append(AIMessage(content=ai_message))
        with st.chat_message("assistant"):
            st.markdown(ai_message)


def extract_text_from_video(llm, files):
    transcript = llm.audio.transcriptions.create(model="whisper-1",
                                                 file=files,
                                                 response_format="text")
    st.markdown(transcript)
    return transcript
