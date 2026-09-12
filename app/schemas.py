from pydantic import BaseModel, Field
from typing import Literal, Optional, TypedDict
from uuid import uuid4
import datetime

class OrderContract(BaseModel):
    order_id : str = Field(...)
    description : str = Field(...)
    amount : float = Field(...)
    urgent : bool = Field(default=False)
    approval_needed : bool = Field(default=False)


class ClaimContract(BaseModel):
    claim_id : str = Field(default_factory=lambda: uuid4().hex)
    reasons : str = Field(...)
    compensation : float = Field(...)
    urgent : bool = Field(default=False)
    approval_needed : bool = Field(default=False)


class RequestContract(BaseModel):
    request_id: str = Field(default_factory=lambda: uuid4().hex)
    task_type: Literal["order", "claim"]
    amount: float = Field(...)
    urgent: bool = Field(default=False)
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now(datetime.timezone.utc))

class GraphState(TypedDict, total=False):
    request: RequestContract
    contract: OrderContract | ClaimContract | None
    file_path: str | None
    error: str | None