from unconformity.detectors.angular import detect_angular


def test_detect_angular(force_push_repo):
    events = detect_angular(force_push_repo)
    assert events
    assert events[0].type.value == "angular"
