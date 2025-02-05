import os
import json
import requests
import datetime
import re

# ----------------------------------------------------------------------
# 1. 讀取 Notion Token & Page ID 設定
# ----------------------------------------------------------------------
with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

NOTION_TOKEN = "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"
# NOTION_TOKEN = os.environ["NOTION_TOKEN"] 
ROOT_PAGE_ID = "166fbb857f9e80eba96ef0091d6ce244"  # 你的最上層 Notion Page ID

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28"
}

# ----------------------------------------------------------------------
# 2. 取得頁面標題 (選擇用 retrieve_page，或直接從 child_page["title"] 取)
# ----------------------------------------------------------------------
def retrieve_page_title(page_id: str) -> str:
    """
    嘗試從 Notion `retrieve_page` API 取得該頁面真正標題。
    若結構複雜，請依實際情況修改。
    """
    url = f"https://api.notion.com/v1/pages/{page_id}"
    res = requests.get(url, headers=HEADERS)
    data = res.json()
    # 這邊假設屬性名稱就是 "title"（若是資料庫頁面有時不同）
    try:
        title_obj = data["properties"]["title"]["title"]
        if title_obj:
            return title_obj[0]["plain_text"]
    except:
        pass
    return "Untitled"


# ----------------------------------------------------------------------
# 3. 取得某頁面下的所有區塊 (含分頁處理)
# ----------------------------------------------------------------------
def fetch_notion_blocks(page_id: str) -> list:
    """
    回傳所有 blocks（list），不包含子頁面下層
    """
    all_blocks = []
    base_url = "https://api.notion.com/v1/blocks"
    url = f"{base_url}/{page_id}/children"
    params = {}

    while True:
        resp = requests.get(url, headers=HEADERS, params=params)
        data = resp.json()
        results = data.get("results", [])
        all_blocks.extend(results)

        if data.get("has_more"):
            params["start_cursor"] = data["next_cursor"]
        else:
            break

    return all_blocks


# ----------------------------------------------------------------------
# 4. 將單一 block 轉成 Markdown（忽略 child_page）
# ----------------------------------------------------------------------
def block_to_markdown(block: dict) -> str:
    """
    僅示範最常見的 paragraph, heading, etc.
    你可將你原本的轉換邏輯複製來這裡
    """
    btype = block.get("type", "")
    if btype == "paragraph":
        texts = block[btype].get("rich_text", [])
        paragraph_text = "".join(t.get("plain_text", "") for t in texts)
        return paragraph_text + "\n\n"

    elif btype == "heading_1":
        texts = block[btype].get("rich_text", [])
        heading_text = "".join(t.get("plain_text", "") for t in texts)
        return f"# {heading_text}\n\n"

    elif btype == "heading_2":
        texts = block[btype].get("rich_text", [])
        heading_text = "".join(t.get("plain_text", "") for t in texts)
        return f"## {heading_text}\n\n"

    elif btype == "heading_3":
        texts = block[btype].get("rich_text", [])
        heading_text = "".join(t.get("plain_text", "") for t in texts)
        return f"### {heading_text}\n\n"
    elif btype == "equation":
        equation_text = block[btype].get("expression", "")
        return f"$$\n{equation_text}\n$$\n\n"

    elif btype == "bulleted_list_item":
        texts = block[btype].get("rich_text", [])
        list_text = "".join(t.get("plain_text", "") for t in texts)
        return f"- {list_text}\n"

    elif btype == "numbered_list_item":
        texts = block[btype].get("rich_text", [])
        list_text = "".join(t.get("plain_text", "") for t in texts)
        return f"1. {list_text}\n"

    # 若遇到 child_page，就不在這裡轉 Markdown，
    # 而是交給外層做遞迴，以產生新的文章檔案
    if btype == "child_page":
        return ""

    # ... 其餘像 code, image, divider, quote 都可自行加入
    # ... 這裡省略

    return ""


