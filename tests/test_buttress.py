from unconformity.detectors.buttress import detect_buttress


def test_detect_buttress(rebase_repo):
    events = detect_buttress(rebase_repo)
    assert events
    assert events[0].type.value == "buttress"
