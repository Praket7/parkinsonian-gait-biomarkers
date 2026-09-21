import hashlib,json
from pathlib import Path
def test_v4_1_frozen_outputs_unchanged():
    for name,expected in json.loads(Path('configs/v4_1_frozen_hashes.json').read_text()).items():
        assert hashlib.sha256(Path(name).read_bytes()).hexdigest()==expected, f'V4_1_FROZEN_OUTPUT_MUTATED: {name}'
