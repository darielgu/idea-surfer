"use client";
import React from "react";
import { useState } from "react";
import Link from "next/link";
import { ArrowRight, Badge } from "lucide-react";
import { Dialog } from "@radix-ui/react-dialog";
import { ProjectModal } from "@/components/ui/projectmodal";
export type Project = {
  id: number;
  name: string;
  short_description: string;
  long_description: string;
  source: string;
  tags: string[];
  metadata: { [key: string]: any };
  url: string;
  similarity: number;
};
const ProjectCard = ({ project }: { project: Project }) => {
  const [open, setOpen] = useState(false);
  return (
    <>
      <div
        onClick={() => setOpen(!open)}
        key={project.id}
        className="group relative flex flex-col gap-1 rounded-lg border border-border bg-card p-6 transition-all duration-200 hover:shadow-md hover:border-border/80 focus-visible:ring-2 focus-visible:ring-ring focus-visible:outline-none hover:cursor-pointer">
        <h2 className="text-xl font-semibold mb-2">{project.name}</h2>
        <p className="text-sm text-muted-foreground mb-4">
          {project.short_description}
        </p>

        {/* Tags Section */}
        <div className="flex flex-wrap gap-2">
          {project.tags.slice(0, 3).map((tag, i) => (
            <div
              key={`${tag}-${i}`}
              className="text-xs font-medium bg-muted text-muted-foreground hover:bg-muted px-2 py-1 rounded-md">
              {tag}
            </div>
          ))}
          {project.tags.length > 3 && (
            <div className="text-xs font-medium bg-muted text-muted-foreground hover:bg-muted px-2 py-1 rounded-md">
              +{project.tags.length - 3}
            </div>
          )}
        </div>
        <br />
        {/* Footer Section - Source and Action */}
        <div className="flex items-center justify-between gap-3 pt-2 border-t border-border/50">
          <span className="text-xs text-muted-foreground font-medium">
            {project.source}
          </span>
          <span className="flex items-center gap-1 text-sm font-medium text-muted-foreground">
            {project.similarity.toFixed(2)}% Similarity
          </span>
          <ArrowRight className="size-4 text-muted-foreground group-hover:text-foreground transition-colors" />
        </div>
      </div>
      {open && (
        <ProjectModal project={project} open={open} onOpenChange={setOpen} />
      )}
    </>
  );
};

export default ProjectCard;
