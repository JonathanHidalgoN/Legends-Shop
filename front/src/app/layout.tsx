import Header from "./components/Header";
import "./styles.css";
import "./globals.css";
import { Item } from "./interfaces/Item";
import { Location } from "./interfaces/Location";
import { StaticDataContextProvider } from "./components/StaticDataContext";
import { AuthContextProvider } from "./components/AuthContext";
import { CarContextProvider } from "./components/CarContext";
import { Toaster } from "react-hot-toast";
import { redirect } from "next/navigation";
import {
  allTagsRequet,
  FromValues,
  getAllEffectNamesRequest,
  getAllLocationsRequest,
  someItemsRequest,
} from "./request";
import { mapAPIItemResponseToItem } from "./mappers";
import { LoadingProvider } from "./components/LoadingRequestContext";
import ErrorBoundary from "./components/ErrorBoundary";
import { checkIfHDImageAvailable, getHDItemImages } from "./serverFunctions";

export const metadata = {
  title: "Legends Shop",
};

export default async function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  console.log("Server log: layout init")
  let items: Item[] = [];
  let tags: string[] = [];
  let effects: string[] = [];
  let locations: Location[] = [];
  try {
    items = (await someItemsRequest(FromValues.SERVER)).map(
      mapAPIItemResponseToItem,
    );
    tags = await allTagsRequet(FromValues.SERVER);
    effects = await getAllEffectNamesRequest(FromValues.SERVER);
    locations = await getAllLocationsRequest(FromValues.SERVER);
    const itemNames: string[] = items.map((item: Item) => (item.name));
    try {
      await getHDItemImages(itemNames);
      items.forEach((item: Item) => {
        item.img = checkIfHDImageAvailable(item.name, "");
      })
    }
    catch (error) {
      console.error("Error changing the image to hd of item", error);
    }
  } catch (error) {
    console.error("Data fetching error in RootLayout:", error);
    redirect("/error/wrong");
  }

  return (
    <html lang="en">
      <body>
        <LoadingProvider>
          <AuthContextProvider>
            <StaticDataContextProvider
              items={items}
              tags={tags}
              effects={effects}
              locations={locations}
            >
              <CarContextProvider>
                <ErrorBoundary>
                  <Header items={items} />
                  <Toaster position="top-left" />
                  {children}
                </ErrorBoundary>
              </CarContextProvider>
            </StaticDataContextProvider>
          </AuthContextProvider>
        </LoadingProvider>
      </body>
    </html>
  );
}
