#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# raycast.title = Create Obsidian Paper Note
# raycast.mode = compact
# raycast.argument1.label = URL
# raycast.argument1.type = text

import sys
import os
import requests
from bs4 import BeautifulSoup
from datetime import date
from pathlib import Path
import google.generativeai as genai
from dotenv import load_dotenv

# 環境変数を読み込み
load_dotenv('config.env')

# Gemini API設定
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# Gemini Model設定
GEMINI_MODEL = 'gemini-1.5-flash'

def extract_paper_info(soup, url):
    """論文の基本情報を抽出"""
    title = soup.title.string.strip() if soup.title else "Unknown Title"
    
    # arXivの場合の特別処理
    if "arxiv.org" in url:
        # タイトルをより正確に抽出
        title_elem = soup.find('h1', class_='title')
        if title_elem:
            title = title_elem.get_text().replace('Title:', '').strip()
        
        # 著者情報を抽出
        authors = []
        authors_elem = soup.find('div', class_='authors')
        if authors_elem:
            author_links = authors_elem.find_all('a')
            authors = [link.get_text().strip() for link in author_links]
        
        # アブストラクトを抽出
        abstract = ""
        abstract_elem = soup.find('blockquote', class_='abstract')
        if abstract_elem:
            abstract = abstract_elem.get_text().replace('Abstract:', '').strip()
        
        return {
            'title': title,
            'authors': authors,
            'abstract': abstract,
            'url': url
        }
    
    # その他のサイトの場合
    return {
        'title': title,
        'authors': [],
        'abstract': "",
        'url': url
    }

def generate_summary_with_gemini(paper_info, url):
    """Gemini APIを使って論文の要約を生成"""
    if not GEMINI_API_KEY:
        return None
    
    try:
        model = genai.GenerativeModel(GEMINI_MODEL)
        
        prompt = f"""
以下の論文情報を基に、論文の要約を日本語で作成してください。

タイトル: {paper_info['title']}
著者: {', '.join(paper_info['authors']) if paper_info['authors'] else 'Unknown'}
アブストラクト: {paper_info['abstract']}
URL: {url}
以下の項目について、簡潔に回答してください：

1. どんなもの？（研究の目的と概要）
2. 先行研究と比べてどこがすごい？（新規性と貢献）
3. 技術や手法のキモはどこ？（主要な技術・手法）
4. どうやって有効だと検証した？（実験・評価方法）
5. 議論はある？（制限事項や今後の課題）
6. 次に読むべき論文は？（関連研究の提案）

各項目は2-3文程度で簡潔にまとめてください。
"""
        
        response = model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        print(f"Gemini API エラー: {e}")
        return None

def extract_keywords_with_gemini(paper_info):
    """Gemini APIを使ってキーワードを抽出"""
    if not GEMINI_API_KEY:
        # APIキーがない場合は従来の方法で検出
        return detect_research_field_fallback(paper_info)
    
    try:
        model = genai.GenerativeModel(GEMINI_MODEL)
        
        prompt = f"""
以下の論文から重要なキーワードを5つ抽出してください。

タイトル: {paper_info['title']}
アブストラクト: {paper_info['abstract']}

以下の形式で5個のキーワードを返してください：
- 技術名（例：LLM, RAG, Transformer）
- 研究分野（例：NLP, Computer Vision, Robotics）
- 手法名（例：Fine-tuning, Prompt Engineering）
- 応用分野（例：Education, Healthcare, Finance）

キーワードは英語で、カンマ区切りで返してください。
"""
        
        response = model.generate_content(prompt)
        keywords_text = response.text.strip()
        # カンマで分割してキーワードを抽出
        keywords = [kw.strip() for kw in keywords_text.split(',') if kw.strip()]
        return keywords[:5]  # 最大5個まで
        
    except Exception as e:
        print(f"キーワード抽出エラー: {e}")
        return []


def detect_research_field_fallback(paper_info):
    """従来のキーワードベースの研究分野検出（フォールバック用）"""
    title_lower = paper_info['title'].lower()
    abstract_lower = paper_info['abstract'].lower()
    
    fields = []
    
    # 研究分野のキーワードマッピング
    field_keywords = {
        'AI/ML': ['machine learning', 'artificial intelligence', 'deep learning', 'neural network', 'llm', 'large language model'],
        'NLP': ['natural language', 'nlp', 'text', 'language model', 'transformer', 'bert', 'gpt'],
        'Computer Vision': ['computer vision', 'image', 'visual', 'cv', 'detection', 'recognition'],
        'Robotics': ['robot', 'robotics', 'autonomous', 'control'],
        'Education': ['education', 'learning', 'teaching', 'pedagogy', 'classroom', 'student'],
        'Healthcare': ['health', 'medical', 'clinical', 'patient', 'diagnosis'],
        'Finance': ['finance', 'financial', 'trading', 'investment', 'banking'],
        'HCI': ['human-computer interaction', 'hci', 'user interface', 'ux', 'usability'],
        'Software Engineering': ['software', 'development', 'programming', 'code', 'engineering'],
        'Data Science': ['data', 'analytics', 'statistics', 'mining', 'big data']
    }
    
    for field, keywords in field_keywords.items():
        for keyword in keywords:
            if keyword in title_lower or keyword in abstract_lower:
                fields.append(field)
                break
    
    return list(set(fields))  # 重複を除去

