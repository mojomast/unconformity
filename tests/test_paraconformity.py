from unconformity.detectors.paraconformity import detect_paraconformity


def test_detect_paraconformity(time_gap_repo):
    events = detect_paraconformity(time_gap_repo)
    assert events
    assert events[0].type.value == "paraconformity"
