# リリースノート自動生成コマンド

## 目的:
- 直近の変更内容（コミットや差分）をもとに、リリースノートを自動生成する。
- docs/release-notes/release-<version>.md に貼り付け可能な形式で出力する。

## 前提
- default ブランチ: main
- 対象範囲: 直近のタグ〜HEAD または 指定範囲

## 入力例
- 対象バージョン: v1.2.0
- 対象範囲: 直近タグ〜現在HEAD、もしくは `git diff` 範囲

## 手順
1. git のコミット履歴または diff を取得する。
2. 変更内容をカテゴリ別に分類する。
- Added
- Changed
- Fixed
- Removed
- Deprecated
- Security
3. docs/release-notes/release-<version>.md 用の Markdown を生成する。

## 出力フォーマット例

```markdown
# Release v<version> - <YYYY-MM-DD>

## Summary
- <1〜3行で概要>

## Added
- ...

## Changed
- ...

## Fixed
- ...

## Known Issues
- ...
````