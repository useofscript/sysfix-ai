from sysfixai.core import diagnose

def test_diagnose():
    issues = diagnose()
    assert isinstance(issues, list)
