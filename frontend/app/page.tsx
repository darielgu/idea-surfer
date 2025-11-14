"use client";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Search, ChevronDown } from "lucide-react";
import Image from "next/image";
import Link from "next/link";
import { useState, useRef, useEffect } from "react";
import axios from "axios";
import { useRouter } from "next/navigation";

export default function Home() {
  // Declare Router & mount
  const router = useRouter();

  // load backend url from env variable
  const BACKEND_URL =
    process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

  // State variables
  const [searchQuery, setSearchQuery] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showFilters, setShowFilters] = useState(false);
  const [selectedFilters, setSelectedFilters] = useState<{
    YC?: boolean;
    "Product Hunt"?: boolean;
    Devpost?: boolean;
  }>({});
  // Carousel prompts
  const prompts = [
    "AI CRM Tool",
    "Healthcare and AI",
    "Fintech + AI",
    "AI for Education",
    "Productivity with AI",
    "Generative Design",
    "Music Generation AI",
    "AI for Social Good",
  ];

  const carouselRef = useRef<HTMLDivElement | null>(null);
  const chipRefs = useRef<Array<HTMLButtonElement | null>>([]);
  const [currentIndex, setCurrentIndex] = useState(0);

  // carousel: move to next chip every 3s and center it smoothly

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentIndex((i) => (i + 2) % prompts.length);
    }, 3000);
    return () => clearInterval(interval);
  }, [prompts.length]);

  useEffect(() => {
    const el = chipRefs.current[currentIndex];
    if (el) {
      el.scrollIntoView({
        behavior: "smooth",
        inline: "start",
        block: "nearest",
      });
    }
  }, [currentIndex]);

  // Search handler
  async function handleSearch(searchQuery: string) {
    // If the query is empty or only whitespace, send user back to home
    if (!searchQuery || searchQuery.trim() === "") {
      router.replace("/");
      return;
    }
    const activeFilters = Object.entries(selectedFilters)
      .filter(([_, value]) => value)
      .map(([key, _]) => key);
    const params = new URLSearchParams({ query: searchQuery });
    activeFilters.forEach((f) => params.append("sources", f));

    // set results and navigate to search page providing the search query & results & loading state
    router.push(`/search?${params.toString()}`);
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
            className="ml-2 mt-.5"
            unoptimized></Image>
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
          <form
            className="flex flex-row"
            onSubmit={(e) => {
              e.preventDefault();
              handleSearch(searchQuery);
            }}>
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
                className="absolute inset-y-0 right-0 mr-2 flex items-center rounded-md px-2 text-muted-foreground hover:text-foreground">
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
                aria-hidden={!showFilters}>
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
                      checked={!!selectedFilters["Product Hunt"]}
                      onChange={(e) =>
                        setSelectedFilters((prev) => ({
                          ...prev,
                          "Product Hunt": e.target.checked,
                        }))
                      }
                    />
                    Product Hunt
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

          {/* Prompt carousel (modern horizontal scroller) */}
          <div className="mt-4 flex items-center">
            <div
              ref={carouselRef}
              // remove horizontal padding so width calc for 4 items is accurate
              className="no-scrollbar flex w-full gap-3 overflow-x-auto py-2 snap-x snap-mandatory"
              role="list"
              style={{ scrollPaddingInline: "0" }}>
              {prompts.map((p, idx) => (
                <button
                  key={p}
                  ref={(el) => {
                    chipRefs.current[idx] = el;
                  }}
                  type="button"
                  onClick={() => setSearchQuery(p)}
                  // make each chip a fixed fraction so exactly 4 are visible
                  className="snap-start whitespace-nowrap rounded-full bg-muted-foreground/10 px-4 py-2 text-sm hover:bg-muted-foreground/20 truncate text-center shrink-0"
                  style={{ flex: "0 0 calc((100% - 2.25rem) / 4)" }}>
                  {p}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
