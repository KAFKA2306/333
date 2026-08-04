# 読売333 批判的検証 — 等ウェート指数をTOPIXと比較する分析試作

このリポジトリは、読売株価指数333（読売333）の構成銘柄と財務データを正規化し、PBR、ROE、配当利回り、セクター集中度をTOPIXと比較するためのPython分析試作です。

**現在、分析に必要なraw dataはリポジトリへ登録されていません。したがって、読売333の現在の割安性、収益性、配当特性、分散効果、TOPIXに対する優位性を、このリポジトリの成果として結論づけることはできません。**

[![CI](https://github.com/KAFKA2306/333/actions/workflows/ci.yml/badge.svg)](https://github.com/KAFKA2306/333/actions/workflows/ci.yml)
[![Pages](https://github.com/KAFKA2306/333/actions/workflows/pages.yml/badge.svg)](https://github.com/KAFKA2306/333/actions/workflows/pages.yml)

> **状態:** 分析コードあり / raw dataなし / metrics未生成  
> **Python:** 3.11以上  
> **公開候補:** https://kafka2306.github.io/333/  
> **既知の問題:** [Issue #2](https://github.com/KAFKA2306/333/issues/2)

---

## 目的

次の問いを、同じ基準日と出典を持つデータで検証することを目的とします。

- 読売333はTOPIXより低PBR銘柄を多く含むか
- ROE分布にどのような差があるか
- 配当利回りに差があるか
- 等ウェート設計で個別銘柄・セクター集中がどう変わるか
- 構成銘柄の入替とウェート調整を考慮した場合、比較可能な評価になるか

指数設計の説明だけから、deep value、低ROE、低momentum、景気循環局面での優位性を推定しません。結論は、入力データ、基準日、計算結果、比較条件が揃った場合だけ生成します。

---

## 現在の状態

| 項目 | 状態 |
|---|---|
| 分析コード | 実装済み |
| unit test | 実装済み |
| CI | workflowあり |
| 読売333構成銘柄raw data | 未登録 |
| TOPIX比較用財務data | 未登録 |
| processed metrics | 未生成 |
| 現在の分析結論 | なし |
| Pages | metrics不在時は未計算statusを表示する設計へ移行中 |
| Codex commentary | optional。分析の正準ではない |

以前のREADMEは、全metricsが`N/A`であるにもかかわらず、読売333をdeep value、低ROE、低momentumなどと固定記述していました。この表現はIssue #2で不適切と判定し、本READMEから除去しました。

---

## 必要な入力

自動分析workflowは、次の2fileが存在する場合だけ計算を実行します。

```text
data/raw/yomiuri333_constituents.yaml
data/raw/financials.yaml
```

### 構成銘柄data

最低限、次を追跡する必要があります。

- 指数名
- 銘柄code
- 企業名
- セクター
- 構成ウェート
- 適用開始日
- 取得元URL
- 取得日時
- 基準日
- source file hash

### 財務data

最低限、次を区別します。

- PBR
- ROE
- 配当利回り
- 対応する会計期間
- 連結・単体
- 実績・予想
- 単位
- 取得元
- 取得日

読売333とTOPIXを比較する場合、同じ基準日または比較可能な時点へ揃えます。欠損を0として扱いません。

### 再配布とlicense

指数構成銘柄、財務data、指数methodologyには利用・再配布条件があります。公開repositoryへraw dataをcommitする前に、取得元の規約を確認します。

---

## 処理の流れ

```text
raw YAML
  ├─ yomiuri333 constituents
  └─ financials / TOPIX comparison
        │
        ▼
src/ingest/csv_to_canonical.py
        │
        ▼
data/processed/canonical.csv
        │
        ├─ PBR statistics
        ├─ ROE statistics
        ├─ dividend yield statistics
        └─ sector HHI / top-10 weight
        │
        ▼
JSON metrics
        │
        ├─ README生成
        └─ GitHub Pages生成
```

raw dataが不足する場合、scheduled workflowは分析をskipします。skipは成功した分析ではありません。

---

## セットアップ

### 必要環境

- Python 3.11以上
- Git

### 依存関係

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Windows PowerShellでは、環境に合うactivate commandを使用します。

---

## 検証

```bash
ruff check src tests
black --check src tests
mypy src
pytest
```

GitHub Actionsの`.github/workflows/ci.yml`でも同じ種類の検証を行います。

テスト成功は、現在の指数dataが揃っていることや、投資上の結論が正しいことを意味しません。

---

## 手動分析

raw dataを準備した後、workflowの処理順に実行します。

```bash
python src/ingest/csv_to_canonical.py \
  --input data/raw/yomiuri333_constituents.yaml \
  --fin data/raw/financials.yaml \
  --out data/processed/canonical.csv

python src/analysis/pbr_stats.py \
  --in data/processed/canonical.csv \
  --out data/processed/pbr.json

python src/analysis/roe_stats.py \
  --in data/processed/canonical.csv \
  --out data/processed/roe.json

python src/analysis/sector_hhi.py \
  --in data/processed/canonical.csv \
  --out data/processed/hhi.json

python src/analysis/yield_stats.py \
  --in data/processed/canonical.csv \
  --out data/processed/yield.json
```

各scriptの正確なargumentは`--help`とsourceを確認してください。

---

## READMEとsiteの生成

metricsが揃った場合:

```bash
python src/render/write_readme.py \
  --template docs/templates/README.template.md \
  --pbr data/processed/pbr.json \
  --roe data/processed/roe.json \
  --hhi data/processed/hhi.json \
  --yield data/processed/yield.json \
  --notes data/processed/codex_notes.md \
  --out README.md
```

```bash
python src/render/build_site.py \
  --pbr data/processed/pbr.json \
  --roe data/processed/roe.json \
  --hhi data/processed/hhi.json \
  --yield data/processed/yield.json \
  --notes data/processed/codex_notes.md \
  --out docs/index.html
```

生成templateは、metricsから導けない固定結論を含めてはいけません。

---

## OpenAI API連携

`src/codex/codex_runner.py`は、計算済みmetricsを日本語で要約するoptional処理です。

```text
OPENAI_API_KEY
```

API keyを設定しても、LLM commentaryは計算結果やsource dataの正準にはなりません。API error時にworkflowが継続する設計であるため、commentaryの欠落を分析成功と混同しません。

---

## GitHub Actions

### CI

- Ruff
- Black
- mypy
- pytest

### Analyze & Update README

平日のscheduled runと手動実行があります。

raw dataが揃っている場合だけ、正規化、metrics、README、Pagesを更新します。data不在時はskipします。

### Pages

metricsが揃っている場合は分析siteを生成します。揃っていない場合は、checked-inの未計算status pageを公開します。

---

## ディレクトリ構成

```text
.github/workflows/          CI、scheduled analysis、Pages
data/raw/                   入力data。現在はplaceholderのみ
data/processed/             生成metrics。現在は未生成
docs/index.html             Pages用statusまたは分析結果
docs/templates/             README・HTML生成template
src/ingest/                 canonical data生成
src/analysis/               PBR、ROE、yield、HHI
src/render/                 README・site生成
src/codex/                  optional LLM commentary
tests/                      unit test
要件定義.yaml               当初の要件
```

---

## セキュリティ

保存しないもの:

- API key、token、cookie
- 契約上再配布できない指数・財務data
- 未公開企業情報
- 個人の証券口座情報
- LLMへ送信してはいけないdata

GitHub Actions secretをREADME、log、生成siteへ出力しません。

---

## 既知の制約

- 現在のraw dataとmetricsはありません。
- 自動更新workflowはdata取得自体を実装しておらず、所定のraw fileが必要です。
- 読売333とTOPIXの構成基準・ウェート・基準日を揃える処理は、入力品質に依存します。
- transaction cost、turnover、rebalance impact、実リターンは現在のmetricsに含みません。
- OpenAI commentaryはoptionalで、未取得でも分析workflowが継続します。
- GitHub Pagesの存在は、最新分析結果の存在を意味しません。
- 本リポジトリは投資助言、売買推奨、将来収益の保証ではありません。

---

## ライセンス

MIT License。詳細は[`LICENSE`](LICENSE)を参照してください。data sourceには別の利用条件が適用されます。

**README実体監査:** 2026年8月4日
