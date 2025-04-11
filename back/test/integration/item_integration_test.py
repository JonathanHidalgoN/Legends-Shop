from config import *
from app.data.models.StatsTable import ItemStatAssociation, StatsTable
from app.data.models.GoldTable import GoldTable
from app.data.models.ItemTable import ItemTable
from app.data.models.TagsTable import TagsTable
import pytest
from sqlalchemy import  insert
from app.data.models.TagsTable import ItemTagsAssociation
from app.data.models.EffectsTable import EffectsTable, ItemEffectAssociation


@pytest.mark.asyncio
async def test_get_unique_tags(client, dbSession):
    """Test the getUniqueTags endpoint."""
    # Create gold records
    gold_table_1 = GoldTable(
        base_cost=100,
        total=100,
        sell=70,
        purchaseable=True
    )
    
    gold_table_2 = GoldTable(
        base_cost=200,
        total=200,
        sell=140,
        purchaseable=True
    )
    
    dbSession.add(gold_table_1)
    dbSession.add(gold_table_2)
    await dbSession.commit()
    
    # Create item records
    item_table_1 = ItemTable(
        name="Test Item 1",
        plain_text="Plain text for test item 1",
        description="Description for test item 1",
        image="item1.jpg",
        imageUrl="http://example.com/item1.jpg",
        updated=False,
        gold_id=gold_table_1.id
    )
    
    item_table_2 = ItemTable(
        name="Test Item 2",
        plain_text="Plain text for test item 2",
        description="Description for test item 2",
        image="item2.jpg",
        imageUrl="http://example.com/item2.jpg",
        updated=False,
        gold_id=gold_table_2.id
    )
    
    dbSession.add(item_table_1)
    dbSession.add(item_table_2)
    await dbSession.commit()
    
    # Create tag records
    tag_table_1 = TagsTable(name="Tag1")
    tag_table_2 = TagsTable(name="Tag2")
    tag_table_3 = TagsTable(name="Tag3")
    
    dbSession.add(tag_table_1)
    dbSession.add(tag_table_2)
    dbSession.add(tag_table_3)
    await dbSession.commit()
    
    # Create item-tag associations
    await dbSession.execute(
        insert(ItemTagsAssociation).values(item_id=item_table_1.id, tags_id=tag_table_1.id)
    )
    await dbSession.execute(
        insert(ItemTagsAssociation).values(item_id=item_table_1.id, tags_id=tag_table_2.id)
    )
    await dbSession.execute(
        insert(ItemTagsAssociation).values(item_id=item_table_2.id, tags_id=tag_table_2.id)
    )
    await dbSession.execute(
        insert(ItemTagsAssociation).values(item_id=item_table_2.id, tags_id=tag_table_3.id)
    )
    await dbSession.commit()
    
    response = client.get("/items/uniqueTags")
    
    assert response.status_code == 200
    tags = response.json()
    
    assert tag_table_1.name in tags
    assert tag_table_2.name in tags
    assert tag_table_3.name in tags
    
    assert len(tags) == 3
    
    assert len(set(tags)) == 3

@pytest.mark.asyncio
async def test_get_item_names(client, dbSession):
    """Test the item_names endpoint."""
    # Create gold records
    gold1 = GoldTable(
        base_cost=100,
        total=100,
        sell=70,
        purchaseable=True
    )
    gold2 = GoldTable(
        base_cost=200,
        total=200,
        sell=140,
        purchaseable=True
    )
    dbSession.add(gold1)
    dbSession.add(gold2)
    await dbSession.commit()
    
    # Create item records
    item1 = ItemTable(
        name="Test Item 1",
        plain_text="Plain text for test item 1",
        description="Description for test item 1",
        image="item1.jpg",
        imageUrl="http://example.com/item1.jpg",
        updated=False,
        gold_id=gold1.id
    )
    item2 = ItemTable(
        name="Test Item 2",
        plain_text="Plain text for test item 2",
        description="Description for test item 2",
        image="item2.jpg",
        imageUrl="http://example.com/item2.jpg",
        updated=False,
        gold_id=gold2.id
    )
    dbSession.add(item1)
    dbSession.add(item2)
    await dbSession.commit()
    
    response = client.get("/items/item_names")
    
    print(f"Response status: {response.status_code}")
    print(f"Response body: {response.text}")
    
    assert response.status_code == 200
    item_names = response.json()
    
    assert "Test Item 1" in item_names
    assert "Test Item 2" in item_names
    
    assert len(item_names) == 2
    
    assert len(set(item_names)) == 2

