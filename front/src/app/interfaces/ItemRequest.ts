export interface GoldNode {
  base: number;
  boolean: boolean;
  total: number;
  sell: number;
}

export interface StatNode {
  name: string;
  kind: "flat" | "percentage";
  value: number;
}

export interface EffectsNode {
  [effectName: string]: number;
}

export interface ItemNode {
  name: string;
  tags?: string[];
  gold: GoldNode;
  effect: EffectsNode;
  stats: StatNode[];
  description: string;
  imageUrl: string;
  id: number;
}
