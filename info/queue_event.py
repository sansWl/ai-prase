from dataclasses import dataclass, asdict
import json
from typing import Optional

@dataclass
class QueueEvent:
    """
    task_type : 类型
    task_id: 唯一标识
    desc: 描述
    data: 额外数据 dict
    """
    task_type: int
    task_id: str
    desc: Optional[str] = None
    data:Optional[dict] = None

    def to_json(self):
        return json.dumps(asdict(self))




    