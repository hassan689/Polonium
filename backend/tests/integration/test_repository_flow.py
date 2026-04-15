import pytest

from app.services.repo_ingestion import RepoIngestionService


def test_detect_language_integration():
    service = RepoIngestionService()
    assert service._detect_language("src/main.py") == "Python"
    assert service._detect_language("app/page.tsx") == "TypeScript"


@pytest.mark.benchmark(group="repository-indexing")
def test_repository_indexing_speed_benchmark(benchmark):
    service = RepoIngestionService()

    def _workload():
        for path in ["a.py", "b.ts", "c.go", "d.rs", "e.md"] * 200:
            service._detect_language(path)

    benchmark(_workload)

