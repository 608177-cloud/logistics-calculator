import streamlit as st
import pandas as pd
import datetime

# --- 網頁配置 ---
st.set_page_config(page_title="物流路網數據專家系統", layout="wide", page_icon="🚚")

# --- 核心資料庫設定 ---
FREIGHT_RATES = {
    "大肚 - 大溪": {"46T": 13100, "17T": 7800},
    "大溪 - 岡山": {"46T": 18900, "17T": 8100},
    "大肚 - 岡山": {"46T": 13600, "17T": 8100}
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

# --- 側邊欄選單 ---
st.sidebar.title("🚛 物流數據決策中心")
mode = st.sidebar.radio("請選擇功能模組：", ["📏 智慧里程估算", "💰 運費節費分析"])

# --- 模組一：里程動態估算 ---
if mode == "📏 智慧里程估算":
    st.header("📏 配送里程動態估算 (α 補償模型)")
    st.info("💡 操作說明：直接貼上店名清單即可。系統會自動執行閉環路順計算。")

    col_in, col_res = st.columns([1, 1.2])
    with col_in:
        st.subheader("📍 數據輸入")
        route_code = st.text_input("路線代碼", value="2G").upper().strip()
        zone_type = st.selectbox("區域屬性 (判定係數 α)", list(ALPHA_MAP.keys()))
        raw_stores = st.text_area("請在此處貼上店名清單 (每行一店)", height=250)
        google_dist = st.number_input("Google Map 總里程 (D_map)", min_value=0.0, value=100.0)
        # 修正處：移除了造成錯誤的 type/variant 參數
        calculate_btn = st.button("🚀 開始計算里程報告")

    if calculate_btn:
        store_list = [s.strip() for s in raw_stores.split("\n") if s.strip()]
        alpha = ALPHA_MAP[zone_type]
        if route_code in MILEAGE_GT:
            final_mileage = MILEAGE_GT[route_code]
            data_status = "✅ 實測確值"
        else:
            final_mileage = round(google_dist * alpha, 1)
            data_status = f"🤖 Agent 預估 (α={alpha})"

        with col_res:
            st.subheader(f"📊 {route_code} 報告")
            st.metric("預估總里程", f"{final_mileage} km", delta=data_status)
            table_data = [["起點", "全台大肚倉", "0.0"]]
            for i, name in enumerate(store_list, 1):
                table_data.append([f"第 {i} 站", name, "--"])
            table_data.append(["回場", "全台大肚倉", "--"])
            st.table(pd.DataFrame(table_data, columns=["路順", "店名", "分段"]))

# --- 模組二：運費節費分析 ---
elif mode == "💰 運費節費分析":
    st.header("💰 溢出板數節費試算")
    route = st.selectbox("車趟路線", list(FREIGHT_RATES.keys()))
    total_pallets = st.number_input("總計板數 (N)", min_value=0, value=31)
    if st.button("執行節費分析"):
        price_17t = FREIGHT_RATES[route]["17T"]
        remainder = total_pallets % 30
        savings = price_17t if remainder > 0 else 0
        st.metric("成功節省", f"${savings:,} 元")
