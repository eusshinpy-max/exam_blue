import streamlit as st
from supabase import create_client, Client
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os

# 저장소에 포함된 한글 폰트 로드
font_path = "./NanumGothic.ttf"  # GitHub repo에 업로드한 폰트 파일
fontprop = fm.FontProperties(fname=font_path)

# Replace with placeholder values or actual values for testing purposes
# In a real application, use environment variables or a secure configuration method
url: str = os.environ.get("SUPABASE_URL", "https://aiengbpxyemtwxytpuks.supabase.co") # Replace with your Supabase URL
key: str = os.environ.get("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFpZW5nYnB4eWVtdHd4eXRwdWtzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1ODYyOTEzOSwiZXhwIjoyMDc0MjA1MTM5fQ.EjwOs-4Tuj93_Pq3GCF3UrgO5LElpJXJO5eccUGzRnQ") # Replace with your Supabase Public API Key

if url == "YOUR_SUPABASE_URL" or key == "YOUR_SUPABASE_KEY":
    st.warning("Using placeholder Supabase URL and Key. Please replace with your actual credentials.")
    # For demonstration purposes, we'll proceed, but in a real scenario, you might want to stop
    # st.stop() # Uncomment this line to stop if credentials are not set

try:
    supabase: Client = create_client(url, key)

    # Fetch data from the '감염병현황' table
    response = supabase.from_('감염병현황').select("*").execute()
    data = response.data

    # Convert to pandas DataFrame
    df = pd.DataFrame(data)

    # st.write("Data loaded successfully!")
    # st.dataframe(df.head()) # Optional: display head of dataframe

except Exception as e:
    st.error(f"An error occurred: {e}")
    df = pd.DataFrame() # Initialize an empty DataFrame in case of error


st.title("감염병 발생 현황")

if '감염병명' in df.columns and not df['감염병명'].empty:
    infectious_diseases = df['감염병명'].unique().tolist()
    selected_disease = st.selectbox("감염병명을 선택하세요", infectious_diseases)
else:
    st.error("데이터에 '감염병명' 컬럼이 없거나 데이터가 비어있습니다.")
    st.stop()


if df.empty:
    st.error("데이터를 불러오지 못했습니다.")
else:
    filtered_df = df[df['감염병명'] == selected_disease].copy()
    # st.write(f"'{selected_disease}' 데이터 필터링 결과:") # Optional: display filtered data head
    # st.dataframe(filtered_df.head())


    if not filtered_df.empty:
        # Monthly cases aggregation
        filtered_df['신고일'] = pd.to_datetime(filtered_df['신고일'])
        filtered_df['신고월'] = filtered_df['신고일'].dt.month

        monthly_cases = filtered_df.groupby('신고월').size().reset_index(name='신고건수')
        monthly_cases = monthly_cases.sort_values(by='신고월')

        # st.write("월별 신고 건수:") # Optional: display monthly cases
        # st.dataframe(monthly_cases)

        # Font setup for matplotlib
        # Find the font file path
        font_dirs = ['/usr/share/fonts/truetype/nanum']
        font_files = fm.findSystemFonts(fontpaths=font_dirs)

        if len(font_files) > 0:
            for font_file in font_files:
                fm.fontManager.addfont(font_file)
            plt.rcParams['font.family'] = 'NanumGothic'
            plt.rcParams['axes.unicode_minus'] = False
            # print("NanumGothic font added and set.") # Optional: print font status
        else:
            st.warning("나눔 글꼴을 찾을 수 없습니다. 그래프에 한글이 깨질 수 있습니다.")


        # Data visualization
        if not monthly_cases.empty:
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.bar(monthly_cases['신고월'], monthly_cases['신고건수'])
            ax.set_xlabel("신고월")
            ax.set_ylabel("신고건수")
            ax.set_title(f"{selected_disease} 월별 신고 건수")
            ax.set_xticks(monthly_cases['신고월'])
            ax.grid(axis='y', linestyle='--')
            st.pyplot(fig)
        else:
            st.write("선택된 감염병에 대한 데이터가 충분하지 않아 월별 그래프를 표시할 수 없습니다.")

        # Major age group information
        age_counts = filtered_df['확진자_연령'].value_counts()

        if not age_counts.empty:
            max_count = age_counts.max()
            major_age_groups = age_counts[age_counts == max_count].index.tolist()

            st.write("주요 감염 연령대:")
            st.write(", ".join(major_age_groups))
        else:
            st.write("주요 감염 연령대 정보를 찾을 수 없습니다 (연령 데이터 없음).")
    else:
        st.write("선택된 감염병에 대한 데이터가 없습니다.")
