export interface Gold {
  base: number,
  purchaseable: boolean,
  total: number,
  sell: number
}

export enum StatType {
  Flat,
  Percentage
}

export enum EffectType {
  effect1,
  effect2
}

export interface Stat {
  name: string,
  type: StatType,
  value: number
}

export interface Effect {
  name: string,
  type: EffectType,
  value: number
}

export interface Item {
  name: string,
  gold: Gold,
  description: string,
  stats: Stat[]
  tag: string[]
  effects: Effect[]
  img: string
}
