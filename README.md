# quest_1

# 神奈川県立JPT高校野球部 タレントマネジメントシステム

## 🌐 デプロイ先URL
- [https://quest-1-main.onrender.com/](https://quest-1-main.onrender.com/)

## 🔐 動作確認用アカウント情報（必須）
| ロール | ユーザー名 | パスワード |
|--------|------------|------------|
| マネージャー | manager1 | dev_manager1_123 | 
| 部員 | player1  | dev_player1_123   |
| 部員 | player2 | dev_player2_123 | 
| コーチ | coach1 | dev_coach1_123 |
| 監督 | director | dev_director_123 | 
| (管理者) | superuser | dev_superuser_123 |
- superuserはDjango管理サイト(`https://quest-1-main.onrender.com/admin/`)の管理者アカウントです

## 🚀 デプロイ手順

このアプリは、以下の構成でデプロイされています。

- **バックエンド**：Django（Render）
- **データベース**：PostgreSQL（Neon）

### Renderへのデプロイ手順（参考）

1. GitLabプロジェクトからGitHubへのミラーを作成
1. GitHubのミラーのリポジトリをRenderに接続
2. "Web Service" を作成
3. Build Command:  
`pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
4. Start Command: `gunicorn django_project.wsgi --log-file -`
5. 環境変数を設定：
    - `ALLOWED_HOSTS`
    - `DATABASE_URL`
    - `SECRET_KEY`
6. 自動デプロイを有効化

### データベース（Neon）

- Renderから自動接続（`.env` 経由で `DATABASE_URL` を設定）

## 🗃 ER図（データベース設計）

ER図は [こちらのドキュメントをご覧ください](doc/README.md)。

## 📝 備考
- アプリは**指定期日まで稼働**させ続けます。
- 上記アカウントでログイン可能です。
- 管理画面：`https://quest-1-main.onrender.com/admin/`
