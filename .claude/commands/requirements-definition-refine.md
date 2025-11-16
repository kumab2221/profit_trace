# 要件定義クリーニング（Open Questions 解消 → 02_system-requirements.md 更新）

## 目的
- docs/requirements/02_system-requirements.md の **6. Open Questions** を解消し、
    要件定義書を完成状態（凍結）にする。
- **完全固定テンプレート構造を絶対に変更しない。**
- 回答内容は、対応するセクション（Functional / Non-Functional / Constraints など）に正しく反映させる。
- 解消不能な質問が残る場合は、Open Questions に残すが、理由と影響範囲を明確化する。

---

## 入力
- 回答したい Open Questions の一覧
- 回答内容（ユーザーが入力）

例:
<<<OpenQuestions回答>>>

---

## 出力要件

1. docs/requirements/02_system-requirements.md を **テンプレート構造そのまま** で再生成する。

2. **見出し構造を絶対に変更してはならない**

    - # 02. System Requirements
    - 1. Overview
    - 2. Definitions
    - 3. Functional Requirements
    - 3.1 構成方針
    - 3.2 要件一覧（REQ-F-xxx）
    - 4. Non-Functional Requirements
    - 5. Constraints
    - 6. Open Questions
    - 7. Appendix

3. 回答済みの質問は、該当する要件へ内容を反映させる
    - 機能要件：REQ-F-xxx
    - 非機能要件：REQ-NF-xxx
    - 制約：5. Constraints
    - Definitions に追加が必要なら反映

4. **解消された Open Questions は削除する**。

5. **新たな曖昧点が見つかった場合は、新しい Open Questions を追加する**。

6. **Open Questions が完全解消された場合**：
    - `6. Open Questions` セクションは `"None"` のみ記載する。

---

## 禁止事項
- 見出し構造の追加・削除・改変
- 02_system-requirements.md に存在しない項目の追加
- REQ-F / REQ-NF の ID を再採番すること
- 機能要件の構造崩壊（概要/詳細/受入条件などの欠落）

---

## 注意
- constraints との整合性が失われる場合、Claude に必ず指摘させる。
- refactor ではなく **要件の純粋なクリーニング** のみに用途を限定する。