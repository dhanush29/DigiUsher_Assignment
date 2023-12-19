
from pydantic import BaseModel

class Item(BaseModel):
    ram_consumed: int
    cpu: float
    disk_usage_percent: float
