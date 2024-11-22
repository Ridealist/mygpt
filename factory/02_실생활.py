import os
import streamlit as st

from langchain_core.messages.chat import ChatMessage
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser


from langchain_community.chat_message_histories import ChatMessageHistory
# from langchain_text_splitters import RecursiveCharacterTextSplitter
# from langchain_community.document_loaders import PDFPlumberLoader
# from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI #, OpenAIEmbeddings

from langchain_teddynote.prompts import load_prompt
from langchain_teddynote import logging

st.session_state.api_key = st.secrets["openai_api_key"]

# 캐시 디렉토리 생성
if not os.path.exists(".cache"):
    os.mkdir(".cache")

# 세션 기록을 저장할 딕셔너리
store = {} 


st.title("교과서 챗봇과 함께 QA💬")
st.text("교과서에서 오늘 배울 내용과 관련 있는 내용을 검색해보세요.")


# 처음 1번만 실행하기 위한 코드
if "messages" not in st.session_state:
    # 대화기록을 저장하기 위한 용도로 생성한다.
    st.session_state["messages"] = []


# 사이드바 생성
with st.sidebar:
    # 초기화 버튼 생성
    clear_btn = st.button("대화 초기화")


# 이전 대화를 출력
def print_messages():
    for chat_message in st.session_state["messages"]:
        st.chat_message(chat_message.role).write(chat_message.content)


# 새로운 메시지를 추가
def add_message(role, message):
    st.session_state["messages"].append(ChatMessage(role=role, content=message))

# 세션 ID를 기반으로 세션 기록을 가져오는 함수
def get_session_history(session_ids: str) -> BaseChatMessageHistory:
    print(session_ids)
    if session_ids not in store:  # 세션 ID가 store에 없는 경우
        # 새로운 ChatMessageHistory 객체를 생성하여 store에 저장
        store[session_ids] = ChatMessageHistory()
    return store[session_ids]  # 해당 세션 ID에 대한 세션 기록 반환

# # 파일을 캐시 저장(시간이 오래 걸리는 작업을 처리할 예정)
# @st.cache_resource(show_spinner="업로드한 파일을 처리 중입니다...")
# def embed_file(file):
#     # 업로드한 파일을 캐시 디렉토리에 저장합니다.
#     file_content = file.read()
#     file_path = f"./.cache/files/{file.name}"
#     with open(file_path, "wb") as f:
#         f.write(file_content)

#     # 단계 1: 문서 로드(Load Documents)
#     loader = PDFPlumberLoader(file_path)
#     docs = loader.load()

#     # 단계 2: 문서 분할(Split Documents)
#     text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=50)
#     split_documents = text_splitter.split_documents(docs)

#     # 단계 3: 임베딩(Embedding) 생성
#     embeddings = OpenAIEmbeddings(model="text-embedding-3-small", openai_api_key = st.session_state.api_key)

#     # 단계 4: DB 생성(Create DB) 및 저장
#     # 벡터스토어를 생성합니다.
#     vectorstore = FAISS.from_documents(documents=split_documents, embedding=embeddings)

#     # 단계 5: 검색기(Retriever) 생성
#     # 문서에 포함되어 있는 정보를 검색하고 생성합니다.
#     retriever = vectorstore.as_retriever()
#     return retriever