# ----------------------------------------------------------------------
# 5. 遞迴函式：parse_and_export_recursively()
# ----------------------------------------------------------------------
def parse_and_export_recursively(page_id: str, parent_slug: str = None):
    # 取得頁面標題
    page_title = retrieve_page_title(page_id)

    # 取得頁面內容 Blocks
    blocks = fetch_notion_blocks(page_id)
    page_markdown_parts = []
    child_pages = []

    for block in blocks:
        btype = block.get("type", "")
        if btype == "child_page":
            child_pages.append(block)
        else:
            page_markdown_parts.append(block_to_markdown(block))

    # 合成 Markdown 內容
    page_markdown = "".join(page_markdown_parts)

    # 確定 slug
    slug = page_title.replace(" ", "-").lower()
    if parent_slug:
        slug = f"{parent_slug}-{slug}"

    # 使用 upsert_post_with_date_update() 更新檔案
    upsert_post_with_date_update(slug, page_title, page_markdown, categories=["NotionExport"])

    # 處理子頁面
    for child_block in child_pages:
        child_id = child_block["id"]
        child_title = child_block["child_page"]["title"]
        parse_and_export_recursively(child_id, parent_slug=slug)



def upsert_post_with_date_update(slug, title, new_markdown, categories=None):
    """
    將 new_markdown 寫入 _posts/yyyy-mm-dd-{slug}.md。
    若檔案已存在，且內文有變動，則更新 front matter 的 date 為今日。
    """
    if not os.path.exists("_posts"):
        os.makedirs("_posts")

    # 預設每篇文章檔名中的日期, 你可以用 old front matter date 也可
    # 或一律用今天, 後面會再自動更新 date: 依變動判斷
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    filename = f"_posts/{today_str}-{slug}.md"
    
    # 避免標題中的雙引號問題
    safe_title = title.replace('"', '\\"')  # 確保雙引號被正確轉義

    # 確保 categories 是正確的 YAML 列表格式
    categories_str = ", ".join([f'"{c}"' for c in categories]) if categories else '"NotionExport"'

    # 生成正確的 front matter 格式
    new_front_matter = f"""---
    layout: post
    title: "{safe_title}"
    date: {today_str} 10:00:00 +0800
    categories: [{categories_str}]
    ---
    """


    new_full_content = new_front_matter + "\n" + new_markdown

    if not os.path.exists(filename):
        # 檔案不存在 => 全新文章 => 直接寫檔
        with open(filename, "w", encoding="utf-8") as f:
            f.write(new_full_content)
        print(f"[NEW] Created file: {filename}")
    else:
        # 檔案已存在 => 讀取舊檔, 分析是否有更新
        with open(filename, "r", encoding="utf-8") as f:
            old_full_content = f.read()

        # 分離舊 front matter 與舊內文
        # 例如用簡單正則: ^---(.*?)--- 來擷取 front matter
        # 這裡是示範, 你可以用 ruamel.yaml 或 pyyaml 做更嚴謹的解析
        match = re.search(r"(?s)^---(.*?)---(.*)$", old_full_content)
        if match:
            old_front = match.group(1)
            old_body = match.group(2).strip()
        else:
            # 如果沒找到 front matter, 全部當作 body
            old_front = ""
            old_body = old_full_content.strip()

        # 比對 new_markdown vs old_body
        if old_body != new_markdown.strip():
            # 有變動 => 更新 date
            new_today_str = datetime.datetime.now().strftime("%Y-%m-%d")
            updated_front_matter = re.sub(
                r"(date:\s*)(.*)",
                rf"\1{new_today_str} 10:00:00 +0800",
                old_front
            )
            # 如果你要保留原本 front matter 的其他欄位, 只改 date
            # 這裡用正則簡易替換, 但需確保 date: 這行存在

            # 產生新的全文
            new_old_front = f"---\n{updated_front_matter}\n---\n\n"
            updated_full = new_old_front + new_markdown

            with open(filename, "w", encoding="utf-8") as f:
                f.write(updated_full)
            print(f"[UPDATE] {filename} content changed, date updated to {new_today_str}")
        else:
            print(f"[NO CHANGE] {filename} remains the same.")

# ----------------------------------------------------------------------
# 7. Main：指定最上層頁面ID，開始遞迴
# ----------------------------------------------------------------------
def main():
    parse_and_export_recursively(ROOT_PAGE_ID)
    print("🎉 全部頁面（含子頁面）匯出完成！")

if __name__ == "__main__":
    main()
