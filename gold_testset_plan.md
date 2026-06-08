# Gold Testset Plan: remote-hiring-radar
> Generated: 2026-06-08  
> Tier: A-core  
> Project bucket: Job matching / signal ranking  
> Priority score: 93  
> GitHub: https://github.com/DavidZhu258/remote-hiring-radar

## Evaluation Goal

验证职位评分是否真的能区分强匹配、弱匹配、误报和地域/资历不可行。

## Target Gold Set

- Target size: **150**
- Eval type: `ranking`
- Seed cases created now: **3**
- First next step from matrix: 把近期 200 个岗位抽样人工标注三档，并锁定 scoring regression suite。

## Test-set Design

120-180 个职位-候选人/项目配对：强匹配、弱匹配、不匹配、边界岗位、地域限制、资历过高岗位。

## Metrics

Accuracy metrics:

```text
Precision@10; NDCG@20; false-positive rate; eligibility error rate; reason-label agreement; calibration by bucket
```

Feasibility metrics:

```text
daily scrape success; source freshness; deterministic reproducibility; manual review time saved; cost per 100 jobs
```

Rubric seed metrics:

- precision_at_10
- ndcg_at_20
- false_positive_rate
- eligibility_error_rate
- reason_agreement
- cost_per_100_jobs

## Required Hard Cases

LATAM-only、美国身份要求、senior/staff 资历错配、标题强匹配但技能缺口大。

## Build Plan

1. Replace the 3 placeholder seed cases in `evals/gold/seed_gold.jsonl` with real examples.
2. Fill `evals/gold/annotation_template.csv` with expected labels, evidence references, and reviewer status.
3. Run a manual seed evaluation and save raw output in `evals/results/`.
4. Only after the seed suite is stable, expand `evals/gold/full_gold.jsonl` toward the target size.
5. Publish evidence only when the report includes both accuracy and feasibility metrics.

## Acceptance Bar

For portfolio use, the project must pass all seed hard negatives, have a reproducible fresh-run path, and show at least one saved result artifact under `evals/results/`.

## Evidence to Add

TopK 命中表、误报案例、规则解释、申请建议样例。
