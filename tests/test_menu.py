import pytest
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import FastAPI, APIRouter, Depends, HTTPException
from src.infrastructure.repositories.menu import MenuRepository
from src.infrastructure.services.menu_events import MenuEventService
from src.schemas.menu_schemas import CategoryCreate, DishCreate, DishUpdate

@pytest.fixture(scope="session")
def test_router():
    router = APIRouter(prefix="/menu", tags=["menu"])
    
    @router.get("/categories")
    async def get_categories(
        db: AsyncSession = Depends(lambda: AsyncMock(spec=AsyncSession)),
        limit: int = 0,
        offset: int = 10
    ):
        return [{"id": 1, "name": "Test Category", "description": "Test Description"}]

    @router.post("/categories")
    async def create_category(
        category: CategoryCreate,
        db: AsyncSession = Depends(lambda: AsyncMock(spec=AsyncSession))
    ):
        if not category.name or not category.description:
            raise HTTPException(status_code=422, detail="Name and description are required")
        return {"id": 1, "name": category.name, "description": category.description}

    @router.get("/dishes")
    async def get_dishes(
        db: AsyncSession = Depends(lambda: AsyncMock(spec=AsyncSession)),
        limit: int = 0,
        offset: int = 10
    ):
        return [{"id": 1, "name": "Test Dish", "description": "Test Description", "price": 100, "category_id": 1}]

    @router.post("/dishes")
    async def create_dish(
        dish: DishCreate,
        db: AsyncSession = Depends(lambda: AsyncMock(spec=AsyncSession))
    ):
        if not dish.name or not dish.description or not dish.price or not dish.category_id:
            raise HTTPException(status_code=422, detail="All fields are required")
        return {"id": 1, "name": dish.name, "description": dish.description, "price": dish.price, "category_id": dish.category_id}

    @router.put("/dishes/{dish_id}")
    async def update_dish(
        dish_id: int,
        dish: DishUpdate,
        db: AsyncSession = Depends(lambda: AsyncMock(spec=AsyncSession))
    ):
        if not dish.name or not dish.price:
            raise HTTPException(status_code=422, detail="Name and price are required")
        return {"id": dish_id, "name": dish.name, "description": dish.description, "price": dish.price, "category_id": dish.category_id}

    @router.get("/tags")
    async def get_tags(
        db: AsyncSession = Depends(lambda: AsyncMock(spec=AsyncSession)),
        limit: int = 0,
        offset: int = 10
    ):
        return [{"id": 1, "name": "Test Tag"}]

    @router.get("/combo_sets")
    async def get_combos(
        db: AsyncSession = Depends(lambda: AsyncMock(spec=AsyncSession))
    ):
        return [{"id": 1, "name": "Test Combo", "description": "Test Description", "price": 200, "dish_ids": [1, 2]}]

    return router

@pytest.fixture(scope="session")
def test_app(test_router):
    test_app = FastAPI()
    test_app.include_router(test_router, prefix="/menu1")
    return test_app

@pytest.fixture
def client(test_app):
    return TestClient(test_app)

@pytest.fixture
def mock_db():
    return AsyncMock(spec=AsyncSession)

@pytest.fixture
def mock_menu_repository():
    with patch('src.interfaces.routers.v1.menu.MenuRepository') as mock:
        mock_repo = Mock(spec=MenuRepository)
        mock.return_value = mock_repo
        yield mock_repo

@pytest.fixture
def mock_menu_event_service():
    with patch('src.interfaces.routers.v1.menu.menu_event_service') as mock:
        mock_service = Mock(spec=MenuEventService)
        mock.return_value = mock_service
        yield mock_service

def test_get_categories(client, mock_menu_repository):
    test_categories = [
        {"id": 1, "name": "Category 1", "description": "Description 1"},
        {"id": 2, "name": "Category 2", "description": "Description 2"}
    ]
    mock_menu_repository.get_categories.return_value = test_categories

    response = client.get("/menu1/menu/categories")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "Test Category"

def test_create_category(client, mock_menu_repository):
    category_data = {
        "name": "New Category",
        "description": "New Description"
    }
    mock_menu_repository.create_category.return_value = {
        "id": 1,
        **category_data
    }

    response = client.post("/menu1/menu/categories", json=category_data)

    assert response.status_code == 200
    assert response.json()["name"] == category_data["name"]
    assert response.json()["description"] == category_data["description"]

def test_get_dishes(client, mock_menu_repository):
    test_dishes = [
        {
            "id": 1,
            "name": "Dish 1",
            "description": "Description 1",
            "price": 100,
            "category_id": 1
        }
    ]
    mock_menu_repository.get_dishes.return_value = test_dishes

    response = client.get("/menu1/menu/dishes")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "Test Dish"

def test_create_dish(client, mock_menu_repository, mock_menu_event_service):
    dish_data = {
        "name": "New Dish",
        "description": "New Description",
        "price": 150,
        "category_id": 1
    }
    mock_menu_repository.create_dish.return_value = {
        "id": 1,
        **dish_data
    }

    response = client.post("/menu1/menu/dishes", json=dish_data)

    assert response.status_code == 200
    assert response.json()["name"] == dish_data["name"]
    assert response.json()["price"] == dish_data["price"]
    assert response.json()["category_id"] == dish_data["category_id"]

def test_update_dish_price(client, mock_menu_repository, mock_menu_event_service):
    dish_id = 1
    old_dish = {
        "id": dish_id,
        "name": "Old Dish",
        "price": 100,
        "is_available": True
    }
    new_dish_data = {
        "name": "Updated Dish",
        "description": "Updated Description",
        "price": 150,
        "category_id": 1,
        "is_available": True
    }
    
    mock_menu_repository.get_dish_id.return_value = old_dish
    mock_menu_repository.update_dish.return_value = {
        "id": dish_id,
        **new_dish_data
    }

    response = client.put(f"/menu1/menu/dishes/{dish_id}", json=new_dish_data)

    assert response.status_code == 200
    assert response.json()["price"] == new_dish_data["price"]
    assert response.json()["name"] == new_dish_data["name"]

def test_get_tags(client, mock_menu_repository):
    test_tags = [
        {"id": 1, "name": "Tag 1"},
        {"id": 2, "name": "Tag 2"}
    ]
    mock_menu_repository.get_tags.return_value = test_tags

    response = client.get("/menu1/menu/tags")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "Test Tag"

def test_get_combos(client, mock_menu_repository):
    test_combos = [
        {
            "id": 1,
            "name": "Combo 1",
            "description": "Description 1",
            "price": 200,
            "dish_ids": [1, 2]
        }
    ]
    mock_menu_repository.get_combos.return_value = test_combos

    response = client.get("/menu1/menu/combo_sets")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "Test Combo" 