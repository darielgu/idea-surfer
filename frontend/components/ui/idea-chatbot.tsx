"use client";
import { useState, useRef, useEffect } from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Send, Bot, User } from "lucide-react";
import axios from "axios";

interface Message {
  role: "user" | "assistant";
  content: string;
}

interface IdeaChatbotProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function IdeaChatbot({ open, onOpenChange }: IdeaChatbotProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content: "Hi! I'm your startup consultant with access to a database of all current ideas being pursued. Tell me about your idea and I can help you put it together!",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const BACKEND_URL =
    process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMessage: Message = {
      role: "user",
      content: input.trim(),
    };

    // Add user message immediately
    setMessages((prev) => [...prev, userMessage]);
    const userInput = input.trim();
    setInput("");
    setLoading(true);

    try {
      // Prepare messages for API (include all previous messages)
      const apiMessages = [...messages, userMessage].map((msg) => ({
        role: msg.role,
        content: msg.content,
      }));

      // Check if user wants to search for similar ideas
      // Look for affirmative responses or explicit requests
      const lowerInput = userInput.toLowerCase();
      const shouldSearch = 
        lowerInput.includes("yes") ||
        lowerInput.includes("check") ||
        lowerInput.includes("search") ||
        lowerInput.includes("similar") ||
        lowerInput.includes("taken") ||
        lowerInput.includes("already") ||
        lowerInput.includes("sure") ||
        lowerInput.includes("please") ||
        lowerInput.includes("do it") ||
        lowerInput.includes("go ahead");

      // Extract the idea query - find the first substantial idea description
      let ideaQuery = "";
      if (shouldSearch) {
        // Find the first substantial idea description from user messages
        // Look through all previous user messages to find the idea
        for (let i = 0; i < messages.length; i++) {
          if (messages[i].role === "user") {
            const msgContent = messages[i].content;
            // If it's a substantial message (not just "yes", "check", etc.) and describes an idea
            if (msgContent.length > 20 && 
                !msgContent.toLowerCase().match(/^(yes|check|search|sure|please|do it|go ahead)/)) {
              ideaQuery = msgContent;
              break;
            }
          }
        }
        // If no previous idea found and current message is substantial (not just affirmation), use it
        if (!ideaQuery && userInput.length > 20) {
          const isJustAffirmation = /^(yes|check|search|sure|please|do it|go ahead)/i.test(userInput);
          if (!isJustAffirmation) {
            ideaQuery = userInput;
          }
        }
      }

      const response = await axios.post(`${BACKEND_URL}/chat/`, {
        messages: apiMessages,
        search_similar: shouldSearch && ideaQuery.length > 0,
        idea_query: ideaQuery,
      });

      const assistantMessage: Message = {
        role: "assistant",
        content: response.data.message,
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error("Error sending message:", error);
      const errorMessage: Message = {
        role: "assistant",
        content: "Sorry, I encountered an error. Please try again.",
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-2xl max-w-[calc(100%-1rem)] h-[80vh] flex flex-col p-0">
        <DialogHeader className="px-6 pt-6 pb-4 border-b">
          <DialogTitle className="flex items-center gap-2">
            <Bot className="size-5" />
            Idea Assistant
          </DialogTitle>
          <DialogDescription>
            Get help developing your startup idea and check if similar ideas already exist.
          </DialogDescription>
        </DialogHeader>

        {/* Messages Container */}
        <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
          {messages.map((message, index) => (
            <div
              key={index}
              className={`flex gap-3 ${
                message.role === "user" ? "justify-end" : "justify-start"
              }`}>
              {message.role === "assistant" && (
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
                  <Bot className="size-4 text-primary" />
                </div>
              )}
              <div
                className={`max-w-[80%] rounded-lg px-4 py-2 ${
                  message.role === "user"
                    ? "bg-primary text-primary-foreground"
                    : "bg-muted text-foreground"
                }`}>
                <p className="text-sm whitespace-pre-wrap">{message.content}</p>
              </div>
              {message.role === "user" && (
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
                  <User className="size-4 text-primary" />
                </div>
              )}
            </div>
          ))}
          {loading && (
            <div className="flex gap-3 justify-start">
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
                <Bot className="size-4 text-primary" />
              </div>
              <div className="bg-muted rounded-lg px-4 py-2">
                <div className="flex gap-1">
                  <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce" />
                  <div
                    className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce"
                    style={{ animationDelay: "0.2s" }}
                  />
                  <div
                    className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce"
                    style={{ animationDelay: "0.4s" }}
                  />
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Container */}
        <div className="border-t px-6 py-4">
          <div className="flex gap-2">
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Type your idea here..."
              disabled={loading}
              className="flex-1"
            />
            <Button
              onClick={handleSend}
              disabled={loading || !input.trim()}
              size="icon">
              <Send className="size-4" />
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}

