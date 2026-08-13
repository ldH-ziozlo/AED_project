import math

import pandas as pd
import numpy as np
import geopandas as gpd
import matplotlib.pyplot as plt
import streamlit as st
from config import AED_FILE, RESULT_DIR, ACCESS_DISTANCES
import matplotlib.font_manager as fm

font_path = "/usr/share/fonts/truetype/nanum/NanumGothic.ttf"
fm.fontManager.addfont(font_path)
plt.rcParams["font.family"] = "NanumGothic"
plt.rcParams["axes.unicode_minus"] = False

st.set_page_config(page_title='AED 접근성 분석', layout='wide')

st.title('AED 접근성 기반 배치 취약지역 분석')

st.header('분석 해석 시 고려사항')

st.info(
    """
    AED 접근거리는 100m 인구격자의 대표 위치에서
    가장 가까운 AED까지의 직선거리를 기준으로 계산합니다.

    따라서 실제 보행거리, 도로망, 횡단보도, 건물 출입구,
    AED 운영시간 등의 요소는 반영되지 않았습니다.

    추가 설치 우선 검토지역은 실제 설치 위치를 확정하는 결과가 아니라,
    공간적 접근성과 인구 특성을 종합하여
    추가 검토가 필요한 지역을 탐색하기 위한 지표입니다.
    """
)

NATIONAL_FILE = RESULT_DIR / '전국_집계구별_AED_접근성.gpkg'

SEOUL_FILE = RESULT_DIR / '서울_집계구별_AED_접근성.gpkg'

DONG_FILE = RESULT_DIR / '서울_행정동별_AED_접근성.gpkg'

DISTRICT_FILE = RESULT_DIR / '서울_자치구별_AED_접근성.gpkg'


required_files = [NATIONAL_FILE, SEOUL_FILE, DONG_FILE, DISTRICT_FILE]


for file in required_files:

    if not file.exists():

        st.error('분석 결과가 없습니다. 먼저 build_analysis.py를 실행해주세요.')

        st.code('uv run python build_analysis.py')

        st.stop()


@st.cache_resource
def load_geo(path):

    return gpd.read_file(path)


@st.cache_data
def load_aed():

    encodings = ['utf-8-sig', 'utf-8', 'cp949', 'euc-kr']

    for encoding in encodings:

        try:

            return pd.read_csv(AED_FILE, encoding=encoding)

        except UnicodeDecodeError:

            continue

    raise ValueError('AED CSV 파일을 읽을 수 없습니다.')


national = load_geo(NATIONAL_FILE)

seoul = load_geo(SEOUL_FILE)

dong = load_geo(DONG_FILE)

district = load_geo(DISTRICT_FILE)

aed = load_aed()



def add_labels(
    ax,
    gdf,
    name_column,
    fontsize=7,
):

    temp = gdf.dropna(subset=[name_column]).copy()


    if temp.empty:

        return


    temp['label_point'] = temp.geometry.representative_point()


    for _, row in temp.iterrows():

        point = row['label_point']

        ax.text(point.x, point.y, str(row[name_column]),
            ha="center",va="center", fontsize = fontsize, fontweight = "bold", zorder = 10,
            bbox={"facecolor" : "white", "alpha" : 0.50, "edgecolor" : "none", "pad" : 0.8,},
        )

def draw_access_map(data, rate_column, label_column, title,):

    map_data = data[data[rate_column].notna()].copy()

    if map_data.empty:

        return None

    raw_min = map_data[rate_column].min()

    color_min = math.floor(raw_min / 10) * 10

    color_min = max(0, color_min)

    fig, ax = plt.subplots(figsize=(6.5, 6))

    map_data.plot(column = rate_column, cmap="cividis", legend=True, ax=ax, edgecolor="white", linewidth=0.6,
        vmin=color_min, vmax=100, legend_kwds={"label" : "AED 접근률 (%)", "shrink" : 0.65,},
    )


    add_labels(ax=ax, gdf=map_data, name_column=label_column, fontsize=7 if label_column == '시군구명' else 6.5)

    ax.set_title(title, fontsize=12)

    ax.axis('off')

    plt.tight_layout()

    return fig

def draw_access_bar(data, rate_column, name_column, title,):

    chart = data[[name_column, rate_column]].dropna().copy()

    cividis_yellow = plt.get_cmap("cividis")(0.85)

    chart = chart.sort_values(rate_column, ascending=True)

    if chart.empty:

        return None

    if len(chart) > 15:

        chart = chart.head(15)

    min_rate = chart[rate_column].min()

    axis_min = math.floor(min_rate / 10) * 10

    axis_min = max(0, axis_min)

    fig, ax = plt.subplots(figsize=(6.5, 5.2))
    ax.barh(chart[name_column], chart[rate_column], color=cividis_yellow)

    ax.set_xlim(axis_min, 100)

    ax.set_xlabel('접근률 (%)')

    ax.set_title(title, fontsize=12)

    ax.grid(axis='x', alpha=0.2)

    plt.tight_layout()

    return fig