# 체인 생성
def create_chain(model_name="gpt-4o"):
    # 단계 6: 프롬프트 생성(Create Prompt)
    # 프롬프트를 생성합니다.
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """당신은 친근하고 대화형 학습을 돕는 **물리 튜터**입니다.
**목표:** 학생이 '등속 원운동'의 개념과 '중심 방향으로 작용하는 힘(구심력)'의 필요성을 이해하도록 돕는 것입니다.  
 
1. 실생활에서 원운동과 관련된 예시를 학생에게 떠올리게 하세요.  
2. 원운동을 유지하는 데 필요한 조건에 대해 자연스럽게 질문하고, 학생이 스스로 탐구하도록 유도하세요.  
3. '구심력'이 원운동의 필수 조건임을 이해하도록 대화를 이끌어주세요.  
 
**대화 스타일:**  
- 학생의 호기심을 자극하는 열린 질문을 활용하세요.  
- 학생의 답변을 격려하고, 부족한 부분은 추가 질문으로 보완하세요.  
- 복잡한 개념을 간단히 설명하되, 학생이 스스로 발견하도록 기회를 주세요.  
 
**대화 시작 제안:**  
- "빙글빙글 돌아가는 놀이기구 타봤어? 몸이 어떻게 느껴졌어?"  
- "자동차가 곡선 도로를 돌 때 몸이 어느 쪽으로 쏠리던가?"  
- "공을 끈에 매달고 돌릴 때, 끈이 없다면 공은 어떻게 될까?"  
 
**핵심 질문 유도:**  
- "왜 몸이 바깥쪽으로 쏠리는 느낌이 들까?"  
- "끈이 없으면 공이 계속 원운동을 할 수 있을까? 왜 그럴까?"  
- "만약 끈이 당기지 않는다면 공은 어떻게 움직일까?"  
 
**핵심 개념 설명 유도:**  
- 원운동에서 속도의 방향은 계속 바뀌며, 이는 가속도(구심 가속도)가 발생함을 의미함.  
- 구심 가속도를 만들어주는 힘(구심력)이 원의 중심 방향으로 작용해야 함.  
- 구심력이 없으면 물체는 직선 방향(등속 직선 운동)으로 움직이려 함.  
 
**대화 마무리:**  
학생이 자신만의 말로 '등속 원운동을 유지하려면 중심 방향의 힘이 필요하다'는 개념을 정리하도록 도와주세요.  
- 예: "그럼 네 말로 정리해보자. 공이 원운동을 하려면 어떤 힘이 필요하고, 그 힘은 어디로 작용해야 할까?""",
            ),
            # 대화 기록을 변수로 사용, history 가 MessageHistory 의 key 가 됨
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}"),  # 사용자 입력을 변수로 사용
        ]
    )

    # 단계 7: 언어모델(LLM) 생성
    # 모델(LLM) 을 생성합니다.
    llm = ChatOpenAI(model_name=model_name, temperature=0, openai_api_key = st.session_state.api_key)
    
    # 단계 8: 체인(Chain) 생성
    with_message_history = (
        RunnableWithMessageHistory(  # RunnableWithMessageHistory 객체 생성
            prompt | llm,
            get_session_history,  # 세션 기록을 가져오는 함수
            input_messages_key="input",  # 입력 메시지의 키
            history_messages_key="history",  # 기록 메시지의 키
        )
    )
    chain = with_message_history | StrOutputParser()

    return chain


# 초기화 버튼이 눌리면...
if clear_btn:
    st.session_state["messages"] = []


# 이전 대화 기록 출력
print_messages()

# 사용자의 입력
user_input = st.chat_input("궁금한 내용을 물어보세요!")

# 경고 메시지를 띄우기 위한 빈 영역
warning_msg = st.empty()


# 체인 생성
st.session_state["chain"] = create_chain()

if user_input:
    chain = st.session_state["chain"]

    if chain is not None:
        # 사용자의 입력
        st.chat_message("user").write(user_input)
        # 스트리밍 호출
        response = chain.stream(
            {"input": user_input},
            # 설정 정보로 세션 ID "abc123"을 전달합니다.
            config={"configurable": {"session_id": "abc123"}},
        )
        with st.chat_message("assistant"):
            # 빈 공간(컨테이너)을 만들어서, 여기에 토큰을 스트리밍 출력한다.
            container = st.empty()

            ai_answer = ""
            for token in response:
                ai_answer += token
                container.markdown(ai_answer)

        # 대화기록을 저장한다.
        add_message("user", user_input)
        add_message("assistant", ai_answer)
