import json
import requests

# 讀取配置檔案
with open("config.json", "r") as file:
    config = json.load(file)

NOTION_TOKEN = config["notion_token"]  # 請替換為你的 Notion Integration Token
PAGE_ID = "166fbb857f9e80eba96ef0091d6ce244"  # 請替換為你的 Notion Page ID

# 設定 Notion API URL 和標頭
HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def fetch_notion_blocks(block_id: str) -> dict:
    """
    向 Notion API 請求指定 block_id 底下的所有子區塊，並自動處理分頁 (pagination)。
    最終回傳形式與官方結構類似，如 {"results": [...]}。
    """
    all_results = []
    base_url = "https://api.notion.com/v1/blocks"
    url = f"{base_url}/{block_id}/children"
    params = {}

    while True:
        response = requests.get(url, headers=HEADERS, params=params)
        data = response.json()

        # 如果需要除錯，可以 print(data) 檢查是否拿到正確的 JSON
        results = data.get("results", [])
        all_results.extend(results)

        # 檢查是否有下一頁
        if data.get("has_more"):
            params["start_cursor"] = data["next_cursor"]
        else:
            break

    # 為了與原程式裡 "main_content" 之後使用 .get("results") 一致，這裡回傳相同結構
    return {"results": all_results}


def block_to_markdown(block: dict) -> str:
    """
    將單一 Notion block 轉成 Markdown 格式。
    若偵測到 child_page，則遞迴呼叫 fetch_notion_blocks() 取得其下層區塊，並繼續轉換。
    """
    block_type = block.get("type", "")
    try:
        if block_type == "paragraph":
            texts = block[block_type].get("rich_text", [])
            paragraph_text = "".join(t.get("plain_text", "") for t in texts)
            return paragraph_text + "\n\n"

        elif block_type == "heading_1":
            texts = block[block_type].get("rich_text", [])
            heading_text = "".join(t.get("plain_text", "") for t in texts)
            return f"# {heading_text}\n\n"

        elif block_type == "heading_2":
            texts = block[block_type].get("rich_text", [])
            heading_text = "".join(t.get("plain_text", "") for t in texts)
            return f"## {heading_text}\n\n"

        elif block_type == "heading_3":
            texts = block[block_type].get("rich_text", [])
            heading_text = "".join(t.get("plain_text", "") for t in texts)
            return f"### {heading_text}\n\n"

        elif block_type == "bulleted_list_item":
            texts = block[block_type].get("rich_text", [])
            list_text = "".join(t.get("plain_text", "") for t in texts)
            return f"- {list_text}\n"

        elif block_type == "numbered_list_item":
            texts = block[block_type].get("rich_text", [])
            list_text = "".join(t.get("plain_text", "") for t in texts)
            return f"1. {list_text}\n"
        elif block_type == "equation":
            equation_text = block[block_type].get("expression", "")
            return f"$$\n{equation_text}\n$$\n\n"

        elif block_type == "quote":
            texts = block[block_type].get("rich_text", [])
            quote_text = "".join(t.get("plain_text", "") for t in texts)
            return f"> {quote_text}\n\n"

        elif block_type == "code":
            language = block[block_type].get("language", "")
            texts = block[block_type].get("rich_text", [])
            code_content = "".join(t.get("plain_text", "") for t in texts)
            return f"```{language}\n{code_content}\n```\n\n"

        elif block_type == "divider":
            return "---\n\n"

        elif block_type == "image":
            # 判斷是 external 還是 file
            if "external" in block[block_type]:
                image_url = block[block_type]["external"]["url"]
            else:
                image_url = block[block_type]["file"]["url"]
            return f"![Image]({image_url})\n\n"

        elif block_type == "child_page":
            # 代表子頁面
            page_title = block["child_page"]["title"]
            child_page_id = block["id"].replace("-", "")
            page_url = f"https://www.notion.so/{child_page_id}"

            child_blocks_data = fetch_notion_blocks(block["id"])
            child_markdown = f"## 子頁面: [{page_title}]({page_url})\n\n"
            
            # 遞迴處理子頁面裡的所有區塊
            for cb in child_blocks_data.get("results", []):
                child_markdown += block_to_markdown(cb)
            
            return child_markdown

        else:
            # 如果遇到尚未支援的 block type
            return f"<!-- Unsupported block type: {block_type} -->\n\n"

    except KeyError:
        # 某些區塊資料結構不齊全
        return f"<!-- Error parsing block type: {block_type} -->\n\n"


def save_to_markdown(content: str, file_name="output.md"):
    """將內容儲存為 Markdown 文件"""
    with open(file_name, "w", encoding="utf-8") as file:
        file.write(content)
    print(f"✅ Markdown 文件已儲存為 {file_name}")


def main():
    # 獲取主頁面內容
    main_content = fetch_notion_blocks(PAGE_ID)
    markdown_content = ""

    if main_content:
        for block in main_content["results"]:
            markdown_content += block_to_markdown(block)

    # 將轉換好的 Markdown 儲存到本地
    save_to_markdown(markdown_content, "output.md")


if __name__ == "__main__":
    main()
