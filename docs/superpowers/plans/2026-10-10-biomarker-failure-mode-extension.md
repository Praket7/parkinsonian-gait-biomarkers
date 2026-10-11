# v4.6 Biomarker Failure-Mode Extension Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan. Follow test-driven development and verification-before-completion. Do not alter frozen v4.1-v4.5 results to improve v4.6 outcomes.

## Goal

Extend the existing fixed healthy-reference Parkinsonian gait biomarker into a failure-mode analysis that answers three prespecified questions using only the currently authorized WearGait-derived data and artifacts:

1. Does the **final composite score**, not merely its eight inputs, agree when computed from PKMAS exports versus independently reconstructed raw walkway data?
2. When the scalar score is unstable across visits separated by at least six months, is the **multivariate direction of gait abnormality** nevertheless conserved within people more than expected by random pairing?
3. Does the existing long-interval stability conclusion materially depend on **which healthy participants define the normative reference**?

No external cohort is required for this version.

## Architecture

v4.6 is a new immutable analysis layer on top of existing versioned work.

- Reuse the exact SHA256-checked frozen v4.1 healthy-reference model.
- Reuse the existing v4.3 raw-walkway reconstruction and 252 matched V1 analytical trials.
- Reuse the corrected v4.5 longitudinal endpoint definition and inclusion logic.
- Add no Parkinson-outcome-trained features or weights.
- Keep all new analyses under `src/v4_6`, `scripts/run_v4_6_*`, `tests/v4_6`, and `results/v4_6`.
- Freeze the v4.6 protocol before any result-producing run.
- Treat all prior result directories as read-only inputs.

The scientific design is specified in:

`docs/superpowers/specs/2026-10-10-biomarker-failure-mode-design.md`

## Tech stack

- Python >= 3.10
- NumPy
- pandas
- SciPy
- statsmodels
- scikit-learn
- matplotlib
- PyYAML
- pytest

No new machine-learning dependency is needed.

## Global constraints

1. **No clinical-outcome leakage.** Parkinson severity outcomes may not enter healthy-reference fitting, feature weighting, covariance estimation, or threshold selection.
2. **No frozen-model mutation.** The v4.1 model file and SHA256 contract remain unchanged.
3. **No rewriting history.** v4.3 and v4.5 outputs remain intact even if v4.6 results conflict with expectations.
4. **Same reference for paired visits.** Within every healthy-reference bootstrap iteration, both longitudinal visits for a participant must be scored under the exact same resampled reference.
5. **Long-interval wording only.** Do not call six-plus-month stability short-term test-retest reliability.
6. **Agreement is not correlation.** Pearson/Spearman are secondary; ICC(A,1), CCC, bias, and limits of agreement carry the analytical interpretation.
7. **No arbitrary new success threshold.** Where no scientifically established error tolerance exists, report estimates and uncertainty instead of inventing a binary clinical qualification gate.
8. **Directional similarity is not reliability.** Call it within-person pattern conservation, directional stability, or precision-metric similarity.
9. **No external data in v4.6.** External transport belongs to a separate later extension.
10. **No source clinical data committed.** Only deidentified derived outputs already consistent with repository policy may be written under `results/`.
11. **Determinism.** Every bootstrap and permutation uses a fixed seed from the versioned config.
12. **Failure is publishable.** Null or unfavorable results remain in the report and cannot trigger redesign of the prespecified primary analysis.

## Review focus

Code review should pay special attention to:

- accidental use of PD rows when fitting a healthy reference,
- unit mismatches between PKMAS and reconstructed features,
- session 1 and session 2 being scored under different bootstrap references,
- covariance/precision orientation errors,
- confusing reference-bootstrap spread with participant sampling confidence intervals,
- treating paired long-interval change as pure measurement error,
- post-hoc switching between mean and median statistics,
- silent exclusion differences from v4.5,
- sign or task-label inversions,
- reporting precision-metric cosine for zero-length residuals,
- modifying historical files rather than adding a new version.

---

# Task 1: Freeze the v4.6 protocol and protect historical results

**Files:**

