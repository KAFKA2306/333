# 読売333 批判的検証 — 自動集計結果

[![CI](https://github.com/KAFKA2306/333/actions/workflows/ci.yml/badge.svg)](https://github.com/KAFKA2306/333/actions/workflows/ci.yml)
[![Pages](https://github.com/KAFKA2306/333/actions/workflows/pages.yml/badge.svg)](https://github.com/KAFKA2306/333/actions/workflows/pages.yml)

> **生成日時:** {{ updated_at }}  
> **注意:** この文書は入力dataから生成したsnapshotです。指数の現在状態を判断する前に、基準日、取得元、欠損、比較条件を確認してください。

## 主要metrics

| 指標 | 読売333 | TOPIX |
|---|---:|---:|
| PBR 1倍未満比率 | {{ pbr.lt1.yomiuri333 | format_percent }} | {{ pbr.lt1.topix | format_percent }} |
| ROE中央値 | {{ roe.median.yomiuri333 | format_number }} | {{ roe.median.topix | format_number }} |
| 配当利回り平均 | {{ dy.mean.yomiuri333 | format_percent(2) }} | {{ dy.mean.topix | format_percent(2) }} |
| セクターHHI | {{ hhi.hhi.yomiuri333 | format_number(3) }} | {{ hhi.hhi.topix | format_number(3) }} |
| 上位10銘柄構成比 | {{ hhi.top10_weight.yomiuri333 | format_percent(1) }} | {{ hhi.top10_weight.topix | format_percent(1) }} |

## dataから導ける観測

### 相対的な特徴

{% if logic.strengths %}
{% for item in logic.strengths %}- {{ item }}
{% endfor %}
{% else %}
- 現在のmetricsから明確な相対的特徴を特定できません。
{% endif %}

### リスク・弱点候補

{% if logic.weaknesses %}
{% for item in logic.weaknesses %}- {{ item }}
{% endfor %}
{% else %}
- 現在のmetricsから明確な弱点を特定できません。
{% endif %}

### data上の注意

{% if logic.cautions %}
{% for item in logic.cautions %}- {{ item }}
{% endfor %}
{% else %}
- 自動検出された追加注意事項はありません。
{% endif %}
- 公開情報には速報値、改訂、欠損、基準日の差が含まれる可能性があります。
- この比較だけではturnover、transaction cost、rebalance impact、将来returnを評価できません。

## optional commentary

{% if notes %}
{{ notes }}
{% else %}
- LLM commentaryは取得されていません。metricsとsource dataを直接確認してください。
{% endif %}

## project説明

目的、入力契約、計算方法、実行方法、既知の制約はrepositoryの通常READMEを参照してください。自動生成結果は、source URLと基準日を伴う場合だけ分析証拠として扱います。

- [scheduled analysis workflow](.github/workflows/analyze-and-readme.yml)
- [Pages workflow](.github/workflows/pages.yml)
- [公開site](docs/index.html)
