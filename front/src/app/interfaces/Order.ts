export interface Order {
  id: number,
  status: string
  itemNames: string[],
  total: number,
  userName: string,
  orderDate: Date,
  deliveryDate: Date,
}
