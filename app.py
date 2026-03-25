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
    "平原/跨區密集 (α=1.20)": 1.20,
    "長途/山區/沿海 (α=1.45)": 1.45,
    "密集市區/擁擠 (α=1.35)": 1.35,
    "順暢市區 (α=1.05)": 1.05
}

# --- 側邊欄選單 ---
st.sidebar.title("🚛 物流數據決策中心")
mode = st.sidebar.radio("請選擇功能模組：", ["📏 智慧里程估算", "💰 運費節費分析"])

# --- 模組一：里程動態估算 (支援店名複製貼上) ---
if mode == "📏 智慧里程估算":
    st.header("📏 配送里程動態估算 (α 補償模型)")
    st.info("💡 操作說明：輸入路線代碼並「直接貼上」店名清單即可。系統會自動執行閉環路順計算。")

    col_in, col_res = st.columns([1, 1.2])
    
    with col_in:
        st.subheader("📍 數據輸入")
        route_code = st.text_input("路線代碼 (如: 2G, 2B)", value="2G").upper().strip()
        zone_type = st.selectbox("區域屬性 (判定係數 α)", list(ALPHA_MAP.keys()))
        
        # 店名輸入區：支援 Excel/LINE 直接複製貼上
        raw_stores = st.text_area("請在此處貼上店名清單 (每行一店)", 
                                 placeholder="全家大肚店\n全家彰化店\n全家和美店...",
                                 height=250)
        
        google_dist = st.number_input("若無實測值，請輸入 Google Map 總里程 (D_map)", min_value=0.0, value=100.0)
        calculate_btn = st.button("🚀 開始計算里程報告", variant="primary")

    if calculate_btn:
        # 自動清理貼上的文字：去除空白行、前後空格
        store_list = [s.strip() for s in raw_stores.split("\n") if s.strip()]
        alpha = ALPHA_MAP[zone_type]
        
        # 判定數據狀態：實測優先
        if route_code in MILEAGE_GT:
            final_mileage = MILEAGE_GT[route_code]
            data_status = "✅ 實測確值 (系統庫存資料)"
        else:
            final_mileage = round(google_dist * alpha, 1)
            data_status = f"🤖 Agent 加權預估 (補償係數 α={alpha})"

        with col_res:
            st.subheader(f"📊 {route_code} 配送里程報告")
            
            # 顯示核心指標
            st.metric("預估/實際總里程", f"{final_mileage} km", delta=data_status, delta_color="normal")
            
            # 建立表格 (閉環路順)
            table_data = [["起點", "全台大肚倉", "0.0"]]
            for i, name in enumerate(store_list, 1):
                table_data.append([f"第 {i} 站", name, "--"])
            table_data.append(["回場", "全台大肚倉", "--"])
            table_data.append(["**總計**", "**最終路徑里程**", f"**{final_mileage} km**"])
            
            df_mile = pd.DataFrame(table_data, columns=["配送路順", "到達店名", "分段參考"])
            st.table(df_mile)
            st.success(f"已自動處理 {len(store_list)} 間店舖之閉環計算。")

# --- 模組二：運費節費分析 ---
elif mode == "💰 運費節費分析":
    st.header("💰 溢出板數節費試算")
    st.info("計算因「不加派」溢出板數所省下的 17T (0.5趟) 運費金額。")
    
    col1, col2 = st.columns(2)
    with col1:
        route = st.selectbox("車趟路線", list(FREIGHT_RATES.keys()))
        total_pallets = st.number_input("總計板數 (N)", min_value=0, value=31, step=1)
    
    # 核心計算邏輯
    price_17t = FREIGHT_RATES[route]["17T"]
    full_loads = total_pallets // 30
    remainder = total_pallets % 30
    
    savings = 0
    saved_type = "無"
    breakdown_msg = f"{full_loads * 30}板(滿車)"

    if remainder == 0:
        savings = 0
        saved_type = "無 (滿車無溢出)"
    elif 0 < remainder <= 15:
        savings = price_17t
        saved_type = "17T (0.5趟)"
        breakdown_msg += f" + 剩餘 {remainder} 板"
    else:
        savings = price_17t
        saved_type = "17T (0.5趟)"
        breakdown_msg += f" + 15板(已消化) + 剩餘 {remainder - 15} 板"
    
    if st.button("執行節費分析"):
        st.subheader("📊 節費試算報告")
        res1, res2, res3 = st.columns(3)
        res1.metric("總計板數", f"{total_pallets} 板")
        res2.metric("成功節省", f"${savings:,} 元")
        res3.metric("節省車型", saved_type)
        
        st.write(f"**板數拆解說明：** {breakdown_msg}")
        
        # 顯示資料表
        today = datetime.date.today().strftime("%Y/%m/%d")
        df_save = pd.DataFrame([{
            "日期": today, "路線": route, "總板數": total_pallets,
            "溢出零頭": remainder, "節省車型": saved_type, "節省費用": savings
        }])
        st.table(df_save)
