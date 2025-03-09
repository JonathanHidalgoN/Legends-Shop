from app.schemas.Item import Effects, Gold, Item, Stat

STATIC_DATA_ITEMS_JSON:dict = {
  "type": "item",
  "version": "15.5.1",
  "basic": {
    "name": "",
    "rune": {
      "isrune": False,
      "tier": 1,
      "type": "red"
    },
    "gold": {
      "base": 0,
      "total": 0,
      "sell": 0,
      "purchasable": False
    },
    "group": "",
    "description": "",
    "colloq": ";",
    "plaintext": "",
    "consumed": False,
    "stacks": 1,
    "depth": 1,
    "consumeOnFull": False,
    "from": [],
    "into": [],
    "specialRecipe": 0,
    "inStore": True,
    "hideFromAll": False,
    "requiredChampion": "",
    "requiredAlly": "",
    "stats": {
      "FlatHPPoolMod": 0,
      "rFlatHPModPerLevel": 0,
      "FlatMPPoolMod": 0,
      "rFlatMPModPerLevel": 0,
      "PercentHPPoolMod": 0,
      "PercentMPPoolMod": 0,
      "FlatHPRegenMod": 0,
      "rFlatHPRegenModPerLevel": 0,
      "PercentHPRegenMod": 0,
      "FlatMPRegenMod": 0,
      "rFlatMPRegenModPerLevel": 0,
      "PercentMPRegenMod": 0,
      "FlatArmorMod": 0,
      "rFlatArmorModPerLevel": 0,
      "PercentArmorMod": 0,
      "rFlatArmorPenetrationMod": 0,
      "rFlatArmorPenetrationModPerLevel": 0,
      "rPercentArmorPenetrationMod": 0,
      "rPercentArmorPenetrationModPerLevel": 0,
      "FlatPhysicalDamageMod": 0,
      "rFlatPhysicalDamageModPerLevel": 0,
      "PercentPhysicalDamageMod": 0,
      "FlatMagicDamageMod": 0,
      "rFlatMagicDamageModPerLevel": 0,
      "PercentMagicDamageMod": 0,
      "FlatMovementSpeedMod": 0,
      "rFlatMovementSpeedModPerLevel": 0,
      "PercentMovementSpeedMod": 0,
      "rPercentMovementSpeedModPerLevel": 0,
      "FlatAttackSpeedMod": 0,
      "PercentAttackSpeedMod": 0,
      "rPercentAttackSpeedModPerLevel": 0,
      "rFlatDodgeMod": 0,
      "rFlatDodgeModPerLevel": 0,
      "PercentDodgeMod": 0,
      "FlatCritChanceMod": 0,
      "rFlatCritChanceModPerLevel": 0,
      "PercentCritChanceMod": 0,
      "FlatCritDamageMod": 0,
      "rFlatCritDamageModPerLevel": 0,
      "PercentCritDamageMod": 0,
      "FlatBlockMod": 0,
      "PercentBlockMod": 0,
      "FlatSpellBlockMod": 0,
      "rFlatSpellBlockModPerLevel": 0,
      "PercentSpellBlockMod": 0,
      "FlatEXPBonus": 0,
      "PercentEXPBonus": 0,
      "rPercentCooldownMod": 0,
      "rPercentCooldownModPerLevel": 0,
      "rFlatTimeDeadMod": 0,
      "rFlatTimeDeadModPerLevel": 0,
      "rPercentTimeDeadMod": 0,
      "rPercentTimeDeadModPerLevel": 0,
      "rFlatGoldPer10Mod": 0,
      "rFlatMagicPenetrationMod": 0,
      "rFlatMagicPenetrationModPerLevel": 0,
      "rPercentMagicPenetrationMod": 0,
      "rPercentMagicPenetrationModPerLevel": 0,
      "FlatEnergyRegenMod": 0,
      "rFlatEnergyRegenModPerLevel": 0,
      "FlatEnergyPoolMod": 0,
      "rFlatEnergyModPerLevel": 0,
      "PercentLifeStealMod": 0,
      "PercentSpellVampMod": 0
    },
    "tags": [],
    "maps": {
      "1": True,
      "8": True,
      "10": True,
      "12": True
    }
  },
  "data": {
    "1001": {
      "name": "Boots",
      "description": "\u003CmainText\u003E\u003Cstats\u003E\u003Cattention\u003E25\u003C/attention\u003E Move Speed\u003C/stats\u003E\u003Cbr\u003E\u003Cbr\u003E\u003C/mainText\u003E",
      "colloq": ";",
      "plaintext": "Slightly increases Move Speed",
      "into": [
        "3005",
        "3047",
        "3006",
        "3009",
        "3010",
        "3020",
        "3111",
        "3117",
        "3158"
      ],
      "image": {
        "full": "1001.png",
        "sprite": "item0.png",
        "group": "item",
        "x": 0,
        "y": 0,
        "w": 48,
        "h": 48
      },
      "gold": {
        "base": 300,
        "purchasable": True,
        "total": 300,
        "sell": 210
      },
      "tags": [
        "Boots"
      ],
      "maps": {
        "11": True,
        "12": True,
        "21": True,
        "22": False,
        "30": False,
        "33": False
      },
      "stats": {
        "FlatMovementSpeedMod": 25
      }
    },
    "1004": {
      "name": "Faerie Charm",
      "description": "\u003CmainText\u003E\u003Cstats\u003E\u003Cattention\u003E50%\u003C/attention\u003E Base Mana Regen\u003C/stats\u003E\u003Cbr\u003E\u003Cbr\u003E\u003C/mainText\u003E",
      "colloq": ";",
      "plaintext": "Slightly increases Mana Regen",
      "into": [
        "3114",
        "4642",
        "3012"
      ],
      "image": {
        "full": "1004.png",
        "sprite": "item0.png",
        "group": "item",
        "x": 48,
        "y": 0,
        "w": 48,
        "h": 48
      },
      "gold": {
        "base": 200,
        "purchasable": True,
        "total": 200,
        "sell": 140
      },
      "tags": [
        "ManaRegen"
      ],
      "maps": {
        "11": True,
        "12": True,
        "21": True,
        "22": False,
        "30": False,
        "33": False
      },
      "stats": {

      }
    },
    "1006": {
      "name": "rejuvenation bead",
      "description": "\u003cmaintext\u003e\u003cstats\u003e\u003cattention\u003e100%\u003c/attention\u003e base health regen\u003c/stats\u003e\u003cbr\u003e\u003cbr\u003e\u003c/maintext\u003e",
      "colloq": ";",
      "plaintext": "slightly increases health regen",
      "into": [
        "3109",
        "3211",
        "323109",
        "3801"
      ],
      "image": {
        "full": "1006.png",
        "sprite": "item0.png",
        "group": "item",
        "x": 96,
        "y": 0,
        "w": 48,
        "h": 48
      },
      "gold": {
        "base": 300,
        "purchasable": True,
        "total": 300,
        "sell": 120
      },
      "tags": [
        "healthregen"
      ],
      "maps": {
        "11": True,
        "12": True,
        "21": True,
        "22": False,
        "30": False,
        "33": False
      },
      "stats": {

      }
    },}}

STATIC_DATA_ITEM1: Item = Item(
            name="Item1",
            plaintext="Test Item 1",
            image="path/to/image1.jpg",
            imageUrl="http://example.com/image1.jpg",
            gold=Gold(base=100, purchasable=True, total=150, sell=75),
            tags={"weapon", "melee"},
            stats={Stat(name="Damage", kind="flat", value=20), Stat(name="Health", kind="percentage", value=10)},
            effect=Effects(root={"effect1": 5}),
            id=1,
            description="A powerful weapon."
        )

STATIC_DATA_ITEM2: Item = Item(
            name="Item2",
            plaintext="Test Item 2",
            image="path/to/image2.jpg",
            imageUrl="http://example.com/image2.jpg",
            gold=Gold(base=50, purchasable=True, total=80, sell=40),
            tags={"armor"},
            stats={Stat(name="Damage", kind="flat", value=10), Stat(name="Armor", kind="percentage", value=5)},
            effect=Effects(root={"effect2": 3}),
            id=2,
            description="Protective gear."
        )
