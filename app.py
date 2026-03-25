import streamlit as st
import pandas as pd
import datetime

# --- 網頁配置 ---
st.set_page_config(page_title="物流路網數據專家系統", layout="wide", page_icon="🚚")

# --- 核心資料庫設定 ---
# 1. 運費費率 (節費分析用)
FREIGHT_RATES = {
    "大肚 - 大溪": {"46T": 13100, "17T": 7800},
    "大溪 - 岡山": {"46T": 18900, "17T": 8100},
    "大肚 - 岡山": {"46T": 13600, "17T": 8100}
}

# 2. 里程實測確值 (Ground Truth)
MILEAGE_GT = {
    "2F": 138.3, "2G": 105.7, "2J": 57.8, 
    "IJ": 188.8, "IN": 260.0, "IR": 199.3
}

# 3. 里程補償係數 (α)
ALPHA_MAP = {
    "平原/標準 (α=1.20)": 1.20,
    "長途/山區 (α=1.45)": 1.45,
    "密集市區 (α=1.35)": 1.35,
    "順暢市區 (α=1.05)": 1.05
}

# --- 側邊欄選單 ---
st.sidebar.title("🚛 物流數據決策中心")
mode = st.sidebar.radio("請選擇功能模組：", ["📏 智慧里程估算", "💰 運費節費分析"])

# --- 模組一：智慧里程估算 (含分段拆解) ---
if mode == "📏 智慧里程估算":
    st.header("📏 配送里程自動估算 (含分段拆解)")
    st.info("💡 操作說明：輸入代碼並貼上店名。若是已知實測路線，系統會自動帶入正確里程。")

    col_in, col_res = st.columns([1, 1.2])
    
    with col_in:
        st.subheader("📍 數據輸入")
        route_code = st.text_input("路線代碼 (如: 2G)", value="2G").upper().strip()
        zone_type = st.selectbox("區域屬性 (判定 α)", list(ALPHA_MAP.keys()))
        raw_stores = st.text_area("請在此處貼上店名清單 (每行一店)", height=250, placeholder="直接從 Excel 貼上...")
        
        # 自動判定：實測路線隱藏輸入框
        if route_code in MILEAGE_GT:
            st.success(f"偵測到實測路線 {route_code}：{MILEAGE_GT[route_code]} km")
            google_dist = 0.0
        else:
            google_dist = st.number_input("請輸入 Google Map 總里程 (D_map)", min_value=0.0, value=0.0)
        
        calculate_btn = st.button("🚀 生成分段報告")

    if calculate_btn:
        store_list = [s.strip() for s in raw_stores.split("\n") if s.strip()]
        num_stores = len(store_list)
        alpha = ALPHA_MAP[zone_type]
        
        # 決定總里程
        final_total = MILEAGE_GT[route_code] if route_code in MILEAGE_GT else round(google_dist * alpha, 1)
        
        # 分段拆解邏輯：平均分配總里程
        avg_segment = round(final_total / (num_stores + 1), 1) if num_stores > 0 else 0

        with col_res:
            st.subheader(f"📊 {route_code} 配送分析")
            st.metric("預估總里程", f"{final_total} km", delta=f"數據狀態: {'實測' if route_code in MILEAGE_GT else '預估'}")
            
            # 建立表格
            table_data = [["0", "起點", "全台大肚倉", "0.0"]]
            for i, name in enumerate(store_list, 1):
                table_data.append([str(i), f"第 {i} 站", name, f"{avg_segment}"])
            
            # 回場計算 (確保總數正確)
            return_dist = round(final_total - (avg_segment * num_stores), 1)
            table_data.append([str(num_stores + 1), "回場", "全台大肚倉", f"{max(0, return_dist)}"])
            
            st.table(pd.DataFrame(table_data, columns=["Index", "路順", "店名", "分段里程(km)"]))
            st.caption(f"註：分段里程係依據總里程進行平均拆解供參考。")

# --- 模組二：運費節費分析 ---
elif mode == "💰 運費節費分析":
    st.header("💰 溢出板數節費試算")
    st.info("計算因「不加派」溢出板數所省下的運費。")
    
    route = st.selectbox("車趟路線", list(FREIGHT_RATES.keys()))
    total_pallets = st.number_input("總計板數 (N)", min_value=0, value=31)
    
    if st.button("執行節費分析"):
        price_17t = FREIGHT_RATES[route]["17T"]
        remainder = total_pallets % 30
        savings = price_17t if remainder > 0 else 0
        
        res1, res2 = st.columns(2)
        res1.metric("總板數", f"{total_pallets} 板")
        res2.metric("節省金額", f"${savings:,} 元")
        
        st.write(f"**分析：** 剩餘 {remainder} 板已透過原有車趟消化，成功省下 0.5 趟派車費用。")
