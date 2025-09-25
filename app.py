import streamlit as st
import pandas as pd
from supabase import create_client, Client

# Supabase connection details
url: str = "https://aiengbpxyemtwxytpuks.supabase.co" # your supabase url
key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFpZW5nYnB4eWVtdHd4eXRwdWtzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1ODYyOTEzOSwiZXhwIjoyMDc0MjA1MTM5fQ.EjwOs-4Tuj93_Pq3GCF3UrgO5LElpJXJO5eccUGzRnQ" # your supabase key
supabase: Client = create_client(url, key)

# Streamlit UI
st.title("취업연계추천시스템")

# Data loading
data = None
try:
    response = supabase.from_('공공참여자').select('*').execute()
    data = response.data
    if not data:
        st.write("데이터를 불러오는데 문제가 발생했습니다. 다시 시도해주세요.")
except Exception as e:
    st.write(f"데이터를 불러오는데 문제가 발생했습니다: {e}")

# Ensure data is loaded before creating selectboxes and button
if data:
    df = pd.DataFrame(data)

    # Assuming '참여자_연령대' and '참여자_성별' are the column names in your data
    # Get unique values from the data for selectbox options
    age_group_options = sorted(df['참여자_연령대'].unique())
    gender_options = sorted(df['참여자_성별'].unique())


    age_group = st.selectbox('연령대를 선택하세요', age_group_options)
    gender = st.selectbox('성별을 선택하세요', gender_options)

    recommend_button = st.button('추천받기')

    # Recommendation logic
    recommended_사업명 = None

    if recommend_button:
        # Filter data based on selected age group and gender
        filtered_df = df[(df['참여자_연령대'] == age_group) & (df['참여자_성별'] == gender)]

        if not filtered_df.empty:
            # Calculate the proportion of '취업_연계_여부' == 1 for each '사업명'
            # Ensure '취업_연계_여부' is numeric for calculation
            filtered_df['취업_연계_여부'] = pd.to_numeric(filtered_df['취업_연계_여부'], errors='coerce')
            # Drop rows where '취업_연계_여부' could not be converted to numeric
            filtered_df.dropna(subset=['취업_연계_여부'], inplace=True)


            사업명_연계_비율 = filtered_df.groupby('사업명')['취업_연계_여부'].apply(lambda x: (x == 1).sum() / len(x) if len(x) > 0 else 0)

            # Find the '사업명' with the highest proportion
            if not 사업명_연계_비율.empty:
                # Get the top recommendation
                recommended_사업명 = 사업명_연계_비율.idxmax()
                st.subheader("추천 사업명:")
                st.write(recommended_사업명)
            else:
                st.write("해당 조건에 맞는 사업 정보가 없습니다. 다른 조건을 선택해주세요.")
        else:
            st.write("해당 조건에 맞는 사업 정보가 없습니다. 다른 조건을 선택해주세요.")
