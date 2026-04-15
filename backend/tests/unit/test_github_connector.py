from app.services.github_service import GitHubService


def test_should_ignore_common_paths():
    service = GitHubService()
    assert service.should_ignore_file("node_modules/pkg/index.js")
    assert service.should_ignore_file(".git/config")
    assert service.should_ignore_file("file.pyc")
    assert not service.should_ignore_file("src/main.py")


def test_headers_include_user_agent():
    service = GitHubService()
    assert "User-Agent" in service.headers

