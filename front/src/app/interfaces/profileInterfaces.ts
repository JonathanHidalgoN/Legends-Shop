import { OrderSummary } from "./Order";

export interface UserInfo {
  userName: string;
  email: string;
  created: Date;
  lastSingIn: Date;
  goldSpend: number;
  currentGold: number;
  birthDate: Date;
  locationId: number;
}

export interface ProfileInfo {
  user: UserInfo;
  ordersInfo: OrderSummary[];
}
