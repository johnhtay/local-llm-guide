# Evidence for benchmark and cost claims

Prepared November 11, 2026. Monetary values are in US dollars. API means application programming interface.

## Verdicts

| Claim | Verdict | Required qualification |
|---|---|---|
| A 27-point capability gap | Supported for one named historical comparison | Gemini 4 Carbon (High), 60, versus DeepSeek V4.1 Flash 1017 (Max), 33, on November 4, 2026. This is not a time-invariant gap between all commercial and open-weight models. |
| US$0.60 per task for leading open weights | Supported for the named DeepSeek configuration | This is an Intelligence-Index-weighted API inference estimate for DeepSeek V4.1 Flash 1017 (Max), not a local or typical scientific-task cost. |
| US$10 to US$13 per task for leading commercial models | Too broad as originally written | US$10.04 applies to Claude Opus 5.5 (Max) and US$12.99 to Claude Fable 5.1 (Max). Other leading commercial configurations cost substantially less. |
| Guide produced for about US$16 | Reproduced as a counterfactual estimate | Eight guide-related sessions yield US$16.040 using the dated rounded OpenRouter rates and the token accounting below. This is not observed expenditure. |

## Artificial Analysis snapshot evidence

### Historical captures, November 4, 2026

1. [Intelligence Index v5.0.1 evaluation page, archived at 02:28 UTC](https://web.archive.org/web/20261104022811/https://artificialanalysis.ai/evaluations/artificial-analysis-intelligence-index):
   > “Gemini 4 Carbon (High) scores the highest on Artificial Analysis Intelligence Index with a score of 60…”

   The page defines the Index as a composite of nine evaluations and defines cost per task as a weighted average across those evaluations.

2. [DeepSeek V4.1 Flash 1017 model record, archived at 17:03 UTC](https://web.archive.org/web/20261104170342/https://artificialanalysis.ai/models/deepseek-v4-1-flash-1017):
   > “DeepSeek V4.1 Flash 1017 (Max) scores 33 on the Artificial Analysis Intelligence Index…”

   and:
   > “On average, it costs $0.60 per task to evaluate DeepSeek V4.1 Flash 1017 (Max) on the Intelligence Index.”

   The archived page explicitly labels this configuration “Open weights model”.

### Dated supporting records

3. [Artificial Analysis Intelligence Index v5 announcement, October 27, 2026](https://artificialanalysis.ai/articles/artificial-analysis-intelligence-index-v5):
   > “Claude Opus 5.5 (max) costs $10.04 per Intelligence Index task…”

   The announcement lists Claude Fable 5.1 (Max) at US$13.04 under v5.0. The v5.0.1 comparison below displays US$12.99, supporting an approximate US$10 to US$13 range for these two configurations only.

4. [Gemini 4 Carbon versus DeepSeek V4.1 Flash comparison](https://artificialanalysis.ai/models/comparisons/gemini-4-carbon-vs-deepseek-v4-1-flash-1017), accessed November 11, 2026:
   - Intelligence Index: 60 versus 33.
   - Cost per task: US$7.76 versus US$0.60.
   - Cost to run the complete Intelligence Index: US$8,240 versus US$521. This confirms that per-task cost is not whole-battery cost.

5. [Claude Opus 5.5 versus Claude Fable 5.1 comparison](https://artificialanalysis.ai/models/comparisons/claude-opus-5-5-vs-claude-fable-5-1), accessed November 11, 2026:
   - Cost per task: US$10.04 versus US$12.99.
   - Both are maximum-effort configurations with the default fallback shown by the source.

6. [Intelligence benchmarking methodology](https://artificialanalysis.ai/methodology/intelligence-benchmarking), accessed November 11, 2026. The source defines cost per task as follows:
   > “Each evaluation’s cost is calculated from input, cache hit, cache write, reasoning, and answer token prices, divided by task count, and weighted by its Intelligence Index weight.”

These are model-, reasoning-effort-, token-use-, cache- and API-price-dependent estimates. They are not measures of scientific validity, total cost of ownership or the cost of a typical research task.

## Guide-cost calculation

The request set is the eight eligible OpenCode sessions whose working directory was the guide-authoring repository. Eligibility applies the same wall-time, active-time, warming-artifact and exclusion filters as the guide's `mine_totals.py` script. Generated tokens include visible output and reasoning tokens. Input tokens include uncached input, cache reads and cache writes. All input categories are charged at the full prompt rate, with no cache discount.

Rounded OpenRouter rates checked November 10, 2026:

| Model used for repricing | Sessions | Input tokens, including cache | Generated tokens, including reasoning | Prompt rate per million | Output rate per million | Cost |
|---|---:|---:|---:|---:|---:|---:|
| GLM-5.3 | 2 | 11,942,251 | 188,990 | US$0.07 | US$1.40 | US$1.101 |
| GLM-5.3-Flash | 6 | 365,993,853 | 3,746,729 | US$0.04 | US$0.08 | US$14.939 |
| **Total** | **8** | **377,936,104** | **3,935,719** | | | **US$16.040** |

Arithmetic:

- GLM-5.3: `11,942,251 / 1,000,000 × 0.07 + 188,990 / 1,000,000 × 1.40 = US$1.10054357`.
- GLM-5.3-Flash: `365,993,853 / 1,000,000 × 0.04 + 3,746,729 / 1,000,000 × 0.08 = US$14.93949244`.
- Combined: `US$16.04003601`, reported as approximately US$16.

The machine-readable rate extract is `openrouter_2026-11-11.json`. Its live values, US$0.0699/US$1.40 for GLM-5.3 and US$0.0399/US$0.0784 for GLM-5.3-Flash per million prompt/generated tokens, are consistent with the rounded rates used above. The calculation deliberately retains the rounded November 10 rates rather than rewriting history with later precision.

This estimate excludes human labor, local hardware, electricity, external tool charges, search charges and credit-purchase fees. Local requests and requests served under other model aliases are assigned the GLM-5.3-Flash surrogate rate, following the guide's published convention.

## Recommended manuscript wording

> Repricing the model requests used to produce the accompanying guide against OpenRouter endpoint rates captured on November 10, 2026 yielded an estimated inference cost of US$16. This counterfactual estimate excludes human labor, local hardware and electricity; token totals, rates and calculations are provided in S1 Text.

> In a November 4, 2026 snapshot of Artificial Analysis Intelligence Index v5.0.1, Gemini 4 Carbon (High) scored 60 and DeepSeek V4.1 Flash 1017 (Max) scored 33, a 27-point difference [13]. The source's Index-weighted API cost per task was US$0.60 for DeepSeek V4.1 Flash 1017 (Max), compared with US$10.04 for Claude Opus 5.5 (Max) and US$12.99 for Claude Fable 5.1 (Max) [13]. These model- and effort-specific inference estimates are neither full-battery costs nor measures of scientific-task validity or total cost of ownership.

## Glossary

- **API:** Application programming interface, the mechanism through which a client requests model inference.
- **Cache read/write:** Reused or newly stored prompt-context tokens. The guide-cost calculation prices both as full-price input.
- **Counterfactual estimate:** The price that a recorded request set would have incurred under a specified provider and rate card, not actual expenditure.
- **Index-weighted cost per task:** Artificial Analysis's weighted average inference cost across the nine evaluations in its Intelligence Index.
