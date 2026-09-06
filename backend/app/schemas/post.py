from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class SignalSchema(BaseModel):
    post_id: int
    title: Optional[str] = None
    cluster_id: Optional[int] = None
    domain: Optional[str] = None
    cluster_size: Optional[int] = None
    cluster_rank: Optional[int] = None
    signal_score: Optional[float] = None
    signal_status: Optional[str] = None
    published_at: Optional[datetime] = None

from typing import List, Optional, Union

class CommunitySignalsResponse(BaseModel):
    community_id: Union[int, str]
    signals: List[SignalSchema]
