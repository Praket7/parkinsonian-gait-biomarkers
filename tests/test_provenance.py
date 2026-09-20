import json
from pathlib import Path

from scripts.run_provenance import build_manifest


def test_manifest_hashes_config_and_never_reads_raw(tmp_path: Path):
    (tmp_path / "configs").mkdir()
    (tmp_path / "configs" / "analysis.yaml").write_text('analysis_version: "3.0"\n')
    (tmp_path / "data" / "raw").mkdir(parents=True)
    (tmp_path / "data" / "raw" / "participant.csv").write_text("participant_id,score\nP1,4\n")
    (tmp_path / "results" / "frozen").mkdir(parents=True)
    (tmp_path / "results" / "frozen" / "results.json").write_text(json.dumps({"status": "ok"}))

    manifest = build_manifest(tmp_path)

    assert manifest["analysis_version"] == "3.0"
    assert manifest["config"]["sha256"]
    assert all("raw" not in path for path in manifest["aggregate_result_sha256"])
    assert manifest["privacy"]["raw_data_read"] is False
