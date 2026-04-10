from unconformity.scanner import scan_repository


def test_scan_repository_returns_result(git_repo):
    result = scan_repository(git_repo.working_tree_dir)
    assert result.repo_path == git_repo.working_tree_dir
    assert result.total_commits_scanned >= 1
