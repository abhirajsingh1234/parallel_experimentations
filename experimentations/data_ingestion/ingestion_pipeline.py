# data_ingestion/ingestion_pipeline.py

import os
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.chains import RetrievalQA

from models.embedding import open_ai_embed_model
from models.llm import open_ai_llm
from config.configuration import Config
from prompt_library.rag_sys_msg import rag_system_message

async def get_rag_chain(
    vectorstore_dir: str = "faiss_index",
    pdf_path: str = None,
    k: int = 5,
):
    pdf_path = pdf_path or Config.FILE_PATH
    print('step 1')

    if os.path.isdir(vectorstore_dir):
        vectorstore = FAISS.load_local(
            vectorstore_dir,
            open_ai_embed_model,
            allow_dangerous_deserialization=True,
        )
    else:
        loader = PyPDFLoader(pdf_path)
        docs = RecursiveCharacterTextSplitter(
            chunk_size=500, chunk_overlap=150, length_function=len
        ).split_documents(loader.load())

        vectorstore = FAISS.from_documents(docs, open_ai_embed_model)
        vectorstore.save_local(vectorstore_dir)

    retriever = vectorstore.as_retriever(search_kwargs={"k": k},use_semantic_ranker=True)

    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(rag_system_message.content),
        HumanMessagePromptTemplate.from_template("{question}")
    ])

    qa = RetrievalQA.from_chain_type(
        llm=open_ai_llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=False,
        chain_type_kwargs={
            "prompt": prompt,
            "document_variable_name": "retrieved_documents"
        },
    )

    return qa
