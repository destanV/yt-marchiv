import subprocess
import sys

import boto3

from common import url_from_id


def download_video(vid, cookie):
    # katil videolarinda cookie zorunlu ve sadece katil videolarini indirir
    cmd = [
        sys.executable, "-m", "yt_dlp",
        "-q", "--no-warnings", "--no-progress",
        "--no-playlist",
        "-f", "bv*+ba/b",
        "-S", "res:720,vcodec:av01,acodec:opus",
        "--merge-output-format", "webm",
        "-o", "-",
        url_from_id(vid),
        "--cookies", cookie,
    ]

    result = subprocess.run(cmd, capture_output=True, timeout=8900)

    if result.returncode != 0:
        stderr = result.stderr.decode("utf-8", "replace")[-1000:]
        raise RuntimeError(f"yt-dlp indirilemedi:\n{stderr}")

    if not result.stdout:
        raise RuntimeError("yt-dlp boş çıktı döndürdü")

    return result.stdout


s3 = boto3.client("s3", region_name="eu-central-1")
