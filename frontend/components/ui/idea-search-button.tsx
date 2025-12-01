"use client";
import { Button } from "@/components/ui/button";
import { Search } from "lucide-react";

export function IdeaSearchButton() {
  return (
    <Button
      variant="outline"
      className="gap-2"
      onClick={() => {
        // Scroll to search or focus search input
        const searchInput = document.querySelector('input[type="text"][placeholder*="Search"]') as HTMLInputElement;
        if (searchInput) {
          searchInput.focus();
          searchInput.scrollIntoView({ behavior: "smooth", block: "center" });
        }
      }}>
      <Search className="size-4" />
      Idea Search
    </Button>
  );
}

