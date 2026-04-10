from unconformity.detectors.disconformity import detect_disconformity


def test_detect_disconformity(squash_repo):
    events = detect_disconformity(squash_repo)
    assert events
    assert events[0].type.value == "disconformity"
    # Should find the hidden commits from the squash merge
    assert events[0].forensic_details["hidden_commit_count"] >= 1
    # Should detect the squash commit touched multiple files
    assert events[0].forensic_details["files_changed"] >= 4
