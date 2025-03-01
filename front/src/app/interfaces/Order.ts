export interface Order {
  id: number,
  status: string
  itemNames: string[],
  total: number,
  userName: string,
  date: Date
}
