"use client";
import React, { useState, useEffect } from "react";
import { Order } from "@/app/interfaces/Order";
import OrderHistoryCard from "@/app/components/OrderHistoryCard";
import { getUserHistoryRequest } from "@/app/request";
import toast from "react-hot-toast";
import { OrderStatus } from "@/app/interfaces/Order";
import { useStaticData } from "./StaticDataContext";
import Select, { ActionMeta, MultiValue } from "react-select";

interface OptionType {
  value: string;
  label: string;
}

type SortField = "price" | "orderDate" | "deliveryDate" | "quantity";
type SortOrder = "asc" | "desc";

export default function OrderHistory({ urlUserName }: { urlUserName: string }) {
  const { items } = useStaticData();
  const itemNameSelectOptions: OptionType[] = items.map((item) => ({
    value: item.name,
    label: item.name,
  }));

  const TODAY = new Date();
  const MIN_DATE = new Date(2025, 0, 1);
  const TODAY_2WEEKS = new Date(TODAY);
  TODAY_2WEEKS.setDate(TODAY.getDate() + 14);

  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [filterOrderStatus, setFilterOrderStatus] = useState<string>("ALL");
  const [filterMinOrderDate, setFilterMinOrderDate] = useState<Date>(MIN_DATE);
  const [filterMaxOrderDate, setFilterMaxOrderDate] = useState<Date>(TODAY);
  const [filterMinDeliveryDate, setFilterMinDeliveryDate] =
    useState<Date>(MIN_DATE);
  const [filterMaxDeliveryDate, setFilterMaxDeliveryDate] =
    useState<Date>(TODAY_2WEEKS);
  const [sortField, setSortField] = useState<SortField>("price");
  const [sortOrder, setSortOrder] = useState<SortOrder>("asc");
  const [filterItemNames, setFilterItemName] = useState<string[] | null>(null);

  function handleItemNameFilterChange(
    selectedNames: MultiValue<OptionType>,
    _actionMeta: ActionMeta<OptionType>,
  ) {
    const itemNames = selectedNames.map((option) => option.value);
    setFilterItemName(itemNames);
  }

  const handleSortFieldChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSortField(e.target.value as SortField);
  };

  const handleSortOrderChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSortOrder(e.target.value as SortOrder);
  };

  useEffect(() => {
    async function fetchUserHistory() {
      try {
        const response = await getUserHistoryRequest(urlUserName, {
          orderStatus: filterOrderStatus,
          minOrderDate: filterMinOrderDate,
          maxOrderDate: filterMaxOrderDate,
          minDeliveryDate: filterMinDeliveryDate,
          maxDeliveryDate: filterMaxDeliveryDate,
          sortField,
          sortOrder,
          filterItemNames: filterItemNames || [],
        });
        if (!response.ok) {
          toast.error("Error fetching order history");
          return;
        }
        const data = await response.json();
        setOrders(data);
      } catch (error) {
        console.log(error);
        toast.error("An unexpected error occurred");
      } finally {
        setLoading(false);
      }
    }
    fetchUserHistory();
  }, [
    urlUserName,
    filterOrderStatus,
    filterMinOrderDate,
    filterMaxOrderDate,
    filterMinDeliveryDate,
    filterMaxDeliveryDate,
    sortField,
    sortOrder,
    filterItemNames,
  ]);
  if (loading) return <div>Loading...</div>;

  return (
    <div className="grid grid-cols-2 grid-cols-[17%_auto] gap-4 h-full">
      <aside className="p-2 flex flex-col shadow-lg bg-[var(--white)] text-[var(--black)]">
        <div className="p-4">
          <h2 className="text-lg font-bold mb-2">Sort By</h2>
          <div className="flex flex-col gap-2">
            <label className="flex items-center">
              <input
                type="radio"
                name="sortField"
                value="price"
                checked={sortField === "price"}
                onChange={handleSortFieldChange}
              />
              <span className="ml-2">Price</span>
            </label>
            <label className="flex items-center">
              <input
                type="radio"
                name="sortField"
                value="orderDate"
                checked={sortField === "orderDate"}
                onChange={handleSortFieldChange}
              />
              <span className="ml-2">Order Date</span>
            </label>
            <label className="flex items-center">
              <input
                type="radio"
                name="sortField"
                value="deliveryDate"
                checked={sortField === "deliveryDate"}
                onChange={handleSortFieldChange}
              />
              <span className="ml-2">Delivery Date</span>
            </label>
            <label className="flex items-center">
              <input
                type="radio"
                name="sortField"
                value="quantity"
                checked={sortField === "quantity"}
                onChange={handleSortFieldChange}
              />
              <span className="ml-2">Quantity</span>
            </label>
          </div>

          <h2 className="text-lg font-bold mt-4 mb-2">Sort Order</h2>
          <div className="flex items-center gap-4">
            <label className="flex items-center">
              <input
                type="radio"
                name="sortOrder"
                value="asc"
                checked={sortOrder === "asc"}
                onChange={handleSortOrderChange}
              />
              <span className="ml-2">Ascending</span>
            </label>
            <label className="flex items-center">
              <input
                type="radio"
                name="sortOrder"
                value="desc"
                checked={sortOrder === "desc"}
                onChange={handleSortOrderChange}
              />
              <span className="ml-2">Descending</span>
            </label>
          </div>
        </div>

        <h2 className="font-bold mb-2">Order status</h2>
        <select
          className="p-2 border rounded  bg-[var(--white)]"
          value={filterOrderStatus}
          onChange={(e) => setFilterOrderStatus(e.target.value)}
        >
          <option key={"ALL"} value={"ALL"}>
            {"ALL"}
          </option>
          {Object.values(OrderStatus).map((status: string) => (
            <option key={status} value={status}>
              {status}
            </option>
          ))}
        </select>

        <h2 className="font-bold mb-2 my-2">Items</h2>
        <Select
          isMulti
          options={itemNameSelectOptions}
          onChange={handleItemNameFilterChange}
          placeholder="Select item names..."
        />

        <h2 className="font-bold mb-2 my-2">Order Date</h2>
        <div className="flex gap-4">
          <div>
            <label className="block font-semibold">From</label>
            <input
              className="border rounded bg-[var(--white)] p-1"
              type="date"
              value={filterMinOrderDate.toISOString().substring(0, 10)}
              onChange={(e) => setFilterMinOrderDate(new Date(e.target.value))}
            />
          </div>
          <div>
            <label className="block font-semibold">To</label>
            <input
              className="border rounded bg-[var(--white)] p-1"
              type="date"
              value={filterMaxOrderDate.toISOString().substring(0, 10)}
              onChange={(e) => setFilterMaxOrderDate(new Date(e.target.value))}
            />
          </div>
        </div>

        <h2 className="font-bold mb-2 my-2">Delivery Date</h2>
        <div className="flex gap-4">
          <div>
            <label className="block font-semibold">From</label>
            <input
              className="border rounded bg-[var(--white)] p-1"
              type="date"
              value={filterMinDeliveryDate.toISOString().substring(0, 10)}
              onChange={(e) =>
                setFilterMinDeliveryDate(new Date(e.target.value))
              }
            />
          </div>
          <div>
            <label className="block font-semibold">To</label>
            <input
              className="border rounded bg-[var(--white)] p-1"
              type="date"
              value={filterMaxDeliveryDate.toISOString().substring(0, 10)}
              onChange={(e) =>
                setFilterMaxDeliveryDate(new Date(e.target.value))
              }
            />
          </div>
        </div>
      </aside>

      <div className="flex flex-col justify-center items-center gap-4 p-4">
        {orders.length > 0 ? (
          orders.map((order) => (
            <OrderHistoryCard key={order.id} order={order} />
          ))
        ) : (
          <div>No orders found.</div>
        )}
      </div>
    </div>
  );
}
