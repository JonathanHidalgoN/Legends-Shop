"use client";

import { useEffect, useState } from "react";
import Image from "next/image";
import Link from "next/link";
import { getChampionIconsRequest } from "./request";

interface ImageItem {
  src: string;
  alt: string;
}

export default function Home() {
  const [mounted, setMounted] = useState(false);
  const [championImages, setChampionImages] = useState<ImageItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    setMounted(true);

    const fetchChampionIcons = async () => {
      try {
        setIsLoading(true);
        const data = await getChampionIconsRequest();
        setChampionImages(data);
      } catch (error) {
        console.error("Error fetching champion icons:", error);
        setChampionImages([]);
      } finally {
        setIsLoading(false);
      }
    };

    fetchChampionIcons();
  }, []);

  if (!mounted) return null;

  return (
    <main className="min-h-screen bg-[var(--white)] text-[var(--black)] overflow-hidden relative z-0">
      {/* Background Pattern */}
      <div className="absolute inset-0 opacity-5">
        <div
          className="absolute inset-0"
          style={{
            backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ff8c00' fill-opacity='1'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
          }}
        />
      </div>

      <div className="container mx-auto px-4 py-8 relative">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-center min-h-[calc(100vh-4rem)]">
          {/* Left Side - Text Content */}
          <div className="space-y-6 animate-fade-in">
            <h1 className="text-5xl md:text-6xl font-bold text-[var(--orange)] animate-slide-up">
              Legends Shop
            </h1>
            <p className="text-xl md:text-2xl text-[var(--black)] animate-slide-up-delayed">
              Where champions come to gear up for battle
            </p>
            <p className="text-lg text-gray-600 animate-slide-up-more-delayed">
              Discover the finest items from across Runeterra. From legendary
              weapons to mystical artifacts, find everything you need to
              dominate the battlefield.
            </p>
            <div className="pt-4 animate-slide-up-more-delayed">
              <Link
                href="/items"
                className="inline-block bg-[var(--orange)] text-white px-8 py-3 rounded-lg text-lg font-semibold hover:bg-opacity-90 transition-all duration-300 transform hover:scale-105"
              >
                Browse Items
              </Link>
            </div>
          </div>

          <div className="relative h-[600px] animate-fade-in">
            <div className="absolute top-0 left-0 w-full h-full">
              {isLoading ? (
                <div className="flex justify-center items-center h-full">
                  <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-[var(--orange)]"></div>
                </div>
              ) : championImages.length > 0 ? (
                championImages.slice(0, 10).map((image, index) => {
                  const positions = [
                    { top: "5%", left: "10%" },
                    { top: "5%", left: "40%" },
                    { top: "5%", left: "70%" },
                    { top: "40%", left: "10%" },
                    { top: "20%", left: "20%" },
                    { top: "40%", left: "70%" },
                    { top: "75%", left: "10%" },
                    { top: "75%", left: "40%" },
                    { top: "75%", left: "70%" },
                    { top: "75%", left: "90%" },
                  ];
                  const position = positions[index];

                  return (
                    <div
                      key={image.src}
                      className="absolute animate-float"
                      style={position}
                    >
                      <Image
                        src={image.src}
                        alt={image.alt}
                        width={100}
                        height={100}
                        className="rounded-full border-2 border-[var(--orange)] shadow-lg"
                      />
                    </div>
                  );
                })
              ) : (
                <div className="flex justify-center items-center h-full">
                  <p className="text-gray-500">No champion icons available</p>
                </div>
              )}
            </div>

            {/* Item Showcase */}
            <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 grid grid-cols-3 gap-4">
              <div className="animate-float">
                <Image
                  src="/hd_images/Rabadon's Deathcap.png"
                  alt="Rabadon's Deathcap"
                  width={80}
                  height={80}
                  className="rounded-lg shadow-lg"
                />
              </div>
              <div className="animate-float-delayed">
                <Image
                  src="/hd_images/Black Cleaver.png"
                  alt="Black Cleaver"
                  width={80}
                  height={80}
                  className="rounded-lg shadow-lg"
                />
              </div>
              <div className="animate-float-more-delayed">
                <Image
                  src="/hd_images/Guardian Angel.png"
                  alt="Guardian Angel"
                  width={80}
                  height={80}
                  className="rounded-lg shadow-lg"
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Add custom animations to global CSS */}
      <style jsx global>{`
        @keyframes float {
          0%,
          100% {
            transform: translateY(0);
          }
          50% {
            transform: translateY(-20px);
          }
        }

        @keyframes fadeIn {
          from {
            opacity: 0;
          }
          to {
            opacity: 1;
          }
        }

        @keyframes slideUp {
          from {
            transform: translateY(20px);
            opacity: 0;
          }
          to {
            transform: translateY(0);
            opacity: 1;
          }
        }

        .animate-float {
          animation: float 6s ease-in-out infinite;
        }

        .animate-float-delayed {
          animation: float 6s ease-in-out infinite;
          animation-delay: 1s;
        }

        .animate-float-more-delayed {
          animation: float 6s ease-in-out infinite;
          animation-delay: 2s;
        }

        .animate-fade-in {
          animation: fadeIn 1s ease-out;
        }

        .animate-slide-up {
          animation: slideUp 0.8s ease-out;
        }

        .animate-slide-up-delayed {
          animation: slideUp 0.8s ease-out;
          animation-delay: 0.2s;
        }

        .animate-slide-up-more-delayed {
          animation: slideUp 0.8s ease-out;
          animation-delay: 0.4s;
        }
      `}</style>
    </main>
  );
}
