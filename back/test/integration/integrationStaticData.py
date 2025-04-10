from app.data.models.GoldTable import GoldTable
from app.data.models.ItemTable import ItemTable
from app.data.models.TagsTable import TagsTable
from app.data.models.UserTable import UserTable


TEST_SINGUP_DATA = {
        "username": "testuser",
        "password": "TestPassword123!",
        "email": "test@example.com",
        "birthDate": "2000-01-01",
        "location_id": 1
}

TEST_SINGUP_DATA_INVALID_LOCATION = {
        "username": "testuser",
        "password": "TestPassword123!",
        "email": "test@example.com",
        "birthDate": "2000-01-01",
        "location_id": 32131231
}
TEST_LOGIN_DATA = {
    "username": TEST_SINGUP_DATA["username"],
    "password": TEST_SINGUP_DATA["password"],
}

GOLD_TABLE_1 = GoldTable(
        base_cost=100,
        total=100,
        sell=70,
        purchaseable=True
)

GOLD_TABLE_2 = GoldTable(
        base_cost=200,
        total=200,
        sell=140,
        purchaseable=True
)

ITEM_TABLE_1 = ItemTable(
    name="Test Item 1",
    plain_text="Plain text for test item 1",
    description="Description for test item 1",
    image="item1.jpg",
    imageUrl="http://example.com/item1.jpg",
    updated=False,
    #This will be None
    gold_id=GOLD_TABLE_1.id
)

ITEM_TABLE_2 = ItemTable(
    name="Test Item 2",
    plain_text="Plain text for test item 2",
    description="Description for test item 2",
    image="item2.jpg",
    imageUrl="http://example.com/item2.jpg",
    updated=False,
    #This will be None
    gold_id=GOLD_TABLE_2.id
)

TAG_TABLE_1 = TagsTable(name="Tag1")
TAG_TABLE_2 = TagsTable(name="Tag2")
TAG_TABLE_3 = TagsTable(name="Tag3")


