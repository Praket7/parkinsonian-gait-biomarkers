from pathlib import Path
def test_measurement_modules_are_outcome_blind():
 forbidden=("mds_updrs","hoehn","clinical severity")
 for path in (Path("src")/"v4").glob("*.py"):
  if path.name in {"qualification.py","evidence_synthesis.py","__init__.py"}: continue
  assert not any(token in path.read_text().lower() for token in forbidden), path
