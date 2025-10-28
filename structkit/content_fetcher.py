# FILE: content_fetcher.py
import os
import re
import requests
import subprocess
from pathlib import Path
import hashlib
import logging

try:
  import boto3
  from botocore.exceptions import NoCredentialsError, ClientError
  boto3_available = True
except ImportError:
  boto3_available = False

try:
  from google.cloud import storage
  from google.api_core.exceptions import GoogleAPIError
  gcs_available = True
except ImportError:
  gcs_available = False


class ContentFetcher:
  def __init__(self, cache_dir=None):
    self.logger = logging.getLogger(__name__)
    self.cache_dir = Path(cache_dir or os.path.expanduser("~/.struct/cache"))
    self.cache_dir.mkdir(parents=True, exist_ok=True)

  def fetch_content(self, content_location):
    """
    Fetch content from a given location. Supported protocols:
    - Local file (file://)
    - HTTP/HTTPS (https://)
    - GitHub repository (github://owner/repo/branch/file_path)
    - GitHub HTTPS (githubhttps://owner/repo/branch/file_path)
    - GitHub SSH (githubssh://owner/repo/branch/file_path)
    - S3 bucket (s3://bucket_name/key)
    - Google Cloud Storage (gs://bucket_name/key)
    """
    protocol_map = {
      "file://": self._fetch_local_file,
      "https://": self._fetch_http_url,
      "github://": self._fetch_github_file,
      "githubhttps://": self._fetch_github_https_file,
      "githubssh://": self._fetch_github_ssh_file,
    }

    if boto3_available:
      protocol_map["s3://"] = self._fetch_s3_file
    if gcs_available:
      protocol_map["gs://"] = self._fetch_gcs_file

    for prefix, method in protocol_map.items():
      if content_location.startswith(prefix):
        # Only treat the raw HTTPS prefix as a direct URL fetch. All other
        # custom prefixes (e.g., githubhttps://, githubssh://) should have
        # their prefix stripped and be dispatched to the appropriate handler.
        if prefix == "https://":
          return method(content_location)
        else:
          return method(content_location[len(prefix):])

    raise ValueError(f"Unsupported content location: {content_location}")

  def _fetch_local_file(self, file_path):
    self.logger.debug(f"Fetching content from local file: {file_path}")
    file_path = Path(file_path)
    with file_path.open('r') as file:
      return file.read()

  def _fetch_http_url(self, url):
    self.logger.debug(f"Fetching content from URL: {url}")
    # Create a hash of the URL to use as a cache key
    cache_key = hashlib.md5(url.encode()).hexdigest()
    cache_file_path = self.cache_dir / cache_key

    if cache_file_path.exists():
      self.logger.debug(f"Loading content from cache: {cache_file_path}")
      with cache_file_path.open('r') as file:
        return file.read()

    response = requests.get(url)
    response.raise_for_status()
    with cache_file_path.open('w') as file:
      file.write(response.text)

    return response.text

  def _fetch_github_file(self, github_path):
    """
    Fetch a file from a GitHub repository using HTTPS.
    Dispatcher passes: owner/repo/branch/file_path
    """
    self.logger.debug(f"Fetching content from GitHub: {github_path}")
    match = re.match(r"([^/]+)/([^/]+)/([^/]+)/(.+)", github_path)
    if not match:
      raise ValueError("Invalid GitHub path. Expected owner/repo/branch/file_path")

    owner, repo, branch, file_path = match.groups()
    return self._github_fetch_with_raw_then_git(owner, repo, branch, file_path, use_https=True)

  def _fetch_github_https_file(self, github_path):
    """
    Fetch a file from a GitHub repository using HTTPS.
    Dispatcher passes: owner/repo/branch/file_path
    """
    self.logger.debug(f"Fetching content from GitHub (HTTPS): {github_path}")
    match = re.match(r"([^/]+)/([^/]+)/([^/]+)/(.+)", github_path)
    if not match:
      raise ValueError("Invalid GitHub path. Expected owner/repo/branch/file_path")

    owner, repo, branch, file_path = match.groups()
    return self._github_fetch_with_raw_then_git(owner, repo, branch, file_path, use_https=True)

  def _fetch_github_ssh_file(self, github_path):
    """
    Fetch a file from a GitHub repository using SSH.
    Dispatcher passes: owner/repo/branch/file_path
    """
    self.logger.debug(f"Fetching content from GitHub (SSH): {github_path}")
    match = re.match(r"([^/]+)/([^/]+)/([^/]+)/(.+)", github_path)
    if not match:
      raise ValueError("Invalid GitHub path. Expected owner/repo/branch/file_path")

    owner, repo, branch, file_path = match.groups()
    return self._github_fetch_with_raw_then_git(owner, repo, branch, file_path, use_https=False)

  def _clone_or_fetch_github(self, owner, repo, branch, file_path, https=True):
    repo_cache_path = self.cache_dir / f"{owner}_{repo}_{branch}"
    clone_url = f"https://github.com/{owner}/{repo}.git" if https else f"git@github.com:{owner}/{repo}.git"

    # Clone or fetch the repository
    if not repo_cache_path.exists():
      self.logger.debug(f"Cloning repository: {owner}/{repo} (branch: {branch})")
      subprocess.run(["git", "clone", "-b", branch, clone_url, str(repo_cache_path)], check=True)
    else:
      self.logger.debug(f"Repository already cloned. Pulling latest changes for: {repo_cache_path}")
      subprocess.run(["git", "-C", str(repo_cache_path), "pull"], check=True)

    # Read the requested file
    file_full_path = repo_cache_path / file_path
    if not file_full_path.exists():
      raise FileNotFoundError(f"File {file_path} not found in repository {owner}/{repo} on branch {branch}")

    with file_full_path.open('r') as file:
      return file.read()

  def _github_fetch_with_raw_then_git(self, owner, repo, branch, file_path, use_https=True):
    """
    Try lightweight fetch via raw.githubusercontent.com first. If it fails
    (network disabled, HTTP error, etc.), fall back to git clone/pull.
    If a local cache repo exists already, prefer using git path directly
    to avoid surprise network requests.
    """
    # Deny network option
    if os.getenv("STRUCTKIT_DENY_NETWORK") == "1":
      self.logger.debug("Network denied by STRUCTKIT_DENY_NETWORK=1; using git fallback if available")
      return self._clone_or_fetch_github(owner, repo, branch, file_path, https=use_https)

    repo_cache_path = self.cache_dir / f"{owner}_{repo}_{branch}"
    if repo_cache_path.exists():
      # Keep existing behavior: use git path if cache exists
      return self._clone_or_fetch_github(owner, repo, branch, file_path, https=use_https)

    # Attempt raw fetch
    raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{file_path}"
    timeout = float(os.getenv("STRUCTKIT_HTTP_TIMEOUT", "10"))
    retries = int(os.getenv("STRUCTKIT_HTTP_RETRIES", "2"))

    last_err = None
    for attempt in range(retries + 1):
      try:
        self.logger.debug(f"Attempting raw fetch: {raw_url} (attempt {attempt+1}/{retries+1})")
        resp = requests.get(raw_url, timeout=timeout)
        resp.raise_for_status()
        return resp.text
      except Exception as e:
        last_err = e
        # simple backoff
        try:
          import time
          time.sleep(min(2 ** attempt, 5))
        except Exception:
          pass

    self.logger.warning(f"Raw GitHub fetch failed, falling back to git. Last error: {last_err}")
    return self._clone_or_fetch_github(owner, repo, branch, file_path, https=use_https)

  def _fetch_s3_file(self, s3_path):
    """
    Fetch a file from an S3 bucket.
    Dispatcher passes: bucket_name/key
    """
    if not boto3_available:
      raise ImportError("boto3 is not installed. Please install it to use S3 fetching.")

    self.logger.debug(f"Fetching content from S3: {s3_path}")
    match = re.match(r"([^/]+)/(.+)", s3_path)
    if not match:
      raise ValueError("Invalid S3 path. Expected bucket_name/key")

    bucket_name, key = match.groups()
    local_file_path = self.cache_dir / Path(key).name

    try:
      session = boto3.Session()  # Create a new session
      s3_client = session.client("s3")
      s3_client.download_file(bucket_name, key, str(local_file_path))
      self.logger.debug(f"Downloaded S3 file to: {local_file_path}")
    except NoCredentialsError:
      raise RuntimeError("AWS credentials not found. Ensure that your credentials are configured properly.")
    except ClientError as e:
      error_code = e.response.get("Error", {}).get("Code")
      if error_code == "404":
        raise FileNotFoundError(f"The specified S3 key does not exist: {key}")
      else:
        raise RuntimeError(f"Failed to download S3 file: {e}")

    with local_file_path.open('r') as file:
      return file.read()

  def _fetch_gcs_file(self, gcs_path):
    """
    Fetch a file from Google Cloud Storage.
    Dispatcher passes: bucket_name/key
    """
    if not gcs_available:
      raise ImportError("google-cloud-storage is not installed. Please install it to use GCS fetching.")

    self.logger.debug(f"Fetching content from GCS: {gcs_path}")
    match = re.match(r"([^/]+)/(.+)", gcs_path)
    if not match:
      raise ValueError("Invalid GCS path. Expected bucket_name/key")

    bucket_name, key = match.groups()
    local_file_path = self.cache_dir / Path(key).name

    try:
      gcs_client = storage.Client()
      bucket = gcs_client.bucket(bucket_name)
      blob = bucket.blob(key)
      blob.download_to_filename(str(local_file_path))
      self.logger.debug(f"Downloaded GCS file to: {local_file_path}")
    except GoogleAPIError as e:
      raise RuntimeError(f"Failed to download GCS file: {e}")

    with local_file_path.open('r') as file:
      return file.read()
