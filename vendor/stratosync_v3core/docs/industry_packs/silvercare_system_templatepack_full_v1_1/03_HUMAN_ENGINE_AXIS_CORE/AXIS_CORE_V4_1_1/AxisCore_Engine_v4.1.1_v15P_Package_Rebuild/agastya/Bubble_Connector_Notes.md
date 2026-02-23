# Bubble 接続変数（Data types / API Connector）
- Job: jobId(text), plan(text), mode(text), status(text), pdfUrl(file/text), jsonPath(text), createdAt(date), finishedAt(date), log(text)
- API Connector:
  - POST /agastia/stripe  body:{plan,birth,latlon,line_user_id}
  - POST /agastia/session body:{plan,birth,latlon,line_user_id}
