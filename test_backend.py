from backend import analyze_message

def test_bullying_medium():
    r=analyze_message("Some senior students keep threatening me after school")
    assert r.category=="Bullying / Personal Safety" and r.risk=="Medium" and not r.emergency

def test_cyber_low():
    r=analyze_message("Someone sent me a strange Instagram message")
    assert r.category=="Cyber Safety" and r.risk=="Low"

def test_high_risk():
    r=analyze_message("Someone is following me with a knife")
    assert r.risk=="High" and r.emergency and "112" in " ".join(r.steps)
