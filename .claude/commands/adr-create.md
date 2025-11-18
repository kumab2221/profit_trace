# ADR 作成コマンド

新しい設計判断またはアーキテクチャ判断について、  
**「読みやすく・短く・複数に分割された ADR」** を生成する。

---

## 目的

- docs/requirements/02_system-requirements.md や docs/design/01_architecture-evaluation.md などを参照し、  
  1 つの **明確な設計判断につき 1 つの ADR ファイル** を作成する。
- フォーマットの揺れ・冗長な長文を避け、  
  短く比較しやすい ADR 一覧を作る。

---

## 入力
docs/requirements/02_system-requirements.md や docs/design/01_architecture-evaluation.md


---

## 出力ポリシー

1. **1 ADR = 1 つの決定** とすること。
2. 入力に複数の決定が含まれている場合：
   - まず「候補となる決定の一覧」を整理して見せる
   - それぞれを **別ファイル**（ADR-XXX-<slug>.md）として生成する
3. 各 ADR は、**過度に長文化しない**（各セクションは数行〜数項目まで）。

---

## ファイル命名規則

- 保存先： `ADR/` ディレクトリ配下
- 形式： `ADR-<3桁番号>-<短いスラグ>.md`
  - 例：`ADR-001-ddd-lite-monolith.md`
- 既存 ADR がある場合：
  - ADR ディレクトリ内の最大番号を確認し、+1 番号から採番すること
  - 番号の再利用や飛び番は禁止

---

## ADR テンプレ（固定フォーマット）

**見出し構造は絶対に変更してはならない。**

```markdown
# ADR-XXX: <短く具体的なタイトル>

## Status
Accepted | Rejected | Deprecated | Superseded（いずれか）

## Context
- プロジェクトや機能の簡潔な説明（2〜3 行）
- 関連する要求・要件（STK / REQ-ID を列挙）
- この決定が必要になった背景（2〜4 行）

## Decision
- 採用したアーキテクチャ / 設計判断を 1〜3 行で要約
- 重要なポイントを箇条書きで 3〜7 個列挙

## Alternatives
- 検討した代替案を 2〜4 個まで列挙
- 各代替案について「一文の説明」と「採用しなかった理由」を書く

例：
- Alternative A: <名前> — 採用しなかった理由（1 行）
- Alternative B: <名前> — 採用しなかった理由（1 行）

## Rationale
- なぜこの Decision が最も妥当と判断されたか
- Quality Attributes（性能、保守性、テスト容易性など）との関係を 3〜6 行で説明

## Consequences
### Positive
- 良い影響を箇条書きで 3〜5 個

### Negative / Risks
- 想定されるデメリット・リスクを 3〜5 個
- 必要であれば、簡単な軽減策も併記してよい

## Links
- 関連ドキュメントへのリンク
  - docs/requirements/02_system-requirements.md
  - docs/design/01_architecture-evaluation.md
  - 関連する他の ADR（あれば）
```

---

## 生成ルール（重要）

1. **1 ファイル = 1 決定**  
   - 「DDD 採用」「UI アーキテクチャ」「データストア選択」などは、それぞれ別 ADR に分ける。
   - 1 つの ADR に複数の大きな決定をまとめないこと。

2. **文章量を制御する**  
   - Context / Rationale は **各 5〜10 行以内** を目安とする。
   - Alternatives / Consequences は **箇条書き中心** にし、読みやすさを優先する。
   - 前回のような **画面スクロールが必要な長大 ADR を 1 つだけ作ることは禁止**。

3. **docs/requirements / docs/design との整合性を必ず確認する**  
   - 02_system-requirements.md に存在しない要求・要件を勝手に前提にしない。
   - 必要なら関連する REQ-ID / STK-ID を明示する。
   - 01_architecture-evaluation.md がある場合は、そこに書かれた評価・候補を優先的に参照する。

4. **曖昧な部分は、ADR 内で「Open Questions」として残さない**  
   - ADR は「決定の記録」であり、「検討中のメモ」ではない。
   - まだ決まっていない論点は別途メモ or 別コマンドで扱う。

---

## 禁止事項

- 1 つの ADR に、複数の大きな設計判断を詰め込むこと
- 見出し構造（Status / Context / Decision / Alternatives / Rationale / Consequences / Links）の追加・削除・並べ替え
- 画面スクロールが必要な長文の「設計書的 ADR」を 1 ファイルだけ出力すること
- ADR 番号の再利用・飛び番