@pytest.mark.asyncio
async def test_get_unique_effects(client, dbSession):
    """Test the unique_effects endpoint."""
    # Create gold records
    gold1 = GoldTable(
        base_cost=100,
        total=100,
        sell=70,
        purchaseable=True
    )
    gold2 = GoldTable(
        base_cost=200,
        total=200,
        sell=140,
        purchaseable=True
    )
    dbSession.add(gold1)
    dbSession.add(gold2)
    await dbSession.commit()
    
    # Create item records
    item1 = ItemTable(
        name="Test Item 1",
        plain_text="Plain text for test item 1",
        description="Description for test item 1",
        image="item1.jpg",
        imageUrl="http://example.com/item1.jpg",
        updated=False,
        gold_id=gold1.id
    )
    item2 = ItemTable(
        name="Test Item 2",
        plain_text="Plain text for test item 2",
        description="Description for test item 2",
        image="item2.jpg",
        imageUrl="http://example.com/item2.jpg",
        updated=False,
        gold_id=gold2.id
    )
    dbSession.add(item1)
    dbSession.add(item2)
    await dbSession.commit()
    
    # Create effect records
    effect1 = EffectsTable(name="Effect1")
    effect2 = EffectsTable(name="Effect2")
    effect3 = EffectsTable(name="Effect3")
    dbSession.add(effect1)
    dbSession.add(effect2)
    dbSession.add(effect3)
    await dbSession.commit()
    
    # Create item-effect associations
    await dbSession.execute(
        insert(ItemEffectAssociation).values(item_id=item1.id, effect_id=effect1.id, value=10.0)
    )
    await dbSession.execute(
        insert(ItemEffectAssociation).values(item_id=item1.id, effect_id=effect2.id, value=20.0)
    )
    await dbSession.execute(
        insert(ItemEffectAssociation).values(item_id=item2.id, effect_id=effect2.id, value=30.0)
    )
    await dbSession.execute(
        insert(ItemEffectAssociation).values(item_id=item2.id, effect_id=effect3.id, value=40.0)
    )
    await dbSession.commit()
    
    response = client.get("/items/unique_effects")
    
    assert response.status_code == 200
    effects = response.json()
    
    assert "Effect1" in effects
    assert "Effect2" in effects
    assert "Effect3" in effects
    
    assert len(effects) == 3
    
    assert len(set(effects)) == 3

