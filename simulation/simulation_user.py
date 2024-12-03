# 시뮬레이션 코드
import uuid
import streamlit as st
import plotly.graph_objects as go
import numpy as np
import math
from datetime import datetime


# 버튼 key 초기화
if 'button1_key' not in st.session_state:
    button1_key = str(uuid.uuid4())[:8]
    st.session_state.button1_key = button1_key

if 'button2_key' not in st.session_state:
    button2_key = str(uuid.uuid4())[:8]
    st.session_state.button2_key = button2_key

if 'button3_key' not in st.session_state:
    button3_key = str(uuid.uuid4())[:8]
    st.session_state.button3_key = button3_key

if 'button4_key' not in st.session_state:
    button4_key = str(uuid.uuid4())[:8]
    st.session_state.button4_key = button4_key

# 버튼 key 초기화 함수
def initialize_button1_key():
    button1_key = str(uuid.uuid4())[:8]
    st.session_state.button1_key = button1_key

def initialize_button2_key():
    button2_key = str(uuid.uuid4())[:8]
    st.session_state.button2_key = button2_key

def initialize_button3_key():
    button3_key = str(uuid.uuid4())[:8]
    st.session_state.button3_key = button3_key

def initialize_button4_key():
    button4_key = str(uuid.uuid4())[:8]
    st.session_state.button4_key = button4_key


def init_simulation_state():
    if 'simulation_state' not in st.session_state:
        # 궤도 반지름 정의
        orbit_radius = 100
        
        # 중심점 계산
        center_x = 400  # width/2
        center_y = 300  # height/2
        
        # 초기 위치를 궤도 위 3시 방향으로 설정
        initial_x = center_x + orbit_radius
        initial_y = center_y
        
        # 초기 속도를 접선 방향(위쪽)으로 설정
        speed = 200
        initial_vx = 0
        initial_vy = -speed  # 접선 방향(위쪽)으로 속도 설정
        
        st.session_state.simulation_state = {
            'width': 800,
            'height': 600,
            'ball_mass': 1,
            'ball_radius': 10,
            'initial_speed': speed,
            'launch_angle': 0,
            'position': [initial_x, initial_y],  # 궤도 위 시작점
            'velocity': [initial_vx, initial_vy],  # 접선 방향 속도
            'trajectory_points': [],
            'force_vectors': [],
            'last_recorded_time': datetime.now(),
            'simulation_running': False,
            'show_velocity_vector': False,
            'show_force_vector': True,
            'show_acceleration_vector': False,  # 가속도 벡터 표시 추가
            'slow_motion_factor': 1.0  # 0.2에서 1.0으로 변경하여 5배 빠르게
        }

def calculate_force(position):
    target_position = [st.session_state.simulation_state['width']/2, 
                       st.session_state.simulation_state['height']/2]
    dx = target_position[0] - position[0]  # 목표 위치에서 현재 위치를 뺌
    dy = target_position[1] - position[1]
    distance = math.sqrt(dx ** 2 + dy ** 2)
    
    if distance == 0:
        return [0, 0]  # 중심에 있을 경우 힘이 0

    # 힘의 크기 조정: 거리의 제곱에 반비례
    force_magnitude = (st.session_state.simulation_state['ball_mass'] * 
                       (st.session_state.simulation_state['initial_speed'] ** 2)) / (distance ** 2 + 1e-6)  # 0으로 나누는 문제 방지
    force = [force_magnitude * dx / distance, force_magnitude * dy / distance]
    return force

def update_position(dt):
    state = st.session_state.simulation_state
    
    # 힘 계산
    force = calculate_force(state['position'])
    
    # 가속도 계산 (F = ma)
    acceleration = [f / state['ball_mass'] for f in force]
    
    # 속도 업데이트 (v = v0 + at)
    state['velocity'][0] += acceleration[0] * dt
    state['velocity'][1] += acceleration[1] * dt
    
    # 위치 업데이트 (x = x0 + vt)
    state['position'][0] += state['velocity'][0] * dt
    state['position'][1] += state['velocity'][1] * dt
    
    # 궤적 저장
    state['trajectory_points'].append(state['position'].copy())

