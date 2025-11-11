"use client";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Search, ChevronDown } from "lucide-react";
import Image from "next/image";
import Link from "next/link";
import { useState, useEffect } from "react";
import axios from "axios";
import ProjectCard from "@/components/ui/projectcard";
import { useSearchParams } from "next/navigation";
import { useRouter } from "next/navigation";
import Loading from "@/components/ui/loading";

type Project = {
  id: number;
  name: string;
  short_description: string;
  long_description: string;
  url: string;
  source: string;
  tags: string[];
  metadata: { [key: string]: any };
  similarity: number;
};
export default function Home() {
  const router = useRouter();
  const query = useSearchParams().get("query");
  const sources = useSearchParams().getAll("sources");
  // load backend url from env variable
  const BACKEND_URL =
    process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

  // State variables
  const [searchQuery, setSearchQuery] = useState("");
  const [results, setResults] = useState<Project[]>([]);
  const [loading, setLoading] = useState(false);
  const [showFilters, setShowFilters] = useState(false);
  const [selectedFilters, setSelectedFilters] = useState<{
    YC?: boolean;
    a16z?: boolean;
    Devpost?: boolean;
  }>({});

  // Search handler
  useEffect(() => {
    if (query === null) return router.replace("/");
    if (query.trim() === "" || query === " ") {
      router.replace("/");
      return;
    }

    setSearchQuery(query);
    handleSearch(query, sources);
  }, [query]);

  async function handleSearch(searchQuery: string, sources?: string[]) {
    setLoading(true);

    try {
      const response = await axios.get(`${BACKEND_URL}/search/`, {
        params: {
          query: searchQuery,
          ...(sources ? { sources } : {}),
        },
        paramsSerializer: (params) => {
          const searchParams = new URLSearchParams();
          Object.entries(params).forEach(([key, value]) => {
            if (Array.isArray(value))
              value.forEach((v) => searchParams.append(key, v));
            else if (value != null) searchParams.append(key, value as string);
          });
          return searchParams.toString();
        },
      });
      setResults(response.data.results);
      console.log(response.data);
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
            src="/assets/IdeaSurf-removebg.png"
            alt="IdeaSurf Logo"
            width={160}
            height={100}
            className="ml-2 mt-.5 mb-2"
            unoptimized
          ></Image>
        </Link>
      </div>
      {/* Main Heading */}
      <div className="relative z-10 flex flex-col items-center justify-center min-h-screen px-4 py-8">
        <h1 className="mb-4 text-center text-5xl md:text-7xl font-bold tracking-tight text-balance mt-7.5">
          IdeaSurf
        </h1>

        {/* Subheading */}
        <p className="mb-12 max-w-2xl text-center text-lg md:text-xl text-muted-foreground text-balance">
          Discover what people are building.
        </p>

        {/* Search Bar */}
        <div className="w-full max-w-2xl mb-8">
          {/* <div className="flex flex-row"> */}
          <form
            className="flex flex-row"
            onSubmit={(e) => {
              e.preventDefault();
              const q = searchQuery?.trim() ?? "";
              if (q === "") {
                // keep the existing behavior: if empty, go home
                router.replace("/");
                return;
              }
              // update the URL query param which the useEffect listens to
              router.push(`/search?query=${encodeURIComponent(q)}`);
            }}
          >
            <div className="relative w-full">
              <Input
                type="text"
                placeholder="Search ideas or keywords..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="bg-white w-full px-4 py-3 text-lg rounded-lg border border-muted-foreground focus:border-foreground focus:ring-2 focus:ring-foreground transition"
              />

              {/* Dropdown icon placed on right end of input */}
              <button
                type="button"
                aria-label="Toggle filters"
                aria-expanded={showFilters}
                onClick={() => setShowFilters((s) => !s)}
                className="absolute inset-y-0 right-0 mr-2 flex items-center rounded-md px-2 text-muted-foreground hover:text-foreground"
              >
                <ChevronDown
                  className={`transition-transform duration-200 ease-out ${
                    showFilters ? "rotate-180" : "rotate-0"
                  }`}
                />
              </button>

              {/* Filters menu (kept in DOM for smooth transitions) */}
              <div
                className={`absolute right-0 left-0 mt-2 z-20 w-full max-w-sm rounded-md border bg-white p-3 shadow-md origin-top-right transform transition-all duration-200 ease-out ${
                  showFilters
                    ? "opacity-100 translate-y-0 scale-100 pointer-events-auto"
                    : "opacity-0 -translate-y-2 scale-95 pointer-events-none"
                }`}
                aria-hidden={!showFilters}
              >
                <div className="flex flex-col gap-2 text-sm text-foreground">
                  <label className="inline-flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={!!selectedFilters.YC}
                      onChange={(e) =>
                        setSelectedFilters((prev) => ({
                          ...prev,
                          YC: e.target.checked,
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
                      checked={!!selectedFilters.Devpost}
                      onChange={(e) =>
                        setSelectedFilters((prev) => ({
                          ...prev,
                          Devpost: e.target.checked,
                        }))
                      }
                    />
                    Devpost
                  </label>
                </div>
              </div>
            </div>

            <Button className="ml-1 " type="submit">
              <Search />
            </Button>
          </form>
        </div>
        {/* Card Display */}
        <div className="w-full max-w-4xl">
          {loading ? (
            // Loading animation, right out line by line
            <Loading idea={searchQuery} className="mt-4" />
          ) : results.length === 0 ? (
            <p className="text-center text-muted-foreground mt-2">
              Too many requests or no results found for "{searchQuery}". Please
              try again later.
            </p>
          ) : (
            <div className="flex flex-col gap-4">
              {results.map((item: any) => (
                <ProjectCard key={item.id} project={item} />
              ))}
            </div>
          )}
        </div>
      </div>
    </main>
  );
}
