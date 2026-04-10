from unconformity.scanner import scan_repository


def test_scan_repository_returns_result(git_repo):
    result = scan_repository(git_repo.working_tree_dir)
    assert result.repo_path == git_repo.working_tree_dir
    assert result.total_commits_scanned >= 1


def test_scan_repository_filters_by_type(force_push_repo):
    result = scan_repository(force_push_repo.working_tree_dir, types=("angular",))
    assert result.unconformities
    assert all(item.type.value == "angular" for item in result.unconformities)


def test_scan_repository_detects_multiple_types(force_push_repo, time_gap_repo):
    force_push_result = scan_repository(force_push_repo.working_tree_dir)
    gap_result = scan_repository(time_gap_repo.working_tree_dir)
    assert force_push_result.unconformities
    assert gap_result.unconformities
