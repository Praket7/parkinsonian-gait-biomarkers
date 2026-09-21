from src.v4.carepd_matched import run
def test_care_route_is_explicit(tmp_path): assert run(tmp_path).empty
