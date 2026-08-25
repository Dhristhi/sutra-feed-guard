"""Remote file acquisition for Feed Guard.

Downloads files from SFTP, S3, HTTPS, Azure Blob, or GCS to a local temp directory,
then returns the local path for classification by the deterministic core.

Credentials are read from environment variables:
- SFTP: FEEDGUARD_SFTP_HOST, FEEDGUARD_SFTP_USER, FEEDGUARD_SFTP_KEY
- S3: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY (or IAM role)
- HTTPS: FEEDGUARD_HTTPS_USER, FEEDGUARD_HTTPS_PASSWORD (basic auth)
- Azure: AZURE_STORAGE_ACCOUNT_NAME, AZURE_STORAGE_ACCOUNT_KEY
- GCS: GOOGLE_APPLICATION_CREDENTIALS (service account JSON path)
"""

from __future__ import annotations

import os
import tempfile
import time
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
    download_duration_ms: int = 0

    def cleanup(self) -> None:
        """Clean up temporary files."""
        if self.temp_dir:
            self.temp_dir.cleanup()

    def __str__(self) -> str:
        duration_sec = self.download_duration_ms / 1000.0
        size_kb = self.bytes_downloaded / 1024.0
        speed_kbs = size_kb / duration_sec if duration_sec > 0 else 0
        return (
            f"DownloadResult(local={self.local_path}, "
            f"size={self.bytes_downloaded:,} bytes, "
            f"duration={duration_sec:.2f}s, "
            f"speed={speed_kbs:.1f} KB/s)"
        )


class AcquisitionError(Exception):
    """Raised when file acquisition fails."""

    pass


def download_from_uri(
    uri: str,
    dest_dir: Path | None = None,
    max_retries: int = 3,
    backoff_factor: float = 2.0,
    show_progress: bool = False,
) -> DownloadResult:
    """Download a file from a remote URI to a local temp file.

    Supports:
    - sftp://host/path/file.csv
    - s3://bucket/path/file.json
    - https://example.com/path/file.csv
    - azblob://container/path/file.csv (Azure Blob Storage)
    - gs://bucket/path/file.json (Google Cloud Storage)

    Args:
        uri: Remote file URI
        dest_dir: Optional destination directory (default: temp dir)
        max_retries: Maximum retry attempts (default: 3)
        backoff_factor: Exponential backoff multiplier (default: 2.0)
        show_progress: Show download progress bar (default: False)

    Returns:
        DownloadResult with local path, cleanup method, and stats

    Raises:
        AcquisitionError: If download fails after all retries
    """
    parsed = urlparse(uri)
    last_error: Exception | None = None

    for attempt in range(max_retries + 1):
        try:
            if parsed.scheme == "sftp":
                return _download_sftp(uri, dest_dir, show_progress)
            elif parsed.scheme == "s3":
                return _download_s3(uri, dest_dir, show_progress)
            elif parsed.scheme in ("https", "http"):
                return _download_https(uri, dest_dir, show_progress)
            elif parsed.scheme == "azblob":
                return _download_azure(uri, dest_dir, show_progress)
            elif parsed.scheme == "gs":
                return _download_gcs(uri, dest_dir, show_progress)
            else:
                raise AcquisitionError(f"Unsupported URI scheme: {parsed.scheme}")

        except Exception as e:
            last_error = e
            if attempt < max_retries:
                wait_time = backoff_factor ** attempt
                print(f"Download attempt {attempt + 1} failed: {e}. Retrying in {wait_time:.1f}s...")
                time.sleep(wait_time)
            else:
                raise AcquisitionError(f"Download failed after {max_retries + 1} attempts: {e}") from last_error

    raise AcquisitionError(f"Download failed: {last_error}")


def _download_sftp(
    uri: str,
    dest_dir: Path | None = None,
    show_progress: bool = False,
) -> DownloadResult:
    """Download from SFTP server."""
    import paramiko

    start_time = time.time()
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
        total_size = stat.st_size if stat.st_size else 0
        bytes_downloaded = 0

        if show_progress and total_size > 0:
            # Download with progress
            def progress_callback(transferred, total):
                percent = (transferred / total) * 100
                print(f"\rSFTP download: {percent:.1f}% ({transferred:,}/{total:,} bytes)", end="")

            sftp.get(path, str(local_path), callback=progress_callback if show_progress else None)
            bytes_downloaded = total_size
            print()  # Newline after progress
        else:
            sftp.get(path, str(local_path))
            bytes_downloaded = total_size

        sftp.close()
        ssh.close()

        duration_ms = int((time.time() - start_time) * 1000)

        return DownloadResult(
            local_path=local_path,
            source_uri=uri,
            bytes_downloaded=bytes_downloaded,
            temp_dir=temp_dir,
            download_duration_ms=duration_ms,
        )

    except Exception as e:
        if temp_dir:
            temp_dir.cleanup()
        raise AcquisitionError(f"SFTP download failed: {e}")


