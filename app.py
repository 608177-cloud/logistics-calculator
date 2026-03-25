import streamlit as st
import pandas as pd
from datetime import datetime

# --- 網頁配置 ---
st.set_page_config(page_title="物流轉運數據專家系統", layout="wide", page_icon="📊")

# --- 核心資料庫 (依據您的截圖數據修正) ---
WH_DATA = {
    "大肚-大溪": {"46T": 13100, "17T": 7800},
    "大溪-大肚": {"46T": 13100, "17T": 7800},
    "大溪-岡山": {"46T": 18900, "17T": 8100},
    "岡山-大溪": {"46T": 18900, "17T": 8100},
    "大肚-岡山": {"46T": 13600, "17T": 8100},
    "岡山-大肚": {"46T": 13600, "17T": 8100}
}

# --- 側邊欄 ---
st.sidebar.title("🚚 轉運數據決策中心")
app_mode = st.sidebar.radio("請選擇功能模組：", ["💰 批次節費試算", "📏 路線里程計算機"])

if app_mode == "💰 批次節費試算":
    st.header("💰 轉運節費試算 (批次自定義模式)")
    st.markdown("請在下方表格直接編輯每一筆配送的 **日期、路線與板數**。")

    # 1. 初始化資料 (提供範例數據)
    if 'input_df' not in st.session_state:
        st.session_state.input_df = pd.DataFrame([
            {"日期": datetime.now().date(), "路線": "大肚-大溪", "總板數": 35},
            {"日期": datetime.now().date(), "路線": "大肚-岡山", "總板數": 40}
        ])

    # 2. 交互式表格編輯器 (確保鍵名一致)
    edited_df = st.data_editor(
        st.session_state.input_df,
        num_rows="dynamic",
        column_config={
            "日期": st.column_config.DateColumn("配送日期", required=True),
            "路線": st.column_config.SelectboxColumn("車趟路線", options=list(WH_DATA.keys()), required=True),
            "總板數": st.column_config.NumberColumn("總板數 (N)", min_value=0, step=1),
        },
        use_container_width=True
    )

    if st.button("🚀 執行批次分析", use_container_width=True):
        final_results = []
        grand_total = 0

        for _, row in edited_df.iterrows():
            route = row["路線"]
            n = row["總板數"]
            rates = WH_DATA.get(route, {"46T": 0, "17T": 0})
            
            # 核心邏輯判定
            r = n % 30
            if r == 0:
                save_amt, save_type = 0, "無 (滿車)"
            elif 0 < r <= 15:
                save_amt, save_type = rates["17T"], "1趟 17T"
            else:
                save_amt, save_type = rates["46T"], "1趟 46T"
            
            grand_total += save_amt
            # 統一使用 '節省金額' 作為鍵名，避免 KeyError
            final_results.append({
                "日期": str(row["日期"]),
                "路線": route,
                "總板數": n,
                "溢出板數": r,
                "節省車型": save_type,
                "節省金額": save_amt 
            })

        # 3. 顯示總結
        st.markdown("---")
        st.success(f"### 批次總節費合計： NT$ {grand_total:,} 元")

        # 4. 顯示報告 (對齊您的截圖需求)
        st.subheader("📋 節費試算報告 (溢出不加派)")
        for res in final_results:
            with st.container():
                st.markdown(f"""
                **【{res['日期']} | {res['路線']}】**
                * 總計板數：{res['總板數']} 板 (溢出 {res['溢出板數']} 板)
                * 節省費用：{res['節省金額']:,} 元 (成功省下 {res['節省車型']} 費用)
                ---
                """)

        # 5. CSV 導出區
        st.subheader("📊 Excel 專用原始資料 (CSV)")
        st.code(pd.DataFrame(final_results).to_csv(index=False), language="text")

elif app_mode == "📏 路線里程計算機":
    st.header("📏 路線里程計算機")
    st.info("請輸入路線代碼與店名清單進行里程分段拆解。")
    # (此處可貼回之前的里程計算代碼)
