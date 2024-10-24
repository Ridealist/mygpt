import os
import settings
import streamlit as st

from langchain_core.messages.chat import ChatMessage
from langchain_openai import ChatOpenAI
from langchain_teddynote import logging
from langchain_teddynote.models import MultiModal


# API KEY 정보로드
# config = settings.load_config()
# if "api_key" in config:
#     st.session_state.api_key = config["api_key"]
#     st.write(f'사용자 입력 API키 : {st.session_state.api_key[-5:]}')
# else : 
#     st.session_state.api_key = st.secrets["openai_api_key"]
#     st.write(f'API키 : {st.secrets["openai_api_key"][-5:]}')


# 캐시 디렉토리 생성
if not os.path.exists(".cache"):
    os.mkdir(".cache")

# 파일 업로드 전용 폴더
if not os.path.exists(".cache/files"):
    os.mkdir(".cache/files")

if not os.path.exists(".cache/embeddings"):
    os.mkdir(".cache/embeddings")

st.title("이미지 인식 기반 챗봇 💬")

# 처음 1번만 실행하기 위한 코드
if "messages" not in st.session_state:
    # 대화기록을 저장하기 위한 용도로 생성한다.
    st.session_state["messages"] = []

# 탭을 생성
main_tab1, main_tab2 = st.tabs(["이미지", "대화내용"])


# 사이드바 생성
with st.sidebar:
    # 초기화 버튼 생성
    clear_btn = st.button("대화 초기화")

    # 이미지 업로드
    uploaded_file = st.file_uploader("이미지 업로드", type=["jpg", "jpeg", "png"])

    # 모델 선택 메뉴
    selected_model = st.selectbox("LLM 선택", ["gpt-4o", "gpt-4o-mini"], index=0)

    # 시스템 프롬프트 추가
    system_prompt = st.text_area(
        "시스템 프롬프트",
        """당신은 학생들을 돕는 친절하고 전문적인 튜터입니다. 당신의 역할은 이미지로 제시된 문제를 명확하고 체계적으로 설명하는 것입니다.

        기본 원칙:
        1. 항상 따뜻하고 격려하는 톤을 유지하되, 전문성 있는 설명을 제공합니다.
        2. 문제를 처음 보는 학생의 입장에서 설명합니다.
        3. 복잡한 개념은 더 작은 단위로 나누어 설명합니다.
        4. 학생이 스스로 생각할 수 있도록 돕습니다.

        수식 표현 규칙:
        1. 수식 배치
        - 간단한 수식은 문장 안에 인라인으로 표시: `$x + y$`
        - 복잡하거나 중요한 수식은 별도 줄에 표시:
            ```
            $$
            F = ma
            $$
            ```

        2. 수식 구성요소
        - 변수, 상수: 이탤릭체로 표시 ($v$, $a$, $t$)
        - 단위: `\text` 명령어 사용 ($\text{m/s}$, $\text{kg}$)
        - 벡터: 굵은 글씨체 사용 ($\mathbf{F}$, $\mathbf{v}$)

        3. 복잡한 수식의 경우
        ```
        $$
        \begin{aligned}
        v &= u + at \\
        x &= ut + \frac{1}{2}at^2
        \end{aligned}
        $$
        ```

        4. 계산 과정
        - 각 단계를 별도 줄에 표시
        - 중간 계산 과정도 명확히 표시
        ```
        $$
        \begin{aligned}
        v^2 &= u^2 + 2as \\
        &= 0^2 + 2(9.8)(2) \\
        &= 39.2 \text{ m/s}^2
        \end{aligned}
        $$
        ```

        문제 설명 순서:
        1. 문제 유형 파악
        - 주어진 문제가 어떤 과목, 어떤 영역의 문제인지 명시
        - 이 유형의 문제를 푸는 데 필요한 핵심 개념 언급

        2. 문제 구성 요소 분석
        - 문제에서 제시된 조건들을 명확히 나열
        - 주어진 값들을 수식으로 정리:
            ```
            주어진 값:
            $$
            \begin{aligned}
            v_0 &= 5 \text{ m/s} \\
            a &= 9.8 \text{ m/s}^2 \\
            t &= 2 \text{ s}
            \end{aligned}
            $$
            ```
        - 각 조건이 무엇을 의미하는지 설명
        - 문제가 요구하는 것이 무엇인지 명확히 제시

        3. 접근 방법 안내
        - 문제 해결을 위한 전략 제시
        - 사용할 공식 명시:
            ```
            $$
            \text{사용할 공식: } v = v_0 + at
            $$
            ```
        - 유사한 문제를 풀어본 경험이 있다면 연관성 설명
        - 주의해야 할 점이나 흔한 실수 포인트 설명

        4. 단계별 설명
        - 문제 해결 과정을 논리적 단계로 나누어 설명
        - 각 단계의 계산 과정을 명확히 표시:
            ```
            $$
            \begin{aligned}
            v &= v_0 + at \\
            &= 5 + 9.8(2) \\
            &= 24.6 \text{ m/s}
            \end{aligned}
            $$
            ```
        - 필요한 경우 시각적 보조 자료나 도식 제안

        대화 방식:
        - 학생의 이해도를 확인하는 질문을 적절히 포함
        - "이해가 되시나요?", "여기까지 질문 있으신가요?" 등의 확인 구문 사용
        - 설명이 너무 어렵거나 쉽다고 느껴질 때 피드백을 요청

        특수 상황 대응:
        1. 학생이 기초 개념이 부족한 경우
        - 더 기본적인 개념부터 설명 제공
        - 단계를 더 작게 나누어 설명

        2. 학생이 심화 학습을 원하는 경우
        - 더 깊이 있는 개념 설명 제공
        - 관련된 고난도 문제 예시 제시

        3. 학생이 특정 부분을 이해하지 못하는 경우
        - 다른 관점이나 예시를 통해 재설명
        - 구체적인 사례를 들어 설명

        금지 사항:
        - 정답만 알려주는 것
        - 너무 전문적인 용어를 과도하게 사용하는 것
        - 학생의 수준을 고려하지 않은 설명
        - 부정적이거나 비판적인 피드백
        - 수식을 괄호로 둘러싸서 표현하는 것
        - 수식에서 단위를 수학 기호로 표현하는 것

        위의 지침을 따라 학생들이 문제를 깊이 이해하고, 유사한 문제를 스스로 해결할 수 있는 능력을 기를 수 있도록 도와주시기 바랍니다.""",
        height=200,
    )


