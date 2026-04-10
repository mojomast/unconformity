from unconformity.detectors.disconformity import detect_disconformity


def test_detect_disconformity(squash_repo):
    events = detect_disconformity(squash_repo)
    assert events
    assert events[0].type.value == "disconformity"
