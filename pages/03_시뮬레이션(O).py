import re
import os
import streamlit as st
from typing import List

from langchain_core.messages.chat import ChatMessage
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory

from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI

import simulation.simulation as simulation


st.session_state.api_key = st.secrets["openai_api_key"]

os.environ["LANGCHAIN_TRACING_V2"] = st.secrets["LANGCHAIN_TRACING_V2"]
os.environ["LANGCHAIN_API_KEY"] = st.secrets["LANGCHAIN_API_KEY"]
os.environ["LANGCHAIN_ENDPOINT"] = st.secrets["LANGCHAIN_ENDPOINT"]
os.environ["LANGCHAIN_PROJECT"] = st.secrets["LANGCHAIN_PROJECT"]

if "submit_button_disabled" not in st.session_state:
    st.session_state["submit_button_disabled"] = True

if "tutor_messages" not in st.session_state:
    # 대화기록을 저장하기 위한 용도로 생성한다.
    st.session_state["tutor_messages"] = []


def enalble_submit_button():
    st.session_state["submit_button_disabled"] = False

def disalble_submit_button():
    st.session_state["submit_button_disabled"] = True


def output_parser(response: str) -> str:
    content = re.search(r'```python\n(.*?)\n```', response, re.DOTALL)

    if content:
        extracted_code = content.group(1)
        print(extracted_code)
        return extracted_code
    else:
        print("No Python code block found.")
        return None

class InMemoryHistory(BaseChatMessageHistory, BaseModel):
    """In memory implementation of chat message history."""

    messages: List[BaseMessage] = Field(default_factory=list)

    def add_messages(self, messages: List[BaseMessage]) -> None:
        """Add a list of messages to the store"""
        self.messages.extend(messages)

    def clear(self) -> None:
        self.messages = []

store = {}

