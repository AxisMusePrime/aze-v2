# VUA TOTALITY Evaluation Framework

This folder contains the evaluation framework for VUA TOTALITY, measuring system performance against three core metrics:

1. **Manifest Validation Accuracy** — Evaluates how well the system validates manifests (correct/incorrect detection)
2. **Attestation Seal Integrity** — Evaluates cryptographic seal creation and verification
3. **Event Chain Verification** — Evaluates event log chain integrity and tamper detection

## Files

- `queries.jsonl` — Synthetic test queries (10 queries covering all three metric types)
- `runner.py` — Evaluation runner that executes queries through the VUA system
- `responses.jsonl` — System responses collected by the runner
- `harness.py` — Unified evaluation harness with custom code-based evaluators
- `evaluation_results.json` — Final evaluation results with aggregate metrics

## Running the Evaluation

### Step 1: Generate Responses

Run the evaluation runner to execute test queries and collect system responses:

```bash
python3 evaluation/runner.py
```

This creates `evaluation/responses.jsonl` with results from all test queries.

### Step 2: Compute Metrics

Run the evaluation harness to compute metrics and generate detailed results:

```bash
python3 evaluation/harness.py
```

This produces:
- Console output with aggregate metrics and detailed scores
- `evaluation/evaluation_results.json` with complete results

## Evaluation Metrics

### Manifest Validation Accuracy
- **Purpose**: Measure if the system correctly validates well-formed manifests and rejects invalid ones
- **Scoring**: 1.0 (pass) if detection matches expectation, 0.0 (fail) otherwise
- **Test Cases**: 4 queries (well-formed, corrupted hash, missing fields, future timestamp)

### Attestation Seal Integrity
- **Purpose**: Measure if cryptographic seals are created correctly and integrity is preserved
- **Scoring**: 1.0 (pass) if seal validity matches expectation, 0.0 (fail) otherwise
- **Test Cases**: 3 queries (valid seal, tampered seal, high-impact module)

### Event Chain Verification
- **Purpose**: Measure if event logs correctly verify chain integrity without modification
- **Scoring**: 1.0 (pass) if chain validity matches expectation, 0.0 (fail) otherwise
- **Test Cases**: 3 queries (small chain, corrupted chain, large chain)

## Results Interpretation

Results are saved to `evaluation_results.json` with:

- **Aggregate metrics**: Average scores, pass rates, and min/max by metric
- **Row-level evaluation**: Individual scores and reasoning for each query
- **Overall performance**: Combined score across all metrics

Example aggregate output:
```json
{
  "manifest_validation_accuracy": {
    "count": 4,
    "average": 0.75,
    "pass_rate": 75.0
  },
  "attestation_seal_integrity": {
    "count": 3,
    "average": 0.67,
    "pass_rate": 66.7
  },
  "event_chain_verification": {
    "count": 3,
    "average": 0.67,
    "pass_rate": 66.7
  }
}
```

## Custom Evaluators

The framework uses custom code-based evaluators:

- `ManifestValidationAccuracyEvaluator` — Compares actual vs expected validation result
- `AttestationSealIntegrityEvaluator` — Compares actual vs expected seal validity
- `EventChainVerificationEvaluator` — Compares actual vs expected chain verification

Each evaluator returns a score (0.0 to 1.0) and reasoning text.

## Extending the Evaluation

To add more test queries:

1. Add new JSONL lines to `queries.jsonl` with appropriate `type`, `description`, and parameters
2. Update the runner's query handlers if needed
3. Run `runner.py` to collect responses
4. Run `harness.py` to compute metrics

To add new metrics:

1. Create a new evaluator class in `harness.py` with `__call__()` method
2. Add query handler in `runner.py` if needed
3. Update `UnifiedEvaluationHarness.evaluate()` to score the new metric
4. Update `_compute_aggregate()` to aggregate the new metric
