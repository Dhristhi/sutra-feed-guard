# Feed Guard Acquisition Extension

This extension adds remote file acquisition capabilities to Feed Guard, enabling automated downloads from SFTP, S3, and HTTPS sources before local classification.

## Installation

```bash
cd /Users/madhavraop/Code/sutra-feed-guard
uv sync --extra dev
```

The acquisition module requires additional dependencies:
- `paramiko` (SFTP)
- `boto3` (S3)
- `requests` (HTTPS, already included)

## Quick Start

### S3 Example

```bash
# Set AWS credentials
export AWS_ACCESS_KEY_ID=your_key_id
export AWS_SECRET_ACCESS_KEY=your_secret_key

# Download and classify
uv run scripts/example_s3_acquisition.py \
    s3://my-bucket/partner-data/daily.json \
    fixtures/contracts/accepted_policy.yaml
```

### SFTP Example

```bash
# Set SFTP credentials
export FEEDGUARD_SFTP_USER=partner_user
export FEEDGUARD_SFTP_KEY=~/.ssh/partner_key

# Download and classify
uv run scripts/example_sftp_acquisition.py \
    sftp://partner.example.com/data/daily.csv \
    fixtures/contracts/accepted_policy.yaml
```

### HTTPS Example

```python
from feedguard.acquisition import download_from_uri
from feedguard.classification import classify_change

# Download from HTTPS (with optional basic auth)
result = download_from_uri("https://partner.com/data.csv")

# Run classification
classification = classify_change(
    baseline_path="fixtures/historical/baseline.csv",
    observation_path=result.local_path,
    policy_path="fixtures/contracts/policy.yaml",
)

print(f"Disposition: {classification.disposition}")
print(f"Exit code: {classification.exit_code}")

# Clean up temp files
result.cleanup()
```

## Architecture

```
┌─────────────────────────────────────────┐
│  Remote Sources                         │
│  - SFTP: sftp://host/path/file.csv      │
│  - S3: s3://bucket/path/file.json       │
│  - HTTPS: https://example.com/file.csv  │
└─────────────────────────────────────────┘
              ↓ download_from_uri()
┌─────────────────────────────────────────┐
│  Local Temp Directory                   │
│  - Downloaded to isolated temp folder   │
│  - Automatic cleanup after classification │
└─────────────────────────────────────────┘
              ↓ classify_change()
┌─────────────────────────────────────────┐
│  Feed Guard Deterministic Core          │
│  - Parse → Digest → Classify → Report   │
│  - Exit code: 0/2/3/4                   │
└─────────────────────────────────────────┘
```

## API Reference

### `download_from_uri(uri: str, dest_dir: Path | None = None) -> DownloadResult`

Download a file from a remote URI to a local temp file.