def get_by_session_id(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = InMemoryHistory()
    return store[session_id]

st.title("시뮬레이션 실험실 🧪")
st.text("다양하게 시뮬레이션을 해보고 관찰한 사실에 대해 적어봅시다.")

main_tab1 = st.container(border=True)
main_tab1.subheader("문제 상황")
main_tab1.image("images/simulation_1.png")

# 모델 선택 메뉴
selected_model = "gpt-4o-mini" # st.selectbox("LLM 선택", ["gpt-4o", "gpt-4o-mini"], index=0)

# 시스템 프롬프트 추가
system_prompt = """당신은 친근하고 대화형 학습을 돕는 **물리 튜터**입니다.  
**목표:** 학생이 '등속 원운동'에서 물체에 작용하는 힘의 방향과 크기에 따른 물체의 운동 변화를 관찰하고, 이를 객관적으로 기록하도록 돕습니다. 학생이 정확한 관찰을 통해 자신의 추론을 검증할 수 있도록 지원하세요.  
**중요:**  
1. 절대로 '등속 원운동'에서 힘의 방향이나 크기에 대한 결론을 직접 알려주지 마세요.  
   - 학생이 시뮬레이션을 통해 스스로 결과를 관찰하고 해석하도록 도와주세요.  
   - 학생이 관찰을 서술하는 과정에서 편견 없이 기록하도록 유도하세요.  
2. 항상 **존댓말**로 대화하세요. 친절하고 격려하는 태도를 유지하며 학생이 부담 없이 실험과 기록을 진행하도록 돕습니다.  
3. **답변 길이 제약:** 각 응답은 **2문장**을 넘지 않도록 간결하고 명확하게 작성하세요.

**설명 전략:**  
1. 시뮬레이션 상황(운동 방향과 힘의 각도를 조정하면서 결과를 관찰)을 학생이 명확히 이해할 수 있도록 안내하세요.  
2. 학생이 힘의 방향과 크기를 조정하면서 관찰한 결과를 글로 서술하도록 지도하세요.  
3. 학생의 관찰이 정확하고 객관적인지 확인하며, 필요하면 추가 질문으로 관찰을 심화하도록 도와주세요.

**대화 시작 제안:**  
- "현재 시뮬레이션에서 힘과 운동 방향의 각도를 변경해보세요. 어떤 변화가 발생하는지 관찰하고 기록해볼까요?"  
- "힘의 방향을 바꿔보았을 때 물체의 운동 궤적에 어떤 변화가 생기는지 정확히 관찰해 보세요."  

**핵심 질문 유도:**  
- "힘의 방향과 물체의 운동 궤도 사이에 어떤 관계가 있다고 생각하시나요?"  
- "만약 힘의 방향이 운동 방향과 나란하다면 어떤 궤적이 나타날까요? 그렇지 않을 때는 어떻게 될까요?"  
- "등속 원운동이 유지되기 위해 힘의 방향이 어떻게 설정되어야 한다고 관찰되었나요?"  

**중요 개념을 유도하는 과정:**  
- 학생이 관찰을 통해 등속 원운동의 조건(힘의 방향과 운동 궤도)을 스스로 도출하도록 유도하세요.  
- 관찰 기록의 세부 사항(운동 궤적, 힘의 크기, 힘과 속도의 각도 등)을 강조하며 정확히 서술하도록 돕습니다.  
- 시뮬레이션 데이터와 실제 물리적 원리가 어떻게 연결되는지 질문을 통해 설명하도록 안내하세요.

**금지된 대화 예시:**  
- "힘은 원의 중심 방향으로 작용해야 궤도가 유지됩니다."  
- "등속 원운동에서는 힘과 속도의 관계가 이렇게 됩니다."  

**대화 마무리:**  
학생이 관찰한 내용을 자신의 말로 정리하도록 유도하세요.  
- 예: "그럼 지금까지 관찰한 내용을 정리해볼까요? 힘의 방향과 크기에 따라 물체의 운동이 어떻게 변화했는지, 그리고 등속 원운동을 유지하기 위해 힘이 어떻게 작용해야 한다고 생각하셨는지 설명해 주세요."""


# 체인 생성
def generate_chain(model_name="gpt-4o-mini"):
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}"),
    ])

    # 객체 생성
    llm = ChatOpenAI(
        temperature=0,
        model_name=model_name,
        openai_api_key = st.session_state.api_key
    )
    chain = prompt | llm
    chain_with_history = RunnableWithMessageHistory(
        chain,
        # Uses the get_by_session_id function defined in the example
        # above.
        get_by_session_id,
        input_messages_key="input",
        history_messages_key="history",
    )

    return chain_with_history


# 사이드바 생성
with st.sidebar:
    # 초기화 버튼 생성
    st.text("AI튜터와 대화하기")
    messages = st.container(height=300)
        
    def print_messages():
        for chat_message in st.session_state["tutor_messages"]:
           messages.chat_message(chat_message.role).write(chat_message.content)

    # 새로운 메시지를 추가
    def add_message(role, message):
        st.session_state["tutor_messages"].append(ChatMessage(role=role, content=message))

    # 이전 대화 기록 출력
    print_messages()

    if user_input := st.chat_input("🤖 AI튜터에게 궁금한 내용을 물어보세요!"):

        conv_chain = generate_chain(selected_model)

        # 사용자의 입력
        messages.chat_message("user").write(user_input)

        with messages.chat_message("assistant"):
            # 빈 공간(컨테이너)을 만들어서, 여기에 토큰을 스트리밍 출력한다.
            container = st.empty()
            generator = conv_chain.stream(
                {"input": user_input},
                config={"configurable": {"session_id": "ab12"}}
            )
            ai_answer = ""
            for token in generator:
                ai_answer += token.content
                container.markdown(ai_answer)

        # 대화기록을 저장한다.
        add_message("user", user_input)
        add_message("assistant", ai_answer)

    facts = st.text_area(
        label="관찰한 사실을 자세히 적어보세요.",
        placeholder="- 변수 조작에 따라 움직임이 달라진 점\n- 예측했던 것과 관찰한 결과가 다른점",
        height=200,
        on_change=enalble_submit_button
    )

    if not facts:
        disalble_submit_button()

    submit_button = st.button(
        label="제출하기",
        type="primary",
        use_container_width=True,
        disabled=st.session_state["submit_button_disabled"]
    )

    if submit_button:
        st.session_state["observation_user_facts"] = facts
        st.success("제출 완료!")


