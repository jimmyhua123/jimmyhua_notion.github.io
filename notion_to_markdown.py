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
    回傳所有 blocks（list），不包含子頁面下層
    """
    all_blocks = []
    base_url = "https://api.notion.com/v1/blocks"
    url = f"{base_url}/{page_id}/children"
    params = {}

    while True:
        resp = requests.get(url, headers=HEADERS, params=params)
        data = resp.json()
        for block in data.get("results", []):
            all_blocks.append(block)
            # 若 block 有子區塊，僅對非 image 類型進行遞迴（避免圖片重複）
            if block.get("has_children", False) and block.get("type") != "image":
                child_blocks = fetch_notion_blocks(block["id"])
                all_blocks.extend(child_blocks)
        if data.get("has_more"):
            params["start_cursor"] = data["next_cursor"]
        else:
            break
    return all_blocks

# ----------------------------------------------------------------------
# 新增函式：下載圖片並儲存到本機
# ----------------------------------------------------------------------
def download_image(image_url: str, block_id: str) -> str:
    """
    下載圖片並儲存到本機 images 資料夾，回傳圖片的相對路徑 (供 Markdown 使用)
    """
    images_dir = "images"
    if not os.path.exists(images_dir):
        os.makedirs(images_dir)

    # 利用 urlparse 解析圖片 URL，取得檔案路徑與副檔名
    parsed_url = urlparse(image_url)
    path = parsed_url.path
    ext = os.path.splitext(path)[1]
    if not ext:
        ext = ".jpg"  # 預設副檔名

    local_filename = f"{block_id}{ext}"
    local_path = os.path.join(images_dir, local_filename)

    # 若圖片尚未下載，則進行下載
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

    # 回傳圖片在網站中的相對路徑
    # 此處採用絕對路徑 '/images/filename'，若需要相對路徑請自行調整
    return f"{{{{ site.baseurl }}}}/images/{local_filename}"

# ----------------------------------------------------------------------
# 4. 將單一 block 轉成 Markdown（忽略 child_page）
# ----------------------------------------------------------------------


def rich_text_array_to_markdown(rich_text_array: list) -> str:
    md_text_parts = []
    inline_math_pattern = re.compile(r'\$(.+?)\$')
    
    for rt in rich_text_array:
        text_content = rt.get("plain_text", "")
        # 進行替換：將所有 $...$ 換成 $$...$$
        new_text = inline_math_pattern.sub(lambda m: "$$" + m.group(1) + "$$", text_content)
        # 印出除錯資訊，檢查轉換前後的差異
        print("原始文本：", text_content)
        print("替換後：", new_text)
        
        link_url = None
        if rt.get("href"):
            link_url = rt.get("href")
        elif rt.get("text") and rt["text"].get("link"):
            link_url = rt["text"]["link"].get("url")
        
        if link_url:
            md_text_parts.append(f"[{new_text}]({link_url})")
        else:
            md_text_parts.append(new_text)
    result = "".join(md_text_parts)
    print("最終轉換結果：", result)
    return result

def block_to_markdown(block: dict, article_title: str = "untitled") -> str:
    """
    將單一 Notion block 轉為 Markdown 的字串。
    示範常見的 block 類型：paragraph, heading, list, equation, code, image, divider, quote, table 等。
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

    # 3. 清單 bulleted_list_item / numbered_list_item
    elif btype == "bulleted_list_item":
        texts = block[btype].get("rich_text", [])
        list_text = rich_text_array_to_markdown(texts)
        if block.get("has_children", False):
            sub_blocks = fetch_notion_blocks(block["id"])
            sub_texts = [block_to_markdown(sub) for sub in sub_blocks]
            sub_content = "\n  ".join(sub_texts)
            return f"- {list_text}\n  {sub_content}\n"
        else:
            return f"- {list_text}\n"

    elif btype == "numbered_list_item":
        texts = block[btype].get("rich_text", [])
        list_text = rich_text_array_to_markdown(texts)
        if block.get("has_children", False):
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

    # 6. 圖片 image（優化圖片處理：下載圖片並引用本地路徑）
    elif btype == "image":
        image_data = block[btype]
        if image_data.get("type") == "external":
            url = image_data["external"].get("url", "")
        else:
            url = image_data["file"].get("url", "")
        local_url = download_image(url, block["id"])
        return f"![image]({local_url})\n\n"

    # 7. 分隔線 divider
    elif btype == "divider":
        return "---\n\n"

    # 8. 引言 quote
    elif btype == "quote":
        texts = block[btype].get("rich_text", [])
        quote_text = rich_text_array_to_markdown(texts)
        return f"> {quote_text}\n\n"

    # 9. 表格 table
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

    # 若遇到 child_page / child_database，則交由外層遞迴處理
    elif btype in ["child_page", "child_database"]:
        return ""

    # 其他不支援的 block 類型，回傳空字串
    return ""

# ----------------------------------------------------------------------
# 5. 遞迴函式：parse_and_export_recursively()
# ----------------------------------------------------------------------
processed_pages = set()  # 全域集合，用來記錄已處理的 page_id

def parse_and_export_recursively(page_id: str, parent_slug: str = None):
    global processed_pages

    if page_id in processed_pages:
        print(f"⚠️ 頁面 {page_id} 已處理，跳過重複操作")
        return

    processed_pages.add(page_id)

    # 取得標題與 slug
    page_title, slug = retrieve_page_title(page_id)
    if parent_slug:
        slug = f"{parent_slug}-{slug}"

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

    # 若沒有子頁面則生成文章
    if not child_pages:
        upsert_post_with_date_update(slug, page_title, page_markdown, categories=["NotionExport"])

    # 遞迴處理子頁面
    for child_block in child_pages:
        child_id = child_block["id"]
        parse_and_export_recursively(child_id, parent_slug=slug)


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

    # 設定最新日期
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    new_date = f"{today_str} 10:00:00 +0800"

    # 更新 front matter（保留其他欄位，但不覆蓋 date）
    front_matter_dict = {
        "layout": "post",
        "title": f'"{title}"',
        "date": new_date,
        "categories": categories if categories else ["NotionExport"],
        "math": "true"
    }
    if old_front:
        for line in old_front.split("\n"):
            key, *value = line.split(":", 1)
            key = key.strip()
            # 若 key 為 date 則跳過，避免覆蓋新日期
            if key != "date" and value:
                front_matter_dict[key] = value[0].strip()

    # 最後再重新設定一次 date，確保為最新日期
    front_matter_dict["date"] = new_date

    updated_front_matter = "---\n" + "\n".join(f"{key}: {value}" for key, value in front_matter_dict.items()) + "\n---\n"
    updated_full = updated_front_matter + "\n" + new_markdown.strip() + "\n"

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
        traceback.print_exc()

if __name__ == "__main__":
    main()
