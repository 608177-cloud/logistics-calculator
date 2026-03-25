import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- 網頁配置 ---
st.set_page_config(page_title="物流路網數據專家系統", layout="wide", page_icon="📊")

# --- 核心資料庫 (依據您的最新截圖調整) ---
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
            # 計算邏輯 (依據截圖：35板 = 溢出5板 -> 省1趟17T)
            rates = WH_DATA.get((start_wh, end_wh), {"46T": 0, "17T": 0})
            overflow = pallets_input - 30
            
            # 判斷節省車種
            if overflow > 15:
                save_type = "46T"
                save_amt = rates["46T"]
            else:
                save_type = "17T"
                save_amt = rates["17T"]

            start_d, end_d = date_range if isinstance(date_range, tuple) else (date_range, date_range)
            days = (end_d - start_d).days + 1
            grand_total = save_amt * days

            # 1. 頂部總結看板
            st.success(f"### 🎊 總節費合計： NT$ {grand_total:,} 元")
            
            # 2. 專業報告格式 (模仿截圖)
            st.markdown(f"### 📋 節費試算報告 (溢出不加派)")
            report_text = f"""
            * **車趟路線**：{start_wh}-{end_wh}
            * **總計板數**：{pallets_input} 板 (溢出 {max(0, overflow)} 板)
            * **節省費用**：{save_amt:,} 元 (成功省下 1 趟 {save_type} 費用)
            """
            st.info(report_text)

            # 3. 數據明細
            st.subheader("📅 每日明細清單")
            date_list = [(start_d + timedelta(days=x)).strftime('%Y-%m-%d') for x in range(days)]
            df = pd.DataFrame({
                "日期": date_list,
                "路段": f"{start_wh}-{end_wh}",
                "總板數": pallets_input,
                "節省車型": save_type,
                "節省費用": save_amt
            })
            st.table(df)

            # 4. CSV 原始資料 (模仿截圖)
            st.markdown("---")
            st.subheader("📊 Excel 專用原始資料 (CSV 格式)")
            csv_string = f"日期,路線,總板數,溢出板數,節省車型,節省費用\n"
            for d in date_list:
                csv_string += f"{d},{start_wh}-{end_wh},{pallets_input},{overflow},{save_type},{save_amt}\n"
            st.code(csv_string, language="text")

# --- 模組二：路線里程計算機 ---
elif app_mode == "📏 路線里程計算機":
    st.header("📏 路線里程計算機")
    
    col_in, col_res = st.columns([1, 1.2])
    with col_in:
        route_code = st.text_input("路線代碼", value="2G").upper()
        zone_type = st.selectbox("區域屬性", list(ALPHA_MAP.keys()))
        raw_stores = st.text_area("店名清單 (每行一家)", value="大肚火車站\n大肚王田\n大肚高山\n大肚新市鎮")
        google_km = st.number_input("Google Map 總里程", min_value=0.0, value=100.0)
        calc_dist = st.button("🚀 生成報告")

    if calc_dist:
        stores = [s.strip() for s in raw_stores.split("\n") if s.strip()]
        n = len(stores)
        alpha = ALPHA_MAP[zone_type]
        total_dist = MILEAGE_GT.get(route_code, google_km * alpha)
        avg_seg = round(total_dist / (n + 1), 1)

        with col_res:
            st.subheader(f"📊 {route_code} 配送分析")
            st.metric("預估總里程", f"{round(total_dist, 1)} km")
            
            table_data = [["0", "起點", "全台大肚倉", "0.0"]]
            for i, name in enumerate(stores, 1):
                table_data.append([str(i), f"第 {i} 站", name, f"{avg_seg}"])
            table_data.append([str(n+1), "回場", "全台大肚倉", f"{round(total_dist - avg_seg*n, 1)}"])
            st.table(pd.DataFrame(table_data, columns=["Index", "路順", "店名", "分段(km)"]))
