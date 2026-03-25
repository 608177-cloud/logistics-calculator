import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- 網頁配置 ---
st.set_page_config(page_title="轉運數據決策系統", layout="wide", page_icon="🚚")

# --- 核心資料庫 (依據 Excel 截圖更新費率) ---
# 包含 46T 與 17T 的完整運費對照
WH_FREIGHT_DATA = {
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
    "平原/標準 (α=1.20)": 1.20,
    "長途/山區 (α=1.45)": 1.45,
    "密集市區 (α=1.35)": 1.35,
    "順暢市區 (α=1.05)": 1.05
}

# --- 側邊欄導航 ---
st.sidebar.title("🚚 轉運數據決策中心")
app_mode = st.sidebar.radio("請選擇功能模組：", ["💰 轉運節費計算", "📏 路線里程計算機"])

# --- 模組一：轉運節費計算 ---
if app_mode == "💰 轉運節費計算":
    st.header("💰 轉運節費計算機")
    
    with st.sidebar:
        st.markdown("---")
        st.subheader("⚙️ 配送倉別設定")
        col_w1, col_a, col_w2 = st.columns([1, 0.4, 1])
        with col_w1: start_wh = st.selectbox("起點", ["大肚", "大溪", "岡山"], index=0)
        with col_a: st.markdown("<h3 style='text-align: center; padding-top: 25px;'>➔</h3>", unsafe_allow_html=True)
        with col_w2: end_wh = st.selectbox("終點", ["大溪", "大肚", "岡山"], index=0)
        
        st.markdown("---")
        date_range = st.date_input("選擇計算日期區間", value=(datetime.now(), datetime.now()))
        avg_pallets = st.number_input("每日平均板數 (N)", min_value=0, value=31)
        calc_saving = st.button("🚀 執行合計分析", use_container_width=True)

    if calc_saving:
        if start_wh == end_wh:
            st.error("❌ 起點與終點不能相同")
        else:
            try:
                start_date, end_date = date_range if isinstance(date_range, tuple) else (date_range, date_range)
            except: st.error("請選擇完整日期區間"); st.stop()
            
            days = (end_date - start_date).days + 1
            
            # 獲取對應路段的費率資料
            rates = WH_FREIGHT_DATA.get((start_wh, end_wh), {"46T": 0, "17T": 0})
            fee_46t = rates["46T"]
            fee_17t = rates["17T"]
            total_saving = fee_17t * days

            # 總合計看板
            st.success(f"### 🎊 總節費合計： NT$ {total_saving:,} 元")
            
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("統計天數", f"{days} 天")
            c2.metric("配送路徑", f"{start_wh}➔{end_wh}")
            c3.metric("46T 運費基準", f"${fee_46t:,}")
            c4.metric("每日節省 (17T)", f"${fee_17t:,}")

            st.subheader("📅 每日明細清單 (含 46T/17T 對照)")
            date_list = [(start_date + timedelta(days=x)).strftime('%Y-%m-%d') for x in range(days)]
            df_save = pd.DataFrame({
                "項次": range(1, days + 1),
                "日期": date_list,
                "路段": f"{start_wh}-{end_wh}",
                "46T 運費": [f"${fee_46t:,}"] * days,
                "狀態": ["✅ 成功節省 17T 派車"] * days,
                "當日節省金額": [f"${fee_17t:,}"] * days
            })
            st.table(df_save)

# --- 模組二：路線里程計算機 ---
elif app_mode == "📏 路線里程計算機":
    st.header("📏 路線里程計算機 (含分段拆解)")
    
    col_in, col_res = st.columns([1, 1.2])
    with col_in:
        route_code = st.text_input("路線代碼 (如: 2G)", value="2G").upper().strip()
        zone_type = st.selectbox("區域屬性 (α)", list(ALPHA_MAP.keys()))
        raw_stores = st.text_area("請貼上店名清單", height=200)
        
        is_known = route_code in MILEAGE_GT
        if is_known:
            st.success(f"偵測到實測路線：{MILEAGE_GT[route_code]} km")
            google_km = 0.0
        else:
            google_km = st.number_input("Google Map 總里程", min_value=0.0, value=0.0)
        
        calc_dist = st.button("🚀 生成分段報告")

    if calc_dist:
        stores = [s.strip() for s in raw_stores.split("\n") if s.strip()]
        n = len(stores)
        alpha = ALPHA_MAP[zone_type]
        
        total_dist = MILEAGE_GT[route_code] if is_known else (google_km * alpha if google_km > 0 else (n+1)*15*alpha)
        avg_seg = round(total_dist / (n + 1), 1) if n > 0 else 0

        with col_res:
            st.subheader(f"📊 {route_code} 分析報告")
            st.metric("預估總里程", f"{round(total_dist, 1)} km")
            
            table_data = [["0", "起點", "全台大肚倉", "0.0"]]
            for i, name in enumerate(stores, 1):
                table_data.append([str(i), f"第 {i} 站", name, f"{avg_seg}"])
            table_data.append([str(n+1), "回場", "全台大肚倉", f"{round(total_dist - avg_seg*n, 1)}"])
            st.table(pd.DataFrame(table_data, columns=["Index", "路順", "店名", "分段里程(km)"]))
