# 高校野球部 タレントマネジメントシステム

[![Build Status](https://github.com/tomoki-shiozaki/baseball-talent-management-app/actions/workflows/ci.yml/badge.svg)](https://github.com/tomoki-shiozaki/baseball-talent-management-app/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/tomoki-shiozaki/baseball-talent-management-app/graph/badge.svg?token=0OO33U5EZZ)](https://codecov.io/gh/tomoki-shiozaki/baseball-talent-management-app)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 概要

本アプリは、高校野球部のチーム向けに、体力測定の記録を登録・管理し、時系列グラフでの可視化を行うほか、チーム全体の管理をサポートするためのシステムです。  
企業のインターンシップで開発しました。

---

**🌐 実際に動くアプリはこちら**  
[https://quest-1-main.onrender.com/](https://quest-1-main.onrender.com/)

また、操作を試せる **テスト用のログインアカウント（マネージャー／部員／コーチ／監督）** もご用意しています。  
ログイン情報の詳細は、[「テスト用アカウント情報」](#動作確認用アカウント情報) セクションをご覧ください。

> ＊ただし、現在は Render での運用のため、最初の起動には約 1 分程度の待機時間が発生することがあります。ご了承ください。
> 私の他の成果物である [図書館アプリ](https://github.com/tomoki-shiozaki/distributed-library) は Cloud Run でデプロイしており、起動が約 10 秒程度で行えます。

---

**機能・マニュアル、工夫点など**

- アプリの機能や利用方法は、[アプリケーションの利用マニュアル](doc/manual.md) をご覧ください。
- 開発時の工夫点や感想などは、プレゼンテーション資料をご参照ください。
  - 📄 [PDF 形式のプレゼン資料](doc/presentation/slides/presentation.pdf) ← スライド形式で閲覧できます

## 動作確認用アカウント情報

| ロール       | ユーザー名 | パスワード       | 名前      |
| ------------ | ---------- | ---------------- | --------- |
| マネージャー | manager1   | dev_manager1_123 | 田中 花子 |
| 部員         | player1    | dev_player1_123  | 渡辺 蒼   |
| 部員         | player2    | dev_player2_123  | 吉田 翔太 |
| 部員         | player3    | dev_player3_123  | 渡辺 樹   |
| コーチ       | coach1     | dev_coach1_123   | 田中 太郎 |
| 監督         | director   | dev_director_123 | 田中 次郎 |

## 🚀 デプロイ手順

このアプリは、以下の構成でデプロイされています。

- **バックエンド**：Django（Render）
- **データベース**：PostgreSQL（Neon）

### Render へのデプロイ手順（参考）

1. GitLab プロジェクトから GitHub へのミラーを作成
1. GitHub のミラーのリポジトリを Render に接続
1. "Web Service" を作成
1. Build Command:  
   `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
1. Start Command: `gunicorn django_project.wsgi --log-file -`
1. 環境変数を設定：
   - `ALLOWED_HOSTS`
   - `DATABASE_URL`
   - `SECRET_KEY`
1. 自動デプロイを有効化

### データベース（Neon）

- Render から自動接続（`.env` 経由で `DATABASE_URL` を設定）

## 📎 提出物一覧

- 🗃 [ER 図（データベース設計）](doc/README.md)
- 📚 [アプリケーションの利用マニュアル](doc/manual.md)
- 🎤 プレゼンテーション資料（課題 1・2、工夫点、感想を含む）
  - 📄 [PDF 形式](doc/presentation/slides/presentation.pdf) ← スライド形式で閲覧できます
  - 📄 [Markdown 形式](doc/presentation/slides/presentation.md) ※Marp 形式。ブラウザでプレゼン形式で閲覧する場合は、PDF 版をご覧ください

## 📝 備考

- 上記アカウントでログイン可能です。
