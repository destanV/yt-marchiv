import os
import re

YT_ID_RE = re.compile(r"(?:v=|youtu\.be/|shorts/|live/|embed/)([A-Za-z0-9_-]{11})")
BARE_ID_RE = re.compile(r"^[A-Za-z0-9_-]{11}$")


def video_id(value):
    # canonical ID extract helper
    if not value:
        return None
    value = value.strip()
    if BARE_ID_RE.fullmatch(value):
        return value
    match = YT_ID_RE.search(value)
    return match.group(1) if match else None


def url_from_id(vid):
    # canonical ID build helper
    return f"https://www.youtube.com/watch?v={vid}"


def get_urls(s3):
    # url lerden olusan list dondurur
    body = s3.get_object(
        Bucket=os.getenv("BUCKET"),
        Key="urls.txt",
    )["Body"].read().decode("utf-8")
    return body.splitlines()


def get_known_ids(s3):
    """urls.txt satırlarından bilinen video ID'lerini döndürür."""
    known_ids = set()
    for line in get_urls(s3):
        vid = video_id(line)
        if vid:
            known_ids.add(vid)
    return known_ids


def append_id(s3, vid):
    """ID'yi urls.txt'e ekler; dosyayı yalnızca ID'lerden oluşacak şekilde normalize eder."""
    bucket = os.getenv("BUCKET")
    if not bucket:
        raise RuntimeError("Bucket undefined")

    ids = []
    for line in get_urls(s3):
        existing = video_id(line)
        if existing and existing not in ids:
            ids.append(existing)

    if vid in ids:
        return False

    ids.append(vid)
    body = "\n".join(ids) + "\n"
    s3.put_object(
        Bucket=bucket,
        Key="urls.txt",
        Body=body.encode("utf-8"),
        ContentType="text/plain; charset=utf-8",
    )
    return True


def upload_file(s3, file, key):
    bucket = os.getenv("BUCKET")
    if not bucket:
        raise RuntimeError("Bucket undefined")
    if isinstance(file, (bytes, bytearray)):
        s3.put_object(
            Bucket=bucket,
            Key=key,
            ContentType="video/webm",
            Body=file,
        )
    else:
        s3.upload_file(
            Filename=str(file),
            Bucket=bucket,
            Key=key,
            ExtraArgs={"ContentType": "video/webm"},
        )