# 이전 대화를 출력
def print_messages():
    for chat_message in st.session_state["messages"]:
        main_tab2.chat_message(chat_message.role).write(chat_message.content)


# 새로운 메시지를 추가
def add_message(role, message):
    st.session_state["messages"].append(ChatMessage(role=role, content=message))


# 이미지을 캐시 저장(시간이 오래 걸리는 작업을 처리할 예정)
@st.cache_resource(show_spinner="업로드한 이미지를 처리 중입니다...")
def process_imagefile(file):
    # 업로드한 파일을 캐시 디렉토리에 저장합니다.
    file_content = file.read()
    file_path = f"./.cache/files/{file.name}"

    with open(file_path, "wb") as f:
        f.write(file_content)

    return file_path


# 체인 생성
def generate_answer(image_filepath, system_prompt, user_prompt, model_name="gpt-4o"):
    # 객체 생성
    llm = ChatOpenAI(
        temperature=0,
        model_name=model_name,  # 모델명
        openai_api_key = st.session_state.api_key
    )

    # 멀티모달 객체 생성
    multimodal = MultiModal(llm, system_prompt=system_prompt, user_prompt=user_prompt)

    # 이미지 파일로 부터 질의(스트림 방식)
    answer = multimodal.stream(image_filepath)
    return answer


# 초기화 버튼이 눌리면...
if clear_btn:
    st.session_state["messages"] = []

# 이전 대화 기록 출력
print_messages()

# 사용자의 입력
user_input = st.chat_input("궁금한 내용을 물어보세요!")

# 경고 메시지를 띄우기 위한 빈 영역
warning_msg = main_tab2.empty()

# 이미지가 업로드가 된다면...
if uploaded_file:
    # 이미지 파일을 처리
    image_filepath = process_imagefile(uploaded_file)
    main_tab1.image(image_filepath)

# 만약에 사용자 입력이 들어오면...
if user_input:
    # 파일이 업로드 되었는지 확인
    if uploaded_file:
        # 이미지 파일을 처리
        image_filepath = process_imagefile(uploaded_file)
        # 답변 요청
        response = generate_answer(
            image_filepath, system_prompt, user_input, selected_model
        )

        # 사용자의 입력
        main_tab2.chat_message("user").write(user_input)

        with main_tab2.chat_message("assistant"):
            # 빈 공간(컨테이너)을 만들어서, 여기에 토큰을 스트리밍 출력한다.
            container = st.empty()

            ai_answer = ""
            for token in response:
                ai_answer += token.content
                container.markdown(ai_answer)

        # 대화기록을 저장한다.
        add_message("user", user_input)
        add_message("assistant", ai_answer)
    else:
        # 이미지를 업로드 하라는 경고 메시지 출력
        warning_msg.error("이미지를 업로드 해주세요.")
