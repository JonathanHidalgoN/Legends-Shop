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
import fs from "fs";
import path from "path";
import { LoadingProvider } from "./components/LoadingRequestContext";

export const metadata = {
  title: "Legends Shop",
};

function checkIfHDImageAvailable(
  itemName: string,
  serverImagePath: string,
): string {
  const fileName = `${itemName}.png`;
  const filePath = path.join(process.cwd(), "public", "hd_images", fileName);
  if (fs.existsSync(filePath)) {
    return `/hd_images/${fileName}`;
  } else {
    return serverImagePath;
  }
}

export default async function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
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
  } catch (error) {
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
                <Header items={items} />
                <Toaster position="top-left" />
                {children}
              </CarContextProvider>
            </StaticDataContextProvider>
          </AuthContextProvider>
        </LoadingProvider>
      </body>
    </html>
  );
}
