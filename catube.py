import re
from abc import ABC
from typing import Iterator

from pytube import extract
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter, JSONFormatter
from langchain.docstore.document import Document
from langchain.document_loaders.base import BaseBlobParser
from langchain.document_loaders.blob_loaders.schema import Blob

from cat.mad_hatter.decorators import hook


def parse_youtube_url(url: str) -> str:
    data = re.findall(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)
    if data:
        return data[0]
    return ""


class YoutubeParser(BaseBlobParser, ABC):
    def __init__(self):
        self.formatter = TextFormatter()

    def lazy_parse(self, blob: Blob) -> Iterator[Document]:
        video_id = extract.video_id(blob.source)

        transcript = YouTubeTranscriptApi.get_transcripts([video_id], languages=["en", "it"], preserve_formatting=True)
        text = self.formatter.format_transcript(transcript[0][video_id])

        yield Document(page_content=text, metadata={})


@hook
def rabbithole_instantiates_parsers(file_handlers: dict, cat) -> dict:
    file_handlers["video/mp4"] = YoutubeParser()
    return file_handlers