- Create: `configs/v4_6_analysis.yaml`
- Create: `docs/v4_6_preregistration.md`
- Create: `scripts/freeze_v4_6_protocol.py`
- Create: `scripts/check_v4_6_freeze.py`
- Create: `tests/v4_6/test_v4_6_freeze.py`
- Create: `tests/v4_6/test_v4_5_immutability.py`

## Step 1.1: Write failing freeze tests

Create `tests/v4_6/test_v4_6_freeze.py` with tests that expect:

- config exists,
- preregistration exists,
- frozen protocol hash manifest exists after freeze script runs,
- `check_v4_6_freeze.py` returns no failures for untouched files,
- modifying a copied protected artifact produces a hash mismatch in the helper logic.

Create `tests/v4_6/test_v4_5_immutability.py` that records or verifies hashes for the historical scientific inputs v4.6 is not allowed to alter. At minimum include:

- `results/v4_1/frozen/v4_1_control_model.json`
- `src/v4_1/normative.py`
- `results/v4_3/v1_reconstruction_agreement.csv`
- `results/v4_3/v1_reconstruction_qc.json`
- `results/v4_5/h4b_endpoint_error_corrected.csv`
- the corrected v4.5 long-interval report/output used as the historical interpretation source

Do not make the test dependent on Git metadata alone. Hash file bytes.

Run:

```bash
pytest -q tests/v4_6/test_v4_6_freeze.py tests/v4_6/test_v4_5_immutability.py
```

Expected: FAIL because v4.6 protocol files do not yet exist.

## Step 1.2: Create the locked config

`configs/v4_6_analysis.yaml` should contain only prespecified choices, for example:

```yaml
protocol_version: v4.6.0
seed: 20261010
participant_bootstrap_iterations: 2000
control_reference_bootstrap_iterations: 2000
direction_permutations: 10000
primary_direction_statistic: median
multiple_testing: holm
primary_tasks:
  - SelfPace
  - HurriedPace
protected_model: results/v4_1/frozen/v4_1_control_model.json
v1_reconstructed_features: results/v4_3/v1_reconstructed_features.csv
v1_reconstruction_qc: results/v4_3/v1_reconstruction_qc.json
v45_longitudinal_source: results/v4_5/h4b_endpoint_error_corrected.csv
```

If implementation needs an additional path, add it before freezing the protocol, not after observing scientific results.

## Step 1.3: Write `docs/v4_6_preregistration.md`

The preregistration must specify before execution:

- three core research questions,
- exact formulas,
- primary versus secondary outputs,
- permutation direction,
- bootstrap units,
- two-task multiplicity correction,
- no external cohort,
- no MDS-UPDRS tuning,
- no new clinically meaningful threshold,
- acceptable interpretations for favorable and unfavorable outcomes.

The preregistration should explicitly state that the prior v4.5 conclusion remains historical truth regardless of v4.6.

## Step 1.4: Implement freeze/check scripts

Follow the established v4.1/v4.2 pattern.

`freeze_v4_6_protocol.py` should hash:

- config,
- preregistration,
- critical implementation files once created,
- protected frozen inputs.

`check_v4_6_freeze.py` should fail fast when:

- a required file is absent,
- a protected file hash differs,
- the frozen v4.1 model hash contract no longer validates,
- config values differ from the frozen manifest.

## Step 1.5: Run freeze tests

```bash
python scripts/freeze_v4_6_protocol.py --write
pytest -q tests/v4_6/test_v4_6_freeze.py tests/v4_6/test_v4_5_immutability.py
```

Expected: PASS.

## Step 1.6: Commit

```bash
git add configs/v4_6_analysis.yaml docs/v4_6_preregistration.md scripts/freeze_v4_6_protocol.py scripts/check_v4_6_freeze.py tests/v4_6

git commit -m "preregister v4.6 biomarker failure-mode analysis"
```

---

# Task 2: Add covariance-aware deviation geometry primitives

**Files:**

- Create: `src/v4_6/__init__.py`
- Create: `src/v4_6/deviation_geometry.py`
- Create: `tests/v4_6/test_deviation_geometry.py`

