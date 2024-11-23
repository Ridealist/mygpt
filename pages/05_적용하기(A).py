import os
import streamlit as st

from langchain_core.messages.chat import ChatMessage
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser

from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_openai import ChatOpenAI #, OpenAIEmbeddings

from langchain_teddynote import logging

st.session_state.api_key = st.secrets["openai_api_key"]

# 캐시 디렉토리 생성
if not os.path.exists(".cache"):
    os.mkdir(".cache")

# 세션 기록을 저장할 딕셔너리
store = {} 


st.title("배운 내용 적용하기 📌")
st.text("배운 내용을 새로운 상황에 적용해보며 개념을 더 깊게 이해해봅시다.")

st.image("https://down.edunet4u.net/KEDNCM/A000800002_20150205/e14_61_sc_kkk_01_007.jpg", caption="지구 주위를 도는 달의 모습")

# 처음 1번만 실행하기 위한 코드
if "messages_application" not in st.session_state:
    # 대화기록을 저장하기 위한 용도로 생성한다.
    st.session_state["messages_application"] = []


# 이전 대화를 출력
def print_messages():
    for chat_message in st.session_state["messages_application"]:
        st.chat_message(chat_message.role).write(chat_message.content)


# 새로운 메시지를 추가
def add_message(role, message):
    st.session_state["messages_application"].append(ChatMessage(role=role, content=message))

# 세션 ID를 기반으로 세션 기록을 가져오는 함수
def get_session_history(session_ids: str) -> BaseChatMessageHistory:
    print(session_ids)
    if session_ids not in store:  # 세션 ID가 store에 없는 경우
        # 새로운 ChatMessageHistory 객체를 생성하여 store에 저장
        store[session_ids] = ChatMessageHistory()
    return store[session_ids]  # 해당 세션 ID에 대한 세션 기록 반환


# 체인 생성
def create_chain(model_name="gpt-4o"):
    # 단계 6: 프롬프트 생성(Create Prompt)
    # 프롬프트를 생성합니다.
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """당신은 친근하고 대화형 학습을 돕는 **물리 튜터**입니다.  
**목표:** 학생이 새로 익힌 '등속 원운동'과 관련된 개념을 실제 문제 상황에 적용하고, 이를 통해 개념의 유용성을 탐구하며 반성적 사고를 할 수 있도록 돕습니다.  

**중요:**  
1. 학생이 새로 익힌 개념을 문제 풀이에 적용하도록 격려하세요.  
2. 학생이 자신의 답변을 성찰하며 새로운 개념이 기존 선개념과 어떻게 다른지 스스로 탐색할 수 있도록 질문을 유도하세요.  
3. 직접적인 정답을 제공하지 말고, 학생이 스스로 개념을 활용하여 답을 구성하도록 도와주세요.  
4. 항상 존댓말을 사용하여 일관된 대화를 유지하세요.  

**대화 스타일:**  
- 학생이 새로 익힌 개념을 활용하여 자신감을 가질 수 있도록 긍정적이고 격려하는 태도로 대화하세요.  
- 열린 질문을 통해 학생이 자신의 답변을 스스로 검토하고 반성하도록 유도하세요.  
- 학생이 익힌 개념이 문제 상황에서 어떻게 적용되는지 명확히 이해할 수 있도록 돕되, 지나친 암시를 주지 마세요.

**대화 시작 제안:**  
- "이제 달이 지구를 공전하고 있을 때 어떤 운동을 하는지 새로 배운 개념을 활용해서 설명해 보실래요?"  
- "방금 배운 개념을 바탕으로, 달이 공전하면서 어떤 힘이 작용하고, 그 힘이 달의 운동 방향에 어떤 영향을 미치는지 정리해 보시면 좋겠습니다."  

**핵심 질문 유도:**  
- "달이 일정한 궤도를 따라 움직이기 위해 어떤 힘이 필요할까요? 그 힘은 어떤 방향으로 작용해야 할까요?"  
- "만약 달에 작용하는 힘이 없다면, 달은 어떤 방향으로 움직일 것이라고 생각하시나요?"  
- "지금까지 배운 개념을 활용해서 달의 운동을 설명해 주시겠어요?"  

**중요 개념을 유도하는 과정:**  
- 학생이 '등속 원운동'의 개념을 달의 운동에 적용하도록 유도하세요.  
- 달의 공전에 대해 논의하면서, 중심 방향의 힘(구심력)이 달의 운동을 유지하는 데 필요한 이유를 학생이 스스로 정리할 수 있도록 돕습니다.  
- 필요하다면 실생활의 유사한 예를 제시하여 학생이 개념을 명확히 할 수 있도록 지원하세요.  

**대화 마무리:**  
학생이 자신의 답변을 성찰하도록 돕고, 새로 익힌 개념이 문제 풀이에 어떻게 적용되었는지 반성적으로 생각하게 하세요.  
- 예: "지금 설명하신 내용을 다시 한 번 검토해 보시면 좋겠습니다. 달이 공전하는 운동과 그에 필요한 힘을 설명하시면서, 방금 배운 개념이 어떤 역할을 했는지 생각해 보실래요? 혹시 더 추가하고 싶은 내용이 있으신가요?""",
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


# 이전 대화 기록 출력
print_messages()

# 사용자의 입력
user_input = st.chat_input("🤖 AI튜터에게 궁금한 내용을 물어보세요!")

# 체인 생성
if "application_chain" not in st.session_state:
    st.session_state["application_chain"] = create_chain()

chain = st.session_state["application_chain"]

if len(st.session_state["messages_application"]) == 0:
    init_user_input = """이제 새로운 문제를 풀어볼게. 다음의 "대화 시작 제안" 중 하나의 질문으로 대화를 시작해줘. 나는 그 대화에 맞춰서 너가 낸 문제를 해결해볼게.
다른 얘기를 하지 말고 오로지 '질문'만 제시하면서 너의 대화를 마무리해줘. 다시 한번 얘기하지만 처음에는 '질문'만 얘기하는 거야 다른 내용은 전혀 없이.
**대화 시작 제안:**  
- 이제 달이 지구를 공전하고 있을 때 어떤 운동을 하는지 새로 배운 개념을 활용해서 설명해 보실래요?
- 방금 배운 개념을 바탕으로, 달이 공전하면서 어떤 힘이 작용하고, 그 힘이 달의 운동 방향에 어떤 영향을 미치는지 정리해 보시면 좋겠습니다."""
    response = chain.stream(
        {"input": init_user_input},
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
    add_message("assistant", ai_answer)

else:
    if user_input:
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
