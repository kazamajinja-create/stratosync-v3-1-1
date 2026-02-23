
【Mode G - SCT課金 & 継続フロー連携（n8n構成案）】

1. Bubble UI から "テーマ使用" リクエスト
2. n8n → Supabase: SCT残高チェック (sct_balance >= 3)
3. 残高OKなら：
    a. SCTを3減算
    b. `modeG_session.themes_used = 0` にリセット
    c. Bubbleに「Mode G 起動OK」をレスポンス
4. 3テーマ使用後：
    a. "継続しますか？" プロンプト
    b. はい → SCT再消費（Step 2に戻る）
    c. いいえ → セッション終了
5. SCT不足時：
    a. Stripe 決済フローへ誘導（WebhookまたはCheckout）

📦 Stripe連携: checkout.session → 成功時に n8n → Supabase 更新 + 起動レスポンス