## Step 2.1: Write failing geometry tests

Tests must establish mathematical correctness independently of the real dataset.

Required cases:

### Existing score identity

For a synthetic residual `r` and covariance `S`:

```python
D2 = r @ np.linalg.pinv(S) @ r
```

must equal the squared magnitude returned by the v4.6 geometry helper and match the v4.1 score formulation.

### Identical direction

`precision_cosine(r, 3*r, P)` returns approximately `1.0`.

### Opposite direction

`precision_cosine(r, -2*r, P)` returns approximately `-1.0`.

### Precision-orthogonal direction

Construct vectors with `a.T @ P @ b == 0`; expected cosine approximately `0.0`.

### Positive scaling invariance

Scaling either vector by a positive constant must not change the direction similarity.

### Zero magnitude

A zero or numerically degenerate residual must return `np.nan` or raise a documented exception. Choose one behavior and test it explicitly.

### Correlated dimensions

Include a non-diagonal covariance matrix to ensure the implementation is not silently using ordinary Euclidean cosine.

Run:

```bash
pytest -q tests/v4_6/test_deviation_geometry.py
```

Expected: FAIL before implementation.

## Step 2.2: Implement minimal geometry API

Recommended interface in `src/v4_6/deviation_geometry.py`:

```python
def conditional_residual(table: pd.DataFrame, model: dict) -> np.ndarray:
    ...


def precision_matrix(model: dict) -> np.ndarray:
    ...


def deviation_magnitude(residual: np.ndarray, precision: np.ndarray) -> float:
    ...


def precision_cosine(a: np.ndarray, b: np.ndarray, precision: np.ndarray) -> float:
    ...


def precision_angle(a: np.ndarray, b: np.ndarray, precision: np.ndarray) -> float:
    ...
```

Use `np.linalg.pinv` exactly as the frozen score does. Clip numerical cosine values to `[-1, 1]` before `arccos`.

Do not introduce PCA, learned embeddings, supervised components, or feature weighting.

## Step 2.3: Add compatibility test against `src.v4_1.normative.score`

Generate a synthetic table with age/height and all eight features. Confirm:

```python
v4_1_score ** 2 == r.T @ P @ r
```

within a strict numerical tolerance.

This is a critical guardrail. If it fails, stop before any scientific analysis.

## Step 2.4: Run tests

```bash
pytest -q tests/v4_6/test_deviation_geometry.py
```

Expected: PASS.

## Step 2.5: Commit

```bash
git add src/v4_6/deviation_geometry.py src/v4_6/__init__.py tests/v4_6/test_deviation_geometry.py

git commit -m "add frozen-reference deviation geometry"
```

---

# Task 3: Implement longitudinal deviation-pattern conservation

**Files:**

- Create: `scripts/run_v4_6_deviation_geometry.py`
- Create: `tests/v4_6/test_deviation_geometry_runner.py`
- Output: `results/v4_6/deviation_direction_pairs.csv`
- Output: `results/v4_6/deviation_direction_summary.csv`
- Output: `results/v4_6/deviation_direction_null.csv`

## Step 3.1: Write failing runner tests using synthetic longitudinal data

Construct deidentified synthetic rows with participant, session, task, age, height, and all eight features.

Required behaviors:

1. Only participants with both sessions enter the paired analysis.
2. SelfPace and HurriedPace are analyzed separately.
3. Duplicate participant/session/task rows raise an error.
4. Session labels are explicitly sorted rather than relying on row order.
5. Within-person cosine is calculated from residual vectors under the frozen precision matrix.
6. Participant bootstrap samples participants, not individual rows.
7. Permutation shuffles session-2 participant pairing within task only.
8. Fixed seed reproduces byte-equivalent summary statistics.
9. Holm correction is applied to exactly the two primary task p-values.
10. Zero-magnitude residuals are counted and excluded according to the preregistered rule rather than silently coerced.

Run:

```bash
pytest -q tests/v4_6/test_deviation_geometry_runner.py
```

Expected: FAIL.

## Step 3.2: Reuse corrected v4.5 endpoint construction

