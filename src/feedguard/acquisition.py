"""Remote file acquisition for Feed Guard.

Downloads files from SFTP, S3, or HTTPS to a local temp directory,
then returns the local path for classification by the deterministic core.

Credentials are read from environment variables:
- SFTP: FEEDGUARD_SFTP_HOST, FEEDGUARD_SFTP_USER, FEEDGUARD_SFTP_KEY
- S3: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY (or IAM role)
- HTTPS: FEEDGUARD_HTTPS_USER, FEEDGUARD_HTTPS_PASSWORD (basic auth)
"""

from __future__ import annotations

import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Protocol
from urllib.parse import urlparse

import requests


@dataclass
class DownloadResult:
    """Result of a remote file download."""

    local_path: Path
    source_uri: str
    bytes_downloaded: int
    temp_dir: tempfile.TemporaryDirectory | None = None

    def cleanup(self) -> None:
        """Clean up temporary files."""
        if self.temp_dir:
            self.temp_dir.cleanup()


class AcquisitionError(Exception):
    """Raised when file acquisition fails."""

    pass


def download_from_uri(uri: str, dest_dir: Path | None = None) -> DownloadResult:
    """Download a file from a remote URI to a local temp file.

    Supports:
    - sftp://host/path/file.csv
    - s3://bucket/path/file.json
    - https://example.com/path/file.csv

    Args:
        uri: Remote file URI
        dest_dir: Optional destination directory (default: temp dir)

    Returns:
        DownloadResult with local path and cleanup method

    Raises:
        AcquisitionError: If download fails
    """
    parsed = urlparse(uri)

    if parsed.scheme == "sftp":
        return _download_sftp(uri, dest_dir)
    elif parsed.scheme == "s3":
        return _download_s3(uri, dest_dir)
    elif parsed.scheme in ("https", "http"):
        return _download_https(uri, dest_dir)
    else:
        raise AcquisitionError(f"Unsupported URI scheme: {parsed.scheme}")


def _download_sftp(uri: str, dest_dir: Path | None = None) -> DownloadResult:
    """Download from SFTP server."""
    import paramiko

    parsed = urlparse(uri)
    host = parsed.hostname
    if not host:
        raise AcquisitionError("SFTP URI missing hostname")
    port = parsed.port or 22
    path = parsed.path
    username = os.environ.get("FEEDGUARD_SFTP_USER")
    key_file = os.environ.get("FEEDGUARD_SFTP_KEY")

    if not username:
        raise AcquisitionError("FEEDGUARD_SFTP_USER environment variable required")
    if not key_file:
        raise AcquisitionError("FEEDGUARD_SFTP_KEY environment variable required")

    temp_dir = tempfile.TemporaryDirectory() if not dest_dir else None
    dest_dir = dest_dir or Path(temp_dir.name)  # type: ignore

    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(
            hostname=host,
            port=port,
            username=username,
            key_filename=key_file,
        )
        sftp = ssh.open_sftp()

        filename = Path(path).name
        local_path = dest_dir / filename

        # Get file size for progress reporting
        stat = sftp.stat(path)
        bytes_downloaded = stat.st_size if stat.st_size else 0

        sftp.get(path, str(local_path))
        sftp.close()
        ssh.close()

        return DownloadResult(
            local_path=local_path,
            source_uri=uri,
            bytes_downloaded=bytes_downloaded,
            temp_dir=temp_dir,
        )

    except Exception as e:
        if temp_dir:
            temp_dir.cleanup()
        raise AcquisitionError(f"SFTP download failed: {e}")


def _download_s3(uri: str, dest_dir: Path | None = None) -> DownloadResult:
    """Download from S3 bucket."""
    import boto3

    parsed = urlparse(uri)
    bucket = parsed.netloc
    key = parsed.path.lstrip("/")

    temp_dir = tempfile.TemporaryDirectory() if not dest_dir else None
    dest_dir = dest_dir or Path(temp_dir.name)  # type: ignore

    try:
        s3 = boto3.client("s3")
        filename = Path(key).name
        local_path = dest_dir / filename

        # Get object metadata
        obj = s3.get_object(Bucket=bucket, Key=key)
        bytes_downloaded = obj["ContentLength"]

        # Download to local file
        with open(local_path, "wb") as f:
            f.write(obj["Body"].read())

        return DownloadResult(
            local_path=local_path,
            source_uri=uri,
            bytes_downloaded=bytes_downloaded,
            temp_dir=temp_dir,
        )

    except Exception as e:
        if temp_dir:
            temp_dir.cleanup()
        raise AcquisitionError(f"S3 download failed: {e}")


def _download_https(uri: str, dest_dir: Path | None = None) -> DownloadResult:
    """Download from HTTPS URL with optional basic auth."""
    temp_dir = tempfile.TemporaryDirectory() if not dest_dir else None
    dest_dir = dest_dir or Path(temp_dir.name)  # type: ignore

    try:
        # Check for basic auth credentials
        auth = None
        username = os.environ.get("FEEDGUARD_HTTPS_USER")
        password = os.environ.get("FEEDGUARD_HTTPS_PASSWORD")
        if username and password:
            auth = (username, password)

        response = requests.get(uri, auth=auth, timeout=300)
        response.raise_for_status()

        filename = Path(urlparse(uri).path).name or "download.csv"
        local_path = dest_dir / filename

        with open(local_path, "wb") as f:
            f.write(response.content)

        return DownloadResult(
            local_path=local_path,
            source_uri=uri,
            bytes_downloaded=len(response.content),
            temp_dir=temp_dir,
        )

    except Exception as e:
        if temp_dir:
            temp_dir.cleanup()
        raise AcquisitionError(f"HTTPS download failed: {e}")
