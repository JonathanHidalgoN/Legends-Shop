import ItemPreView from "./components/ItemPreView";
import { Item, StatType, EffectType } from "./interfaces/Item";

const myItem: Item = {
  name: "Excalibur",
  gold: {
    base: 3000,
    purchaseable: true,
    total: 3500,
    sell: 2100,
  },
  description: "A legendary sword with unmatched power.",
  stats: [
    {
      name: "Attack Damage",
      type: StatType.Flat,
      value: 50,
    },
    {
      name: "Attack Speed",
      type: StatType.Percentage,
      value: 20,
    },
  ],
  tag: ["Legendary", "Melee"],
  effects: [
    {
      name: "Lifesteal",
      type: EffectType.effect1,
      value: 15,
    },
    {
      name: "Critical Strike",
      type: EffectType.effect2,
      value: 10,
    },
  ],
  img: "/sanginaria.jpeg",
};

export default function Home() {
  return (
    <div className="flex flex-wrap gap-4">
      <ItemPreView item={myItem} />
      <ItemPreView item={myItem} />
      <ItemPreView item={myItem} />
      <ItemPreView item={myItem} />
      <ItemPreView item={myItem} />
      <ItemPreView item={myItem} />
      <ItemPreView item={myItem} />
      <ItemPreView item={myItem} />
      <ItemPreView item={myItem} />
      <ItemPreView item={myItem} />
      <ItemPreView item={myItem} />
    </div>
  );
}
