# evals/ for remote-hiring-radar

Minimum evaluation scaffold for `remote-hiring-radar`.

## Layout

```text
evals/
  gold/seed_gold.jsonl
  gold/full_gold.jsonl
  gold/annotation_template.csv
  rubrics/rubric.yaml
  scripts/README.md
  fixtures/
  results/
```

## Contract

- Eval type: `ranking`
- Target full gold size: `150`
- Seed cases: `3`
- Metrics: precision_at_10, ndcg_at_20, false_positive_rate, eligibility_error_rate, reason_agreement, cost_per_100_jobs

Replace placeholders with real fixtures/records before using any result as portfolio evidence.
