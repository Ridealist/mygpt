import os
import sys
import streamlit as st
import re
import getpass
from langchain_openai import ChatOpenAI
# from langchain_anthropic import ChatAnthropic

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.globals import set_verbose
import time
import importlib

set_verbose(False)

st.session_state.api_key = st.secrets["openai_api_key"]

# 초기 세션 상태 설정
if 'button_timestamp' not in st.session_state:
    st.session_state.button_timestamp = time.time()
if 'last_input' not in st.session_state:
    st.session_state.last_input = ''

st.title("물리 시뮬레이션 실험실 🧪")

main_tab1 = st.container(border=True)
main_tab1.text("문제 상황")
main_tab1.image("images/simulation_1.png")

operation = st.selectbox("시뮬레이션 사이트 선택", ["자바 실험실", "PhET", "자율실험실"])
if operation == "자바 실험실":
    # CSS 스타일 적용
    st.markdown("""
        <style>
        /* iframe 컨테이너 스타일링 */
        .iframe-container {
            width: 700px;
            height: 600px;
            overflow: hidden;
            position: relative;
        }
        
        /* iframe 자체 스타일링 */
        .iframe-container iframe {
            width: 720px;  /* 스크롤바 여유 공간 */
            height: 800px;
            border: none;
            position: absolute;
            top: -250px;  /* 상단 여백 조절 */
            left: 0;
            margin: 0;
            padding: 0;
        }
        </style>
    """, unsafe_allow_html=True)

    # HTML div로 감싸서 iframe 생성
    st.markdown("""
        <div class="iframe-container">
            <iframe 
                src="https://javalab.org/condition_of_circular_movement/"
                scrolling="no"
                frameborder="0"
            ></iframe>
        </div>
    """, unsafe_allow_html=True)
elif operation == "PhET":
    st.components.v1.iframe("https://phet.colorado.edu/sims/html/gravity-and-orbits/latest/gravity-and-orbits_all.html?locale=ko", height=800, width=1000)
