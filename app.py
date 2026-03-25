import streamlit as st
import pandas as pd
from datetime import datetime

# --- 核心邏輯類別 ---
class LogisticsAnalyst:
    def __init__(self):
        self.transfer_rates = {
            "大肚-大溪": {"46T": 13100, "17T": 7800},
            "大溪-岡山": {"46T": 18900, "17T": 8100},
            "大肚-岡山": {"46T": 13600, "17T": 8100}
        }
        self.verified_routes = {
            "IN": {"name": "嘉義沿海", "km": 260.0, "alpha": 1.45},
            "IR": {"name": "國姓/魚池", "km": 199.3, "alpha": 1.45},
            "2G": {"name": "彰化南部", "km": 105.7, "alpha": 1.20},
            "2J": {"name": "烏日", "km": 57.8, "alpha": 1.05}
        }
        self.alpha_presets = {"長途/山區/沿海 (1.45)": 1.45, "平原/跨區密集 (1.20)": 1.20, "市區順暢 (1.05)": 1.05, "市區擁擠 (1.35)": 1.35}

# --- Streamlit 網頁介面 ---
st.set_page_config(page_title="物流節費與里程分析器", layout="wide")
analyst = LogisticsAnalyst()

st.title("🚚 中部物流數據分析系統")
st.markdown("---")

tab1, tab2 = st.tabs(["💰 轉運節費計算", "📍 里程動態估算"])

# --- Tab 1: 轉運節費 ---
with tab1:
    st.header("轉運節費試算")
    col1, col2 = st.columns(2)
    with col1:
        route = st.selectbox("選擇車趟路線", list(analyst.transfer_rates.keys()))
        pallets = st.number_input("輸入總計板數", min_value=0, value=30, step=1)
    
    # 計算邏輯
    rate_info = analyst.transfer_rates[route]
    r = pallets % 30
    savings = rate_info["17T"] if r > 0 else 0
    saving_type = "0.5 趟 (17T)" if r > 0 else "無節省"

    with col2:
        st.metric("預估節省金額", f"${savings:,} 元")
        st.write(f"**板數拆解：** {pallets // 30} 滿車 + 剩餘 {r} 板")

# --- Tab 2: 里程估算 ---
with tab2:
    st.header("里程動態估算報告")
    c1, c2, c3 = st.columns(3)
    with c1:
        route_code = st.text_input("路線代碼 (如：2B, IN)", value="2B")
    with c2:
        map_km = st.number_input("Google 地圖里程 (km)", min_value=0.0, value=100.0)
    with c3:
        mode = st.selectbox("區域屬性 (Alpha)", list(analyst.alpha_presets.keys()))

    # 計算里程
    alpha = analyst.alpha_presets[mode]
    if route_code in analyst.verified_routes:
        d_real = analyst.verified_routes[route_code]["km"]
        status = "✅ 實測確值"
        alpha = analyst.verified_routes[route_code]["alpha"]
    else:
        d_real = round(map_km * alpha, 1)
        status = "🤖 Agent 加權預估"

    st.success(f"預估實跑里程：**{d_real} km** ({status})")

    # CSV 下載功能
    st.markdown("### 📊 CSV 原始資料")
    csv_data = pd.DataFrame([{
        "日期": datetime.now().strftime("%Y/%m/%d"),
        "路線代碼": route_code,
        "總里程": d_real,
        "係數": alpha,
        "狀態": status
    }])
    st.dataframe(csv_data)
