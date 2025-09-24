# 読売333 批判的検証（自動更新）

[![CI Status]({{ badges.ci.image }})]({{ badges.ci.link }}) [![Pages]({{ badges.pages.image }})]({{ badges.pages.link }})

最終更新: {{ updated_at }}

## 結論（要約）
1. 読売333は等ウェート設計によりディープバリュー要素が強く、景気循環の再評価局面で相対優位を取りやすい。
2. 低ROE・低モメンタム銘柄への比重が高く、恒常的な超過リターンはロジック上限定的である。
3. 年1回の入替＋年3回のウェート調整でコストは抑えられるが、分散メリットは指標データに依存する。

## 主要メトリクス（自動集計）
| 指標 | 読売333 | TOPIX |
| --- | --- | --- |
| PBR<1倍比率 | {{ pbr.lt1.yomiuri333 | format_percent }} | {{ pbr.lt1.topix | format_percent }} |
| ROE中央値 | {{ roe.median.yomiuri333 | format_number }} | {{ roe.median.topix | format_number }} |
| 配当利回り平均 | {{ dy.mean.yomiuri333 | format_percent(2) }} | {{ dy.mean.topix | format_percent(2) }} |
| セクター集中度（HHI） | {{ hhi.hhi.yomiuri333 | format_number(3) }} | {{ hhi.hhi.topix | format_number(3) }} |
| 上位10銘柄構成比 | {{ hhi.top10_weight.yomiuri333 | format_percent(1) }} | {{ hhi.top10_weight.topix | format_percent(1) }} |

> 備考: データは公開情報に基づく近似値であり、欠損補完・推定が含まれる場合があります。

## ロジック上の強み
{% if logic.strengths %}
{% for item in logic.strengths %}- {{ item }}
{% endfor %}
{% else %}
- データ不足のため強みを特定できません。
{% endif %}

## ロジック上の弱み
{% if logic.weaknesses %}
{% for item in logic.weaknesses %}- {{ item }}
{% endfor %}
{% else %}
- データ不足のため弱みを特定できません。
{% endif %}

## データの限界（注意事項）
{% if logic.cautions %}
{% for item in logic.cautions %}- {{ item }}
{% endfor %}
{% endif %}
- 公開情報ベースでの推定値であり、速報値・リバランス時のタイムラグを含む可能性があります。
- 算出ロジックは自動化済みですが、入力データの更新頻度・品質に依存します。

## モニタリングノート
{% if notes %}
{{ notes }}
{% else %}
- 最新のCodexコメントは未取得です（OPENAI_API_KEY未設定またはエラー）。
{% endif %}

## 変更履歴
- 自動更新ワークフロー: [Analyze & Update README](.github/workflows/analyze-and-readme.yml)
- 静的サイト出力: [docs/index.html](docs/index.html)