elif operation == "자율실험실":
    st.title("자율실험실")
    
    # 챗봇 설정
    #chat = ChatAnthropic(model="claude-3-5-sonnet-20240620")
    chat = ChatOpenAI(model="gpt-4o-mini", api_key=st.session_state.api_key)

    # 시뮬레이션 수정중에는 화면 보이지 않게 스위치
    fixingNow = False
    afterFixing = False

    # 원본 코드 읽기 
    if "original_code" not in st.session_state:
        if os.path.exists('./simulation/simulation_user.py') and st.session_state.last_input:
            with open('./simulation/simulation_user.py', 'r', encoding='utf-8') as file:
                st.session_state.original_code = file.read()
        else:
            with open('./simulation/simulation.py', 'r', encoding='utf-8') as file:
                st.session_state.original_code = file.read()
        st.session_state.current_code = st.session_state.original_code
    
    # 수정된 시뮬레이션이 있는 경우
    if os.path.exists('./simulation/simulation_user.py') and st.session_state.last_input:
        st.info("🔄 수정된 시뮬레이션이 실행 중입니다")
        
        # 원본으로 돌아가기 버튼
        if st.button("원본 시뮬레이션으로 돌아가기"):
            if 'simulation_user' in sys.modules:
                del sys.modules['simulation_user']
            os.remove('./simulation/simulation_user.py')
            st.session_state.current_code = st.session_state.original_code
            st.session_state.last_input = ''
            st.rerun()
        
        # 사용자 입력 받기
        user_input = st.text_input("시뮬레이션을 어떻게 더 수정하고 싶은지 설명해주세요")
        
        # 사용자가 입력한 경우
        if user_input and user_input != st.session_state.get('last_input', ''):
            fixingNow = True
            st.session_state.last_input = user_input
            
            with st.spinner("AI가 시뮬레이션을 수정하고 있습니다..."):
                # AI 응답 받기
                full_prompt = f"""
현재 시뮬레이션 코드를 분석하고, 사용자의 요청에 따라 수정해주세요.
코드는 Python과 Streamlit을 사용하는 물리 시뮬레이션입니다.

현재 코드:
{st.session_state.current_code}

사용자 요청: "{user_input}"

다음 사항들을 고려하여 수정해주세요:
1. 시뮬레이션의 물리적 특성 (속도, 힘, 궤도 등)
2. 시각적 요소 (색상, 크기, 벡터 표시 등)

응답 형식:
1. 수정이 필요한 함수나 클래스의 전체 코드를 ```python ``` 블록 안에 작성하세요
2. 여러 함수를 수정할 경우 각각 별도의 코드 블록으로 작성하세요
3. 수정된 부분에 대한 설명을 추가해주세요
"""
                response = chat.invoke([HumanMessage(content=full_prompt)])
                
                try:
                    # AI 응답 처리 및 코드 수정
                    modified_section = response.content
                    code_pattern = r'```python\n(.*?)```'
                    code_matches = re.findall(code_pattern, modified_section, re.DOTALL)
                    
                    if code_matches:
                        modified_code = st.session_state.current_code
                        
                        for code_block in code_matches:
                            match = re.search(r'(def|class)\s+(\w+)', code_block)
                            if match:
                                target_name = match.group(2)
                                pattern = rf'(def|class)\s+{target_name}[^\n]*\n(?:(?!def|class).*\n)*'
                                modified_code = re.sub(pattern, code_block + '\n', modified_code)
                        
                        # 수정된 코드 저장
                        with open('./simulation/simulation_user.py', 'w', encoding='utf-8') as file:
                            file.write(modified_code)
                        
                        st.session_state.current_code = modified_code
                        fixingNow = False
                        st.rerun()
                    else:
                        st.error("AI 응답에서 코드 블록을 찾을 수 없습니다.")
                        
                except Exception as e:
                    st.error(f"코드 수정 중 오류가 발생했습니다: {str(e)}")
        
        # 수정된 시뮬레이션 실행
        max_attempts = 5  # 최대 수정 시도 횟수 (AI가 코드를 잘못 수정해서 재수정하는 최대 횟수)
        attempt = 0
        success = False
        
        while not success and attempt < max_attempts:
            try:
                if 'simulation_user' in sys.modules:
                    del sys.modules['simulation_user']
                from simulation_user import main
                main()
                fixingNow = False
                # 시뮬레이션 실행 전 컨테이너 초기화
                success = True  # 성공적으로 실행됨
                
            except Exception as e:
                attempt += 1
                error_msg = str(e)
                st.error(f"시뮬레이션 실행 중 오류가 발생했습니다 (시도 {attempt}/{max_attempts}): {error_msg}")
                
                if attempt < max_attempts:  # 마지막 시도가 아닌 경우에만 수정 시도
                    with st.spinner(f"AI가 오류를 분석하고 코드를 수정하고 있습니다... (시도 {attempt}/{max_attempts})"):
                        error_prompt = f"""
이전에 수정한 시뮬레이션 코드에서 오류가 발생했습니다.
오류 내용: {error_msg}

현재 코드:
{st.session_state.current_code}

다음 사항들을 고려하여 수정해주세요:
1. 시뮬레이션의 물리적 특성 (속도, 힘, 위치 등)
2. 시각적 요소 (색상, 크기, 벡터 표시 등)

응답 형식:
1. 수정이 필요한 함수나 클래스의 전체 코드를 ```python ``` 블록 안에 작성하세요
2. 여러 함수를 수정할 경우 각각 별도의 코드 블록으로 작성하세요
3. 수정된 부분에 대한 설명을 추가해주세요
"""
                        response = chat.invoke([HumanMessage(content=error_prompt)])
                        
                        try:
                            # AI 응답 처리 및 코드 수정
                            modified_section = response.content
                            code_pattern = r'```python\n(.*?)```'
                            code_matches = re.findall(code_pattern, modified_section, re.DOTALL)
                            
                            if code_matches:
                                modified_code = st.session_state.current_code
                                
                                for code_block in code_matches:
                                    match = re.search(r'(def|class)\s+(\w+)', code_block)
                                    if match:
                                        target_name = match.group(2)
                                        pattern = rf'(def|class)\s+{target_name}[^\n]*\n(?:(?!def|class).*\n)*'
                                        modified_code = re.sub(pattern, code_block + '\n', modified_code)
                                        
                                # 수정된 코드 저장
                                with open('./simulation/simulation_user.py', 'w', encoding='utf-8') as file:
                                    file.write(modified_code)
                                
                                st.session_state.current_code = modified_code
                                st.rerun()

                            else:
                                st.error("AI 응답에서 코드 블록을 찾을 수 없습니다.")
                                break
                                
                        except Exception as e:
                            st.error(f"코드 수정 중 오류가 발생했습니다: {str(e)}")
                            break
                else:
                    st.error("최대 시도 횟수를 초과했습니다. 수정에 실패했습니다.")
    
    # 기본 시뮬레이션 실행 중인 경우
    else:
        st.success("✨ 기본 시뮬레이션이 실행 중입니다", icon="✅")
        user_input = st.text_input("시뮬레이션을 어떻게 수정하고 싶은지 설명해주세요")
        
        # 사용자의 답변을 반영한 시뮬레이션 보기 버튼 추가
        if st.button("'문제'에서 답한 내용을 반영한 시뮬레이션 보기"):
            if "predict_user_reason" in st.session_state and "predict_user_drawing" in st.session_state:
                user_input_already = f"""
    사용자의 설명: {st.session_state['predict_user_reason']}
    사용자의 그림 설명: {st.session_state['predict_user_drawing']}

    위 내용을 바탕으로 시뮬레이션을 수정해주세요.
    """
                user_input = user_input_already
                
            else:
                st.warning("먼저 '문제' 페이지에서 답변을 입력해주세요.")
                
        # 기본 시뮬레이션 실행
        if not user_input and not fixingNow:
            from simulation.simulation import main
            main()
        
        # 사용자가 입력한 경우
        if user_input and user_input != st.session_state.get('last_input', ''):
            st.session_state.last_input = user_input
            fixingNow = True
            with st.spinner("AI가 시뮬레이션을 수정하고 있습니다..."):
                # AI 응답 받기
                full_prompt = f"""
현재 시뮬레이션 코드를 분석하고, 사용자의 요청에 따라 수정해주세요.
코드는 Python과 Streamlit을 사용하는 물리 시뮬레이션입니다.

현재 코드:
{st.session_state.current_code}

사용자 요청: "{user_input}"

다음 사항들을 고려하여 수정해주세요:
1. 시뮬레이션의 물리적 특성 (속도, 힘, 궤도 등)
2. 시각적 요소 (색상, 크기, 벡터 표시 등)

응답 형식:
1. 수정이 필요한 함수나 클래스의 전체 코드를 ```python ``` 블록 안에 작성하세요
2. 여러 함수를 수정할 경우 각각 별도의 코드 블록으로 작성하세요
3. 수정된 부분에 대한 설명을 추가해주세요
"""
                response = chat.invoke([HumanMessage(content=full_prompt)])
                
                try:
                    # AI 응답 처리 및 코드 수정
                    modified_section = response.content
                    code_pattern = r'```python\n(.*?)```'
                    code_matches = re.findall(code_pattern, modified_section, re.DOTALL)
                    
                    if code_matches:
                        modified_code = st.session_state.current_code
                        
                        for code_block in code_matches:
                            match = re.search(r'(def|class)\s+(\w+)', code_block)
                            if match:
                                target_name = match.group(2)
                                pattern = rf'(def|class)\s+{target_name}[^\n]*\n(?:(?!def|class).*\n)*'
                                modified_code = re.sub(pattern, code_block + '\n', modified_code)
                        
                        # 수정된 코드 저장
                        with open('./simulation/simulation_user.py', 'w', encoding='utf-8') as file:
                            file.write(modified_code)
                        
                        st.session_state.current_code = modified_code
                        fixingNow = False
                        st.rerun()
                    else:
                        st.error("AI 응답에서 코드 블록을 찾을 수 없습니다.")
                        
                except Exception as e:
                    st.error(f"코드 수정 중 오류가 발생했습니다: {str(e)}")
        