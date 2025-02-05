import os
import json
import requests
import datetime

# ----------------------------------------------------------------------
# 1. 讀取 Notion Token & Page ID 設定
# ----------------------------------------------------------------------
with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

NOTION_TOKEN = os.environ["NOTION_TOKEN"] 
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
    """
    一邊遞迴處理，一邊匯出 Markdown 檔：
      1. 取得當前頁面標題 + blocks
      2. 非 child_page block -> 拼成 Markdown
      3. 輸出成一篇 _posts/xxx.md
      4. 若發現 child_page -> 對其做遞迴
    parent_slug: 用來把父層 slug 帶下去 (可做分類等)
    """

    # 1. 先取得頁面標題
    page_title = retrieve_page_title(page_id)  # or "block['child_page']['title']"

    # 2. 取得頁面 blocks
    blocks = fetch_notion_blocks(page_id)
    page_markdown_parts = []
    child_pages = []

    # 分開「非子頁面」跟「子頁面」
    for block in blocks:
        btype = block.get("type", "")
        if btype == "child_page":
            child_pages.append(block)
        else:
            page_markdown_parts.append(block_to_markdown(block))

    page_markdown = "".join(page_markdown_parts)

    # 3. 在 _posts/ 寫檔
    if not os.path.exists("_posts"):
        os.makedirs("_posts")

    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    # 生成 slug
    slug = page_title.replace(" ", "-").lower()
    if parent_slug:
        slug = f"{parent_slug}-{slug}"

    filename = f"_posts/{today_str}-{slug}.md"

    with open(filename, "w", encoding="utf-8") as fp:
        fp.write("---\n")
        fp.write("layout: post\n")
        fp.write(f"title: \"{page_title}\"\n")
        fp.write(f"date: {today_str} 10:00:00 +0800\n")
        if parent_slug:
            fp.write(f"categories: [{parent_slug}]\n")
        else:
            fp.write("categories: [NotionExport]\n")
        fp.write("---\n\n")
        fp.write(page_markdown)

    print(f"✅ 已輸出: {filename}")

    # 4. 子頁面 => 遞迴
    for child_block in child_pages:
        child_id = child_block["id"]
        child_title = child_block["child_page"]["title"]  # 也可用 retrieve_page_title
        parse_and_export_recursively(child_id, parent_slug=slug)


# ----------------------------------------------------------------------
# 6. Main：指定最上層頁面ID，開始遞迴
# ----------------------------------------------------------------------
def main():
    parse_and_export_recursively(ROOT_PAGE_ID)
    print("🎉 全部頁面（含子頁面）匯出完成！")

if __name__ == "__main__":
    main()
