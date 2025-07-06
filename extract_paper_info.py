import requests
from bs4 import BeautifulSoup
from datetime import date

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

def extract_year_from_arxiv_url(url):
    """arXiv URLから年号を抽出"""
    year = date.today().year
    if "arxiv.org" in url:
        try:
            # URLから年号を抽出（例: 2505.19443 -> 2025）
            arxiv_id = url.split('/')[-1]
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
    return year

def get_paper_info_from_url(url):
    """URLから論文情報を取得する統合関数"""
    # HTML取得
    res = requests.get(url)
    soup = BeautifulSoup(res.text, "html.parser")
    
    # 論文情報を抽出
    paper_info = extract_paper_info(soup, url)
    
    # 年号を追加
    paper_info['year'] = extract_year_from_arxiv_url(url)
    
    return paper_info
