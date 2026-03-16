from pydantic import BaseModel
from typing import Optional


class graphNode(BaseModel):
    """图节点模型"""
    nodeId: str
    nodeType: str
    nodeName: str
    positionX: Optional[float] = None
    positionY: Optional[float] = None
    nodeDesc: Optional[str] = None

class graphEdge(BaseModel):
    """图边模型"""
    edgeId: str
    edgeType: str
    edgeName: str
    positionX: Optional[float] = None
    positionY: Optional[float] = None
    edgeDesc: Optional[str] = None
    sourceNodeId: str
    targetNodeId: str
    
