from datetime import datetime
from pydantic import BaseModel

class Order(BaseModel):
    id: int
    userId: int 
    itemId: int
    total: int
    orderDate: datetime
