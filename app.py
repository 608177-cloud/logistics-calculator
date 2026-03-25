import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- 網頁配置 ---
st.set_page_config(page_title="物流路網數據專家系統", layout="wide", page_icon="📊")

# --- 核心資料庫 (嚴格對照 Excel 截圖數據) ---
WH_DATA = {
    ("大肚", "大溪"): {"46T": 13100, "17T": 7800},
    ("大溪", "大肚"): {"46T": 13100, "17T": 7800},
    ("大溪", "岡山"): {"46T": 18900, "17T": 8100},
    ("岡山", "大溪"): {"46T": 18900, "17T": 8100},
    ("大肚", "岡山"): {"46T": 13600, "17T": 8100},
    ("岡山", "大肚"): {"46T": 13600, "17T": 8100}
}

MILEAGE_GT = {
    "2F": 138.3, "2G": 105.7, "2J": 57.8, 
    "IJ": 188.8, "IN": 260.0, "IR": 199.3
}

ALPHA_MAP = {
    "平原/跨區密集 (α=1.20)": 1.20,
    "長途/山區/沿海 (α=1.45)": 1.45,
    "密集市區/擁擠 (α=1.35)": 1.35,
    "順暢市區 (α=1.05)": 1.05
}

# --- 側邊欄 ---
st.sidebar.title("🚚 轉運數據決策中心")
app_mode = st.sidebar.radio("請選擇功能模組：", ["💰 轉運節費計算", "📏 路線里程計算機"])

# --- 模組一：轉運節費計算 ---
if app_mode == "💰 轉運節費計算":
    st.header("💰 轉運節費計算機")
    
    with st.sidebar:
        st.markdown("---")
        st.subheader("⚙️ 配送倉別與參數")
        # 保持雙格箭頭畫面不動
        col1, arrow, col2 = st.columns([1, 0.4, 1])
        with col1: start_wh = st.selectbox("起點", ["大肚", "大溪", "岡山"])
        with arrow: st.markdown("<h3 style='text-align: center; padding-top: 25px;'>➔</h3>", unsafe_allow_html=True)
        with col2: end_wh = st.selectbox("終點", ["大溪", "大肚", "岡山"])
        
        date_range = st.date_input("選擇日期區間", value=(datetime.now(), datetime.now()))
        pallets_input = st.number_input("每日總板數 (N)", min_value=0, value=35)
        calc_btn = st.button("🚀 執行節費分析", use_container_width=True)

    if calc_btn:
        if start_wh == end_wh:
            st.error("起終點不可相同")
        else:
            rates = WH_DATA.get((start_wh, end_wh), {"46T": 0, "17T": 0})
            overflow = pallets_input - 30 # 溢出板數計算邏輯
            
            # 判斷節省車種 (30-45板省17T，超過45板省46T)
            if overflow > 15:
                save_type, save_amt = "46T", rates["46T"]
            else:
                save_type, save_amt = "17T", rates["17T"]

            try:
                start_d, end_d = date_range if isinstance(date_range, tuple) else (date_range, date_range)
            except: st.stop()
            
            days = (end_d - start_d).days + 1
            grand_total = save_amt * days

            st.success(f"### 🎊 總節費合計： NT$ {grand_total:,} 元")
            
            # 專業點列式報告 (依據截圖)
            st.markdown(f"### 📋 節費試算報告 (溢出不加派)")
            st.info(f"""
            * **車趟路線**：{start_wh}-{end_wh}
            * **總計板數**：{pallets_input} 板 (溢出 {max(0, overflow)} 板)
            * **節省費用**：{save_amt:,} 元 (成功省下 1 趟 {save_type} 費用)
            """)

            # CSV 格式預覽 (方便貼回 Excel)
            st.markdown("---")
            st.subheader("📊 Excel 專用原始資料 (CSV)")
            csv_data = f"日期,路線,總板數,節省車型,節省費用\n"
            for x in range(days):
                curr_date = (start_d + timedelta(days=x)).strftime('%Y-%m-%d')
                csv_data += f"{curr_date},{start_wh}-{end_wh},{pallets_input},{save_type},{save_amt}\n"
            st.code(csv_data, language="text")

# --- 模組二：路線里程計算機 ---
elif app_mode == "📏 路線里程計算機":
    st.header("📏 路線里程計算機")
    # ... (里程計算邏輯保持不變) ...
