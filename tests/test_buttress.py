from unconformity.detectors.buttress import detect_buttress


def test_detect_buttress(rebase_repo):
    events = detect_buttress(rebase_repo)
    assert events
    assert events[0].type.value == "buttress"
    # Rebase should produce author_date ≠ committer_date
    assert (
        events[0].forensic_details["author_date"]
        != events[0].forensic_details["committer_date"]
    )
    # Delta should be significant (> 1 hour)
    assert events[0].forensic_details["delta_seconds"] >= 3600