def draw_priority_map(data, label_column, title,):

    map_data = data[data['우선검토점수'].notna()].copy()

    if map_data.empty:

        return None

    raw_min = map_data['우선검토점수'].min()

    color_min = math.floor(raw_min / 10) * 10

    color_min = max(0, color_min)

    fig, ax = plt.subplots(figsize=(6.5, 6))

    map_data.plot(column="우선검토점수", cmap="cividis_r", legend=True, ax=ax, edgecolor="white", linewidth=0.6,
        vmin=color_min, vmax=100, legend_kwds={"label" : "우선검토점수", "shrink" : 0.65,},
    )


    add_labels(ax=ax, gdf=map_data, name_column=label_column, fontsize=7 if label_column == '시군구명' else 6.5)

    ax.set_title(title, fontsize=12)

    ax.axis('off')

    plt.tight_layout()

    return fig

def draw_priority_bar(data, name_column, title, top_n):

    score_cols = ["접근성취약점수", "미접근인구점수", "인구점수", "고령인구점수",]

    score_labels = ["접근 취약성", "미접근 인구", "전체 인구", "고령 인구",]

    available_cols = [col for col in score_cols if col in data.columns]

    if not available_cols:
        return None

    chart = data[[name_column, "우선검토점수"] + available_cols].dropna(subset=[name_column, "우선검토점수"]).copy()

    chart = (chart.sort_values("우선검토점수", ascending=False).head(top_n).sort_values("우선검토점수", ascending=True))

    if chart.empty:

        return None
    
    weight = 100 / len(available_cols)

    contribution_cols = []

    for col in available_cols:
        contribution_col = f"{col}_기여도"
        chart[contribution_col] = chart[col] * weight
        contribution_cols.append(contribution_col)

    fig, ax = plt.subplots(figsize=(7.5, 6))

    left = np.zeros(len(chart))

    cmap = plt.get_cmap("cividis_r")

    colors = np.linspace(0.15, 0.9, len(available_cols))

    for col, label, color_value in zip(contribution_cols,[score_labels[score_cols.index(col.replace("_기여도", ""))] for col in contribution_cols], colors,):

        values = chart[col].to_numpy()

        ax.barh(chart[name_column], values, left=left, label=label, color=cmap(color_value),)

        left += values

    
    for i, score in enumerate(chart["우선검토점수"]):
        ax.text(score + 0.8, i, f"{score:.1f}", va="center", fontsize=8,)

    ax.set_xlim(0, 100)

    ax.set_xlabel("우선검토점수")

    ax.set_title(title, fontsize=12)

    ax.legend(title="평가요소", bbox_to_anchor=(1.02, 1), loc="upper left",)

    ax.grid(axis="x", alpha=0.2)

    plt.tight_layout()

    return fig

st.sidebar.header('분석 설정')

distance = st.sidebar.radio('AED 접근거리', ACCESS_DISTANCES, index=2, horizontal=True)

rate_col = f'{distance}m_접근률'

access_col = f'접근{distance}m_인구'

unaccess_col = f'{distance}m_미접근인구'

district_list = district['시군구명'].dropna().sort_values().unique().tolist()

selected_district = st.sidebar.selectbox('서울 자치구', ['서울 전체'] + district_list)

valid_seoul = seoul[seoul['격자인구'] > 0].copy()

if selected_district == "서울 전체":

    view = valid_seoul.copy()

    access_map_data = district.copy()

    access_label_col = '시군구명'

else:

    view = valid_seoul[valid_seoul['시군구명'] == selected_district].copy()

    access_map_data = dong[dong['시군구명'] == selected_district].copy()

    access_label_col = '행정동명'

st.divider()

st.header('1. 서울 AED 현황')

st.caption(f'현재 선택 기준: {selected_district} · AED {distance}m')

total_population = view['격자인구'].sum()

access_population = view[access_col].sum()

unaccess_population = view[unaccess_col].sum()

if total_population > 0:

    access_rate = access_population / total_population * 100

else:

    access_rate = np.nan

elderly_population = view['65세이상인구'].sum()

valid_distance = view[view['평균_AED거리'].notna() & (view['격자인구'] > 0)].copy()

if not valid_distance.empty:

    average_distance = np.average(valid_distance['평균_AED거리'], weights=valid_distance['격자인구'])

else:

    average_distance = np.nan

