from unconformity.reporter import render_report
from unconformity.scanner import scan_repository


def test_reporter_outputs_text(git_repo):
    result = scan_repository(git_repo.working_tree_dir)
    content = render_report(result)
    assert "Unconformity Report" not in content
    assert "Repository:" in content
