from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any

class DocumentInsight(BaseModel):
    summary: str = Field(description="A concise summary of the document")
    entities: List[str] = Field(description="Key entities mentioned in the document")
    risks: List[str] = Field(description="Potential risks or concerns identified")
    metrics: Dict[str, Any] = Field(description="Quantitative metrics from the document")
    
    class Config:
        extra = "ignore"