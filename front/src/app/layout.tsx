import Header from "./components/Header";
import "./styles.css";
import "./globals.css";
import { StaticDataContextProvider } from "./components/StaticDataContext";
import { AuthContextProvider } from "./components/AuthContext";
import { CarContextProvider } from "./components/CarContext";
import { Toaster } from "react-hot-toast";
import { redirect } from "next/navigation";
import { LoadingProvider } from "./components/LoadingRequestContext";
import ErrorBoundary from "./components/ErrorBoundary";
import { loadStaticData } from "./staticDataLoader";

export const metadata = {
  title: "Legends Shop",
};

export default async function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  let items = [];
  let tags = [];
  let effects = [];
  let locations = [];
  try {
    const data = await loadStaticData(true);
    items = data.items;
    tags = data.tags;
    effects = data.effects;
    locations = data.locations;
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
