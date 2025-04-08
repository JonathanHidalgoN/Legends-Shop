"use client";
import OrderHistoryCard from "@/app/components/OrderHistoryCard";
import {
  FilterSortField,
  FilterSortOrder,
  OptionType,
  Order,
  OrderStatus,
} from "@/app/interfaces/Order";
import { APIOrderResponse } from "../interfaces/APIResponse";
import { mapAPIOrderResponseToOrder } from "../mappers";
import {
  FromValues,
  getOrderHistoryWithCredentialsRequest,
} from "@/app/request";
import React, { useState } from "react";
import Select, { ActionMeta, MultiValue } from "react-select";
import { useStaticData } from "./StaticDataContext";
import { useSWRWithErrorRedirect } from "./useErrorRedirect";

export default function OrderHistory() {
  const { items } = useStaticData();
  const TODAY = new Date();
  const MIN_DATE = new Date(2025, 0, 1);
  const TODAY_2WEEKS = new Date(TODAY);
  TODAY_2WEEKS.setDate(TODAY.getDate() + 14);

  const itemNameSelectOptions: OptionType[] = items.map((item) => ({
    value: item.name,
    label: item.name,
  }));

  const [filterOrderStatus, setFilterOrderStatus] = useState<OrderStatus>(
    OrderStatus.ALL,
  );
  const [filterMinOrderDate, setFilterMinOrderDate] = useState<Date>(MIN_DATE);
  const [filterMaxOrderDate, setFilterMaxOrderDate] = useState<Date>(TODAY);
  const [filterMinDeliveryDate, setFilterMinDeliveryDate] =
    useState<Date>(MIN_DATE);
  const [filterMaxDeliveryDate, setFilterMaxDeliveryDate] =
    useState<Date>(TODAY_2WEEKS);
  const [sortField, setSortField] = useState<FilterSortField>(
    FilterSortField.ORDERDATE,
  );
  const [sortOrder, setSortOrder] = useState<FilterSortOrder>(
    FilterSortOrder.DESC,
  );
  const [filterItemNames, setFilterItemName] = useState<string[]>([]);
  const [currentPage, setCurrentPage] = useState<number>(1);
  const ordersPerPage = 5;

  const { data } = useSWRWithErrorRedirect<APIOrderResponse[]>(
    getOrderHistoryWithCredentialsRequest,
    () => ["orders-client", FromValues.CLIENT]
  );

  if (!data) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-[var(--orange)]"></div>
      </div>
    );
  }

  function orderMatchItemNames(
    orderItemNames: string[],
    filterItemNames: string[],
  ): boolean {
    if (filterItemNames.length == 0) {
      return true;
    } else {
      return orderItemNames.some((name) => filterItemNames.includes(name));
    }
  }

  const orders: Order[] = data
    .map((apiOrder: APIOrderResponse) => mapAPIOrderResponseToOrder(apiOrder))
    .filter(
      (order: Order) =>
        (filterOrderStatus === "ALL"
          ? true
          : order.status === filterOrderStatus) &&
        order.orderDate >= filterMinOrderDate &&
        order.orderDate <= filterMaxOrderDate &&
        order.deliveryDate >= filterMinDeliveryDate &&
        order.deliveryDate <= filterMaxDeliveryDate &&
        orderMatchItemNames(order.itemNames, filterItemNames),
    )
    .sort((a, b) => {
      let comparison: number = 0;
      switch (sortField) {
        case FilterSortField.ORDERDATE:
          comparison = a.orderDate.getTime() - b.orderDate.getTime();
          break;
        case FilterSortField.DELIVERYDATE:
          comparison = a.deliveryDate.getTime() - b.deliveryDate.getTime();
          break;
        case FilterSortField.PRICE:
          comparison = a.total - b.total;
          break;
        case FilterSortField.QUANTITY:
          comparison = a.itemNames.length - b.itemNames.length;
          break;
        default:
          break;
      }
      return sortOrder === FilterSortOrder.DESC ? -comparison : comparison;
    });

  // Calculate pagination
  const totalPages = Math.ceil(orders.length / ordersPerPage);
  const startIndex = (currentPage - 1) * ordersPerPage;
  const paginatedOrders = orders.slice(startIndex, startIndex + ordersPerPage);

  function handleItemNameFilterChange(
    selectedNames: MultiValue<OptionType>,
    _actionMeta: ActionMeta<OptionType>,
  ) {
    const itemNames = selectedNames.map((option) => option.value);
    setFilterItemName(itemNames);
  }

  const handleSortFieldChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSortField(e.target.value as FilterSortField);
  };

  const handleSortOrderChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSortOrder(e.target.value as FilterSortOrder);
  };

  return (
    <div className="grid grid-cols-2 grid-cols-[17%_auto] gap-4 h-full">
      <aside
        className="p-4 flex flex-col shadow-lg overflow-y-auto h-screen 
        bg-[var(--white)] text-[var(--black)] sticky top-0 rounded-lg"
      >
        <div className="space-y-6">
          <div>
            <h2 className="text-lg text-[var(--orange)] font-bold mb-4">
              Sort By
            </h2>
            <div className="flex flex-col gap-3">
              <label className="flex items-center cursor-pointer hover:text-[var(--orange)] transition-colors duration-200">
                <input
                  type="radio"
                  name="sortField"
                  value={FilterSortField.PRICE}
                  checked={sortField === FilterSortField.PRICE}
                  onChange={handleSortFieldChange}
                  className="mr-2"
                />
                <span>Price</span>
              </label>
              <label className="flex items-center cursor-pointer hover:text-[var(--orange)] transition-colors duration-200">
                <input
                  type="radio"
                  name="sortField"
                  value={FilterSortField.ORDERDATE}
                  checked={sortField === FilterSortField.ORDERDATE}
                  onChange={handleSortFieldChange}
                  className="mr-2"
                />
                <span>Order Date</span>
              </label>
              <label className="flex items-center cursor-pointer hover:text-[var(--orange)] transition-colors duration-200">
                <input
                  type="radio"
                  name="sortField"
                  value={FilterSortField.DELIVERYDATE}
                  checked={sortField === FilterSortField.DELIVERYDATE}
                  onChange={handleSortFieldChange}
                  className="mr-2"
                />
                <span>Delivery Date</span>
              </label>
              <label className="flex items-center cursor-pointer hover:text-[var(--orange)] transition-colors duration-200">
                <input
                  type="radio"
                  name="sortField"
                  value={FilterSortField.QUANTITY}
                  checked={sortField === FilterSortField.QUANTITY}
                  onChange={handleSortFieldChange}
                  className="mr-2"
                />
                <span>Quantity</span>
              </label>
            </div>
          </div>

          <div>
            <h2 className="text-lg font-bold mb-4 text-[var(--orange)]">
              Sort Order
            </h2>
            <div className="flex items-center gap-6">
              <label className="flex items-center cursor-pointer hover:text-[var(--orange)] transition-colors duration-200">
                <input
                  type="radio"
                  name="sortOrder"
                  value="asc"
                  checked={sortOrder === "asc"}
                  onChange={handleSortOrderChange}
                  className="mr-2"
                />
                <span>Ascending</span>
              </label>
              <label className="flex items-center cursor-pointer hover:text-[var(--orange)] transition-colors duration-200">
                <input
                  type="radio"
                  name="sortOrder"
                  value="desc"
                  checked={sortOrder === "desc"}
                  onChange={handleSortOrderChange}
                  className="mr-2"
                />
                <span>Descending</span>
              </label>
            </div>
          </div>

          <div>
            <h2 className="font-bold mb-3 text-[var(--orange)]">
              Order Status
            </h2>
            <select
              className="w-full p-2 border rounded-lg bg-[var(--white)] hover:border-[var(--orange)] 
                focus:outline-none focus:ring-2 focus:ring-[var(--orange)] focus:border-transparent
                transition-colors duration-200"
              value={filterOrderStatus}
              onChange={(e) =>
                setFilterOrderStatus(e.target.value as OrderStatus)
              }
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
          </div>

          <div>
            <h2 className="font-bold mb-3 text-[var(--orange)]">Items</h2>
            <Select
              isMulti
              options={itemNameSelectOptions}
              onChange={handleItemNameFilterChange}
              placeholder="Select item names..."
              className="react-select-container"
              classNamePrefix="react-select"
              styles={{
                control: (base) => ({
                  ...base,
                  borderColor: "var(--orange)",
                  "&:hover": {
                    borderColor: "var(--pink1)",
                  },
                }),
                option: (base, state) => ({
                  ...base,
                  backgroundColor: state.isSelected ? "var(--orange)" : "white",
                  color: state.isSelected ? "white" : "black",
                  "&:hover": {
                    backgroundColor: "var(--pink1)",
                  },
                }),
              }}
            />
          </div>

          <div>
            <h2 className="font-bold mb-3 text-[var(--orange)]">Order Date</h2>
            <div className="flex flex-col gap-3">
              <div>
                <label className="block font-semibold mb-1">From</label>
                <input
                  className="w-full p-2 border rounded-lg bg-[var(--white)] hover:border-[var(--orange)] 
                    focus:outline-none focus:ring-2 focus:ring-[var(--orange)] focus:border-transparent
                    transition-colors duration-200"
                  type="date"
                  value={filterMinOrderDate.toISOString().substring(0, 10)}
                  onChange={(e) =>
                    setFilterMinOrderDate(new Date(e.target.value))
                  }
                />
              </div>
              <div>
                <label className="block font-semibold mb-1">To</label>
                <input
                  className="w-full p-2 border rounded-lg bg-[var(--white)] hover:border-[var(--orange)] 
                    focus:outline-none focus:ring-2 focus:ring-[var(--orange)] focus:border-transparent
                    transition-colors duration-200"
                  type="date"
                  value={filterMaxOrderDate.toISOString().substring(0, 10)}
                  onChange={(e) =>
                    setFilterMaxOrderDate(new Date(e.target.value))
                  }
                />
              </div>
            </div>
          </div>

          <div>
            <h2 className="font-bold mb-3 text-[var(--orange)]">
              Delivery Date
            </h2>
            <div className="flex flex-col gap-3">
              <div>
                <label className="block font-semibold mb-1">From</label>
                <input
                  className="w-full p-2 border rounded-lg bg-[var(--white)] hover:border-[var(--orange)] 
                    focus:outline-none focus:ring-2 focus:ring-[var(--orange)] focus:border-transparent
                    transition-colors duration-200"
                  type="date"
                  value={filterMinDeliveryDate.toISOString().substring(0, 10)}
                  onChange={(e) =>
                    setFilterMinDeliveryDate(new Date(e.target.value))
                  }
                />
              </div>
              <div>
                <label className="block font-semibold mb-1">To</label>
                <input
                  className="w-full p-2 border rounded-lg bg-[var(--white)] hover:border-[var(--orange)] 
                    focus:outline-none focus:ring-2 focus:ring-[var(--orange)] focus:border-transparent
                    transition-colors duration-200"
                  type="date"
                  value={filterMaxDeliveryDate.toISOString().substring(0, 10)}
                  onChange={(e) =>
                    setFilterMaxDeliveryDate(new Date(e.target.value))
                  }
                />
              </div>
            </div>
          </div>
        </div>
      </aside>

      {orders && (
        <div className="flex flex-col items-center gap-6 p-4">
          {paginatedOrders.length > 0 ? (
            <>
              {paginatedOrders.map((order) => (
                <OrderHistoryCard key={order.id} order={order} />
              ))}
              {totalPages > 1 && (
                <div className="flex justify-center items-center gap-4 mt-6">
                  <button
                    onClick={() => {
                      setCurrentPage((prev) => Math.max(prev - 1, 1));
                      window.scrollTo({ top: 0, behavior: "smooth" });
                    }}
                    disabled={currentPage === 1}
                    className="px-6 py-2 bg-[var(--orange)] text-white rounded-lg hover:bg-[var(--pink1)] 
                    transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed
                    shadow-sm hover:shadow-md"
                  >
                    Previous
                  </button>
                  <span className="text-gray-600 font-medium">
                    Page {currentPage} of {totalPages}
                  </span>
                  <button
                    onClick={() => {
                      setCurrentPage((prev) => Math.min(prev + 1, totalPages));
                      window.scrollTo({ top: 0, behavior: "smooth" });
                    }}
                    disabled={currentPage === totalPages}
                    className="px-6 py-2 bg-[var(--orange)] text-white rounded-lg hover:bg-[var(--pink1)] 
                    transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed
                    shadow-sm hover:shadow-md"
                  >
                    Next
                  </button>
                </div>
              )}
            </>
          ) : (
            <div className="text-center text-gray-500 py-12 text-lg">
              No orders found matching your criteria.
            </div>
          )}
        </div>
      )}
    </div>
  );
}