Do not rewrite the longitudinal parser from scratch if the existing v4.5 pipeline already produces the correct featurewise-median session endpoint. Extract or reuse the common endpoint-building function.

If reusable logic is currently embedded in a script, refactor without changing historical outputs:

- move shared pure functions into a version-neutral helper only if tests prove historical output identity,
- otherwise import the existing result-producing helper directly.

The implementation must preserve:

- exact four-pass rule,
- unit conversion,
- participant inclusion,
- task names,
- age and height mapping,
- session pairing.

## Step 3.3: Implement observed within-person statistic

For each primary task:

1. load frozen v4.1 model,
2. calculate residual vector for each visit,
3. calculate precision-metric cosine for each participant,
4. calculate median observed cosine,
5. calculate 2,000 participant-bootstrap medians and percentile 95% CI.

Save per-participant deidentified records to `deviation_direction_pairs.csv` with fields such as:

```text
participant
task
score_s1
score_s2
absolute_magnitude_change
precision_cosine
precision_angle_radians
precision_angle_degrees
```

Do not include names, dates of birth, source file paths containing sensitive information, or clinical free text.

## Step 3.4: Implement 10,000-label permutation null

For each task:

- freeze session-1 participant order,
- permute session-2 participant assignments,
- calculate median cosine,
- save one row per permutation with task, iteration, null statistic.

Compute one-sided p-value using the plus-one correction.

Apply Holm correction across the two tasks.

`deviation_direction_summary.csv` should include at minimum:

```text
task
n_pairs
median_within_similarity
bootstrap_ci_low
bootstrap_ci_high
null_median
permutation_p
holm_p
median_angle_degrees
zero_residual_exclusions
```

## Step 3.5: Add null calibration test

On synthetic independent/randomly paired data, confirm permutation p-values do not deterministically report significance due to an implementation bug.

On synthetic perfectly conserved within-person directions with shuffled between-person directions, confirm the test detects the known signal.

## Step 3.6: Run tests

```bash
pytest -q tests/v4_6/test_deviation_geometry.py tests/v4_6/test_deviation_geometry_runner.py
```

Expected: PASS.

## Step 3.7: Commit

```bash
git add scripts/run_v4_6_deviation_geometry.py tests/v4_6/test_deviation_geometry_runner.py

git commit -m "add longitudinal deviation-pattern analysis"
```

Do not commit result files until the protocol is frozen and the real-data run has been verified.

---

# Task 4: Validate the final composite score analytically

**Files:**

- Create: `src/v4_6/score_agreement.py`
- Create: `scripts/run_v4_6_score_agreement.py`
- Create: `tests/v4_6/test_score_agreement.py`
- Output: `results/v4_6/score_level_analytical_agreement.csv`
- Optional deidentified pair output: `results/v4_6/score_level_analytical_pairs.csv`

## Step 4.1: Write failing agreement tests

Required synthetic cases:

### Perfect identity

Reference and candidate arrays identical:

- ICC(A,1) approximately 1
- CCC approximately 1
- bias 0
- MAE 0
- RMSE 0
- Bland-Altman lower/upper 0

### Systematic additive bias

Use `candidate = reference + constant`.

Expected:

- Pearson approximately 1
- agreement metrics detect nonzero bias

This test prevents correlation from being misreported as equivalence.

### Scale distortion

Use `candidate = 1.2 * reference`.

Expected:

- high correlation can coexist with degraded CCC/absolute agreement.

### Frozen-score propagation

Construct two eight-feature rows and confirm the runner applies the same frozen model and same age/height covariates to both PKMAS and raw versions.

## Step 4.2: Build score-pair table from existing v4.3 reconstruction

Input:

`results/v4_3/v1_reconstructed_features.csv`

This table already contains matched PKMAS and raw feature columns. Join the correct V1 age/height covariates using the same verified logic as v4.3/v4.1.

Apply the exact same unit conversion to both measurement paths before scoring.

For each matched trial produce:

```text
participant
task
score_pkmas
score_raw
difference_pkmas_minus_raw
absolute_difference
pair_mean
```