def create_obsidian_template(paper_info, summary=None, keywords=None, research_fields=None):
    """Obsidianテンプレートを作成"""
    
    # 著者情報の処理
    authors_str = ', '.join(paper_info['authors']) if paper_info['authors'] else ""
    
    # 年号の抽出（arXiv URLから）
    year = date.today().year
    if "arxiv.org" in paper_info['url']:
        try:
            # URLから年号を抽出（例: 2505.19443 -> 2025）
            arxiv_id = paper_info['url'].split('/')[-1]
            # 最初の2桁を取得(50以下なら2000年台、50以上なら1900年台 と仮定)
            year_prefix = arxiv_id[:2]
            if year_prefix.isdigit():
                year_num = int(year_prefix)
                if year_num <= 50:
                    year = 2000 + year_num
                else:
                    year = 1900 + year_num
        except:
            pass
    
    # タグの構築
    tags = []
    
    # 研究分野のタグ
    if research_fields:
        tags.extend(research_fields)
    
    # キーワードのタグ
    if keywords:
        tags.extend(keywords)
    
    # 著者をタグとして追加（Graph Viewで表示される）
    if paper_info['authors']:
        for author in paper_info['authors']:
            # 著者名をクリーンアップしてタグ化
            author_tag = author.replace(' ', '_').replace('.', '').replace(',', '')
            tags.append(f"author/{author_tag}")
    
    # タグ文字列の作成
    tags_str = ', '.join([f'"{tag}"' for tag in tags]) if tags else ""
    
    # 著者リンクの作成（Obsidianの内部リンク形式）
    author_links = ""
    if paper_info['authors']:
        author_links = "\n## 著者\n"
        for author in paper_info['authors']:
            author_links += f"- [[{author}]]\n"
    
    md_content = f"""---
title: "{paper_info['title']}"
authors: [{authors_str}]
venue: ""
year: {year}
tags: [{tags_str}]
status: "未読"
thumbnail: 
pdf: "{paper_info['url']}"
aliases: []
---

{author_links}
## どんなもの？

{summary.split('1. どんなもの？（研究の目的と概要）')[1].split('2. 先行研究と比べてどこがすごい？（新規性と貢献）')[0].strip() if summary and '1. どんなもの？（研究の目的と概要）' in summary else ''}

## 先行研究と比べてどこがすごい？

{summary.split('2. 先行研究と比べてどこがすごい？（新規性と貢献）')[1].split('3. 技術や手法のキモはどこ？（主要な技術・手法）')[0].strip() if summary and '2. 先行研究と比べてどこがすごい？（新規性と貢献）' in summary else ''}

## 技術や手法のキモはどこ？

{summary.split('3. 技術や手法のキモはどこ？（主要な技術・手法）')[1].split('4. どうやって有効だと検証した？（実験・評価方法）')[0].strip() if summary and '3. 技術や手法のキモはどこ？（主要な技術・手法）' in summary else ''}

## どうやって有効だと検証した？

{summary.split('4. どうやって有効だと検証した？（実験・評価方法）')[1].split('5. 議論はある？（制限事項や今後の課題）')[0].strip() if summary and '4. どうやって有効だと検証した？（実験・評価方法）' in summary else ''}

## 議論はある？

{summary.split('5. 議論はある？（制限事項や今後の課題）')[1].split('6. 次に読むべき論文は？（関連研究の提案）')[0].strip() if summary and '5. 議論はある？（制限事項や今後の課題）' in summary else ''}

## 次に読むべき論文は？

{summary.split('6. 次に読むべき論文は？（関連研究の提案）')[1].strip() if summary and '6. 次に読むべき論文は？（関連研究の提案）' in summary else ''}

## 関連リンク

### 研究分野
{chr(10).join([f'- [[{field}]]' for field in (research_fields or [])])}

### キーワード
{chr(10).join([f'- [[{keyword}]]' for keyword in (keywords or [])])}
"""
    
    return md_content

# 引数でURL受け取り
url = sys.argv[1]

# 1. HTML取得
print("📄 論文ページを取得中...")
res = requests.get(url)
soup = BeautifulSoup(res.text, "html.parser")

# 2. 論文情報を抽出
print("🔍 論文情報を抽出中...")
paper_info = extract_paper_info(soup, url)

# 3. Gemini APIで要約生成
print("🤖 Gemini APIで要約を生成中...")
summary = generate_summary_with_gemini(paper_info, url)

# 4. キーワード抽出と研究分野検出
print("🔍 キーワードと研究分野を抽出中...")
keywords = extract_keywords_with_gemini(paper_info)
research_fields = detect_research_field(paper_info)

# 5. Obsidianテンプレートを作成
print("📝 テンプレートを作成中...")
md_content = create_obsidian_template(paper_info, summary, keywords, research_fields)

# 6. ObsidianのVault内に保存
vault_path = Path.home() / "ObsidianVault" / "Papers"
vault_path.mkdir(parents=True, exist_ok=True)
filename = f"{paper_info['title'].replace(' ', '_').replace('/', '_')}.md"
with open(vault_path / filename, "w", encoding='utf-8') as f:
    f.write(md_content)

print(f"✅ {filename} を Obsidian に作成しました")
if summary:
    print("✨ Gemini APIによる要約が完了しました")
else:
    print("⚠️  Gemini APIキーが設定されていないか、エラーが発生しました")
