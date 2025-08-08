# Olist 電商分析作品集

## 🎯 專案概述
**端對端分析解決方案**，將原始巴西電商數據轉化為可執行的商業洞察。此作品集專案展示先進的數據科學能力，包括客戶分析、預測建模和商業智能儀表板開發。

🎯 **專案目標**: 建立全面的客戶分析平台，識別高價值客戶，預測流失風險，並提供具體的收益優化策略。

### 商業影響亮點
- 💎 **客戶分群**: RFM 分析識別冠軍客戶 (17%) 驅動 30% 收益
- 📈 **留存智能**: 同期群分析揭示 $50K+ 風險客戶價值
- 🎯 **收益優化**: LTV 建模預估 15-25% 收益提升
- 📊 **互動洞察**: 利害關係人就緒的儀表板配有白話解釋

## 📊 主要功能
- **RFM 分析**: 客戶分群與可執行建議
- **同期群分析**: 留存模式和收益同期群追蹤
- **LTV 預測**: 客戶生命週期價值機器學習模型
- **行銷歸因**: 多點觸控歸因建模
- **互動儀表板**: 即時 KPI 監控和視覺化

## 🛠️ 技術架構
- **數據處理**: Python (pandas, numpy, scipy)
- **資料庫**: PostgreSQL 星型架構設計
- **ML/分析**: scikit-learn, lifetimes
- **視覺化**: Plotly, Dash, Tableau
- **測試**: pytest, Great Expectations
- **編排**: Apache Airflow (選用)

## 📁 專案結構
```
olist_analytics/
├── data/               # 原始和處理過的數據
├── notebooks/          # Jupyter 筆記本用於分析
├── src/               # 原始碼
│   ├── data_ingestion/    # 數據載入和驗證
│   ├── transformations/   # ETL 和特徵工程
│   ├── analytics/         # 核心分析模組
│   ├── visualizations/    # 儀表板組件
│   └── utils/            # 輔助函數
├── tests/             # 單元和整合測試
├── docs/              # 文檔
├── dashboards/        # 儀表板配置
└── outputs/           # 結果和報告
```

## 🚀 快速開始

### 先決條件
- Python 3.8+
- PostgreSQL (選用，可使用 SQLite)
- Git

### 安裝
```bash
# 複製儲存庫
git clone [repository-url]
cd olist_analytics

# 建立虛擬環境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安裝相依套件
pip install -r requirements.txt

# 下載 Olist 數據集
python scripts/download_data.py
```

### 執行分析
```bash
# 執行完整分析流程
python src/main.py --analysis all

# 執行特定分析
python src/main.py --analysis rfm
python src/main.py --analysis cohort
python src/main.py --analysis ltv
```

### 🎥 現場演示
```bash
# 啟動互動儀表板
python launch_dashboard.py
# 在瀏覽器開啟 http://localhost:8050
```

**🎯 您將看到的內容:**
- **概述頁籤**: 關鍵指標和業務健康指標
- **同期群分析**: 互動留存熱力圖與解釋
- **RFM 分析**: 客戶分群與行動計劃
- **LTV 分析**: 客戶價值分佈和洞察
- **洞察頁籤**: 高管摘要與投資回報率預測

> 💡 **演示提示**: 儀表板包含「這對您的業務意味著什麼」部分，將技術圖表轉化為業務行動！

## 📈 主要成果

### 客戶洞察
- **17.4%** 的客戶 (冠軍) 產生 **30.4%** 的總收益
- **27.1%** 第一個月留存率 (達到行業基準)
- **$50,738** 風險客戶分群的收益風險

### 績效指標
- **287** 位客戶完整購買旅程分析
- **$940.42** 平均客戶生命週期價值
- **3.48** 每位客戶平均訂單數
- **$268.27** 平均訂單價值

### 商業機會
- **$12,684** 潛在挽回收益 (25% 成功率)
- **15-25%** 建議預估收益提升
- **20-30%** 客戶 LTV 改善潛力
- **+5-10 百分點** 留存率改善目標

## 🧪 測試
```bash
# 執行所有測試
pytest

# 執行覆蓋率測試
pytest --cov=src --cov-report=html

# 執行特定測試套件
pytest tests/test_rfm.py
```

## 📚 文檔
- [技術文檔](docs/technical.md)
- [商業洞察報告](docs/insights.md)
- [API 參考](docs/api.md)
- [儀表板使用指南](docs/dashboard_guide.md)

## 🎯 未來增強
- [ ] 即時串流分析
- [ ] 進階 ML 模型 (深度學習)
- [ ] A/B 測試框架
- [ ] 推薦引擎
- [ ] 自動化報告系統

## 👤 作者
**您的姓名**
- LinkedIn: [profile-link]
- GitHub: [@username]
- Email: email@example.com

## 📄 授權
此專案採用 MIT 授權 - 詳見 [LICENSE](LICENSE) 檔案。

## 🙏 致謝
- Olist 提供數據集
- Kaggle 社群的洞察
- [原始 RFM 筆記本](https://www.kaggle.com/code/alpamys/rfm-cohort-analysis) 由 alpamys 提供

---
*此作品集專案展示數據工程、分析、機器學習和商業智能的熟練度。*