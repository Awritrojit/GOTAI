from pydantic import BaseModel, Field
from typing import Optional, List
import uuid

class Node(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    parent_id: Optional[str] = None
    trajectory_id: str
    text: str
    score: float = 0.0
    cumulative_score: float = 0.0
    is_pruned: bool = False
    is_fully_explored: bool = False
    depth: int = 0
    # To store the vector representation
    embedding: Optional[List[float]] = None

class GraphData(BaseModel):
    nodes: List[Node]
    links: List[dict]

class StartRequest(BaseModel):
    hypothesis: str
    max_depth: Optional[int] = 3
    max_nodes: Optional[int] = 50

class StopRequest(BaseModel):
    run_name: str

class ArchiveResponse(BaseModel):
    success: bool
    message: str
    archive_name: Optional[str] = None
    nodes_count: Optional[int] = None
