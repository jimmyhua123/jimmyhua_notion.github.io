這是你的專案 README 文件：


# Jimmy Hua's Notion Export

這個專案使用 Jekyll 主題 **Not Pure Poole**，並透過 GitHub Actions 自動同步 Notion 筆記，轉換為 Markdown，並發布到 GitHub Pages。

## 專案概述

- **主題**: [Not Pure Poole](https://github.com/vszhub/not-pure-poole)
- **網站地址**: [Jimmy Hua's Notion Export](https://jimmyhua123.github.io/jimmyhua_notion.github.io)
- **自動同步**: 每日從 Notion 獲取內容，轉換為 Markdown，並發布至 `_posts/`

## 目錄結構


jimmyhua_notion.github.io/
├── _config.yml              # Jekyll 設定檔
├── _posts/                  # 存放 Notion 匯出的 Markdown 文章
│   ├── 2024-01-01-example.md
│   └── ...
├── _layouts/                # Jekyll 版型
│   ├── default.html
│   ├── post.html
│   └── ...
├── _includes/               # Jekyll 內嵌模板
│   ├── head.html
│   ├── sidebar.html
│   ├── footer.html
│   └── ...
├── _sass/                   # 樣式文件
├── assets/                  # 靜態資源 (CSS, JS, images)
├── .github/
│   └── workflows/
│       └── notion_daily.yml # GitHub Actions 自動同步腳本
├── avatar.jpeg      # 頭像
├── bg.jpeg          # 背景圖
├── 404.html                 # 404 頁面
├── index.html               # 首頁
├── dates.md                 # 日期歸檔
├── categories.md            # 分類歸檔
├── tags.md                  # 標籤歸檔
├── notion_to_markdown.py    # Notion 轉 Markdown 腳本
└── README.md                # 本文件


## 設定與使用

### 1. 安裝與開發環境

請確保已安裝 **Ruby** 和 **Bundler**，然後執行：

```sh
bundle install
```

啟動本地 Jekyll 伺服器：

```sh
bundle exec jekyll serve
```

網站將運行在 `http://localhost:4000`。

### 2. 自動同步 Notion 筆記

**GitHub Actions** 每日自動執行 `notion_to_markdown.py`，步驟如下：

- 使用 `requests` API 連接 Notion
- 轉換內容為 Markdown
- 儲存至 `_posts/` 並推送到 GitHub

你可以手動執行同步：

```sh
python notion_to_markdown.py
```

### 3. 佈署到 GitHub Pages

Jekyll 會自動將 `_posts/` 中的 Markdown 轉為靜態網站。若要手動更新 GitHub Pages，請執行：

```sh
git add .
git commit -m "更新 Notion 筆記"
git push
```

## 設定檔 `_config.yml`

- **網站標題**: `Jimmy Hua's Notion Export`
- **Jekyll 佈景主題**: `not-pure-poole`
- **社交連結**:
  - GitHub: [jimmyhua123](https://github.com/jimmyhua123)
- **數學公式支援**: MathJax
- **語言**: `zh-TW`

## 其他功能

- **日期、分類、標籤歸檔**: 透過 `dates.md`、`categories.md`、`tags.md` 管理文章
- **深色模式**: 根據系統設定自動啟用


## 授權

本專案採用 [MIT License](https://opensource.org/licenses/MIT)。

---

💡 **專案作者**: Jimmy Hua  
📧 **Email**: [jimmy0624062461@gmail.com](mailto:jimmy0624062461@gmail.com)


這份 README 清楚說明了專案的功能、目錄結構、安裝步驟、同步 Notion 的方法，以及 GitHub Pages 部署方式。如果需要進一步修改或補充，請告訴我！🚀