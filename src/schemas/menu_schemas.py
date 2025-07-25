from pydantic import BaseModel, ConfigDict


class CategoryCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
    description: str

class CategoryUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
    description: str

class DishCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
    description: str
    price: int
    category_id: int
    is_available: bool = True

class DishUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
    description: str
    price: int
    category_id: int
    is_available: bool = True
    
    
    
    
class TagCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str

class TagUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str


class ComboSetCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
    description: str
    price: int
    

class ComboSetUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
    description: str
    price: int


    
    

    
    