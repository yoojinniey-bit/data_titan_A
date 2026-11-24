import streamlit as st
import pandas as pd
import plotly.express as px

# 가장 먼저 실행되는 st 명령으로 페이지 제목과 넓은 화면 설정
st.set_page_config(page_title="Titanic 대시보드", layout="wide")

# ===== 함수 =====
# 조건에 맞는 승객만 골라내는 함수
def filter_data(df, sexes, classes, age_range):
    f = df[df["sex"].isin(sexes) & df["pclass"].isin(classes)]  # [수정]
    if age_range != (0, 80):                                    # [수정]
        f = f[f["age"].between(*age_range)]                     # [수정]
    return f                                                    # [수정]

# 상단 핵심 지표 3개(승객 수, 생존율, 평균 나이) 계산 함수
def kpi(df):
    if len(df) == 0:
        return 0, 0, 0
    n = len(df)
    rate = round(df["survived"].mean() * 100, 1)
    age = round(df["age"].mean(), 1)
    return n, rate, age

# 객실 등급별 생존율(%) 막대그래프 함수
def class_rate_bar(df):
    r = (df.groupby("pclass")["survived"].mean().mul(100).round(1).reset_index())
    fig = px.bar(r, x="pclass", y="survived", text="survived", title="객실 등급별 생존율(%)")
    return fig

# 생존 여부별 나이 분포 히스토그램 함수
def age_hist(df):
    fig = px.histogram(df, x="age", color="survived", barmode="overlay", opacity=0.6, title="생존 여부별 나이 분포")
    return fig

# ===== 데이터 읽기 =====
# titanic.csv를 한 번만 읽고 캐시에 기억
@st.cache_data
def load_data():
    return pd.read_csv("titanic.csv")

df = load_data()

# ===== 제목 =====
st.title("타이타닉, 누가 살아남았나?")

# ===== 사이드바 =====
# 성별, 객실 등급(기본값 모두 선택), 나이 범위(0~80) 위젯 생성
sexes = st.sidebar.multiselect("성별", ["male", "female"], ["male", "female"])
classes = st.sidebar.multiselect("객실 등급", [1, 2, 3], [1, 2, 3])
ages = st.sidebar.slider("나이", 0, 80, (0, 80))

# ===== 본문 =====
# 조건 1: 성별이나 등급을 하나도 고르지 않으면 안내 후 멈춤
if not sexes or not classes:                                    # [수정]
    st.warning("성별과 등급을 하나 이상 선택하세요.")           # [수정]
    st.stop()                                                   # [수정]

# 필터 적용
f = filter_data(df, sexes, classes, ages)

# 조건 2: 필터 결과가 0명이면 안내 후 멈춤
if len(f) == 0:                                                 # [수정]
    st.warning("조건에 맞는 승객이 없습니다.")                  # [수정]
    st.stop()                                                   # [수정]

# KPI 숫자 카드 3개
n, rate, age = kpi(f)
c1, c2, c3 = st.columns(3)
c1.metric("승객 수", f"{n}명")
c2.metric("생존율", f"{rate}%")
c3.metric("평균 나이", f"{age}세")

# KPI 아래 2칸을 만들어 왼쪽에 등급별 생존율, 오른쪽에 나이 분포 차트 배치
left, right = st.columns(2)
left.plotly_chart(class_rate_bar(f))
right.plotly_chart(age_hist(f))

# 맨 아래 접었다 펼치는 영역 안에 필터된 데이터 표 표시
with st.expander("데이터 보기"):
    st.dataframe(f)
