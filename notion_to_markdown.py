import os
import requests
import datetime
import re
import glob
import unicodedata
from urllib.parse import urlparse

# ----------------------------------------------------------------------
# 1. 讀取 Notion Token & Page ID 設定
# ----------------------------------------------------------------------

NOTION_TOKEN = "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"
# NOTION_TOKEN = os.environ["NOTION_TOKEN"] 
ROOT_PAGE_ID = "166fbb857f9e80eba96ef0091d6ce244"  # 你的最上層 Notion Page ID

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28"
}

processed_pages = set()

def slugify(text):
    """
    轉換標題為檔案名稱友善格式：
    - 移除特殊符號
    - 轉換為小寫
    - 空格變成 "-"
    """
    text = unicodedata.normalize('NFKD', text)
    text = re.sub(r'[^\w\s-]', '', text).strip().lower()
    return re.sub(r'[-\s]+', '-', text)

# ----------------------------------------------------------------------
# 2. 取得頁面標題 (選擇用 retrieve_page，或直接從 child_page["title"] 取)
# ----------------------------------------------------------------------
def retrieve_page_title(page_id: str) -> tuple:
    """
    獲取 Notion 頁面標題，並產生 `slug`
    """
    url = f"https://api.notion.com/v1/pages/{page_id}"
    try:
        res = requests.get(url, headers=HEADERS)
        data = res.json()
        title_obj = data["properties"]["title"]["title"]
        if title_obj:
            page_title = title_obj[0]["plain_text"]
            return page_title, slugify(page_title)  # ⚡️ 回傳 slug
    except (KeyError, IndexError, requests.exceptions.RequestException) as e:
        print(f"⚠️ 無法獲取頁面標題：{e}")
    return "Untitled", "untitled"

# ----------------------------------------------------------------------
# 3. 取得某頁面下的所有區塊 (含分頁處理)
# ----------------------------------------------------------------------
def fetch_notion_blocks(page_id: str) -> list:
    """
    回傳指定 page_id 的直接 children 區塊，不進行遞迴
    """
    all_blocks = []
    base_url = "https://api.notion.com/v1/blocks"
    url = f"{base_url}/{page_id}/children"
    params = {}
    while True:
        resp = requests.get(url, headers=HEADERS, params=params)
        data = resp.json()
        all_blocks.extend(data.get("results", []))
        if data.get("has_more"):
            params["start_cursor"] = data["next_cursor"]
        else:
            break
    return all_blocks

# ----------------------------------------------------------------------
# 4. 下載圖片並儲存到本機
# ----------------------------------------------------------------------
def download_image(image_url: str, block_id: str) -> str:
    images_dir = "images"
    if not os.path.exists(images_dir):
        os.makedirs(images_dir)
    parsed_url = urlparse(image_url)
    path = parsed_url.path
    ext = os.path.splitext(path)[1]
    if not ext:
        ext = ".jpg"
    local_filename = f"{block_id}{ext}"
    local_path = os.path.join(images_dir, local_filename)
    if not os.path.exists(local_path):
        try:
            r = requests.get(image_url, stream=True, timeout=10)
            if r.status_code == 200:
                with open(local_path, "wb") as f:
                    for chunk in r.iter_content(1024):
                        f.write(chunk)
                print(f"下載圖片成功: {local_path}")
            else:
                print(f"下載圖片失敗: {image_url}，狀態碼: {r.status_code}")
        except Exception as e:
            print(f"下載圖片失敗: {image_url}，錯誤: {e}")
    else:
        print(f"圖片已存在，跳過下載: {local_path}")
    return f"{{{{ site.baseurl }}}}/images/{local_filename}"


def rich_text_array_to_markdown(rich_text_array: list) -> str:
    md_text_parts = []
    inline_math_pattern = re.compile(r'\$(.+?)\$')
    
    for rt in rich_text_array:
        text_content = rt.get("plain_text", "")
        def replace_math(match):
            content = match.group(1)
            if content.startswith('$') and content.endswith('$'):
                return match.group(0)
            return "$$" + content + "$$"
        new_text = inline_math_pattern.sub(replace_math, text_content)
        link_url = None
        if rt.get("href"):
            link_url = rt.get("href")
        elif rt.get("text") and rt["text"].get("link"):
            link_url = rt["text"]["link"].get("url")
        if link_url:
            md_text_parts.append(f"[{new_text}]({link_url})")
        else:
            md_text_parts.append(new_text)
    return "".join(md_text_parts)

