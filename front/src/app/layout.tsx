import Header from "./components/Header";
import "./styles.css"
import "./globals.css";
import { Item } from "./interfaces/Item";
import { fetchItems, fetchTags } from "./itemsFetcher";
import { StaticDataContextProvider } from "./components/StaticDataContext";
import { AuthContextProvider } from "./components/AuthContext";
import { CarContextProvider } from "./components/CarContext";

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
  try {
    items = await fetchItems();
    tags = await fetchTags();
  } catch (error) {
    console.log(error);
  }

  return (
    <html lang="en">
      <body>
        <AuthContextProvider>
          <StaticDataContextProvider items={items} tags={tags}>
            <CarContextProvider>
              <Header items={items} />
              {children}
            </CarContextProvider>
          </StaticDataContextProvider>
        </AuthContextProvider>
      </body>
    </html>
  );
}