if selected_district == "서울 전체":

    aed_count = district['AED대수'].sum()

    unique_aed_count = district['AED고유설치지점수'].sum()

else:

    current_district = district[district['시군구명'] == selected_district]

    aed_count = current_district['AED대수'].sum()

    unique_aed_count = current_district['AED고유설치지점수'].sum()


k1, k2, k3, k4 = st.columns(4)
k5, k6, k7 = st.columns(3)

k1.metric('분석대상 인구', f'{total_population:,.0f}명')

k2.metric(f'{distance}m 접근 가능 인구', f'{access_population:,.0f}명')

k3.metric(f'{distance}m 접근률', f'{access_rate:.1f}%' if pd.notna(access_rate) else '-')

k4.metric(f'{distance}m 미접근 인구', f'{unaccess_population:,.0f}명')

k5.metric('AED 설치 대수', f'{aed_count:,.0f}대')

k6.metric('고유 AED 설치지점', f'{unique_aed_count:,.0f}곳')

k7.metric('평균 최근접 AED 거리', f'{average_distance:.0f}m' if pd.notna(average_distance) else '-')

st.divider()

st.header('2. 서울 AED 접근성')

left_col, right_col = st.columns([1, 1], gap='medium')

with left_col:

    access_map_fig = draw_access_map(data=access_map_data, rate_column=rate_col, label_column=access_label_col,
        title=(f"{selected_district} " f"AED {distance}m 접근률"),
    )

    if access_map_fig is not None:

        st.pyplot(access_map_fig, use_container_width=True)

with right_col:

    if selected_district == "서울 전체":

        access_bar_data = district.copy()

        access_bar_name = '시군구명'

        access_bar_title = f'자치구별 AED {distance}m 접근률'

    else:

        access_bar_data = dong[dong['시군구명'] == selected_district].copy()

        access_bar_name = '행정동명'

        access_bar_title = f'{selected_district} 행정동별 AED {distance}m 접근률'

    access_bar_fig = draw_access_bar(data=access_bar_data, rate_column=rate_col, name_column=access_bar_name, title=access_bar_title)

    if access_bar_fig is not None:

        st.pyplot(access_bar_fig, use_container_width=True)


st.divider()

st.metric('65세 이상 인구', f'{elderly_population:,.0f}명')

st.divider()

st.header('3. AED 추가 설치 우선 검토지역')

if selected_district == "서울 전체":

    priority_map_data = district.copy()

    priority_map_label = '시군구명'

    priority_bar_data = dong.copy()

    priority_bar_name = '지역명'

    priority_top_n = 20

else:

    priority_map_data = dong[dong['시군구명'] == selected_district].copy()

    priority_map_label = '행정동명'

    priority_bar_data = priority_map_data.copy()

    priority_bar_name = '행정동명'

    priority_top_n = 10

priority_left, priority_right = st.columns([1, 1], gap='medium')

with priority_left:

    priority_map_fig = draw_priority_map(
        data=priority_map_data,
        label_column=priority_map_label,
        title=(f"{selected_district} " "AED 설치 우선 검토점수"),)

    if priority_map_fig is not None:

        st.pyplot(priority_map_fig, use_container_width=True)

with priority_right:

    priority_bar_fig = draw_priority_bar(
        data=priority_bar_data,
        name_column=priority_bar_name,
        title=(
            f"AED 추가 설치 우선 TOP {priority_top_n}"
        ),
        top_n=priority_top_n,
    )

    if priority_bar_fig is not None:

        st.pyplot(priority_bar_fig, use_container_width=True)

st.divider()

st.header('4. 분석 결과 해석')

current_access_rank = access_bar_data[[access_bar_name, rate_col]].dropna().sort_values(rate_col, ascending=True)

current_priority_rank = priority_bar_data[[priority_bar_name, '우선검토점수']].dropna().sort_values('우선검토점수', ascending=False)

if (
    not current_access_rank.empty
    and
    not current_priority_rank.empty
):

    lowest_region = current_access_rank.iloc[0]

    priority_region = current_priority_rank.iloc[0]

    st.info(
        f"""
        현재 {distance}m 기준 접근률이 가장 낮은 지역은
        {lowest_region[access_bar_name]}
        ({lowest_region[rate_col]:.1f}%)입니다.

        종합적인 AED 추가 설치 우선검토점수가 가장 높은 지역은
        {priority_region[priority_bar_name]}
        ({priority_region["우선검토점수"]:.1f}점)입니다.

        접근률만 낮은 지역과 실제 추가 설치 우선지역은
        인구 규모와 65세 이상 인구를 함께 고려하기 때문에
        서로 다르게 나타날 수 있습니다.
        """
    )

st.divider()
