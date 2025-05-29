from pydantic import BaseModel


class CategoryCreate(BaseModel):
    name: str
    description: str

class CategoryUpdate(BaseModel):
    name: str
    description: str

class DishCreate(BaseModel):
    name: str
    description: str
    price: int
    category_id: int

class DishUpdate(BaseModel):
    name: str
    description: str
    price: int
    category_id: int
    
    
class TagCreate(BaseModel):
    name: str

class TagUpdate(BaseModel):
    name: str


class ComboSetCreate(BaseModel):
    name: str
    description: str
    price: int
    

class ComboSetUpdate(BaseModel):
    name: str
    description: str
    price: int


    
    

    
    