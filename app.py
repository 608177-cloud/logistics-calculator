import pandas as pd
from datetime import datetime

class CentralLogisticsAnalyst:
    def __init__(self):
        # 1. 轉運費率基準 (大肚/大溪/岡山)
        self.transfer_rates = {
            "大肚-大溪": {"46T": 13100, "17T": 7800},
            "大溪-岡山": {"46T": 18900, "17T": 8100},
            "大肚-岡山": {"46T": 13600, "17T": 8100}
        }
        
        # 2. 里程實測基準與係數 (Alpha)
        self.verified_routes = {
            "IN": {"name": "嘉義沿海", "km": 260.0, "alpha": 1.45},
            "IR": {"name": "國姓/魚池", "km": 199.3, "alpha": 1.45},
            "2G": {"name": "彰化南部", "km": 105.7, "alpha": 1.20},
            "2J": {"name": "烏日", "km": 57.8, "alpha": 1.05}
        }
        self.alpha_presets = {"long": 1.45, "plain": 1.20, "urban": 1.15}

    # --- 功能一：轉運節費分析 ---
    def analyze_savings(self, total_pallets, route="大肚-大溪"):
        rate_info = self.transfer_rates.get(route, self.transfer_rates["大肚-大溪"])
        cost_17t = rate_info["17T"]
        
        full_30 = total_pallets // 30
        r = total_pallets % 30
        
        savings = 0
        saving_type = "無節省"
        remainder_csv = 0

        if 0 < r <= 15:
            savings = cost_17t
            saving_type = "0.5 趟 (17T)"
            remainder_csv = r
        elif r > 15:
            savings = cost_17t
            saving_type = "0.5 趟 (17T)"
            remainder_csv = r - 15

        print(f"### 💰 轉運節費報告：{route}")
        print(f"- 總板數：{total_pallets} | 拆解：{full_30}滿車 + 餘{r}板")
        print(f"- 節省金額：${savings:,} ({saving_type})")
        return {"route": route, "pallets": total_pallets, "savings": savings, "rem": remainder_csv}

    # --- 功能二：里程與路順預估 ---
    def estimate_mileage(self, route_code, stops, map_km=None, mode="plain"):
        status = "Agent 加權預估"
        alpha = self.alpha_presets.get(mode, 1.20)
        
        if route_code in self.verified_routes:
            d_real = self.verified_routes[route_code]["km"]
            alpha = self.verified_routes[route_code]["alpha"]
            status = "實測確值"
        else:
            d_real = round(map_km * alpha, 1) if map_km else 0
            
        print(f"### 🚚 里程動態報告：[{route_code}]")
        print(f"- 數據狀態：{status} (α={alpha})")
        print(f"| 順序 | 站點 | 累計里程(km) |")
        print(f"| :--- | :--- | :---: |")
        print(f"| 起點 | 全台大肚倉 | 0.0 |")
        
        # 簡易閉環分配顯示
        avg = round(d_real / (len(stops) + 1), 1)
        for i, stop in enumerate(stops, 1):
            print(f"| {i} | {stop} | {avg * i:.1f} |")
        print(f"| 回場 | 全台大肚倉 | {d_real} |")
        print(f"- **總預估里程：{d_real} km**\n")
        return d_real

# --- 執行示範 ---
expert = CentralLogisticsAnalyst()

# 1. 先算轉運節費
transfer_data = expert.analyze_savings(total_pallets=47, route="大溪-岡山")

print("-" * 30)

# 2. 再算配送路順里程 (假設這是接續的配送任務)
mileage_data = expert.estimate_mileage("2B", ["苗栗店", "頭份店"], map_km=95.0, mode="long")
