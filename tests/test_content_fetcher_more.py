import io
import os
import stat
import subprocess
from pathlib import Path

import pytest

from structkit.content_fetcher import ContentFetcher


def test_fetch_local_file(tmp_path):
    p = tmp_path / "file.txt"
    p.write_text("hello")
    cf = ContentFetcher(cache_dir=tmp_path / "cache")
    assert cf.fetch_content(f"file://{p}") == "hello"


def test_fetch_http_url_caches(monkeypatch, tmp_path):
    url = "https://example.com/data.txt"

    class Resp:
        text = "DATA"
        def raise_for_status(self):
            return None

    def fake_get(u):
        assert u == url
        return Resp()

    cf = ContentFetcher(cache_dir=tmp_path / "cache")
    monkeypatch.setattr("structkit.content_fetcher.requests.get", fake_get)

    # First call populates cache
    assert cf.fetch_content(url) == "DATA"

    # Second call should read from cache and not invoke requests.get
    def boom(u):
        raise AssertionError("should not be called due to cache hit")
    monkeypatch.setattr("structkit.content_fetcher.requests.get", boom)
    assert cf.fetch_content(url) == "DATA"


def test_fetch_github_https_and_pull(monkeypatch, tmp_path):
    cf = ContentFetcher(cache_dir=tmp_path / "cache")
    repo_dir = tmp_path / "cache" / "owner_repo_main"
    file_rel = "path/to/file.txt"
    file_full = repo_dir / file_rel

    # Simulate repo already cloned -> should call pull
    repo_dir.mkdir(parents=True, exist_ok=True)
    file_full.parent.mkdir(parents=True, exist_ok=True)
    file_full.write_text("GDATA")

    calls = {"pull": 0, "clone": 0}

    def fake_run(args, check):
        if args[:2] == ["git", "clone"]:
            calls["clone"] += 1
            # create the structure for clone case
            repo_dir.mkdir(parents=True, exist_ok=True)
            file_full.parent.mkdir(parents=True, exist_ok=True)
            file_full.write_text("GDATA")
        elif args[:3] == ["git", "-C", str(repo_dir)]:
            calls["pull"] += 1
        else:
            raise AssertionError(f"Unexpected git call: {args}")

    monkeypatch.setattr(subprocess, "run", fake_run)

    out = cf.fetch_content("githubhttps://owner/repo/main/path/to/file.txt")
    assert out == "GDATA"
    # Since repo existed, should have pulled
    assert calls["pull"] == 1


def test_fetch_github_clone_path(monkeypatch, tmp_path):
    # Force fresh clone path
    cf = ContentFetcher(cache_dir=tmp_path / "cache")
    repo_dir = tmp_path / "cache" / "owner_repo_dev"
    file_rel = "f.txt"
    file_full = repo_dir / file_rel

    calls = {"clone": 0}

    def fake_run(args, check):
        if args[:2] == ["git", "clone"]:
            calls["clone"] += 1
            repo_dir.mkdir(parents=True, exist_ok=True)
            file_full.parent.mkdir(parents=True, exist_ok=True)
            file_full.write_text("X")
        else:
            raise AssertionError("Only clone expected")

    monkeypatch.setattr(subprocess, "run", fake_run)

    out = cf.fetch_content("github://owner/repo/dev/f.txt")
    assert out == "X"
    assert calls["clone"] == 1


def test_fetch_github_file_not_found(monkeypatch, tmp_path):
    cf = ContentFetcher(cache_dir=tmp_path / "cache")
    repo_dir = tmp_path / "cache" / "owner_repo_main"

    def fake_run(args, check):
        # Ensure repo exists but no file
        if args[:2] == ["git", "clone"]:
            repo_dir.mkdir(parents=True, exist_ok=True)
        elif args[:3] == ["git", "-C", str(repo_dir)]:
            return None

    monkeypatch.setattr(subprocess, "run", fake_run)

    with pytest.raises(FileNotFoundError):
        cf.fetch_content("githubssh://owner/repo/main/does_not_exist.txt")


def test_fetch_unsupported():
    cf = ContentFetcher(cache_dir=Path("/tmp/cache"))
    with pytest.raises(ValueError):
        cf.fetch_content("unknown://foo")


