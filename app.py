import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- 1. 核心分析類別 ---
class CentralLogisticsAnalyst:
    def __init__(self):
        # 費率對照基準
        self.transfer_rates = {
            "大肚-大溪": {"46T": 13100, "17T": 7800}, # 預設路線
            "大溪-岡山": {"46T": 18900, "17T": 8100},
            "大肚-岡山": {"46T": 13600, "17T": 8100},
            "大溪-大肚": {"46T": 13100, "17T": 7800}
        }
        # 里程實測基準
        self.verified_routes = {
            "IN": {"name": "嘉義沿海", "km": 260.0, "alpha": 1.45},
            "IR": {"name": "國姓/魚池", "km": 199.3, "alpha": 1.45},
            "2G": {"name": "彰化南部", "km": 105.7, "alpha": 1.20},
            "2J": {"name": "烏日", "km": 57.8, "alpha": 1.05}
        }
        self.alpha_presets = {
            "平原/標準 (α=1.20)": 1.20,
            "長途/山區 (α=1.45)": 1.45,
            "密集市區 (α=1.35)": 1.35,
            "順暢市區 (α=1.05)": 1.05
        }

    def analyze_savings(self, total_pallets, route):
        rate_info = self.transfer_rates.get(route)
        cost_17t = rate_info["17T"]
        
        full_30 = (total_pallets // 30) * 30
        r = total_pallets % 30
        
        savings = 0
        saving_type = "無節省"
        remainder_csv = 0

        # 核心計算邏輯
        if 0 < r <= 15:
            savings = cost_17t
            saving_type = "0.5 趟 (17T)"
            remainder_csv = r
        elif r > 15:
            savings = cost_17t
            saving_type = "0.5 趟 (17T)"
            remainder_csv = r - 15 # 溢出判定邏輯
            
        return {
            "route": route, 
            "pallets": total_pallets, 
            "full_30": full_30,
            "r": r,
            "savings": savings, 
            "saving_type": saving_type,
            "rem": remainder_csv
        }

# --- 2. Streamlit 介面 ---
st.set_page_config(page_title="物流數據決策中心", layout="wide", page_icon="🚚")
expert = CentralLogisticsAnalyst()

st.sidebar.title("🚚 轉運數據決策中心")
app_mode = st.sidebar.radio("請選擇功能模組：", ["💰 轉運節費計算", "📏 路線里程估算"])

# --- 功能一：轉運節費計算 ---
if app_mode == "💰 轉運節費計算":
    st.header("💰 轉運節費計算機")
    
    with st.sidebar:
        st.markdown("---")
        st.subheader("⚙️ 節費參數")
        # 設定「大肚-大溪」為預設 (index=0)
        route = st.selectbox("選擇配送路線", list(expert.transfer_rates.keys()), index=0)
        n_pallets = st.number_input("每日平均板數 (N)", min_value=0, value=35)
        date_range = st.date_input("選擇計算日期區間", value=(datetime.now(), datetime.now()))
        run_calc = st.button("🚀 執行合計分析", use_container_width=True)

    if run_calc:
        res = expert.analyze_savings(n_pallets, route)
        start_d, end_d = date_range if isinstance(date_range, tuple) else (date_range, date_range)
        days = (end_d - start_d).days + 1
        total_sum = res['savings'] * days

        # 頂部總結
        st.success(f"### 🎊 總節費合計： NT$ {total_sum:,} 元")
        
        # 報告明細
        st.info(f"""
        #### 📋 節費試算報告 (溢出不加派)
        - **車趟路線**：{res['route']}
        - **總計板數**：{res['pallets']} 板
        - **板數拆解**：{res['full_30']}板(滿車) + {"15板 + " if res['r'] > 15 else ""}剩餘 {res['rem']} 板
        - **節省費用**：{res['savings']:,} 元 (成功省下 {res['saving_type']} 費用)
        """)

        # CSV 輸出
        st.markdown("---")
        st.subheader("📊 Excel 專用原始資料 (CSV)")
        csv_str = f"日期,路線,總板數,溢出零頭,節省車型,節省費用\n"
        for i in range(days):
            d = (start_d + timedelta(days=i)).strftime('%Y-%m-%d')
            csv_str += f"{d},{res['route']},{res['pallets']},{res['rem']},{res['saving_type']},{res['savings']}\n"
        st.code(csv_str, language="text")

# --- 功能二：路線里程估算 ---
elif app_mode == "📏 路線里程估算":
    st.header("📏 智慧里程估算 (含分段拆解)")
    
    col_in, col_res = st.columns([1, 1.2])
    with col_in:
        st.subheader("📍 數據輸入")
        route_code = st.text_input("路線代碼 (如: 2
