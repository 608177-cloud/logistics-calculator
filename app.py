import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- 網頁配置 ---
st.set_page_config(page_title="轉運節費計算機", layout="wide", page_icon="🚚")

# --- 核心資料庫 ---
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
    "平原/標準 (α=1.20)": 1.20,
    "長途/山區 (α=1.45)": 1.45,
    "密集市區 (α=1.35)": 1.35,
    "順暢市區 (α=1.05)": 1.05
}

# --- 側邊欄：功能導航與設定 ---
st.sidebar.title("🚚 轉運數據決策中心")
app_mode = st.sidebar.radio("請選擇功能模組：", ["💰 轉運節費計算", "📏 智慧里程估算"])

# --- 模組一：轉運節費計算 (含多天合計) ---
if app_mode == "💰 轉運節費計算":
    st.header("💰 轉運節費計算機")
    st.info("計算優化溢出板數所省下的派車費用。")
    
    with st.sidebar:
        st.markdown("---")
        st.subheader("⚙️ 節費參數")
        route_sel = st.selectbox("選擇配送路線", list(FREIGHT_RATES.keys()))
        today = datetime.now()
        date_range = st.date_input("選擇計算日期區間", value=(today, today))
        avg_pallets = st.number_input("每日平均板數 (N)", min_value=0, value=31)
        calc_saving = st.button("🚀 執行合計分析", use_container_width=True)

    if calc_saving:
        # 日期邏輯處理
        try:
            start_date, end_date = date_range if isinstance(date_range, tuple) else (date_range, date_range)
        except:
            st.error("請選擇完整的日期區間（點選開始日與結束日）"); st.stop()
            
        days = (end_date - start_date).days + 1
        daily_val = FREIGHT_RATES[route_sel]["17T"]
        total_val = daily_val * days

        # 總合計看板
        st.success(f"## 🎊 總節費合計： NT$ {total_val:,} 元")
        
        c1, c2, c3 = st.columns(3)
        c1.metric("統計天數", f"{days} 天")
        c2.metric("路線", route_sel)
        c3.metric("每日節省", f"${daily_val:,}")

        # 明細表
        st.subheader("📅 每日明細清單")
        date_list = [(start_date + timedelta(days=x)).strftime('%Y-%m-%d') for x in range(days)]
        df_save = pd.DataFrame({
            "項次": range(1, days + 1),
            "日期": date_list,
            "狀態": ["✅ 成功節省 0.5 趟 17T"] * days,
            "節省金額": [f"${daily_val:,}"] * days
        })
        st.table(df_save)

# --- 模組二：智慧里程估算 (閉環分段版) ---
elif app_mode == "📏 智慧里程估算":
    st.header("📏 智慧里程估算 (含分段拆解)")
    
    col_in, col_res = st.columns([1, 1.2])
    with col_in:
        route_code = st.text_input("路線代碼 (如: 2G)", value="2G").upper().strip()
        zone_type = st.selectbox("區域屬性 (α)", list(ALPHA_MAP.keys()))
        raw_stores = st.text_area("請貼上店名清單", height=200)
        
        is_known = route_code in MILEAGE_GT
        if is_known:
            st.success(f"已帶入實測值: {MILEAGE_GT[route_code]} km")
            google_km = 0.0
        else:
            google_km = st.number_input("Google Map 總里程 (未輸入則依店數預估)", min_value=0.0, value=0.0)
        
        calc_dist = st.button("🚀 生成分段報告")

    if calc_dist:
        store_list = [s.strip() for s in raw_stores.split("\n") if s.strip()]
        n = len(store_list)
        alpha = ALPHA_MAP[zone_type]
        
        total_dist = MILEAGE_GT[route_code] if is_known else (google_km * alpha if google_km > 0 else (n+1)*15*alpha)
        avg_seg = round(total_dist / (n + 1), 1) if n > 0 else 0

        with col_res:
            st.subheader(f"📊 {route_code} 報告結果")
            st.metric("配送總里程", f"{round(total_dist,1)} km")
            
            table_data = [["0", "起點", "大肚倉", "0.0"]]
            for i, name in enumerate(store_list, 1):
                table_data.append([str(i), f"第 {i} 站", name, f"{avg_seg}"])
            table_data.append([str(n+1), "回場", "大肚倉", f"{round(total_dist - avg_seg*n, 1)}"])
            
            st.table(pd.DataFrame(table_data, columns=["Index", "路順", "店名", "分段(km)"]))
