# Project memory

このファイルは Claude Code の振る舞いを制御するための **プロジェクト仕様** である。  
本プロジェクトにおいて Claude は、ここに定められた規則を常に守らなければならない。

---

# 1. Project Overview
- Project name: Profit Trace
- Purpose: 契約時の複数の見積もりに対して、各人の使用した時間（工数）から最終的な利益を可視化する
- Primary language: Python (uv)
- Entrypoint: src/main.py

---

# 2. Document Templates (Structural Integrity Rules)

以下のドキュメントは **見出し構造が完全固定** であり、  
Claude は、**追記以外の変更（削除 / 並び替え / 統合 / 分解 / 改名）を一切行ってはならない**。

## 2.1 01_stakeholder-needs.md の構造（固定）
```
# 01. Stakeholder Needs
## 1. Purpose
## 2. Scope
### 2.1 In Scope
### 2.2 Out of Scope
## 3. Stakeholder List
## 4. Stakeholder Needs
### 4.x <Stakeholder Name>
#### STK-xxx: <Title>
## 5. Constraints
## 6. Assumptions
## 7. Open Questions
## 8. Appendix
```

## 2.2 02_system-requirements.md の構造（固定）
```
# 02. System Requirements
## 1. Overview
## 2. Definitions
## 3. Functional Requirements
### 3.1 構成方針
### 3.2 要件一覧
#### REQ-F-xxx: <Title>
## 4. Non-Functional Requirements
#### REQ-NF-xxx: <Title>
## 5. Constraints
## 6. Open Questions
## 7. Appendix
```

### 【重要】
Claude がこれらに触れるときは、  
**・追記は許可  
・既存見出しの削除は禁止  
・既存見出しの名称変更は禁止  
・既存見出しの階層変更は禁止  
・新しい章の追加は禁止（Appendix 内は可）  
・内容の書き換えは Claude が明確な理由（要件反映）がある場合のみ許可**  
とする。

---

# 3. Repository Layout
- src/
- tests/
- docs/requirements/
- docs/design/
- ADR/
- plans/
- docs/release-notes/

---

# 4. Process Rules
- 開発フロー：要件 → 設計 → ADR → 実装 → テスト
- 要件・設計の前に、必ず docs/requirements を参照する
- 重要な判断は必ず ADR に記録する
- main ブランチは常に動作保証状態とする

---

# 5. Claude Usage Policy (行動規範)

Claude は以下の行動規範に従う。

## 5.1 テンプレ遵守ルール（最重要）
- 固定テンプレ構造を **絶対に変更してはならない**
- 見出し構造を “省略して要約” する行為も禁止
- 「別の構造のほうがよい」などの提案は Appendix へ書くが、構造自体は変えない
- 要件追加は **既存の適切な見出しの下に追記** のみ許可

## 5.2 ドキュメント編集ルール
- 編集前に該当 doc の全文を読み込む
- 差分パッチ形式での変更を優先する
- 変更理由を説明する（例：STK-xxx との整合性）

## 5.3 技術ドキュメントの一貫性
- STK-xxx → REQ-F/REQ-NF のトレーサビリティを維持する  
- 不確実性は Open Questions に送る（埋めない）

---

# 6. MCP Usage Rules
- context7：公式ドキュメント参照に使用  
- filesystem：Markdown ドキュメントの自動編集  
---

# 7. 禁止事項
Claude は **以下の行為を禁止** される。

- ドキュメント構造（見出し）の変更  
- 章タイトルの変更  
- 階層構造の変更  
- 分割/統合による章の再構成  
- 任意の新章追加（Appendix 以外）  
- テンプレの自動要約や省略  

---

# 8. Development Principles
- 情報不足は “補完しない”。Open Questions に送る。
- 数値の省略禁止（例：「高速」→ “500ms 以下” 提案）
- 曖昧表現禁止

---

# 9. Appendix
必要なら補足を追加する。