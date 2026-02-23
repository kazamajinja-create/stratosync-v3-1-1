# Agastya Bridge & Rename Kit v2

このキットは、プロジェクト内の **"agastia" → "agastya"** 統一を
「止めずに」安全に行うための実運用ツール集です。

## ファイル一覧
- `rename_agastia_to_agastya.py` … ファイル/フォルダ名のリネーム＋内容一括置換（.bak作成）
- `patch_folder_names_in_meta.py` … JSON/TXT/MD/YAML のメタ表記（engine/source等）だけ先に修正
- `scan_and_patch_agastia_paths.py` … 旧パス/旧importをスキャン→CSV→必要なら一括修正

## 推奨フロー
1. まず **ドライラン** で影響範囲可視化  
   ```bash
   python3 rename_agastia_to_agastya.py . --dry-run
   python3 scan_and_patch_agastia_paths.py .          # CSVレポート生成
   ```
2. **メタ表記だけ先に直す**（任意）  
   ```bash
   python3 patch_folder_names_in_meta.py
   ```
3. **本適用**  
   ```bash
   python3 rename_agastia_to_agastya.py . --apply
   python3 scan_and_patch_agastia_paths.py . --apply
   ```
4. 変更確認（Git 推奨）：  
   ```bash
   git add -A && git diff --cached --stat
   ```

> すべての編集は `.bak` バックアップが作成されます。バイナリは自動除外されます。
