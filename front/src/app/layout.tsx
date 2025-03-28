import Header from "./components/Header";
import "./styles.css";
import "./globals.css";
import { Item } from "./interfaces/Item";
import { fetchItems, fetchTags } from "./itemsFetcher";
import { StaticDataContextProvider } from "./components/StaticDataContext";
import { AuthContextProvider } from "./components/AuthContext";
import { CarContextProvider } from "./components/CarContext";
import { Toaster } from "react-hot-toast";
import { redirect } from "next/navigation";
import { getAllEffectNamesRequest } from "./request";

export const metadata = {
  title: "Legends Shop",
};

export default async function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  let items: Item[] = [];
  let tags: string[] = [];
  let effects: string[] = [];
  try {
    items = await fetchItems();
    tags = await fetchTags();
    effects = await getAllEffectNamesRequest();
  } catch (error) {
    redirect("/error/wrong");
  }

  return (
    <html lang="en">
      <body>
        <AuthContextProvider>
          <StaticDataContextProvider items={items} tags={tags} effects={effects}>
            <CarContextProvider>
              <Header items={items} />
              <Toaster position="top-left" />
              {children}
            </CarContextProvider>
          </StaticDataContextProvider>
        </AuthContextProvider>
      </body>
    </html>
  );
}
