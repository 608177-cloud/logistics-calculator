import streamlit as st
import datetime
import pandas as pd

# 網頁標題
st.set_page_config(page_title="物流轉運節費分析器", layout="centered")
st.title("💰 物流轉運節費分析系統")
st.markdown("---")

# 1. 費率對照資料
rates = {
    "大肚 - 大溪": {"46T": 13100, "17T": 7800},
    "大溪 - 岡山": {"46T": 18900, "17T": 8100},
    "大肚 - 岡山": {"46T": 13600, "17T": 8100}
}

# 2. 側邊欄輸入介面
with st.sidebar:
    st.header("⚙️ 設定參數")
    route = st.selectbox("選擇車趟路線", list(rates.keys()))
    total_pallets = st.number_input("輸入總計板數 (N)", min_value=0, value=31, step=1)
    submit_btn = st.button("開始計算節費")

# 3. 核心計算邏輯
current_rate = rates[route]
price_17t = current_rate["17T"]

full_loads = total_pallets // 30
remainder = total_pallets % 30

savings = 0
saved_type = "無"
breakdown_msg = f"{full_loads * 30}板 (滿車)"

if remainder == 0:
    savings = 0
    saved_type = "無 (滿車)"
elif 0 < remainder <= 15:
    savings = price_17t
    saved_type = "17T (0.5趟)"
    breakdown_msg += f" + 剩餘 {remainder} 板"
else:
    savings = price_17t
    saved_type = "17T (0.5趟)"
    breakdown_msg += f" + 15板 + 剩餘 {remainder - 15} 板"

# 4. 顯示結果
if submit_btn:
    st.subheader("📊 節費試算報告")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("總計板數", f"{total_pallets} 板")
    with col2:
        st.metric("節省費用", f"${savings:,}", delta=f"省下 {saved_type}")
    
    st.info(f"**板數拆解：** {breakdown_msg}")
    st.markdown("---")
    
    # 5. 表格資料
    today = datetime.date.today().strftime("%Y/%m/%d")
    df = pd.DataFrame([{
        "日期": today, "路線": route, "總板數": total_pallets,
        "溢出零頭": remainder, "節省車型": saved_type, "節省費用": savings
    }])
    st.table(df)