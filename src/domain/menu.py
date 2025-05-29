from pydantic import BaseModel


class Category(BaseModel):
    id: int
    name: str
    description: str

    

class CategoryCreate(Category):
    pass

class CategoryUpdate(Category):
    pass

class Dish(BaseModel):
    id: int
    name: str
    description: str
    price: int
    category_id: int

class DishCreate(Dish):
    pass

class DishUpdate(Dish):
    pass


class Tag(BaseModel):
    id: int
    name: str

class TagCreate(Tag):
    pass

class TagUpdate(Tag):
    pass


class ComboSet(BaseModel):
    id: int
    name: str
    description: str
    price: int
    
    
class ComboSetCreate(ComboSet):
    pass


class ComboSetUpdate(ComboSet):
    pass

