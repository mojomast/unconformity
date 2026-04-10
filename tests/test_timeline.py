from unconformity.scanner import scan_repository
from unconformity.timeline import render_timeline


def test_timeline_renders(git_repo):
    result = scan_repository(git_repo.working_tree_dir)
    content = render_timeline(result)
    assert "Timeline:" in content
