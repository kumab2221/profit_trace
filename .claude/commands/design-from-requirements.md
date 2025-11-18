# 設計書生成（UI / ドメイン / IF 設計）

docs/requirements/02_system-requirements.md と  
ADR ディレクトリ内の **全 ADR**（特にアーキテクチャ/設計判断に関するもの）を参照し、  
指定した設計対象（UI / Domain / Infrastructure / IF / Module）の設計書を  
docs/design/<設計対象>.md として生成する。

---

## 目的

- **要件定義書（02_system-requirements）**と  
  **ADR（Architecture Decision Record）**に基づき、  
  設計の一貫性と変更履歴を保証する。
- 設計書が「要件 → 設計 → 実装」のエラーなし連動を実現するようにする。
- UI・ドメイン・インターフェース（IF）・データフローを  
  すべて **ADR の決定に沿った形で反映する**。

---

## 入力

- docs/requirements/02_system-requirements.md  
- ADR ディレクトリ内の ADR 全件（採用: Accepted のもの）
- 必要なら context7 を使って関連仕様を参照してよい。

入力例：

```
UI 設計を生成したいので、
docs/design/01_ui-design.md を作成してください。
対象は「日別工数読み込み UI」と「チャート表示 UI」です。
```

---

## 出力要件

以下の構造に従い、  
**指定された設計対象の Markdown（docs/design/<name>.md）**  
を生成する。

---

# <設計対象名> Design

## 1. Overview（概要）
- 設計対象の目的  
- 関連する REQ-ID（機能/非機能）を列挙  
- 関連する ADR を列挙  
  - 例：ADR-003-ui-architecture.md, ADR-001-ddd-architecture.md

---

## 2. Architecture Alignment（アーキテクチャ整合性）
- 関連 ADR の要点を要約し、今回の設計への影響を 3〜6 行で記述
- 禁止事項／制約／依存方向（Layered / MVVM / Repository）などを明記
- 02_system-requirements の制約との整合性を明示

---

## 3. Design Details（詳細設計）
設計対象に応じて次を含める：

### 3.1 構造（Structure）
- クラス構成図（Mermaid OK）
- レイヤー配置
- 使用するデザインパターン（MVVM、Repository、Service など）

### 3.2 データフロー
- 入力 → 処理 → 出力
- 状態遷移
- 外部要素（CSV, API, DB）との関係

### 3.3 振る舞い（Behavior）
- 主要ユースケースのシーケンス図（Mermaid）
- 例外処理方針
- エラー時の UI / Domain の振る舞い

---

## 4. Mapping to Requirements（要件への対応）
- 必要な REQ-F / REQ-NF の一覧を表形式で列挙
- どの設計要素がどの要件を満たすかを記述
- 未対応の REQ があれば警告を出す

例：

| 設計要素 | 対応する REQ | 説明 |
|---------|--------------|-------|
| ImportService | REQ-F-002 | CSV 読み込み機能 |
| ChartViewModel | REQ-F-005 | チャート描画ロジック |

---

## 5. Trade-offs（設計上の判断）
- ADR には書ききれないレベルでの詳細判断
- 選択肢 A/B/C とその理由を簡潔に記述
- 今回の設計決定の根拠を明確にする

---

## 6. Risks & Future Considerations（リスクと将来拡張）
- この設計のリスク（保守性・性能・依存）
- 将来の変更時に影響が出る箇所
- ADR を再評価するべきトリガー

---

## 7. Appendix
- 補足図
- 詳細メモ
- 必要に応じて仕様参照

---

## 禁止事項

- 02_system-requirements.md に無い機能を勝手に追加する  
- ADR 記録と矛盾する設計を生成する  
- レイヤー依存ルールの破壊（Domain → Infrastructure 依存など）
- 章構成を変更したり削除したりすること
