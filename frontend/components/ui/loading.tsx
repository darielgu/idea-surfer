"use client";

import React, { useEffect, useState } from "react";

type Props = {
  idea?: string;
  /** ms per character */
  speed?: number;
  /** pause between lines in ms */
  pauseBetweenLines?: number;
  className?: string;
};

export default function Loading({
  idea = "your idea",
  speed = 30,
  pauseBetweenLines = 700,
  className = "",
}: Props) {
  const lines = [
    `Parsing your idea: "${idea}"`,
    `Embedding "${idea}" into vector space`,
    `Scanning 5,604 related ideas`,
    `Ranking the most relevant waves for you...`,
  ];

  const [displayed, setDisplayed] = useState<string[]>(() =>
    lines.map(() => "")
  );
  const [currentLine, setCurrentLine] = useState(0);
  const [done, setDone] = useState(false);

  useEffect(() => {
    let mounted = true;

    async function typeAll() {
      for (let i = 0; i < lines.length; i++) {
        setCurrentLine(i);
        const text = lines[i];
        for (let j = 0; j < text.length; j++) {
          if (!mounted) return;
          await new Promise((r) => setTimeout(r, speed));
          setDisplayed((prev) => {
            const copy = [...prev];
            // use slice instead of append to make updates idempotent
            // (prevents duplicated characters if the effect runs more than once)
            copy[i] = text.slice(0, j + 1);
            return copy;
          });
        }
        // small pause after finishing a line
        await new Promise((r) => setTimeout(r, pauseBetweenLines));
      }
      if (mounted) setDone(true);
    }

    typeAll();

    return () => {
      mounted = false;
    };
    // We intentionally don't include `lines` in deps to treat them as constants here.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [speed, pauseBetweenLines]);

  return (
    <div
      className={`text-sm text-muted-foreground ${className}  bg-muted/50 rounded-lg p-4 font-mono text-sm shadow-sm border border-border/50 align-center justify-center mx-auto w-lg`}
    >
      {displayed.map((line, idx) => (
        <p
          key={idx}
          className={`mb-1 wrap-break-word ${
            idx === currentLine ? "text-foreground" : "text-muted-foreground"
          }`}
        >
          {renderLineWithHighlight(line, idea)}
          {idx === currentLine && !done ? (
            <span className="inline-block ml-1 w-0.5 h-4 bg-foreground align-middle animate-pulse" />
          ) : null}
        </p>
      ))}
    </div>
  );
}

/**
 * Helper that highlights occurrences of the idea inside the typed line.
 * It splits the line by the idea (case-sensitive) and wraps the idea in a span
 * with stronger styling so it stands out while typing.
 */
function renderLineWithHighlight(line: string, idea: string) {
  if (!idea) return <>{line}</>;
  const parts = line.split(idea);
  if (parts.length === 1) return <>{line}</>;

  return (
    <>
      {parts.map((part, i) => (
        <React.Fragment key={i}>
          <span className="inline-block">{part}</span>
          {i !== parts.length - 1 ? (
            <span className="inline-block font-medium text-primary">
              {idea}
            </span>
          ) : null}
        </React.Fragment>
      ))}
    </>
  );
}
