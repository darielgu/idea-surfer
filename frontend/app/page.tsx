"use client";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Search, ChevronDown } from "lucide-react";
import Image from "next/image";
import Link from "next/link";
import { useState } from "react";
import axios from "axios";

export default function Home() {
  // load backend url from env variable
  const BACKEND_URL =
    process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

  // State variables
  const [searchQuery, setSearchQuery] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showFilters, setShowFilters] = useState(false);
  const [selectedFilters, setSelectedFilters] = useState<{
    yc?: boolean;
    a16z?: boolean;
    devpost?: boolean;
  }>({});

  // Search handler
  async function handleSearch(searchQuery: string) {
    setLoading(true);
    try {
      const response = await axios.get(`${BACKEND_URL}/search`, {
        params: { query: searchQuery },
      });
      setResults(response.data);
    } catch (error) {
      console.error("Error fetching search results:", error);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="relative min-h-screen w-full overflow-hidden bg-background">
      <div className="absolute inset-0 bg-grid pointer-events-none" />
      {/* Top Left Logo */}
      <div className="absolute z-15">
        <Link href="/">
          <Image
            src="/assets/ideaSurf-removebg.png"
            alt="IdeaSurf Logo"
            width={160}
            height={100}
            className="ml-2 mt-.5"
          ></Image>
        </Link>
      </div>
      {/* Main Heading */}
      <div className="relative z-10 flex flex-col items-center justify-center min-h-screen px-4 py-8">
        <h1 className="mb-4 text-center text-5xl md:text-7xl font-bold tracking-tight text-balance">
          IdeaSurf
        </h1>

        {/* Subheading */}
        <p className="mb-12 max-w-2xl text-center text-lg md:text-xl text-muted-foreground text-balance">
          Discover what people are building.
        </p>

        {/* Search Bar */}
        <div className="w-full max-w-2xl mb-8">
          {/* <div className="flex flex-row"> */}
          <form className="flex flex-row">
            <div className="relative w-full">
              <Input
                type="text"
                placeholder="Search projects, companies, or keywords..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="bg-white w-full px-4 py-3 text-lg rounded-lg border border-muted-foreground focus:border-foreground focus:ring-2 focus:ring-foreground transition"
              />

              {/* Dropdown icon placed on right end of input */}
              <button
                type="button"
                aria-label="Toggle filters"
                onClick={() => setShowFilters((s) => !s)}
                className="absolute inset-y-0 right-0 mr-2 flex items-center rounded-md px-2 text-muted-foreground hover:text-foreground"
              >
                <ChevronDown />
              </button>

              {/* Filters menu */}
              {showFilters && (
                <div className="absolute right-0 left-0 mt-2 z-20 w-full max-w-sm rounded-md border bg-white p-3 shadow-md">
                  <div className="flex flex-col gap-2 text-sm text-foreground">
                    <label className="inline-flex items-center gap-2">
                      <input
                        type="checkbox"
                        checked={!!selectedFilters.yc}
                        onChange={(e) =>
                          setSelectedFilters((prev) => ({
                            ...prev,
                            yc: e.target.checked,
                          }))
                        }
                      />
                      YC
                    </label>

                    <label className="inline-flex items-center gap-2">
                      <input
                        type="checkbox"
                        checked={!!selectedFilters.a16z}
                        onChange={(e) =>
                          setSelectedFilters((prev) => ({
                            ...prev,
                            a16z: e.target.checked,
                          }))
                        }
                      />
                      A16z
                    </label>

                    <label className="inline-flex items-center gap-2">
                      <input
                        type="checkbox"
                        checked={!!selectedFilters.devpost}
                        onChange={(e) =>
                          setSelectedFilters((prev) => ({
                            ...prev,
                            devpost: e.target.checked,
                          }))
                        }
                      />
                      Devpost
                    </label>
                  </div>
                </div>
              )}
            </div>

            <Button className="ml-1 ">
              <Search />
            </Button>
          </form>
        </div>
      </div>
    </main>
  );
}
