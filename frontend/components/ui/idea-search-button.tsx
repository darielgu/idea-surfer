"use client";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Search } from "lucide-react";
import { IdeaChatbot } from "@/components/ui/idea-chatbot";

export function IdeaSearchButton() {
  const [chatbotOpen, setChatbotOpen] = useState(false);

  return (
    <>
      <Button
        variant="outline"
        className="gap-2"
        onClick={() => setChatbotOpen(true)}>
        <Search className="size-4" />
        Idea Search
      </Button>
      <IdeaChatbot open={chatbotOpen} onOpenChange={setChatbotOpen} />
    </>
  );
}