def test_http_error_bubbles_and_no_cache(monkeypatch, tmp_path):
    url = "https://example.com/oops"

    class Resp:
        def raise_for_status(self):
            raise Exception("HTTP error")

    def fake_get(u):
        assert u == url
        return Resp()

    cf = ContentFetcher(cache_dir=tmp_path / "cache")
    monkeypatch.setattr("structkit.content_fetcher.requests.get", fake_get)

    with pytest.raises(Exception):
        cf.fetch_content(url)

    # Subsequent call uses requests again (no cache file was created)
    called = {"count": 0}
    def fake_get2(u):
        called["count"] += 1
        return Resp()
    monkeypatch.setattr("structkit.content_fetcher.requests.get", fake_get2)
    with pytest.raises(Exception):
        cf.fetch_content(url)
    assert called["count"] == 1


def test_github_invalid_path_raises(monkeypatch, tmp_path):
    cf = ContentFetcher(cache_dir=tmp_path / "cache")
    with pytest.raises(ValueError):
        cf.fetch_content("github://owner/repo-only")
    with pytest.raises(ValueError):
        cf.fetch_content("githubhttps://owner/repo-only")
    with pytest.raises(ValueError):
        cf.fetch_content("githubssh://owner/repo-only")


def test_s3_unavailable_raises_valueerror(monkeypatch, tmp_path):
    cf = ContentFetcher(cache_dir=tmp_path / "cache")
    # Force unavailable path; dispatcher will not include s3 and treat as unsupported
    import structkit.content_fetcher as mod
    monkeypatch.setattr(mod, "boto3_available", False)
    with pytest.raises(ValueError):
        cf.fetch_content("s3://bucket/key.txt")


def test_gcs_unavailable_raises_valueerror(monkeypatch, tmp_path):
    cf = ContentFetcher(cache_dir=tmp_path / "cache")
    import structkit.content_fetcher as mod
    monkeypatch.setattr(mod, "gcs_available", False)
    with pytest.raises(ValueError):
        cf.fetch_content("gs://bucket/key.txt")


def test_s3_invalid_path_raises_valueerror(monkeypatch, tmp_path):
    cf = ContentFetcher(cache_dir=tmp_path / "cache")
    # Ensure available so it reaches regex
    import structkit.content_fetcher as mod
    monkeypatch.setattr(mod, "boto3_available", True)
    # Do not mock boto3 since we only test invalid pattern, which raises earlier
    with pytest.raises(ValueError):
        cf.fetch_content("s3://invalid-format")


def test_gcs_invalid_path_raises_valueerror(monkeypatch, tmp_path):
    cf = ContentFetcher(cache_dir=tmp_path / "cache")
    import structkit.content_fetcher as mod
    monkeypatch.setattr(mod, "gcs_available", True)
    with pytest.raises(ValueError):
        cf.fetch_content("gs://invalid-format")


def test_git_clone_error_bubbles(monkeypatch, tmp_path):
    cf = ContentFetcher(cache_dir=tmp_path / "cache")
    def fake_run(args, check):
        if args[:2] == ["git", "clone"]:
            raise subprocess.CalledProcessError(1, args)
    monkeypatch.setattr(subprocess, "run", fake_run)
    with pytest.raises(subprocess.CalledProcessError):
        cf.fetch_content("github://owner/repo/main/file.txt")


def test_git_pull_error_bubbles(monkeypatch, tmp_path):
    cf = ContentFetcher(cache_dir=tmp_path / "cache")
    repo_dir = tmp_path / "cache" / "owner_repo_main"
    # Simulate existing repo so it tries pull
    repo_dir.mkdir(parents=True, exist_ok=True)
    (repo_dir / "file.txt").write_text("x")

    def fake_run(args, check):
        if args[:3] == ["git", "-C", str(repo_dir)]:
            raise subprocess.CalledProcessError(1, args)
    monkeypatch.setattr(subprocess, "run", fake_run)

    with pytest.raises(subprocess.CalledProcessError):
        cf.fetch_content("githubhttps://owner/repo/main/file.txt")


