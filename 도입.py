import streamlit as st

# API KEY 정보로드
#load_dotenv()

# python -m streamlit run main.py
st.title("📚얘들아 물리 쉬워✨")


st.session_state.api_key = st.secrets["openai_api_key"]


## 학생에게 api-key를 입력하게 할 경우
## ------(아래 주석을 해제해주세요)------
# api_key = st.text_input("🔑 새로운 OPENAI API Key", type="password")
# save_btn = st.button("설정 저장", key="save_btn")

# if save_btn:
#    settings.save_config({"api_key": api_key})
#    st.session_state.api_key = api_key
#    st.write("설정이 저장되었습니다.")
## --------------------------------


# 처음 1번만 실행하기 위한 코드
if "messages" not in st.session_state:
    # 대화기록을 저장하기 위한 용도로 생성한다.
    st.session_state["messages"] = []

# 사이드바 생성
with st.sidebar:

    if st.secrets["openai_api_key"]:
        st.success(f'API키 세팅 완료: {st.secrets["openai_api_key"][-5:]}')


st.subheader("오늘 배운 물리 개념은?")

col1, col2 = st.columns(2)
cont = st.container(border=True)

with col1:
    st.image("https://blog.kakaocdn.net/dn/dve48V/btqzx7xvXtM/lVxQZ8s7bY86RSZeVoCzc1/img.jpg", caption="이 운동의 이름을 맞춰라!")

with col2:
    st.image("https://i0.wp.com/imagine.gsfc.nasa.gov/features/yba/CygX1_mass/gravity/images/circular_motion_animation.gif?resize=350%2C350&ssl=1", caption="인공위성도 이 운동을 합니다.")
    answer2 = st.radio("이 운동의 이름을 선택하세요", ["포물선 운동", "등속 원운동", "진자 운동"], key="answer2")
    if st.button("제출", key="btn2"):
        if answer2.strip().lower() == "등속 원운동":
            st.success("정답입니다!")
            st.balloons()
            with cont:
                st.markdown(
                    body="""
## 등속 원운동

운동 방향만 변하는 운동 놀이공원의 회전하는 관람차, 지구 주위를 도는 인공위성, 시계의 바늘 등은 일정한 속력으로 원을 그리며 운동하는데, 이러한 운동을 등속 원운동이라고 한다.
등속 원운동 하는 물체는 속력이 변하지 않고 운동 방향만 변한다. (교과서 16쪽)
"""
                )
        else:
            st.error("틀렸습니다. 다시 시도하세요.")


st.subheader("더 알아봅시다!")

# # 1. 탭 레이아웃 (수학 LaTeX, 유튜브, 데스모스 계산기)
# st.subheader("머리에 기름칠 하기")
with st.container(border=True):
#     st.text("아인슈타인은 머리가 복잡할 때 수학 문제를 풀면서 머리를 식혔다고 합니다.")
    tab1, tab2 = st.tabs(["읽어보면 좋은 글", "관련 유튜브 영상"])

    with tab1:
        st.write("아래 기사를 참고해보세요. (기사 제목 누르기👇)")
        st.page_link(page="https://blog.hyundai-rotem.co.kr/671", label="철도에 사용되는 과학기술: 고속 주행에도 안전한 커브는 OOO덕분?!", icon="📰")
        st.image("https://img1.daumcdn.net/thumb/R1280x0/?scode=mtistory2&fname=https%3A%2F%2Fblog.kakaocdn.net%2Fdn%2Fc4OysX%2FbtruRMLUUsC%2FI2IEaLfd8YNZzB9p6Apzs0%2Fimg.jpg")

#         # 문제와 정답을 미리 설정 (LaTeX 수식 포함)
#         problems = {
#             "문제 1": r"12 + 8 = ?",
#             "문제 2": r"25 \div 5 = ?",
#             "문제 3": r"3 \times 7 = ?",
#             "문제 4": r"2x-1=3의 해는?"
#         }

#         # 정답 설정
#         answers = {
#             "문제 1": 20,
#             "문제 2": 5,
#             "문제 3": 21,
#             "문제 4": 2
#         }


#         # 사용자가 문제를 선택할 수 있도록 selectbox 추가
#         selected_problem_key = st.selectbox("풀고 싶은 문제를 선택하세요", list(problems.keys()))
        
#         # 세션 상태에 선택한 문제와 정답 저장
#         if selected_problem_key != st.session_state.get('selected_problem_key'):
#             st.session_state['selected_problem_key'] = selected_problem_key
#             st.session_state['correct_answer'] = answers[selected_problem_key]

#         # 세션 상태에서 문제와 정답 가져오기
#         selected_problem = problems[st.session_state['selected_problem_key']]
#         correct_answer = st.session_state['correct_answer']

#         # 문제 출력 (LaTeX 형식으로 수식 출력)
#         st.latex(rf"{selected_problem}")  # 수식 출력

#         # 답을 입력받기
#         user_answer = st.text_input("답을 입력하세요")

#         # spinner와 제출 버튼 생성 및 채점
#         if st.button("제출"):
#             with st.spinner('채점 중...'):
#                 if user_answer:
#                     try:
#                         if int(user_answer) == correct_answer:
#                             st.success("정답입니다!")
#                             st.balloons()  # 정답을 맞추면 풍선이 나타남
#                             # 문제를 초기화하여 새로운 문제를 풀 수 있도록 함
#                             del st.session_state['selected_problem_key']
#                         else:
#                             st.error("틀렸습니다. 다시 시도해보세요.")
#                     except ValueError:
#                         st.error("숫자를 입력해주세요.")
#                 else:
#                     st.error("답을 입력해주세요.")

    with tab2:
        st.write("유튜브 영상으로 알아보는 오늘의 공부")
        st.video("https://youtu.be/FHrR_W4w_MA?feature=shared")
        # st.write("애니메이션으로 보는 시리즈(By Alan Becker)")
        # video = st.selectbox("강의 선택", ["애니메이션으로 보는 수학", "애니메이션으로 보는 물리학", "애니메이션으로 보는 기하학"])
        # if video == "애니메이션으로 보는 수학":
        #     st.video("https://www.youtube.com/watch?v=B1J6Ou4q8vE&list=PL7z8SQeih5Af9B2DshZul4KvTLI74NkUQ&index=1")
        # if video == "애니메이션으로 보는 물리학":
        #     st.video("https://youtu.be/ErMSHiQRnc8?list=PL7z8SQeih5Af9B2DshZul4KvTLI74NkUQ")
        # elif video == "애니메이션으로 보는 기하학":
        #     st.video("https://youtu.be/VEJWE6cpqw0?list=PL7z8SQeih5Af9B2DshZul4KvTLI74NkUQ")

    # with tab3:
    #     st.write("아래 계산기를 사용해보세요.")
    #     operation = st.selectbox("수학 연산 선택", ["과학용 계산기", "수학용 그래핑 계산기"])
    #     if operation == "과학용 계산기":
    #         st.components.v1.iframe("https://www.desmos.com/scientific", height=500)
    #     elif operation == "수학용 그래핑 계산기":
    #         st.components.v1.iframe("https://www.desmos.com/calculator", height=500)
