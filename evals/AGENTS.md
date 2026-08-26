# Evaluation-Specific Instructions

- Treat expected results, assertions, rubrics, and fault injections as Harness-private data. Never pass them to the Agent adapter or runtime prompt.
- Contract cases may encode an expected recommendation only when all inputs and policy outcomes are fixed. Reference research cases must not contain a completed report or expected recommendation.
- Every deterministic evaluator change requires one passing contract case and one fault fixture proving the defect is detected.
- Keep case inputs, hidden expectations, and generated run artifacts structurally separate. Generated artifacts belong under ignored `.eval-runs/` paths.
