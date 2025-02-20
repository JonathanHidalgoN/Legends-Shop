import Header from "./components/Header";
import "./styles.css"
import "./globals.css";
import { Item } from "./interfaces/Item";
import { fetchItems, fetchTags } from "./itemsFetcher";
import { StaticDataContextProvider } from "./components/StaticDataContext";

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
        <StaticDataContextProvider items={items} tags={tags}>
          <Header />
          {children}
        </StaticDataContextProvider>
      </body>
    </html>
  );
}
