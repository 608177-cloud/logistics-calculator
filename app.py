import streamlit as st
import pandas as pd
from datetime import datetime

# --- 網頁配置 ---
st.set_page_config(page_title="物流轉運數據專家系統", layout="wide", page_icon="📊")

# --- 核心資料庫 (根據 Excel 費率設定) ---
WH_DATA = {
    "大肚-大溪": {"46T": 13100, "17T": 7800},
    "大溪-大肚": {"46T": 13100, "17T": 7800},
    "大溪-岡山": {"46T": 18900, "17T": 8100},
    "岡山-大溪": {"46T": 18900, "17T": 8100},
    "大肚-岡山": {"46T": 13600, "17T": 8100},
    "岡山-大肚": {"46T": 13600, "17T": 8100}
}

# --- 側邊欄：功能導航 ---
st.sidebar.title("🚚 轉運數據決策中心")
app_mode = st.sidebar.radio("請選擇功能模組：", ["💰 批次節費試算", "📏 路線里程計算機"])

if app_mode == "💰 批次節費試算":
    st.header("💰 轉運節費試算 (批次自定義模式)")
    st.markdown("請在下方表格編輯每筆配送。**預設僅顯示一排**，可自行新增或刪除列。")

    # 1. 初始化資料庫 (預設僅 1 排)
    if 'input_table' not in st.session_state:
        st.session_state.input_table = pd.DataFrame([
            {"配送日期": datetime.now().date(), "車趟路線": "大肚-大溪", "總板數": 0}
        ])

    # 2. 交互式表格編輯器
    # 使用 dynamic 模式支援新增與刪除
    edited_df = st.data_editor(
        st.session_state.input_table,
        num_rows="dynamic",
        column_config={
            "配送日期": st.column_config.DateColumn("配送日期", required=True, format="YYYY-MM-DD"),
            "車趟路線": st.column_config.SelectboxColumn("車趟路線", options=list(WH_DATA.keys()), required=True),
            "總板數": st.column_config.NumberColumn("總板數 (N)", min_value=0, step=1, required=True),
        },
        use_container_width=True,
        hide_index=True  # 隱藏索引讓畫面更像截圖
    )

    if st.button("🚀 執行批次分析", use_container_width=True):
        final_results = []
        grand_total = 0

        for _, row in edited_df.iterrows():
            # 跳過未填寫板數的空白行
            if row["總板數"] <= 0: continue
            
            route = row["車趟路線"]
            n = row["總板數"]
            rates = WH_DATA.get(route, {"46T": 0, "17T": 0})
            
            # 溢出不加派逻辑
            r = n % 30
            if r == 0:
                save_amt, save_type = 0, "無 (滿車)"
            elif 0 < r <= 15:
                save_amt, save_type = rates["17T"], "1 趟 17T"
            else:
                save_amt, save_type = rates["46T"], "1 趟 46T"
            
            grand_total += save_amt
            final_results.append({
                "日期": str(row["配送日期"]),
                "路線": route,
                "總板數": n,
                "溢出板數": r,
                "節省車型": save_type,
                "節省金額": save_amt
            })

        if final_results:
            # 3. 顯示結果看板
            st.markdown("---")
            st.success(f"### 🏆 批次總節費合計： NT$ {grand_total:,} 元")

            # 4. 顯示明細報告
            st.subheader("📋 節費試算報告 (溢出不加派)")
            for res in final_results:
                st.info(f"""
                **【{res['日期']} | {res['路線']}】**
                * 總計板數：{res['總板數']} 板 (溢出 {res['溢出板數']} 板)
                * 節省費用：{res['節省金額']:,} 元 (省下 {res['節省車型']})
                """)

            # 5. CSV 原始資料
            st.code(pd.DataFrame(final_results).to_csv(index=False), language="text")
        else:
            st.warning("請先在表格中輸入板數數據。")

elif app_mode == "📏 路線里程計算機":
    st.header("📏 路線里程計算機")
    st.info("請輸入路線代碼與店名清單進行里程分析。")
