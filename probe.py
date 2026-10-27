import os

import boto3
from yt_dlp import YoutubeDL

from common import get_known_ids


def get_videos(kanal):
    """Kanalı cookie olmadan flat listeler; subscriber_only videolar görünür."""
    opts = {
        "extract_flat": True,
        "quiet": True,
        "playlistend": int(os.getenv("LIST_DEPTH") or "4"),
    }
    with YoutubeDL(opts) as ydl:
        info = ydl.extract_info(kanal, download=False)

    entries = info.get("entries") or []
    # Kanal kök URL'i tab listesi döndürürse ilk (Videos) tabı kullan.
    if entries and entries[0].get("_type") == "playlist":
        entries = entries[0].get("entries") or []

    videos = {}
    for entry in entries:
        if entry.get("availability") != "subscriber_only":
            continue
        vid = entry.get("id")
        if not vid:
            continue
        videos[vid] = {
            "id": vid,
            "title": entry.get("title"),
            "duration": entry.get("duration"),  # saniye
        }
    return videos


def probe_channel(s3, kanal):
    # yeni videolari bulur liste dondurur
    videos = get_videos(kanal)
    known_ids = get_known_ids(s3)

    new_videos = []
    for vid, video in videos.items():
        if vid not in known_ids:
            new_videos.append(video)
    return new_videos


s3 = boto3.client("s3", region_name="eu-central-1")
sqs = boto3.client("sqs", region_name="eu-central-1")
