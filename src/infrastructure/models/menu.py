from sqlalchemy import Column, ForeignKey, Integer, String
from src.database import Base
from sqlalchemy.orm import relationship

class Category(Base):
    __tablename__ = "categories"
    __table_args__ = {"schema": "menu"}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, index=True)
    dishes = relationship("Dish", back_populates="category")


class Dish(Base):
    __tablename__ = "dishes"
    __table_args__ = {"schema": "menu"}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, index=True)
    price = Column(Integer, index=True)
    category_id = Column(Integer, ForeignKey("menu.categories.id"))
    category = relationship("Category", back_populates="dishes")
    tags = relationship("Tag", secondary="menu.dish_tags", back_populates="dishes")
    combo_sets = relationship("ComboSet", secondary="menu.combo_dishes", back_populates="dishes")
    
    
class Tag(Base):
    __tablename__ = "tags"
    __table_args__ = {"schema": "menu"}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    dishes = relationship("Dish", secondary="menu.dish_tags", back_populates="tags")
    
    
class DishTag(Base):
    __tablename__ = "dish_tags"
    __table_args__ = {"schema": "menu"}

    dish_id = Column(Integer, ForeignKey("menu.dishes.id"), primary_key=True)
    tag_id = Column(Integer, ForeignKey("menu.tags.id"), primary_key=True)
    
    
class ComboSet(Base):
    __tablename__ = "combo_sets"
    __table_args__ = {"schema": "menu"}
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, index=True)
    price = Column(Integer, index=True)
    dishes = relationship("Dish", secondary="menu.combo_dishes", back_populates="combo_sets")
    
    
class ComboDish(Base):
    __tablename__ = "combo_dishes"
    __table_args__ = {"schema": "menu"}

    combo_id = Column(Integer, ForeignKey("menu.combo_sets.id"), primary_key=True)
    dish_id = Column(Integer, ForeignKey("menu.dishes.id"), primary_key=True)
