import zipfile

def export_code_blocks(job_id: str, phases: list = None) -> str:
    """Exports code blocks to a zip file."""
    zip_path = f"/tmp/{job_id}_code.zip"
    with zipfile.ZipFile(zip_path, 'w') as zf:
        zf.writestr("README.md", f"Code for job {job_id}")
    return zip_path
