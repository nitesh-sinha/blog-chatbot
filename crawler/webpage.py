from dataclasses import dataclass
from typing import Optional

@dataclass
class WebPage:
    text: str
    metadata: Optional[dict]
