from pydantic import BaseModel, ConfigDict
from typing import Optional


class StoreSettingResponse(BaseModel):
    id: int
    store_name: str
    currency: str
    online_ordering_enabled: bool
    pay_at_counter_enabled: bool
    splash_background_color: Optional[str] = None
    splash_image_url: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class StoreSettingUpdateRequest(BaseModel):
    store_name: Optional[str] = None
    currency: Optional[str] = None
    online_ordering_enabled: Optional[bool] = None
    pay_at_counter_enabled: Optional[bool] = None
    splash_background_color: Optional[str] = None
    splash_image_url: Optional[str] = None