**Parameters:**
- `uri`: Remote file URI (sftp://, s3://, https://, http://)
- `dest_dir`: Optional destination directory (default: temp dir with auto-cleanup)

**Returns:**
- `DownloadResult` dataclass with:
  - `local_path`: Path to downloaded file
  - `source_uri`: Original URI
  - `bytes_downloaded`: File size
  - `temp_dir`: TemporaryDirectory object (for cleanup)
  - `cleanup()`: Method to clean up temp files

**Raises:**
- `AcquisitionError`: If download fails (unsupported URI, auth failure, network error)

### Environment Variables

| Source | Variables | Required |
|--------|-----------|----------|
| **SFTP** | `FEEDGUARD_SFTP_USER`, `FEEDGUARD_SFTP_KEY` | Yes |
| **S3** | `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` (or IAM role) | Yes (unless IAM role) |
| **HTTPS** | `FEEDGUARD_HTTPS_USER`, `FEEDGUARD_HTTPS_PASSWORD` | No (basic auth optional) |

## Integration Patterns

### Pattern 1: Cron Job with S3

```bash
#!/bin/bash
# /etc/cron.d/feedguard-s3
0 9 * * * feedguard \
    export AWS_ACCESS_KEY_ID=xxx && \
    export AWS_SECRET_ACCESS_KEY=yyy && \
    cd /opt/feedguard && \
    uv run scripts/example_s3_acquisition.py \
        s3://partner-bucket/daily/data.json \
        fixtures/contracts/policy.yaml \
    >> /var/log/feedguard.log 2>&1
```

### Pattern 2: Airflow DAG

```python
from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG('feedguard_sftp_check', default_args=default_args)

download_and_check = BashOperator(
    task_id='run_feedguard',
    bash_command='''
        export FEEDGUARD_SFTP_USER={{ var.value.sftp_user }}
        export FEEDGUARD_SFTP_KEY=/opt/keys/partner_key
        cd /opt/feedguard
        uv run scripts/example_sftp_acquisition.py \
            sftp://partner.com/data.csv \
            fixtures/contracts/policy.yaml
    ''',
    dag=dag,
)
```

### Pattern 3: Python Wrapper

```python
from feedguard.acquisition import download_from_uri
from feedguard.classification import classify_change
from pathlib import Path

def daily_partner_check(s3_uri: str, policy_path: Path) -> dict:
    """Download and classify partner data."""
    
    # Download
    result = download_from_uri(s3_uri)
    
    try:
        # Classify
        classification = classify_change(
            baseline_path=Path("fixtures/historical/baseline.csv"),
            observation_path=result.local_path,
            policy_path=policy_path,
        )
        
        return {
            "disposition": classification.disposition,
            "exit_code": classification.exit_code,
            "affected_count": classification.affected_count,
            "reason": classification.primary_reason,
        }
    
    finally:
        result.cleanup()

# Usage
result = daily_partner_check(
    s3_uri="s3://partner-bucket/daily.json",
    policy_path=Path("policy.yaml"),
)

if result["exit_code"] == 3:  # Breaking change
    # Alert engineering team
    send_slack_alert(f"Breaking change detected: {result['reason']}")
```

## Security Considerations

### Credential Management

- **Never hardcode credentials** in scripts or config files
- Use environment variables or secret managers (AWS Secrets Manager, HashiCorp Vault)
- Rotate credentials regularly
- Use IAM roles for S3 when running on AWS infrastructure

### Network Security

- SFTP: Verify host keys, use key-based authentication (not passwords)
- S3: Use VPC endpoints when possible, restrict bucket policies
- HTTPS: Validate SSL certificates, use basic auth only over TLS

### File Handling

- Downloaded files are stored in isolated temp directories
- Always call `result.cleanup()` after classification
- Consider encrypting temp files if handling sensitive data

## Troubleshooting

### SFTP Connection Failed

```
AcquisitionError: SFTP download failed: Authentication failed
```

**Fix:**
1. Verify `FEEDGUARD_SFTP_USER` is correct
2. Check `FEEDGUARD_SFTP_KEY` points to valid private key
3. Ensure key has correct permissions (`chmod 600 ~/.ssh/key`)
4. Test manually: `sftp -i ~/.ssh/key user@host`

### S3 Access Denied

```
AcquisitionError: S3 download failed: Access Denied
```

**Fix:**
1. Verify AWS credentials are valid
2. Check IAM policy allows `s3:GetObject` on the bucket
3. Ensure bucket name and key path are correct
4. Test with AWS CLI: `aws s3 cp s3://bucket/key.json .`

### HTTPS Download Timeout

```
AcquisitionError: HTTPS download failed: Read timed out
```

**Fix:**
1. Increase timeout in `acquisition.py` (default 300s)
2. Check network connectivity to the host
3. Verify the URL is accessible from your network
4. Consider adding retry logic with exponential backoff

## Next Steps

After validating the acquisition pattern with real partner feeds:

1. **Add retry logic** with exponential backoff for transient failures
2. **Implement progress reporting** for large files (>100MB)
3. **Add support for additional protocols** (Azure Blob, GCS, SCP)
4. **Integrate with Feed Guard CLI** as a native subcommand:
   ```bash
   feedguard fetch s3://bucket/data.json --policy policy.yaml
   ```

See `ARCHITECTURE.md` for the full extension points documentation.
