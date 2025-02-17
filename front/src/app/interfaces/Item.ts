export interface Gold {
  base: number,
  purchaseable: boolean,
  total: number,
  sell: number
}

export enum StatKind {
  Flat,
  Percentage
}

export enum EffectKind {
  effect1,
  effect2
}

export interface Stat {
  name: string,
  kind: StatKind,
  value: number
}

export interface Effect {
  name: string,
  kind: EffectKind,
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
