from dataclasses import dataclass
from typing import Optional

@dataclass
class WebPage:
    text: str
    metadata: Optional[dict]
    # url: str
    # title: Optional[str]
    # description: Optional[str]
    # meta_keywords: Optional[str]