import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- 網頁配置 ---
st.set_page_config(page_title="物流轉運節費分析系統", layout="wide", page_icon="💰")

# --- 1. 費率對照基準 ---
WH_FREIGHT_BASE = {
    "大肚-大溪": {"46T": 13100, "17T": 7800},
    "大溪-大肚": {"46T": 13100, "17T": 7800},
    "大溪-岡山": {"46T": 18900, "17T": 8100},
    "岡山-大溪": {"46T": 18900, "17T": 8100},
    "大肚-岡山": {"46T": 13600, "17T": 8100},
    "岡山-大肚": {"46T": 13600, "17T": 8100}
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

# --- 側邊欄 ---
st.sidebar.title("🚚 轉運數據決策中心")
app_mode = st.sidebar.radio("請選擇功能模組：", ["💰 轉運節費計算", "📏 路線里程計算機"])

# --- 模組一：轉運節費計算 ---
if app_mode == "💰 轉運節費計算":
    st.header("💰 轉運節費計算機 (多日批次分析)")
    
    with st.sidebar:
        st.markdown("---")
        st.subheader("⚙️ 批次參數設定")
        
        # 路線選擇
        route_options = list(WH_FREIGHT_BASE.keys())
        selected_route = st.selectbox("車趟路線", route_options, index=1) 
        
        # 多日板數輸入
        st.info("請輸入每日總板數，用逗號或換行隔開：")
        pallets_text = st.text_area("多日板數錄入", value="35, 40, 50", height=100)
        
        start_date = st.date_input("起始日期", value=datetime.now())
        calc_btn = st.button("🚀 執行多日節費分析", use_container_width=True)

    if calc_btn:
        # 解析輸入的板數
        try:
            # 處理逗號或換行
            raw_list = pallets_text.replace('\n', ',').split(',')
            pallet_list = [int(p.strip()) for p in raw_list if p.strip()]
        except ValueError:
            st.error("❌ 板數格式錯誤，請輸入數字並以逗號隔開。")
            st.stop()

        rates = WH_FREIGHT_BASE[selected_route]
        results = []
        grand_total = 0

        # 核心計算邏輯 (循環處理每一天)
        for i, n_pallets in enumerate(pallet_list):
            curr_date = (start_date + timedelta(days=i)).strftime('%Y-%m-%d')
            
            full_trucks = (n_pallets // 30) * 30
            r_pallets = n_pallets % 30
            
            # 判定邏輯：R<=15 省17T；R>15 省46T (或依分析師手動指定之邏輯)
            if r_pallets == 0:
                save_amt, save_type, last_frag = 0, "無 (滿車)", 0
            elif 0 < r_pallets <= 15:
                save_amt, save_type, last_frag = rates["17T"], "1趟 17T", r_pallets
            else: # R > 15
                save_amt, save_type, last_frag = rates["46T"], "1趟 46T", r_pallets
            
            grand_total += save_amt
            results.append({
                "日期": curr_date,
                "總板數": n_pallets,
                "拆解": f"{full_trucks}板(滿) + {r_pallets}板(溢)",
                "節省車型": save_type,
                "金額": save_amt,
                "最後零頭": last_frag
            })

        # --- 輸出結果 ---
        st.success(f"### 🎊 多日總節費合計： NT$ {grand_total:,} 元")
        
        # 顯示專業點列報告 (針對每一筆錄入)
        st.subheader("📋 節費試算報告 (明細)")
        for res in results:
            with st.expander(f"📅 日期：{res['日期']} | 板數：{res['總板數']} | 節省：${res['金額']:,}"):
                st.markdown(f"""
                * **車趟路線**：{selected_route}
                * **板數拆解**：{res['拆解']}
                * **節省費用**：{res['金額']:,} 元 (成功省下 {res['節省車型']} 費用)
                """)

        # 每日明細表
        st.subheader("📅 數據總覽表")
        df = pd.DataFrame(results)
        st.table(df[["日期", "總板數", "節省車型", "金額"]])

        # CSV 原始資料 (方便貼回 Excel)
        st.markdown("---")
        st.subheader("📊 Excel 專用原始資料 (CSV)")
        csv_str = "日期,路線,總板數,溢出零頭,節省車型,節省費用\n"
        for res in results:
            csv_str += f"{res['日期']},{selected_route},{res['總板數']},{res['最後零頭']},{res['節省車型']},{res['金額']}\n"
        st.code(csv_str, language="text")

# --- 模組二：路線里程計算機 (畫面不動) ---
elif app_mode == "📏 路線里程計算機":
    st.header("📏 路線里程計算機")
    # ... (里程計算程式碼保持不變) ...
