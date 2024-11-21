import streamlit as st

st.title("물리 시뮬레이션 실험실 🧪")

main_tab1 = st.container(border=True)
main_tab1.text("문제 상황")
main_tab1.image("images/simulation_1.png")

operation = st.selectbox("시뮬레이션 사이트 선택", ["자바 실험실", "PhET"])
if operation == "자바 실험실":
    st.components.v1.iframe("https://javalab.org/condition_of_circular_movement/", height=800, width=1000)
elif operation == "PhET":
    st.components.v1.iframe("https://phet.colorado.edu/sims/html/gravity-and-orbits/latest/gravity-and-orbits_all.html?locale=ko", height=800, width=1000)

