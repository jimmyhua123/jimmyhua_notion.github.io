import os
import json
import requests
import datetime
import re
import glob

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
    try:
        res = requests.get(url, headers=HEADERS)
        data = res.json()
        title_obj = data["properties"]["title"]["title"]
        if title_obj:
            return title_obj[0]["plain_text"]
    except (KeyError, IndexError, requests.exceptions.RequestException) as e:
        print(f"⚠️ 無法獲取頁面標題：{e}")
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
def rich_text_array_to_markdown(rich_text_array: list) -> str:
    """
    處理 notion API 回傳的 rich_text 陣列，將超連結轉為 Markdown 格式。
    - 如果該 text 有 link，就回傳 [文字](連結)
    - 否則就直接回傳文字
    """
    md_text_parts = []
    for rt in rich_text_array:
        text_content = rt.get("plain_text", "")
        link_url = None

        # 正確獲取超連結
        if rt.get("href"):  # 第一種可能
            link_url = rt.get("href")
        elif rt.get("text") and rt["text"].get("link"):  # 第二種可能
            link_url = rt["text"]["link"].get("url")

        if link_url:
            md_text_parts.append(f"[{text_content}]({link_url})")
        else:
            md_text_parts.append(text_content)

    return "".join(md_text_parts)


def block_to_markdown(block: dict, article_title: str = "untitled") -> str:
    """
    將單一個 notion block 轉為 Markdown 的字串。
    僅示範常見的 paragraph, heading, bulleted_list_item, numbered_list_item, 
    equation, code, image, divider, quote, etc.
    如需 child_page, child_database 則視情況自行處理。
    """
    btype = block.get("type", "")
    # 1. 段落 paragraph
    if btype == "paragraph":
        texts = block[btype].get("rich_text", [])
        paragraph_text = rich_text_array_to_markdown(texts)
        return paragraph_text + "\n\n"

    # 2. 標題 heading_1 / heading_2 / heading_3
    elif btype == "heading_1":
        texts = block[btype].get("rich_text", [])
        heading_text = rich_text_array_to_markdown(texts)
        return f"# {heading_text}\n\n"

    elif btype == "heading_2":
        texts = block[btype].get("rich_text", [])
        heading_text = rich_text_array_to_markdown(texts)
        return f"## {heading_text}\n\n"

    elif btype == "heading_3":
        texts = block[btype].get("rich_text", [])
        heading_text = rich_text_array_to_markdown(texts)
        return f"### {heading_text}\n\n"

    # 3. 處理清單 bulleted_list_item / numbered_list_item
    elif btype == "bulleted_list_item":
        texts = block[btype].get("rich_text", [])
        children = block.get("has_children", False)  # 是否有子內容
        list_text = rich_text_array_to_markdown(texts)

        if children:
            sub_blocks = fetch_notion_blocks(block["id"])  # 獲取子區塊
            sub_texts = [block_to_markdown(sub) for sub in sub_blocks]
            sub_content = "\n  ".join(sub_texts)  # 縮排處理
            return f"- {list_text}\n  {sub_content}\n"
        else:
            return f"- {list_text}\n"


    elif btype == "numbered_list_item":
        texts = block[btype].get("rich_text", [])
        children = block.get("has_children", False)
        list_text = rich_text_array_to_markdown(texts)

        if children:
            sub_blocks = fetch_notion_blocks(block["id"])
            sub_texts = [block_to_markdown(sub) for sub in sub_blocks]
            sub_content = "\n  ".join(sub_texts)
            return f"1. {list_text}\n  {sub_content}\n"
        else:
            return f"1. {list_text}\n"


    # 4. 數學方程式 equation
    elif btype == "equation":
        equation_text = block[btype].get("expression", "")
        return f"$$\n{equation_text}\n$$\n\n"

    # 5. 程式碼 code
    elif btype == "code":
        texts = block[btype].get("rich_text", [])
        code_text = "".join(rich_text_array_to_markdown([t]) for t in texts)
        language = block[btype].get("language", "plaintext")
        return f"```{language}\n{code_text}\n```\n\n"

    # 6. 圖片 image
    if btype == "image":
        image_data = block[btype]
        if image_data.get("type") == "external":
            url = image_data["external"].get("url", "")
        else:
            url = image_data["file"].get("url", "")

        # 確保 URL 去掉 AWS 簽名參數
        url = url.split("?")[0]

        # 基於文章標題生成圖片前綴
        image_prefix = article_title.replace(" ", "_").lower()
        image_filename = f"{image_prefix}_image.png"

        local_path = f"assets/images/{image_filename}"
        try:
            img_data = requests.get(url).content
            with open(local_path, "wb") as img_file:
                img_file.write(img_data)
            print(f"✅ 圖片下載成功: {local_path}")
        except Exception as e:
            print(f"⚠️ 圖片下載失敗: {e}")

        baseurl = "/jimmyhua_notion.github.io"  # 與 _config.yml 的 baseurl 一致
        return f"![image]({baseurl}/assets/images/{image_filename})\n\n"
    # 7. 分隔線 divider
    elif btype == "divider":
        return "---\n\n"

    # 8. 引言 quote
    elif btype == "quote":
        texts = block[btype].get("rich_text", [])
        quote_text = rich_text_array_to_markdown(texts)
        # 可以用 Markdown 的引用符號 '>' 來表示
        return f"> {quote_text}\n\n"

    # 若遇到 child_page / child_database，就不在這裡轉 Markdown，
    # 而是交給外層做遞迴，以產生新的文章或檔案
    elif btype == "child_page" or btype == "child_database":
        return ""

    # ... 其餘 block 類型可自行擴充 ...
    #   e.g. video, embed, file, toggle, callout 等

    # 如果遇到不支援的區塊類型，這裡視需求決定如何處理：可忽略或回傳空字串。
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
            page_markdown_parts.append(block_to_markdown(block, article_title=page_title))

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
    只有當內容有變動時才更新文章，並確保 front matter（YAML 區塊）完整
    """
    if not os.path.exists("_posts"):
        os.makedirs("_posts")

    # 查找是否已有該標題的文章
    existing_files = glob.glob(f"_posts/*-{slug}.md")
    if existing_files:
        filename = existing_files[0]  # 使用第一個匹配的檔案
        with open(filename, "r", encoding="utf-8") as f:
            old_full_content = f.read()
    else:
        today_str = datetime.datetime.now().strftime("%Y-%m-%d")
        filename = f"_posts/{today_str}-{slug}.md"
        old_full_content = ""

    # 提取舊的 front matter 和內容
    match = re.search(r"(?s)^---(.*?)---(.*)$", old_full_content)
    if match:
        old_front = match.group(1).strip()
        old_body = match.group(2).strip()
    else:
        old_front = ""
        old_body = old_full_content.strip()

    today_str = datetime.datetime.now().strftime("%Y-%m-%d")

    # **確保 front matter 欄位完整**
    front_matter_dict = {
        "layout": "post",
        "title": f'"{title}"',
        "date": f"{today_str} 10:00:00 +0800",
        "categories": categories if categories else ["NotionExport"],
        "math": "true"
    }

    # 如果舊的 front matter 存在，解析它
    if old_front:
        for line in old_front.split("\n"):
            key, *value = line.split(":", 1)
            key = key.strip()
            if value:
                front_matter_dict[key] = value[0].strip()

    # **更新 `date:`**
    front_matter_dict["date"] = f"{today_str} 10:00:00 +0800"

    # **轉換回 YAML 格式**
    updated_front_matter = "---\n" + "\n".join(f"{key}: {value}" for key, value in front_matter_dict.items()) + "\n---\n"

    # **完整 Markdown 內容**
    updated_full = updated_front_matter + "\n" + new_markdown.strip() + "\n"

    # **只有當內文變更時才更新 `date`**
    if old_body != new_markdown.strip():
        with open(filename, "w", encoding="utf-8") as f:
            f.write(updated_full)
        print(f"[UPDATE] {filename} 內容變更，日期已更新")
    else:
        print(f"[NO CHANGE] {filename} 內容未變更，無需更新")

# ----------------------------------------------------------------------
# 7. Main：指定最上層頁面ID，開始遞迴
# ----------------------------------------------------------------------
def main():
    """
    主函式：從 Notion 獲取所有頁面，遞迴轉換為 Markdown，並儲存到 _posts/ 目錄。
    """
    print("🚀 開始匯出 Notion 內容...")
    
    try:
        parse_and_export_recursively(ROOT_PAGE_ID)
        print("🎉 全部頁面（含子頁面）匯出完成！")
    except Exception as e:
        print(f"❌ 錯誤發生：{e}")
        import traceback
        traceback.print_exc()  # 顯示完整錯誤訊息，方便除錯

if __name__ == "__main__":
    main()