def create_simulation_plot():
    state = st.session_state.simulation_state
    
    fig = go.Figure()
    
    # 원형 궤도 그리기
    theta = np.linspace(0, 2*np.pi, 100)
    center_x = state['width']/2
    center_y = state['height']/2
    radius = 100
    
    fig.add_trace(go.Scatter(
        x=center_x + radius * np.cos(theta),
        y=center_y + radius * np.sin(theta),
        mode='lines',
        line=dict(color='black', width=1),
        name='orbit'
    ))
    
    # 중심점 그리기
    fig.add_trace(go.Scatter(
        x=[center_x],
        y=[center_y],
        mode='markers',
        marker=dict(color='red', size=12),  # 크기 조정
        name='center'
    ))
    
    # 궤적 그리기
    if state['trajectory_points']:
        trajectory_x = [p[0] for p in state['trajectory_points']]
        trajectory_y = [p[1] for p in state['trajectory_points']]
        fig.add_trace(go.Scatter(
            x=trajectory_x,
            y=trajectory_y,
            mode='markers',
            marker=dict(color='lightgrey', size=2),
            name='trajectory'
        ))
    
    # 공 그리기
    fig.add_trace(go.Scatter(
        x=[state['position'][0]],
        y=[state['position'][1]],
        mode='markers',
        marker=dict(color='orange', size=20),  # 크기 조정
        name='ball'
    ))
    
    # 벡터 그리기
    vector_ratio = 0.1  # 벡터의 길이를 상대적으로 줄임
    if state['show_velocity_vector']:
        velocity_end = [
            state['position'][0] + state['velocity'][0] * vector_ratio,
            state['position'][1] + state['velocity'][1] * vector_ratio
        ]
        fig.add_trace(go.Scatter(
            x=[state['position'][0], velocity_end[0]],
            y=[state['position'][1], velocity_end[1]],
            mode='lines',
            line=dict(color='blue', width=3),  # 두께 조정
            name='velocity'
        ))
    
    if state['show_force_vector']:
        force = calculate_force(state['position'])
        force_end = [
            state['position'][0] + force[0] * vector_ratio,
            state['position'][1] + force[1] * vector_ratio
        ]
        fig.add_trace(go.Scatter(
            x=[state['position'][0], force_end[0]],
            y=[state['position'][1], force_end[1]],
            mode='lines',
            line=dict(color='green', width=3, dash='dot'),  # 두께 조정 및 점선 유지
            name='force'
        ))
    
    if state['show_acceleration_vector']:  # 가속도 벡터 표시 추가
        force = calculate_force(state['position'])
        acceleration = [f/state['ball_mass'] for f in force]
        acceleration_end = [
            state['position'][0] + acceleration[0] * vector_ratio,
            state['position'][1] + acceleration[1] * vector_ratio
        ]
        fig.add_trace(go.Scatter(
            x=[state['position'][0], acceleration_end[0]],
            y=[state['position'][1], acceleration_end[1]],
            mode='lines',
            line=dict(color='purple', width=3, dash='dash'),  # 두께 조정 및 점선으로 표시
            name='acceleration'
        ))
    
    fig.update_layout(
        width=800,
        height=600,
        showlegend=False,
        xaxis=dict(
            range=[0, state['width']],
            scaleanchor="y",
            scaleratio=1,
        ),
        yaxis=dict(
            range=[0, state['height']],
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        plot_bgcolor='white',
    )
    
    return fig

def main():
    st.subheader("원운동 시뮬레이션")
    
    # 초기화
    init_simulation_state()
    
    # 컨트롤 버튼들
    col1, col2, col3, col4, col5 = st.columns(5)  # 컬럼 수 변경
    with col1:
        try:
            button1 = st.button("시뮬레이션 시작/정지", key=st.session_state.button1_key)
        except:
            initialize_button1_key()
            button1 = st.button("시뮬레이션 시작/정지", key=st.session_state.button1_key)

        if button1:
            st.session_state.simulation_state['simulation_running'] = \
                not st.session_state.simulation_state['simulation_running']
    
    with col2:
        try:
            button2 = st.button("다시 재생", key=st.session_state.button2_key)
        except:
            initialize_button2_key()
            button2 = st.button("다시 재생", key=st.session_state.button2_key)
        
        if button2:
            st.session_state.simulation_state['position'] = [500, 300]  # 중심에서 오른쪽으로 100
            st.session_state.simulation_state['velocity'] = [0, -200]   # 위쪽 방향으로 초기 속도
            st.session_state.simulation_state['trajectory_points'] = []
            st.session_state.simulation_state['force_vectors'] = []
            st.session_state.simulation_state['simulation_running'] = False
    
    with col3:
        try:
            button3 = st.button("속도 벡터 표시", key=st.session_state.button3_key)
        except:
            initialize_button3_key()
            button3 = st.button("속도 벡터 표시", key=st.session_state.button3_key)

        if button3:
            st.session_state.simulation_state['show_velocity_vector'] = \
                not st.session_state.simulation_state['show_velocity_vector']

    with col4:
        try:
            button4 = st.button("힘 벡터 표시", key=st.session_state.button4_key)
        except:
            initialize_button4_key()
            button4 = st.button("힘 벡터 표시", key=st.session_state.button4_key)
        
        if button4:
            st.session_state.simulation_state['show_force_vector'] = \
                not st.session_state.simulation_state['show_force_vector']
    
    with col5:  # 새로운 버튼 컬럼 추가
        try:
            button5 = st.button("가속도 벡터 표시", key='acceleration_vector')
        except:
            button5 = st.button("가속도 벡터 표시", key='acceleration_vector')
        
        if button5:
            st.session_state.simulation_state['show_acceleration_vector'] = \
                not st.session_state.simulation_state['show_acceleration_vector']
    
    # 시뮬레이션 실행
    if st.session_state.simulation_state['simulation_running']:
        update_position(1/60 * st.session_state.simulation_state['slow_motion_factor'])
    
    # 플롯을 고정된 크기의 컨테이너에 표시
    plot_container = st.container()
    with plot_container:
        fig = create_simulation_plot()
        st.plotly_chart(fig, use_container_width=False)
    
    # 60fps로 업데이트
    st.empty()
    st.rerun()

    main()