def _download_s3(
    uri: str,
    dest_dir: Path | None = None,
    show_progress: bool = False,
) -> DownloadResult:
    """Download from S3 bucket."""
    import boto3
    from boto3.s3.transfer import TransferConfig

    start_time = time.time()
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
        obj = s3.head_object(Bucket=bucket, Key=key)
        total_size = obj["ContentLength"]

        # Configure transfer with progress callback
        class ProgressCallback:
            def __init__(self, total_size: int):
                self._seen_so_far = 0
                self._total_size = total_size

            def __call__(self, bytes_amount: int):
                self._seen_so_far += bytes_amount
                if show_progress and self._total_size > 0:
                    percentage = (self._seen_so_far / self._total_size) * 100
                    print(f"\rS3 download: {percentage:.1f}% ({self._seen_so_far:,}/{self._total_size:,} bytes)", end="")

        # Download with progress
        transfer_config = TransferConfig(
            multipart_threshold=8 * 1024 * 1024,
            multipart_chunksize=8 * 1024 * 1024,
        )
        s3.download_file(
            Bucket=bucket,
            Key=key,
            Filename=str(local_path),
            Config=transfer_config,
            Callback=ProgressCallback(total_size) if show_progress else None,
        )

        if show_progress:
            print()  # Newline after progress

        duration_ms = int((time.time() - start_time) * 1000)

        return DownloadResult(
            local_path=local_path,
            source_uri=uri,
            bytes_downloaded=total_size,
            temp_dir=temp_dir,
            download_duration_ms=duration_ms,
        )

    except Exception as e:
        if temp_dir:
            temp_dir.cleanup()
        raise AcquisitionError(f"S3 download failed: {e}")


def _download_https(
    uri: str,
    dest_dir: Path | None = None,
    show_progress: bool = False,
) -> DownloadResult:
    """Download from HTTPS URL with optional basic auth."""
    start_time = time.time()
    temp_dir = tempfile.TemporaryDirectory() if not dest_dir else None
    dest_dir = dest_dir or Path(temp_dir.name)  # type: ignore

    try:
        # Check for basic auth credentials
        auth = None
        username = os.environ.get("FEEDGUARD_HTTPS_USER")
        password = os.environ.get("FEEDGUARD_HTTPS_PASSWORD")
        if username and password:
            auth = (username, password)

        # Stream download with progress
        response = requests.get(uri, auth=auth, timeout=300, stream=True)
        response.raise_for_status()

        total_size = int(response.headers.get("content-length", 0))
        bytes_downloaded = 0

        filename = Path(urlparse(uri).path).name or "download.csv"
        local_path = dest_dir / filename

        with open(local_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    bytes_downloaded += len(chunk)
                    if show_progress and total_size > 0:
                        percentage = (bytes_downloaded / total_size) * 100
                        print(f"\rHTTPS download: {percentage:.1f}% ({bytes_downloaded:,}/{total_size:,} bytes)", end="")

        if show_progress:
            print()

        duration_ms = int((time.time() - start_time) * 1000)

        return DownloadResult(
            local_path=local_path,
            source_uri=uri,
            bytes_downloaded=bytes_downloaded,
            temp_dir=temp_dir,
            download_duration_ms=duration_ms,
        )

    except Exception as e:
        if temp_dir:
            temp_dir.cleanup()
        raise AcquisitionError(f"HTTPS download failed: {e}")


def _download_azure(
    uri: str,
    dest_dir: Path | None = None,
    show_progress: bool = False,
) -> DownloadResult:
    """Download from Azure Blob Storage.

    Requires: azure-storage-blob package
    Environment: AZURE_STORAGE_ACCOUNT_NAME, AZURE_STORAGE_ACCOUNT_KEY
    """
    start_time = time.time()
    parsed = urlparse(uri)
    container = parsed.netloc
    blob_path = parsed.path.lstrip("/")

    account_name = os.environ.get("AZURE_STORAGE_ACCOUNT_NAME")
    account_key = os.environ.get("AZURE_STORAGE_ACCOUNT_KEY")

    if not account_name or not account_key:
        raise AcquisitionError("AZURE_STORAGE_ACCOUNT_NAME and AZURE_STORAGE_ACCOUNT_KEY required")

    try:
        from azure.storage.blob import BlobServiceClient

        account_url = f"https://{account_name}.blob.core.windows.net"
        blob_service_client = BlobServiceClient(account_url=account_url, credential=account_key)
        blob_client = blob_service_client.get_blob_client(container=container, blob=blob_path)

        temp_dir = tempfile.TemporaryDirectory() if not dest_dir else None
        dest_dir = dest_dir or Path(temp_dir.name)  # type: ignore

        filename = Path(blob_path).name
        local_path = dest_dir / filename

        # Download blob
        download_stream = blob_client.download_blob()
        blob_properties = blob_client.get_blob_properties()
        total_size = blob_properties.size

        with open(local_path, "wb") as f:
            data = download_stream.readall()
            f.write(data)

        duration_ms = int((time.time() - start_time) * 1000)

        return DownloadResult(
            local_path=local_path,
            source_uri=uri,
            bytes_downloaded=len(data),
            temp_dir=temp_dir,
            download_duration_ms=duration_ms,
        )

    except Exception as e:
        raise AcquisitionError(f"Azure Blob download failed: {e}")


def _download_gcs(
    uri: str,
    dest_dir: Path | None = None,
    show_progress: bool = False,
) -> DownloadResult:
    """Download from Google Cloud Storage.

    Requires: google-cloud-storage package
    Environment: GOOGLE_APPLICATION_CREDENTIALS (service account JSON path)
    """
    start_time = time.time()
    parsed = urlparse(uri)
    bucket_name = parsed.netloc
    blob_name = parsed.path.lstrip("/")

    try:
        from google.cloud import storage

        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(blob_name)

        temp_dir = tempfile.TemporaryDirectory() if not dest_dir else None
        dest_dir = dest_dir or Path(temp_dir.name)  # type: ignore

        filename = Path(blob_name).name
        local_path = dest_dir / filename

        # Download blob
        blob.download_to_filename(str(local_path))

        # Get blob metadata for size
        blob.reload()
        total_size = blob.size

        duration_ms = int((time.time() - start_time) * 1000)

        return DownloadResult(
            local_path=local_path,
            source_uri=uri,
            bytes_downloaded=total_size if total_size else 0,
            temp_dir=temp_dir,
            download_duration_ms=duration_ms,
        )

    except Exception as e:
        raise AcquisitionError(f"GCS download failed: {e}")
