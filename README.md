# Paper Summary Generator

論文のURLを入力すると、Obsidian用のMarkdownファイルを自動生成し、Gemini APIを使って論文の要約を自動で埋めるツールです。

## セットアップ

### 1. 仮想環境の作成と有効化

```bash
python3 -m venv paper_summary_env
source paper_summary_env/bin/activate
```

### 2. 必要なパッケージのインストール

```bash
pip install requests beautifulsoup4 google-generativeai python-dotenv
```

### 3. Gemini APIキーの設定

1. [Google AI Studio](https://makersuite.google.com/app/apikey) でAPIキーを取得
2. `config.env` ファイルを編集して、APIキーを設定：

```bash
GEMINI_API_KEY=your_actual_api_key_here
```

## 使用方法

```bash
python main.py <論文のURL>
```

### 例

```bash
python main.py https://arxiv.org/abs/2505.19443
```

## 機能

- **自動情報抽出**: 論文のタイトル、著者、アブストラクトを自動抽出
- **Gemini API要約**: 論文の内容を6つの項目に分けて自動要約
- **Obsidian対応**: ObsidianのVault（`~/ObsidianVault/Papers/`）にMarkdownファイルを保存
- **arXiv対応**: arXivのページ構造に最適化

## 生成されるテンプレート

```markdown
---
title: "論文タイトル"
authors: [著者名]
venue: ""
year: 2025
tags: []
status: "未読"
thumbnail: 
pdf: "URL"
---

## どんなもの？

## 先行研究と比べてどこがすごい？

## 技術や手法のキモはどこ？

## どうやって有効だと検証した？

## 議論はある？

## 次に読むべき論文は？
```

## 注意事項

- Gemini APIキーが設定されていない場合、テンプレートのみが生成されます
- インターネット接続が必要です
- ObsidianのVaultフォルダが存在しない場合は自動で作成されます
