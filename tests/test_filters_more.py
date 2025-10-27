import os
import types
import pytest

from structkit import filters


def test_slugify_basic():
    assert filters.slugify("Hello World!") == "hello-world"
    assert filters.slugify("Already-Slugified_123") == "already-slugified123"


def test_get_default_branch_success(monkeypatch):
    # Build a minimal fake Github client
    class FakeRepo:
        default_branch = "main"

    class FakeGithub:
        def __init__(self, token=None):
            self.token = token
        def get_repo(self, name):
            assert name == "owner/repo"
            return FakeRepo()

    monkeypatch.setenv("GITHUB_TOKEN", "tok")
    monkeypatch.setattr(filters, "Github", FakeGithub)

    assert filters.get_default_branch("owner/repo") == "main"


def test_get_default_branch_error(monkeypatch):
    class FakeGithub:
        def get_repo(self, name):
            raise Exception("boom")

    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.setattr(filters, "Github", FakeGithub)
    filters.cache.clear()

    assert filters.get_default_branch("owner/repo") == "DEFAULT_BRANCH_ERROR"


def test_get_latest_release_success(monkeypatch):
    class FakeRepo:
        default_branch = "dev"
        def get_latest_release(self):
            class R:
                tag_name = "v1.2.3"
            return R()

    class FakeGithub:
        def __init__(self, token=None):
            pass
        def get_repo(self, name):
            return FakeRepo()

    monkeypatch.setattr(filters, "Github", FakeGithub)
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    # Clear cache between tests to ensure function recomputes
    filters.cache.clear()

    assert filters.get_latest_release("owner/repo") == "v1.2.3"


def test_get_latest_release_falls_back_to_default_branch(monkeypatch):
    class FakeRepo:
        default_branch = "main"
        def get_latest_release(self):
            raise Exception("no releases")

    class FakeGithub:
        def get_repo(self, name):
            return FakeRepo()

    monkeypatch.setattr(filters, "Github", FakeGithub)
    filters.cache.clear()

    assert filters.get_latest_release("owner/repo") == "main"


def test_get_latest_release_error(monkeypatch):
    class FakeRepo:
        def get_latest_release(self):
            raise Exception("no releases")

    class FakeGithub:
        def get_repo(self, name):
            raise Exception("bad repo")

    monkeypatch.setattr(filters, "Github", FakeGithub)
    filters.cache.clear()

    assert filters.get_latest_release("owner/repo") == "LATEST_RELEASE_ERROR"