st.subheader("시뮬레이션 실험")
operation = st.selectbox("시뮬레이션 사이트 선택", ["자바실험실", "PhET", "자율실험실"])
if operation == "자바실험실":
    st.components.v1.iframe("https://javalab.org/condition_of_circular_movement/", height=800, width=1000)
elif operation == "PhET":
    st.components.v1.iframe("https://phet.colorado.edu/sims/html/gravity-and-orbits/latest/gravity-and-orbits_all.html?locale=ko", height=800, width=1000)
elif operation == "자율실험실":
    st.title("자율실험실")
    
    # 초기 시스템 메시지 설정
    system_prompt = """당신은 물리 시뮬레이션 전문가입니다. 
    당신의 역할은 다음과 같습니다:
    1. simulation.py 파일의 시뮬레이션 코드를 기반으로 작업합니다.
    2. 학생의 요구사항을 분석하여 시뮬레이션 코드를 적절히 수정합니다.
    3. 수정된 코드를 'simulation_user.py' 파일로 저장합니다.
    4. 수정 사항에 대해 명확히 설명합니다.

    코드 수정 시 다음 사항을 준수하세요:
    - 기본 물리법칙을 준수하는 현실적인 시뮬레이션을 구현하세요
    - 코드는 실행 가능해야 하며 오류가 없어야 합니다
    - 학생이 이해할 수 있도록 주요 변경사항을 설명하세요

    응답 형식:
    1. 수정된 내용 설명
    2. 수정된 코드 전체
    """

    if "simulation_messages" not in st.session_state:
        st.session_state.simulation_messages = [
            SystemMessage(content=system_prompt)
        ]

    # 원본 코드 읽기
    with open('simulation/simulation.py', 'r', encoding='utf-8') as file:
        original_code = file.read()
        if "original_code" not in st.session_state:
            st.session_state.original_code = original_code
    file.close()

    # 챗봇 설정
    chat = ChatOpenAI(
        model_name="gpt-4o",
        temperature=0,
        openai_api_key=st.secrets["openai_api_key"]
    )

    simulation_container = st.container()
    with simulation_container:
        # 사용자 입력
        user_input = st.text_input(
            label="시뮬레이션을 어떻게 수정하고 싶은지 설명해주세요",
            key="user_input"
        )

        if button := st.button("수정하기", type="primary", key="modify_button"):
            # 원본 코드와 함께 사용자 입력 전달
            full_prompt = f"원본 코드:\n{st.session_state.original_code}\n\n사용자 요청: {user_input}"
            st.session_state.simulation_messages.append(HumanMessage(content=full_prompt))

            # handle_input(user_input)
            with st.spinner("시뮬레이션 코드 수정 중..."):
                response = chat(st.session_state.simulation_messages)
                res_parsed = output_parser(response.content)

                try:
                    # 수정된 코드를 파일로 저장
                    with open('simulation_user.py', 'w', encoding='utf-8') as file:
                        file.write(res_parsed)
                    
                    # 수정된 코드 import 및 실행
                    import importlib.util
                    spec = importlib.util.spec_from_file_location("simulation_user", "simulation_user.py")
                    simulation_module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(simulation_module)
                    
                    # 시뮬레이션 실행
                    simulation_module.main()
                    
                except Exception as e:
                    print(e)
                    st.error(f"코드 실행 중 오류가 발생했습니다: {str(e)}")
                    # 오류 발생 시 원본 시뮬레이션으로 복귀
                    simulation.main()
                
                st.session_state.simulation_messages.append(AIMessage(content=response.content))

        else:
            # 기본 시뮬레이션 실행
            simulation.main()
            # import simulation_user as simul
            # simul.main()

