from unconformity.detectors.nonconformity import detect_nonconformity


def test_detect_nonconformity(deleted_branch_repo):
    events = detect_nonconformity(deleted_branch_repo)
    assert events
    assert events[0].type.value == "nonconformity"
    assert events[0].forensic_details["unreachable_commit_count"] >= 1
