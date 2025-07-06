# Paper Summary Generator

論文のURLを入力すると、Obsidian用のMarkdownファイルを自動生成し、Gemini APIを使って論文の要約を自動で埋めるツールです。

## 主な機能

- **自動情報抽出**: 論文のタイトル、著者、アブストラクトを自動抽出
- **Gemini API要約**: 論文の内容を6つの項目に分けて自動要約
- **キーワード抽出**: 論文固有の技術キーワードを自動抽出
- **Graph View対応**: ObsidianのGraph Viewで著者・キーワードの関係性を可視化
- **Obsidian対応**: ObsidianのVault（`~/ObsidianVault/Papers/`）にMarkdownファイルを保存
- **arXiv対応**: arXivのページ構造に最適化

## 📁 プロジェクト構造

```
paper_summary/
├── main.py
├── extract_paper_info.py   # 論文情報抽出モジュール
├── gemini_utils.py         # Gemini API処理モジュール
├── config.env
├── requirements.txt 
└── README.md
```

## セットアップ

### 1. リポジトリのクローン

```bash
git clone <repository-url>
cd paper_summary
```

### 2. 仮想環境の作成と有効化

```bash
python3 -m venv paper_summary_env
source paper_summary_env/bin/activate  # macOS
```

### 3. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 4. Gemini APIキーの設定

1. [Google AI Studio](https://makersuite.google.com/app/apikey) でAPIキーを取得
2. `config.env` ファイルを編集して、APIキーを設定：

```bash
GEMINI_API_KEY=your_actual_api_key_here
```

## 使用方法

### 基本的な使用方法

```bash
python main.py <論文のURL>
```

### 使用例

```bash
# arXiv論文
python main.py https://arxiv.org/abs/2505.19443

# Nature論文
python main.py https://www.nature.com/articles/s41586-023-06924-6
```

## 📋 生成されるテンプレート

```markdown
---
title: "論文タイトル"
authors: [著者名]
year: 2025
tags: []
status: "未読"
pdf: "URL"
---

## 著者
- [[著者名1]]
- [[著者名2]]

## どんなもの？
（Gemini APIによる自動要約）

## 先行研究と比べてどこがすごい？
（Gemini APIによる自動要約）

## 技術や手法のキモはどこ？
（Gemini APIによる自動要約）

## どうやって有効だと検証した？
（Gemini APIによる自動要約）

## 議論はある？
（Gemini APIによる自動要約）

## 次に読むべき論文は？
（Gemini APIによる自動要約）

## キーワード
- [[LLM]]
- [[Agentic AI]]
- [[Software Engineering]]
```

## Obsidian Graph View対応

### 表示される要素

1. **著者ノード**: 同じ著者の論文が接続される
2. **キーワードノード**: 同じ技術を使った論文が接続される


## ⚠️ 注意事項

- Gemini APIキーが設定されていない場合、テンプレートのみが生成されます
- インターネット接続が必要です
- ObsidianのVaultフォルダが存在しない場合は自動で作成されます
- API使用量に応じて料金が発生する場合があります
