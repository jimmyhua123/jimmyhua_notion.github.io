
import json
import requests

# 讀取配置檔案
with open("config.json", "r") as file:
    config = json.load(file)

NOTION_TOKEN = config["notion_token"]
PAGE_ID = "166fbb857f9e80eba96ef0091d6ce244"  # 替換為你的 Notion 頁面 ID

# 設定 API URL
url = f"https://api.notion.com/v1/pages/{PAGE_ID}"

# 設定請求標頭
headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

# 發送 GET 請求
response = requests.get(url, headers=headers)

# 輸出 API 回應
if response.status_code == 200:
    print("✅ Notion API 連線成功！")
    print(json.dumps(response.json(), indent=4, ensure_ascii=False))
else:
    print(f"❌ 連線失敗，狀態碼: {response.status_code}")
    print(response.text)