@pytest.mark.asyncio
async def test_get_all_items(client, dbSession):
    """Test the /items/all endpoint."""
    # Create gold records
    gold1 = GoldTable(
        base_cost=100,
        sell=70,
        total=100,
        purchaseable=True
    )
    gold2 = GoldTable(
        base_cost=200,
        total=200,
        sell=140,
        purchaseable=True
    )
    dbSession.add(gold1)
    dbSession.add(gold2)
    await dbSession.commit()
    
    # Create item records
    item1 = ItemTable(
        name="Test Item 1",
        plain_text="Plain text for test item 1",
        description="Description for test item 1",
        image="item1.jpg",
        imageUrl="http://example.com/item1.jpg",
        updated=False,
        gold_id=gold1.id
    )
    item2 = ItemTable(
        name="Test Item 2",
        plain_text="Plain text for test item 2",
        description="Description for test item 2",
        image="item2.jpg",
        imageUrl="http://example.com/item2.jpg",
        updated=False,
        gold_id=gold2.id
    )
    dbSession.add(item1)
    dbSession.add(item2)
    await dbSession.commit()
    
    # Create tag records
    tag1 = TagsTable(name="Tag1")
    tag2 = TagsTable(name="Tag2")
    dbSession.add(tag1)
    dbSession.add(tag2)
    await dbSession.commit()
    
    # Create item-tag associations
    await dbSession.execute(
        insert(ItemTagsAssociation).values(item_id=item1.id, tags_id=tag1.id)
    )
    await dbSession.execute(
        insert(ItemTagsAssociation).values(item_id=item2.id, tags_id=tag2.id)
    )
    await dbSession.commit()
    
    # Create effect records
    effect1 = EffectsTable(name="Effect1")
    effect2 = EffectsTable(name="Effect2")
    dbSession.add(effect1)
    dbSession.add(effect2)
    await dbSession.commit()
    
    # Create item-effect associations
    await dbSession.execute(
        insert(ItemEffectAssociation).values(item_id=item1.id, effect_id=effect1.id, value=10.0)
    )
    await dbSession.execute(
        insert(ItemEffectAssociation).values(item_id=item2.id, effect_id=effect2.id, value=20.0)
    )
    await dbSession.commit()
    
    # Create stat records
    stat1 = StatsTable(name="Stat1", kind="flat")
    stat2 = StatsTable(name="Stat2", kind="percentage")
    dbSession.add(stat1)
    dbSession.add(stat2)
    await dbSession.commit()
    
    # Create item-stat associations
    await dbSession.execute(
        insert(ItemStatAssociation).values(item_id=item1.id, stat_id=stat1.id, value=5.0)
    )
    await dbSession.execute(
        insert(ItemStatAssociation).values(item_id=item2.id, stat_id=stat2.id, value=15.0)
    )
    await dbSession.commit()
    
    response = client.get("/items/all")
    
    assert response.status_code == 200
    items = response.json()
    
    assert len(items) == 2
    
    # Check first item
    item1_response = next((item for item in items if item["name"] == "Test Item 1"), None)
    assert item1_response is not None
    assert item1_response["plaintext"] == "Plain text for test item 1"
    assert item1_response["description"] == "Description for test item 1"
    assert item1_response["image"] == "item1.jpg"
    assert item1_response["imageUrl"] == "http://example.com/item1.jpg"
    assert item1_response["id"] == item1.id
    
    # Check gold for first item
    assert item1_response["gold"]["base"] == 100
    assert item1_response["gold"]["total"] == 100
    assert item1_response["gold"]["sell"] == 70
    assert item1_response["gold"]["purchasable"] is True
    
    # Check tags for first item
    assert "Tag1" in item1_response["tags"]
    assert len(item1_response["tags"]) == 1
    
    # Check effects for first item
    assert "Effect1" in item1_response["effect"]
    assert item1_response["effect"]["Effect1"] == 10.0
    assert len(item1_response["effect"]) == 1
    
    # Check stats for first item
    stat1_response = next((stat for stat in item1_response["stats"] if stat["name"] == "Stat1"), None)
    assert stat1_response is not None
    assert stat1_response["kind"] == "flat"
    assert stat1_response["value"] == 5.0
    assert len(item1_response["stats"]) == 1
    
    # Check second item
    item2_response = next((item for item in items if item["name"] == "Test Item 2"), None)
    assert item2_response is not None
    assert item2_response["plaintext"] == "Plain text for test item 2"
    assert item2_response["description"] == "Description for test item 2"
    assert item2_response["image"] == "item2.jpg"
    assert item2_response["imageUrl"] == "http://example.com/item2.jpg"
    assert item2_response["id"] == item2.id
    
    # Check gold for second item
    assert item2_response["gold"]["base"] == 200
    assert item2_response["gold"]["total"] == 200
    assert item2_response["gold"]["sell"] == 140
    assert item2_response["gold"]["purchasable"] is True
    
    # Check tags for second item
    assert "Tag2" in item2_response["tags"]
    assert len(item2_response["tags"]) == 1
    
    # Check effects for second item
    assert "Effect2" in item2_response["effect"]
    assert item2_response["effect"]["Effect2"] == 20.0
    assert len(item2_response["effect"]) == 1
    
    # Check stats for second item
    stat2_response = next((stat for stat in item2_response["stats"] if stat["name"] == "Stat2"), None)
    assert stat2_response is not None
    assert stat2_response["kind"] == "percentage"
    assert stat2_response["value"] == 15.0
    assert len(item2_response["stats"]) == 1
