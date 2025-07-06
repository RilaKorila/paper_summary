import os
import google.generativeai as genai
from dotenv import load_dotenv
from pathlib import Path

# .env 読み込み
load_dotenv(dotenv_path=Path(__file__).parent / "config.env")

# Gemini API設定
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# Gemini Model設定
GEMINI_MODEL = 'gemini-1.5-flash'

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
各章の冒頭には##をつけ、間には空行を入れてください。
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