No outcome variable is needed.

## Step 4.3: Calculate final-score agreement

Use or extend `src/v4_2/analytical_equivalence.py` rather than duplicating formulas.

Primary summary:

- n matched trials
- ICC(A,1)
- CCC
- mean bias
- MAE
- RMSE
- Bland-Altman low/high

Secondary:

- Pearson r
- Spearman rho

Where feasible, bootstrap matched trials or preferably participants for confidence intervals around ICC/CCC while preserving repeated trials belonging to a participant. If added, this decision must be present in the preregistration before the freeze is finalized.

## Step 4.4: Compare analytical disagreement with long-interval change descriptively

Read the corrected v4.5 paired-change output rather than recomputing or altering it.

Report scale comparisons such as:

- median absolute PKMAS/raw score difference
- 95th percentile absolute PKMAS/raw score difference
- median six-plus-month absolute score change by task
- ratio of these descriptive quantities

Do not compute a p-value whose only purpose is to claim analytical error is “significantly smaller.” The scientific point is scale, not null-hypothesis theater.

## Step 4.5: Run tests

```bash
pytest -q tests/v4_6/test_score_agreement.py
```

Expected: PASS.

## Step 4.6: Commit

```bash
git add src/v4_6/score_agreement.py scripts/run_v4_6_score_agreement.py tests/v4_6/test_score_agreement.py

git commit -m "validate final gait score analytical agreement"
```

---

# Task 5: Propagate healthy-reference uncertainty through longitudinal results

**Files:**

- Create: `src/v4_6/reference_uncertainty.py`
- Create: `scripts/run_v4_6_reference_uncertainty.py`
- Create: `tests/v4_6/test_reference_uncertainty.py`
- Output: `results/v4_6/reference_uncertainty_longitudinal.csv`
- Output: `results/v4_6/reference_uncertainty_individual.csv`

## Step 5.1: Write failing bootstrap-contract tests

Required tests:

1. Control-only fitting rejects any table containing PD rows, matching v4.1 behavior.
2. Resampling unit is participant, not row.
3. All rows for a sampled control participant remain together.
4. Duplicate bootstrap draws are assigned unique synthetic IDs before fitting, matching the established v4.1 bootstrap approach.
5. Both longitudinal sessions in one bootstrap iteration use the same fitted model.
6. Fixed seed produces identical first N bootstrap draws.
7. Number of iterations comes only from config.
8. The reference bootstrap does not call a Parkinson outcome association function.
9. Reference-bootstrap percentiles are labeled as reference uncertainty, not confidence intervals for population sampling.

Run:

```bash
pytest -q tests/v4_6/test_reference_uncertainty.py
```

Expected: FAIL.

## Step 5.2: Reuse the exact control bootstrap sampling logic from v4.1

The established v4.1 pattern is:

```python
people = controls.participant_id.unique()
chosen = rng.choice(people, len(people), replace=True)
sampled = pd.concat([
    controls[controls.participant_id.eq(person)].assign(
        participant_id=f"control_boot_{j}"
    )
    for j, person in enumerate(chosen)
], ignore_index=True)
```

Move this into a tested helper only if doing so leaves historical v4.1 unchanged. Otherwise reproduce the algorithm exactly in the new module and test equivalence on a synthetic fixture.

## Step 5.3: For each of 2,000 control-reference resamples

For each iteration:

1. fit age/height healthy conditional mean,
2. fit healthy residual covariance using the frozen covariance method,
3. calculate the precision matrix,
4. apply this same reference to every eligible longitudinal session,
5. calculate task-specific ICC(A,1),
6. calculate task-specific median within-person precision cosine,
7. calculate task-specific mean and median paired scalar change,
8. retain participant-level paired scalar change.

Do **not** compute a nested 2,000-person bootstrap inside each control bootstrap. That would conflate two uncertainty sources and add huge computational cost without answering the prespecified question.

## Step 5.4: Build aggregate reference-uncertainty output

`reference_uncertainty_longitudinal.csv` should contain one row per reference bootstrap per task:

```text
resample
task
n_pairs
icc_a1
median_precision_cosine
mean_score_change
median_score_change
```

The final report computes across-reference summaries:

- median ICC
- 2.5th/97.5th reference percentiles
- fraction ICC >= 0.80
- median directional similarity
- 2.5th/97.5th reference percentiles for directional similarity

The historical participant-bootstrap BCa CI remains the primary sampling uncertainty for the original stability estimate.

## Step 5.5: Build individual reference-sensitivity output

For each deidentified participant/task summarize across 2,000 references:

```text
participant
task
original_change
reference_bootstrap_median_change
reference_bootstrap_low
reference_bootstrap_high
sign_stability_fraction
```

This is exploratory. The report must explicitly say it is not a clinically meaningful change interval.

## Step 5.6: Add adversarial tests

Synthetic test A:

- healthy reference is extremely stable across bootstrap samples,
- longitudinal score changes should barely move.

Synthetic test B:

- healthy controls contain two strongly separated subgroups,
- reference-bootstrap score changes should show wider uncertainty.

This confirms that the implementation is actually sensitive to reference uncertainty rather than accidentally reusing the original model every iteration.

## Step 5.7: Run tests

```bash
pytest -q tests/v4_6/test_reference_uncertainty.py
```

Expected: PASS.

## Step 5.8: Commit

```bash
git add src/v4_6/reference_uncertainty.py scripts/run_v4_6_reference_uncertainty.py tests/v4_6/test_reference_uncertainty.py

git commit -m "propagate healthy-reference uncertainty longitudinally"
```

---

# Task 6: Build an integrated failure-mode report and figures

**Files:**

- Create: `scripts/build_v4_6_report.py`
- Create: `tests/v4_6/test_v4_6_report.py`
- Output: `results/v4_6/failure_mode_summary.json`
- Output: `results/v4_6/v4_6_report.md`
- Output figures under: `results/v4_6/figures/`

## Step 6.1: Write failing report-integrity tests

Tests should assert that the generated report:

- contains exact sample sizes pulled from outputs, not handwritten constants,
- labels visits as six-plus-month long-interval observations,
- never calls the long-interval ICC short-term test-retest reliability,
- never says measurement error was ruled out,
- never claims diagnosis, progression tracking, treatment response, or clinical utility,
- distinguishes participant sampling uncertainty from control-reference uncertainty,
- reports unfavorable results when present,
- includes provenance paths for each headline number.

Use exact forbidden-claim strings and semantic pattern checks where practical.

## Step 6.2: Build `failure_mode_summary.json`

The JSON should be machine-readable and contain separate evidence blocks:

```json
{
  "protocol": "v4.6.0",
  "historical_score": {...},
  "score_level_analytical_agreement": {...},
  "longitudinal_direction_conservation": {...},
  "healthy_reference_uncertainty": {...},
  "claim_boundaries": {...}
}
```

Do not overwrite `report/AAN_submission_values.json` or any existing frozen submission artifact as part of the scientific run. Any later submission update must be a separate, explicit step after results are reviewed.

## Step 6.3: Generate figure 1 — validation/failure-mode map

A simple schematic should show:

```text
raw gait
   ↓
8 reconstructed inputs
   ↓ analytical bridge
fixed healthy-reference score
   ↓
cross-sectional severity evidence
   ↓
long-interval stability test
   ↓
failure-mode decomposition
   ├─ final-score analytical agreement
   ├─ magnitude vs direction
   └─ healthy-reference uncertainty
```

This figure is explanatory, not statistical.

## Step 6.4: Generate figure 2 — final-score analytical agreement

Include:

- PKMAS score vs raw-reconstructed score scatter with identity line
- Bland-Altman plot or a compact two-panel export if repository figure conventions allow

If the figure generator must remain one figure per file, create two files rather than a matplotlib subplot.

## Step 6.5: Generate figure 3 — direction conservation

Primary visual:

- observed within-person precision-cosine distribution
- null/random-pair distribution

Use separate task figures or clearly separated outputs. Do not manipulate axis ranges to exaggerate differences.

Optional descriptive heatmap:

- participant rows
- visit 1 and visit 2 signed deviation components
- fixed feature order

If a whitening representation is used for visualization, document the exact transform and state that inferential direction similarity is calculated by the precision-form equation.

## Step 6.6: Generate figure 4 — reference uncertainty

For each task show:

- distribution of ICC(A,1) across 2,000 healthy-reference resamples
- vertical line for original-reference ICC
- visual reference at 0.80 labeled as the historical benchmark, not a newly optimized threshold

Do the same for median directional similarity if useful, but avoid excessive figures.

## Step 6.7: Write report in evidence-first order

Recommended report structure:

1. **Question** — what failure mode is being tested?
2. **Locked design** — what was frozen before results?
3. **Final-score analytical agreement**
4. **Magnitude versus direction**
5. **Healthy-reference uncertainty**
6. **Integrated interpretation**
7. **What remains unresolved**

The integrated interpretation should use a truth table such as:

| Analytical score agreement | Direction conservation | Reference sensitivity | Interpretation |
|---|---|---|---|
| Strong | Present | Low | scalar instability is not explained by raw-score derivation or reference choice; multivariate pattern may persist |
| Strong | Absent | Low | longitudinal instability extends to phenotype composition |
| Weak | Any | Any | analytical score propagation is a plausible contributor and must be addressed first |
| Strong | Any | High | normative reference sampling materially affects the conclusion |

This table is a reasoning aid, not an automated decision rule.

## Step 6.8: Run report tests

```bash
pytest -q tests/v4_6/test_v4_6_report.py
```

Expected: PASS.

## Step 6.9: Commit

```bash
git add scripts/build_v4_6_report.py tests/v4_6/test_v4_6_report.py

git commit -m "add v4.6 failure-mode report builder"
```

---

# Task 7: Execute the frozen analysis and verify results

**Prerequisite:** The v4.6 protocol hash must already be frozen and `check_v4_6_freeze.py` must pass.

## Step 7.1: Verify freeze before touching real results

```bash
python scripts/check_v4_6_freeze.py
```

Expected: PASS with zero failures.

## Step 7.2: Run final-score agreement

Use the same authorized V1 source paths or precomputed versioned derivatives already accepted by v4.3.

Example interface:

```bash
python scripts/run_v4_6_score_agreement.py \
  --model results/v4_1/frozen/v4_1_control_model.json \
  --reconstructed results/v4_3/v1_reconstructed_features.csv \
  --output results/v4_6
```

The exact CLI must be documented in `--help` and the preregistration.

## Step 7.3: Run deviation geometry

Example:

```bash
python scripts/run_v4_6_deviation_geometry.py \
  --model results/v4_1/frozen/v4_1_control_model.json \
  --output results/v4_6 \
  <existing authorized longitudinal input arguments>
```

No session outcome labels are permitted as model-fitting inputs.

## Step 7.4: Run reference uncertainty

Example:

```bash
python scripts/run_v4_6_reference_uncertainty.py \
  --config configs/v4_6_analysis.yaml \
  --output results/v4_6 \
  <existing authorized V1 control and longitudinal input arguments>
```

Log:

- seed
- number of iterations
- number of controls per resample
- eligible longitudinal pair counts
- frozen model provenance

## Step 7.5: Build report

```bash
python scripts/build_v4_6_report.py \
  --results results/v4_6 \
  --output results/v4_6/v4_6_report.md
```

## Step 7.6: Run targeted tests

```bash
pytest -q tests/v4_6
```

Expected: all PASS.

## Step 7.7: Run full repository test suite

```bash
pytest -q
```

Expected: all PASS.

Do not report completion if any historical test fails.

## Step 7.8: Recheck historical hashes

```bash
python scripts/check_v4_6_freeze.py
```

Expected: protected historical artifacts unchanged.

## Step 7.9: Inspect scientific outputs manually

Before committing results, inspect:

- pair counts against v4.5,
- score distributions for impossible values,
- zero/NaN residual counts,
- ICC numerical stability,
- permutation null centering,
- bootstrap tails,
- any single participant dominating direction similarity,
- task labels,
- scale/unit consistency.

