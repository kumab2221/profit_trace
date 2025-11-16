# 要求クリーニング（Open Questions 解消 → 01_stakeholder-needs.md 更新）

## 目的:
- docs/requirements/01_stakeholder-needs.md の **7. Open Questions** を解消し、
    要求を完成状態（凍結）にする。
- 既存テンプレート構造を絶対に変更しない。
- 解消された質問内容は、対応するセクション（Purpose / Scope / Needs / Constraints など）に反映させる。

---

## 入力
- 回答したい Open Questions の一覧  
- 回答内容（ユーザーが入力）

例:
<<<OpenQuestions回答>>>

---

## 出力要件

1. docs/requirements/01_stakeholder-needs.md を再生成する。  
2. 見出し構造は **以下の固定構造を絶対に変更しない**  

    - # 01. Stakeholder Needs  
    - 1. Purpose  
    - 2. Scope  
    - 2.1 In Scope  
    - 2.2 Out of Scope  
    - 3. Stakeholder List  
    - 4. Stakeholder Needs  
    - 5. Constraints  
    - 6. Assumptions  
    - 7. Open Questions  
    - 8. Appendix  

3. 質問に回答された箇所は適切なセクションに反映する。  
4. 解消された Open Questions は削除する。  
5. まだ不足があれば、新たな Open Questions を追加する。  
6. すべての質問が解消された場合、7 は `None` のみとする。

---

## 禁止事項
- 見出し構造の追加・削除・並び替え
- 01_stakeholder-needs.md に存在しない要素の追加
- STK-ID や STKH-ID の再採番
