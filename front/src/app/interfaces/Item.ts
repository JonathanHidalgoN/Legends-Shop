export interface Gold {
  base: number;
  purchaseable: boolean;
  total: number;
  sell: number;
}

export enum StatKind {
  Flat,
  Percentage,
}

export enum EffectKind {
  effect1,
  effect2,
}

export interface Stat {
  name: string;
  kind: StatKind;
  value: number;
}

export interface Effect {
  name: string;
  value: number;
  kind: EffectKind;
}

export interface Item {
  name: string;
  gold: Gold;
  description: string;
  stats: Stat[];
  tags: string[];
  effects: Effect[];
  img: string;
  id: number;
  hasHdImage?: boolean;
}

export enum FilterItemSortField {
  PRICE = "Price",
  NAME = "Name",
}

export enum FilterSortOrder {
  ASC = "asc",
  DESC = "desc",
}