At minimum rerun direction analysis after leave-one-participant-out influence screening as a **diagnostic only**. Do not replace the preregistered primary statistic based on that diagnostic.

## Step 7.10: Commit verified results

Only after all tests and checks pass:

```bash
git add results/v4_6

git commit -m "add frozen v4.6 biomarker failure-mode results"
```

---

# Task 8: Claim audit and scientific release gate

**Files:**

- Create: `scripts/check_v4_6_claims.py`
- Create: `tests/v4_6/test_v4_6_claims.py`
- Update only after results are final: `README.md` and research documentation that summarizes the latest evidence

## Step 8.1: Write failing claim tests

The checker should flag unsupported phrases in v4.6-generated documentation such as:

- `diagnoses Parkinson`
- `tracks disease progression`
- `clinically validated biomarker`
- `treatment response established`
- `short-term reliable`
- `measurement error ruled out`
- `externally validated`
- `generalizes across sites`

Allow those strings only where explicitly negated or quoted in a claim-boundary section if the checker can distinguish context safely; otherwise phrase the report differently.

## Step 8.2: Add evidence-state table

The final documentation should maintain explicit states such as:

- cross-sectional severity association: SUPPORTED
- healthy-reference robustness of cross-sectional association: SUPPORTED
- incremental severity ranking beyond speed: SUPPORTED
- eight-input analytical reconstruction: SUPPORTED
- final-score analytical agreement: report v4.6 result without overstating qualification
- six-plus-month scalar stability: FAILED historical criterion
- longitudinal deviation-pattern conservation: v4.6 result
- sensitivity to healthy-reference sampling: v4.6 result
- short-term test-retest reliability: NOT ESTIMABLE
- responsiveness: NOT ESTIMABLE
- independent full-score transport: NOT ESTIMABLE

## Step 8.3: Run claim checker and tests

```bash
python scripts/check_v4_6_claims.py
pytest -q tests/v4_6/test_v4_6_claims.py
pytest -q
```

Expected: PASS.

## Step 8.4: Final verification evidence

Capture in the final commit message or release note:

- exact `pytest -q` pass count,
- protocol hash,
- frozen v4.1 model SHA256,
- v4.6 result file hashes,
- exact git commit SHA.

Never state that the analysis is complete based only on generated files; tests and freeze checks must have run successfully.

## Step 8.5: Commit

```bash
git add scripts/check_v4_6_claims.py tests/v4_6/test_v4_6_claims.py README.md docs results/v4_6

git commit -m "finalize v4.6 evidence and claim audit"
```

---

# Deferred follow-up: external transport

Do not implement this inside v4.6.

The next extension should be frozen separately because it introduces a new population and measurement-compatibility decisions. The preferred first external cohort is the UNESP spatiotemporal gait dataset because it provides 63 PD participants, 63 matched controls, age, height, UPDRS-III, Hoehn and Yahr stage, and several features compatible with the existing healthy-reference framework.

A later external protocol should define a **locked compatible-feature projection before opening target outcomes**. It should not claim the full eight-input score replicated when the external walking protocol cannot estimate the two variability features comparably.

Secondary external datasets can test narrower questions such as timing/variability transport or multisite representation transport.

---

# Why this plan is scientifically stronger than adding another prediction model

The current evidence problem is not lack of algorithmic complexity. It is lack of resolution about *where* validation succeeds and fails.

This plan adds three orthogonal pieces of evidence:

1. **Endpoint-level analytical evidence** — whether the actual composite survives raw reconstruction.
2. **Phenotype-geometry evidence** — whether a scalar instability hides a more conserved multivariate pattern.
3. **Normative-reference uncertainty evidence** — whether the conclusion depends on which healthy participants define normal.

These additions directly attack the most credible skeptical explanations for the current longitudinal result while preserving the outcome-blind design. Favorable findings would materially strengthen the biomarker framework. Unfavorable findings would still produce a sharper and more defensible scientific conclusion.

That asymmetry is intentional: the extension is designed to discover what is true, not to force the biomarker to pass.
