from supabase import create_client, Client
import streamlit as st
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Replace with your actual Supabase URL and key
# Example: SUPABASE_URL: str = "https://your-project-id.supabase.co"
SUPABASE_URL: str = "https://aiengbpxyemtwxytpuks.supabase.co"
# Example: SUPABASE_KEY: str = "your-anon-key"
SUPABASE_KEY: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFpZW5nYnB4eWVtdHd4eXRwdWtzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1ODYyOTEzOSwiZXhwIjoyMDc0MjA1MTM5fQ.EjwOs-4Tuj93_Pq3GCF3UrgO5LElpJXJO5eccUGzRnQ"
supabase_client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_product_prices(product_name: str):
    """
    Queries the Supabase database for the latest and previous day's prices
    of the specified product.

    Args:
        product_name: The name of the product to query.

    Returns:
        A tuple containing the latest price and the previous day's price.
        Returns (None, None) if no data is found for the product or previous day.
    """
    today = datetime.now().strftime('%Y-%m-%d')
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

    latest_price_data = None
    previous_day_price_data = None

    try:
        # Query for the latest price
        latest_price_response = supabase_client.from_('농산물가격').select('평균가격').eq('품목', product_name).order('일자', desc=True).limit(1).execute()
        latest_price_data = latest_price_response.data
        logging.info(f"Latest price response data: {latest_price_data}")

        # Query for the previous day's price
        previous_day_price_response = supabase_client.from_('농산물가격').select('평균가격').eq('품목', product_name).eq('일자', yesterday).execute()
        previous_day_price_data = previous_day_price_response.data
        logging.info(f"Previous day price response data: {previous_day_price_data}")

    except Exception as e:
        logging.error(f"Error fetching data from Supabase: {e}")
        st.error(f"데이터를 가져오는 중 오류가 발생했습니다: {e}")
        return None, None


    latest_price = latest_price_data[0]['평균가격'] if latest_price_data else None
    previous_day_price = previous_day_price_data[0]['평균가격'] if previous_day_price_data else None

    return latest_price, previous_day_price

def calculate_price_change(latest_price, previous_day_price):
    """
    Calculates the percentage change in price from the previous day.

    Args:
        latest_price: The latest price of the product.
        previous_day_price: The previous day's price of the product.

    Returns:
        The percentage change in price, or None if the change cannot be calculated.
    """
    if latest_price is not None and previous_day_price is not None:
        if previous_day_price != 0:
            return ((latest_price - previous_day_price) / previous_day_price) * 100
        else:
            return None  # Avoid division by zero
    else:
        return None # Handle cases where prices are not available

st.title("농산물 가격 조회")

product_name = st.text_input("제품 이름을 입력하세요:")

if st.button("가격 조회"):
    if not product_name:
        st.warning("제품 이름을 입력해주세요.")
    else:
        latest_price, previous_day_price = get_product_prices(product_name)

        if latest_price is not None:
            price_change_percentage = calculate_price_change(latest_price, previous_day_price)

            st.info(f"**{product_name}**의 최신 가격: {latest_price} 원")

            if price_change_percentage is not None:
                st.info(f"어제 대비 가격 변화율: {price_change_percentage:.2f} %")
            else:
                 st.warning("어제 가격 정보를 찾을 수 없거나 0이어서 가격 변화율을 계산할 수 없습니다.")
        else:
            st.error(f"**{product_name}**에 대한 데이터를 찾을 수 없습니다.")
