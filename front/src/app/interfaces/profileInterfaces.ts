import { OrderSummary } from "./Order";

export interface UserInfo {
  userName: string;
  email: string;
  created: Date;
  lastSingIn: Date;
  goldSpend: number;
  currentGold: number;
  birthDate: Date;
}

export interface ProfileInfo {
  user: UserInfo;
  ordersInfo: OrderSummary[];
}
