from src.v4.qualification import evidence_row
def test_execution_is_not_association_pass(): assert evidence_row("x",{"status":"OK","q_value":.7},family="x",speed_construct="requires_speed_adjustment")["association_status"] == "FAIL"
