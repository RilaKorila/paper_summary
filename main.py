import sys
import os
from datetime import date
from pathlib import Path
from extract_paper_info import get_paper_info_from_url
from gemini_utils import generate_summary_with_gemini, extract_keywords_with_gemini, detect_research_field_fallback
from dotenv import load_dotenv
import google.generativeai as genai

def create_obsidian_template(paper_info, summary=None, keywords=None):
    """Obsidianテンプレートを作成"""
    
    # 著者情報の処理
    authors_str = ', '.join(paper_info['authors']) if paper_info['authors'] else ""
    # 年号の取得
    year = paper_info.get('year', date.today().year)

    # タグの構築
    tags = []    
    # キーワードのタグ
    if keywords:
        tags.extend(keywords)
    # タグ文字列の作成
    tags_str = ', '.join([f'"{tag}"' for tag in tags]) if tags else ""
    
    # 著者リンクの作成（Obsidianの内部リンク形式）
    author_links = ""
    if paper_info['authors']:
        for author in paper_info['authors']:
            author_links += f"- [[{author}]]\n"
    
    md_content = f"""---
title: "{paper_info['title']}"
authors: [{authors_str}]
year: {year}
tags: [{tags_str}]
status: "未読"
pdf: "{paper_info['url']}"
---

{summary}

## キーワード
{chr(10).join([f'- [[{keyword}]]' for keyword in (keywords or [])])}

## 著者
{author_links}
"""
    
    return md_content


if __name__ == "__main__":
    # 引数でURL受け取り
    url = sys.argv[1]

    # 1. 論文情報を抽出
    print("論文ページを取得中...")
    print("論文情報を抽出中...")
    paper_info = get_paper_info_from_url(url)

    # 3. Gemini APIで要約生成
    print("Gemini APIで要約を生成中...")
    summary = generate_summary_with_gemini(paper_info, url)

    # 4. キーワード抽出
    print("キーワードを抽出中...")
    keywords = extract_keywords_with_gemini(paper_info)

    # 5. Obsidianテンプレートを作成
    print("テンプレートを作成中...")
    md_content = create_obsidian_template(paper_info, summary, keywords)

    # 6. ObsidianのVault内に保存
    vault_path = Path.home() / "ObsidianVault" / "Papers"
    vault_path.mkdir(parents=True, exist_ok=True)
    filename = f"{paper_info['title'].replace('/', '_')}.md"
    with open(vault_path / filename, "w", encoding='utf-8') as f:
        f.write(md_content)

    print(f"{filename} を Obsidian に作成しました")
    if summary:
        print("Gemini APIによる要約が完了しました")
    else:
        print("Gemini APIキーが設定されていないか、エラーが発生しました")
