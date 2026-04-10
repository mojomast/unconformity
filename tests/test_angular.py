from unconformity.detectors.angular import detect_angular


def test_detect_angular(force_push_repo):
    events = detect_angular(force_push_repo)
    assert events
    assert events[0].type.value == "angular"
    assert events[0].forensic_details["fast_forward"] is False
    assert len(events[0].affected_commits) == 2