def block_to_markdown(block: dict, article_title: str = "untitled") -> str:
    btype = block.get("type", "")
    # 段落
    if btype == "paragraph":
        texts = block[btype].get("rich_text", [])
        return rich_text_array_to_markdown(texts) + "\n\n"
    # 標題
    elif btype == "heading_1":
        texts = block[btype].get("rich_text", [])
        return f"# {rich_text_array_to_markdown(texts)}\n\n"
    elif btype == "heading_2":
        texts = block[btype].get("rich_text", [])
        return f"## {rich_text_array_to_markdown(texts)}\n\n"
    elif btype == "heading_3":
        texts = block[btype].get("rich_text", [])
        return f"### {rich_text_array_to_markdown(texts)}\n\n"
    # 清單：僅取得直接子區塊，遞迴處理子區塊
    elif btype == "bulleted_list_item":
        texts = block[btype].get("rich_text", [])
        list_text = rich_text_array_to_markdown(texts)
        if block.get("has_children", False):
            child_blocks = fetch_notion_blocks(block["id"])
            child_texts = [block_to_markdown(child) for child in child_blocks]
            sub_content = "\n  ".join(child_texts)
            return f"- {list_text}\n  {sub_content}\n"
        else:
            return f"- {list_text}\n"
    elif btype == "numbered_list_item":
        texts = block[btype].get("rich_text", [])
        list_text = rich_text_array_to_markdown(texts)
        if block.get("has_children", False):
            child_blocks = fetch_notion_blocks(block["id"])
            child_texts = [block_to_markdown(child) for child in child_blocks]
            sub_content = "\n  ".join(child_texts)
            return f"1. {list_text}\n  {sub_content}\n"
        else:
            return f"1. {list_text}\n"
    # 數學方程式
    elif btype == "equation":
        equation_text = block[btype].get("expression", "")
        return f"$$\n{equation_text}\n$$\n\n"
    # 程式碼
    elif btype == "code":
        texts = block[btype].get("rich_text", [])
        code_text = "".join(rich_text_array_to_markdown([t]) for t in texts)
        language = block[btype].get("language", "plaintext")
        return f"```{language}\n{code_text}\n```\n\n"
    # 圖片
    elif btype == "image":
        image_data = block[btype]
        if image_data.get("type") == "external":
            url = image_data["external"].get("url", "")
        else:
            url = image_data["file"].get("url", "")
        local_url = download_image(url, block["id"])
        return f"![image]({local_url})\n\n"
    # 分隔線
    elif btype == "divider":
        return "---\n\n"
    # 引言
    elif btype == "quote":
        texts = block[btype].get("rich_text", [])
        return f"> {rich_text_array_to_markdown(texts)}\n\n"
    # 表格
    elif btype == "table":
        table_info = block.get("table", {})
        table_width = table_info.get("table_width", 3)
        if block.get("has_children", False):
            table_rows = fetch_notion_blocks(block["id"])
        else:
            return ""
        md_table = []
        for row in table_rows:
            if row["type"] == "table_row":
                cells = row["table_row"].get("cells", [])
                md_row = " | ".join(rich_text_array_to_markdown(cell) for cell in cells)
                md_table.append(f"| {md_row} |")
        if md_table:
            separator = "| " + " | ".join(["---"] * table_width) + " |"
            md_table.insert(1, separator)
        return "\n".join(md_table) + "\n\n"
    # child_page 與 child_database 不在此處理
    elif btype in ["child_page", "child_database"]:
        return ""
    return ""

def upsert_post_with_date_update(slug, title, new_markdown, categories=None):
    if not os.path.exists("_posts"):
        os.makedirs("_posts")

    # 查找是否已有該標題的文章
    existing_files = glob.glob(f"_posts/*-{slug}.md")
    if existing_files:
        filename = existing_files[0]
        with open(filename, "r", encoding="utf-8") as f:
            old_full_content = f.read()
    else:
        today_str = datetime.datetime.now().strftime("%Y-%m-%d")
        filename = f"_posts/{today_str}-{slug}.md"
        old_full_content = ""

    # 刪除重複檔案
    for file in existing_files:
        if file != filename:
            os.remove(file)
            print(f"⚠️ 刪除重複檔案：{file}")

    # 提取舊的 front matter 與內容
    match = re.search(r"(?s)^---(.*?)---(.*)$", old_full_content)
    if match:
        old_front = match.group(1).strip()
        old_body = match.group(2).strip()
    else:
        old_front = ""
        old_body = old_full_content.strip()

    # 正確設定 date，只在內容更新時才更新 date
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    new_date = f"{today_str} 10:00:00 +0800"
    
    # 更新 front matter（保留其他欄位，但不覆蓋 date）
    front_matter_dict = {
        "layout": "post",
        "title": f'"{title}"',
        "categories": categories if categories else ["NotionExport"],
        "math": "true"
    }
    if old_front:
        for line in old_front.split("\n"):
            key, *value = line.split(":", 1)
            key = key.strip()
            if key != "date" and value:
                front_matter_dict[key] = value[0].strip()
    
    # 如果內容有更新，才更新 date
    if old_body != new_markdown.strip():
        front_matter_dict["date"] = new_date
    
    updated_front_matter = "---\n" + "\n".join(f"{key}: {value}" for key, value in front_matter_dict.items()) + "\n---\n"
    updated_full = updated_front_matter + "\n" + new_markdown.strip() + "\n"

    if old_body != new_markdown.strip():
        with open(filename, "w", encoding="utf-8") as f:
            f.write(updated_full)
        print(f"[UPDATE] {filename} 內容變更，日期已更新")
    else:
        print(f"[NO CHANGE] {filename} 內容未變更，日期保持原樣")

processed_pages = set()
def parse_and_export_recursively(page_id: str, parent_slug: str = None):
    global processed_pages
    if page_id in processed_pages:
        print(f"⚠️ 頁面 {page_id} 已處理，跳過")
        return
    processed_pages.add(page_id)
    page_title, slug = retrieve_page_title(page_id)
    if parent_slug:
        slug = f"{parent_slug}-{slug}"
    blocks = fetch_notion_blocks(page_id)
    page_markdown_parts = []
    child_pages = []
    for block in blocks:
        if block.get("type") == "child_page":
            child_pages.append(block)
        else:
            page_markdown_parts.append(block_to_markdown(block, article_title=page_title))
    page_markdown = "".join(page_markdown_parts)
    if not child_pages:
        upsert_post_with_date_update(slug, page_title, page_markdown, categories=["NotionExport"])
    for child_block in child_pages:
        child_id = child_block["id"]
        parse_and_export_recursively(child_id, parent_slug=slug)

# 以下省略 retrieve_page_title 與 upsert_post_with_date_update 等其他函式...
# 主程式執行
def main():
    print("🚀 開始匯出 Notion 內容...")
    try:
        parse_and_export_recursively(ROOT_PAGE_ID)
        print("🎉 全部頁面匯出完成！")
    except Exception as e:
        print(f"❌ 錯誤發生：{e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()