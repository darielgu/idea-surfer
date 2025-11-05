"use client";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Search } from "lucide-react";
import Image from "next/image";
import Link from "next/link";
import { useState } from "react";

export default function Home() {
  const [searchQuery, setSearchQuery] = useState("");
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
      <div className="relative z-10 flex flex-col items-center justify-center min-h-screen px-4 py-8">
        {/* Main Heading */}
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
            <Input
              type="text"
              placeholder="Search projects, companies, or keywords..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="bg-white w-full px-4 py-3 text-lg rounded-lg border border-muted-foreground focus:border-foreground focus:ring-2 focus:ring-foreground transition"
            />
            <Button className="ml-1 ">
              <Search />
            </Button>
          </form>
          <div className="mt-4 flex justify-center">
            <Button>Filters</Button>
          </div>
          {/* </div> */}
        </div>
      </div>
    </main>
  );
}