def test_github_raw_fetch_success_no_git_calls(monkeypatch, tmp_path):
    cf = ContentFetcher(cache_dir=tmp_path / "cache")
    # Ensure no existing cache repo
    # Prepare requests.get to return content
    class Resp:
        def __init__(self, text):
            self.text = text
        def raise_for_status(self):
            return None
    called = {"http": 0, "git": 0}
    def fake_get(url, timeout=None):
        called["http"] += 1
        assert url == "https://raw.githubusercontent.com/owner/repo/main/path/to/file.txt"
        return Resp("RAW_DATA")
    def fake_run(args, check):
        called["git"] += 1
        raise AssertionError("git should not be called on raw success")
    monkeypatch.setattr("structkit.content_fetcher.requests.get", fake_get)
    monkeypatch.setattr(subprocess, "run", fake_run)

    out = cf.fetch_content("githubhttps://owner/repo/main/path/to/file.txt")
    assert out == "RAW_DATA"
    assert called["http"] == 1
    assert called["git"] == 0


def test_github_raw_fetch_retries_then_fallback_to_git(monkeypatch, tmp_path):
    cf = ContentFetcher(cache_dir=tmp_path / "cache")
    repo_dir = tmp_path / "cache" / "owner_repo_main"
    file_rel = "path/to/file.txt"
    file_full = repo_dir / file_rel

    # Fail HTTP calls
    def bad_get(url, timeout=None):
        raise Exception("network down")
    monkeypatch.setattr("structkit.content_fetcher.requests.get", bad_get)

    calls = {"clone": 0}
    def fake_run(args, check):
        if args[:2] == ["git", "clone"]:
            calls["clone"] += 1
            repo_dir.mkdir(parents=True, exist_ok=True)
            file_full.parent.mkdir(parents=True, exist_ok=True)
            file_full.write_text("GIT_DATA")
        elif args[:3] == ["git", "-C", str(repo_dir)]:
            # no-op for pull after clone path (not expected here)
            return None
        else:
            raise AssertionError(f"Unexpected git call: {args}")
    monkeypatch.setattr(subprocess, "run", fake_run)

    # Speed up retries/backoff by setting retries=0 via env
    monkeypatch.setenv("STRUCTKIT_HTTP_RETRIES", "0")

    out = cf.fetch_content("githubhttps://owner/repo/main/path/to/file.txt")
    assert out == "GIT_DATA"
    assert calls["clone"] == 1


def test_github_deny_network_uses_git(monkeypatch, tmp_path):
    cf = ContentFetcher(cache_dir=tmp_path / "cache")
    repo_dir = tmp_path / "cache" / "owner_repo_main"
    file_full = repo_dir / "path.txt"

    # Deny network
    monkeypatch.setenv("STRUCTKIT_DENY_NETWORK", "1")

    # HTTP must not be called
    def bad_get(url, timeout=None):
        raise AssertionError("HTTP should not be invoked when STRUCTKIT_DENY_NETWORK=1")
    monkeypatch.setattr("structkit.content_fetcher.requests.get", bad_get)

    def fake_run(args, check):
        if args[:2] == ["git", "clone"]:
            repo_dir.mkdir(parents=True, exist_ok=True)
            file_full.write_text("OK")
        elif args[:3] == ["git", "-C", str(repo_dir)]:
            return None
    monkeypatch.setattr(subprocess, "run", fake_run)

    out = cf.fetch_content("githubhttps://owner/repo/main/path.txt")
    assert out == "OK"


def test_github_existing_cache_prefers_git(monkeypatch, tmp_path):
    cf = ContentFetcher(cache_dir=tmp_path / "cache")
    repo_dir = tmp_path / "cache" / "owner_repo_main"
    file_full = repo_dir / "path.txt"
    repo_dir.mkdir(parents=True, exist_ok=True)
    file_full.write_text("CACHE_DATA")

    # HTTP must not be needed; if called, fail
    def bad_get(url, timeout=None):
        raise AssertionError("HTTP should not be called when cache exists")
    monkeypatch.setattr("structkit.content_fetcher.requests.get", bad_get)

    pulls = {"count": 0}
    def fake_run(args, check):
        if args[:3] == ["git", "-C", str(repo_dir)]:
            pulls["count"] += 1
    monkeypatch.setattr(subprocess, "run", fake_run)

    out = cf.fetch_content("githubhttps://owner/repo/main/path.txt")
    assert out == "CACHE_DATA"
    assert pulls["count"] == 1
