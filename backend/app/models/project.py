from typing import List, Optional

from pydantic import BaseModel, HttpUrl


class Project(BaseModel):
    name: str
    short_description: Optional[str] = None
    long_description: Optional[str] = None
    url: HttpUrl
    source: str
    tags: List[str] = []
    batch: Optional[str] = None
    founded: Optional[str] = None
    team_size: Optional[str] = None
    status: Optional[str] = None
    primary_partner: Optional[str] = None
    location: Optional[str] = None
