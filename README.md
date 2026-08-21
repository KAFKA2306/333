# 読売333 批判的検証

[![CI](https://github.com/KAFKA2306/333/actions/workflows/ci.yml/badge.svg)](https://github.com/KAFKA2306/333/actions/workflows/ci.yml)
[![Pages](https://github.com/KAFKA2306/333/actions/workflows/pages.yml/badge.svg)](https://github.com/KAFKA2306/333/actions/workflows/pages.yml)

読売株価指数333（読売333）とTOPIXを、同じ基準日・定義・出典を持つデータで比較するPython分析repositoryです。PBR、ROE、配当利回り、セクター集中度などを計算します。

> **現在の重要な境界:** 分析に必要なraw dataはrepositoryへ登録されていません。したがって、読売333の割安性・収益性・配当特性・分散効果・TOPIXに対する優位性について、現在このrepositoryから実証的な結論は出せません。

公開site: https://kafka2306.github.io/333/

## 検証する問い

- 読売333とTOPIXでPBR分布はどう違うか
- ROEと配当利回りの分布はどう違うか
- 等ウェート設計で銘柄・セクター集中度はどう変わるか
- 入替・ウェート調整・基準日の違いを考慮して比較可能か

指数設計の説明だけから `deep value`、低ROE、低momentum、将来の優位性などを推定しません。観測結果は入力dataと計算結果からのみ生成します。

## 入力契約

分析には少なくとも次が必要です。

```text
data/raw/yomiuri333_constituents.yaml
data/raw/financials.yaml
```

構成銘柄dataでは銘柄code、企業名、sector、weight、適用開始日、source URL、取得日時、基準日を追跡します。財務dataではPBR、ROE、配当利回りに加え、会計期間、連結/単体、実績/予想、単位、取得元、取得日を区別します。

欠損値を0へ変換しません。読売333とTOPIXは同じ基準日、または比較可能性を説明できる時点へ揃えます。指数・財務dataの再配布条件も取得元ごとに確認します。

## Data flow

```text
raw data
  -> src/ingest/csv_to_canonical.py
  -> data/processed/canonical.csv
  -> src/analysis/*
  -> JSON metrics
  -> README / GitHub Pages
```

raw dataが不足するscheduled runは分析をskipします。**skipは分析成功でも、metric=0でもありません。**

自動生成READMEの正準templateは [`docs/templates/README.template.md`](docs/templates/README.template.md) です。templateはmetricsから導けない固定結論を持たず、観測・注意点・optional commentaryを分離します。

## Setup / verification

Python 3.11以上を使用します。

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt

ruff check src tests
black --check src tests
mypy src
pytest
```

各analysis scriptの引数はsourceまたは`--help`を確認してください。CIの成功はcode/testの成功を示すだけで、現在の指数dataが揃っていることや投資上の結論を証明しません。

## Automation

- `.github/workflows/ci.yml`: lint / format / type / tests
- `.github/workflows/analyze-and-readme.yml`: raw dataがある場合だけ正規化・metric計算・README更新
- `.github/workflows/pages.yml`: Pages artifact生成・deploy

`src/codex/codex_runner.py` のLLM commentaryはoptionalです。計算済みmetricsやsource dataの代替authorityにはしません。

## Repository map

```text
data/raw/          input data
data/processed/    generated canonical data / metrics
src/ingest/        normalization
src/analysis/      PBR / ROE / yield / HHI
src/render/        README / Pages generation
src/codex/         optional commentary
docs/templates/    generated output templates
docs/index.html    current Pages artifact/status
tests/             regression tests
```

## Evidence and safety

保存しないもの:

- API key、token、cookie
- 再配布できない指数・財務data
- 未公開企業情報
- 個人の証券口座情報

Pagesの存在、LLM commentary、CI greenだけを分析結果の証拠にしません。source URL、基準日、入力data、計算結果を確認します。本repositoryは投資助言、売買推奨、将来収益の保証を目的としません。

## License

Codeは [MIT License](LICENSE) です。data sourceには取得元ごとの利用条件が適用されます。
