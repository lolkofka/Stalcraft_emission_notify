from datetime import datetime

from beanie import Document, Indexed
from pydantic import BaseModel, Field


class Emission(Document):
    region: str
    emission_time: str
    emission_timestamp: int
    message_id: int
    group: str
    last_online: int = 0

    def __init__(self, **kwargs) -> None:
        super(Document, self).__init__(**kwargs)