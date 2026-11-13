# Phase 4 — Evaluation and Ablations (about 2 weeks)

## Goal
Turn the pipeline into measured engineering: a golden dataset, a reproducible harness, ablation results and calibrated defaults.

## Scope
**In**: corpus assembly, question set (200), labelling, retrieval and answer runners, judge with calibration, ablations, abstention calibration, report, CI smoke gate.
**Out**: fine-tuning (Phase 7).

## Learning checklist
- [ ] IR evaluation metrics and bootstrap confidence intervals
- [ ] LLM-as-judge pitfalls (position bias, verbosity bias) and calibration with human labels
- [ ] Experiment tracking (MLflow optional) and reproducibility hygiene
- [ ] Dataset licensing basics

## Tasks
- [ ] Assemble 40 to 60 licensed documents; record in `SOURCES.md`
- [ ] Ingest corpus through the real pipeline (stable chunk anchors by doc + span)
- [ ] Generate candidate questions with an LLM; review and fix by hand; add 30 unanswerable questions manually; target 200 total with at least 150 reviewed
- [ ] Split by document: dev 30% / test 70%
- [ ] Implement metrics (Recall@k, MRR, nDCG, Hit@k) with chunk-to-anchor mapping
- [ ] Implement answer runner storing outputs and retrieved context
- [ ] Implement judge (structured output); hand-label 50 to 80 answers; compute Cohen's kappa; refine rubric until agreement is acceptable
- [ ] Add citation hard check and sentence-level support check
- [ ] Define ablation configs in YAML; run one-factor sweeps then a small grid
- [ ] Abstention sweep: precision/recall curve; choose and justify `tau`
- [ ] Run adversarial injection set; record attack success rate
- [ ] Generate report (doc 12 template) with tables and plots
- [ ] Update defaults in `PipelineConfig` based on dev results; **confirm on test split once**
- [ ] CI `eval-smoke` workflow with baseline tolerance
- [ ] Write ADR(s) for decisions driven by the data

## Tests required
- Metric implementations verified on tiny hand-computed cases.
- Harness determinism: two runs with the same config produce identical metrics (judge cache aside).
- Split integrity test: no document appears in both dev and test.

## Deliverables
`evals/reports/phase4-report.md`, results folder, README results table draft, CI gate, `v0.5`.

## Exit criteria
- [ ] Golden set of 200 questions with documented provenance and splits
- [ ] Ablation table with 95% CIs for retrieval configs
- [ ] Judge agreement (kappa) documented
- [ ] Chosen defaults justified by data; test-split numbers recorded once
- [ ] Smoke eval blocks regressions in CI
- [ ] Failure analysis of the 10 worst questions written

## Risks
Labelling effort; judge unreliability; overfitting to dev. Mitigation: timebox labelling in sessions of 50; calibrate judge; touch the test split sparingly.

## First tasks
1. Corpus + ingestion.
2. 60 questions labelled first; build metrics on those.
3. Remaining questions + splits.
4. Ablations; then judge and answer metrics.
