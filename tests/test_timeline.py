from unconformity.scanner import scan_repository
from unconformity.timeline import render_timeline


def test_timeline_renders(git_repo):
    result = scan_repository(git_repo.working_tree_dir)
    content = render_timeline(result)
    assert "Timeline:" in content


def test_timeline_marks_unconformities(force_push_repo):
    result = scan_repository(force_push_repo.working_tree_dir)
    content = render_timeline(result)
    assert "angular" in content
    assert "Legend:" in content
