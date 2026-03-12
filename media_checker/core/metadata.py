"""Metadata extraction for video and audio files."""

import hashlib
from pathlib import Path
from typing import TYPE_CHECKING

from PIL import Image

from media_checker.core.models import MediaFile
from media_checker.core.utils import calculate_file_hash

if TYPE_CHECKING:
    import cv2
    import imagehash
else:
    try:
        import cv2
    except ImportError:
        cv2 = None

    try:
        import imagehash
    except ImportError:
        imagehash = None

if TYPE_CHECKING:
    from mutagen import File as MutagenFile
else:
    try:
        from mutagen import File as MutagenFile
    except ImportError:
        MutagenFile = None


def extract_video_metadata(media_file: MediaFile) -> None:
    """
    Extract metadata from video file using OpenCV.

    Args:
        media_file: MediaFile to update with metadata
    """
    if cv2 is None:
        return

    try:
        cap = cv2.VideoCapture(str(media_file.path))
        if not cap.isOpened():
            return

        # Get video properties
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # Calculate duration
        if fps > 0 and frame_count > 0:
            duration = frame_count / fps
            media_file.duration = duration

        media_file.width = width
        media_file.height = height

        # Extract frame for thumbnail hash (middle frame)
        if frame_count > 0 and imagehash is not None:
            middle_frame = int(frame_count / 2)
            cap.set(cv2.CAP_PROP_POS_FRAMES, middle_frame)
            ret, frame = cap.read()
            if ret and frame is not None:
                # Convert BGR to RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_image = Image.fromarray(frame_rgb)
                # Calculate perceptual hash
                phash = imagehash.phash(pil_image)
                media_file.thumbnail_hash = str(phash)

        # Try to get codec info
        fourcc = int(cap.get(cv2.CAP_PROP_FOURCC))
        codec = "".join([chr((fourcc >> 8 * i) & 0xFF) for i in range(4)])
        if codec.strip():
            media_file.codec = codec.strip()

        cap.release()

    except Exception:
        # If OpenCV fails, try to get basic info from file
        pass


def extract_audio_metadata(media_file: MediaFile) -> None:
    """
    Extract metadata from audio file using Mutagen.

    Args:
        media_file: MediaFile to update with metadata
    """
    if MutagenFile is None:
        return

    try:
        audio_file = MutagenFile(str(media_file.path))
        if audio_file is None:
            return

        # Get duration
        if hasattr(audio_file, "info") and hasattr(audio_file.info, "length"):
            media_file.duration = float(audio_file.info.length)

        # Get bitrate
        if hasattr(audio_file, "info") and hasattr(audio_file.info, "bitrate"):
            media_file.bitrate = audio_file.info.bitrate

        # Get sample rate
        if hasattr(audio_file, "info") and hasattr(audio_file.info, "sample_rate"):
            media_file.sample_rate = int(audio_file.info.sample_rate)

        # Get channels
        if hasattr(audio_file, "info") and hasattr(audio_file.info, "channels"):
            media_file.channels = int(audio_file.info.channels)

        # Get codec
        if hasattr(audio_file, "mime"):
            mime = audio_file.mime[0] if isinstance(audio_file.mime, list) else audio_file.mime
            if mime:
                # Extract codec from MIME type
                if "mp3" in mime.lower():
                    media_file.codec = "MP3"
                elif "flac" in mime.lower():
                    media_file.codec = "FLAC"
                elif "aac" in mime.lower():
                    media_file.codec = "AAC"
                elif "ogg" in mime.lower() or "opus" in mime.lower():
                    media_file.codec = "Opus"
                elif "wav" in mime.lower():
                    media_file.codec = "WAV"

    except Exception:
        # If Mutagen fails, continue without metadata
        pass


def extract_all_metadata(
    media_file: MediaFile,
    calculate_hash: bool = True,
    hash_algorithm: str = "md5",
) -> None:
    """
    Extract all metadata for a media file.

    Args:
        media_file: MediaFile to update
        calculate_hash: Whether to calculate file hash
        hash_algorithm: Hash algorithm to use ("md5" or "sha256")
    """
    # Calculate file hash if requested
    if calculate_hash:
        media_file.file_hash = calculate_file_hash(media_file.path, hash_algorithm)

    # Extract type-specific metadata
    if media_file.file_type == "video":
        extract_video_metadata(media_file)
    elif media_file.file_type == "audio":
        extract_audio_metadata(media_file)

    # Get modified time
    try:
        stat = media_file.path.stat()
        from datetime import datetime

        media_file.modified_time = datetime.fromtimestamp(stat.st_mtime)
    except (OSError, ValueError):
        pass

