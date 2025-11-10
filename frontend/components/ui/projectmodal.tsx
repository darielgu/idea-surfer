"use client";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogClose,
} from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { X, ExternalLink } from "lucide-react";
import type { Project } from "./projectcard";

interface ProjectDetailModalProps {
  project: Project;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function ProjectModal({
  project,
  open,
  onOpenChange,
}: ProjectDetailModalProps) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-6xl max-w-[calc(100%-1rem)] max-h-[90vh] overflow-y-auto">
        {/* Header with close button */}
        <DialogHeader className="flex flex-row items-start justify-between space-y-0 pb-4 border-b border-border">
          <div className="flex-1">
            <DialogTitle className="text-2xl font-bold text-foreground">
              {project.name}
            </DialogTitle>
            {project.source && (
              <p className="text-sm text-muted-foreground mt-2">
                Source: {project.source}
              </p>
            )}
          </div>
          <DialogClose className="rounded-md opacity-70 ring-offset-background transition-opacity hover:opacity-100 focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:pointer-events-none"></DialogClose>
        </DialogHeader>

        {/* Modal Content */}
        <div className="space-y-6 py-4">
          {/* Description Section */}
          <div>
            <h3 className="text-sm font-semibold text-foreground mb-2">
              Overview
            </h3>
            <p className="text-base leading-relaxed text-foreground">
              {project.long_description
                ? project.long_description
                : project.short_description}
            </p>
          </div>

          {/* Tags Section */}
          <div>
            <h3 className="text-sm font-semibold text-foreground mb-3">
              Technologies & Tags
            </h3>
            <div className="flex flex-wrap gap-2">
              {project.tags.map((tag) => (
                <Badge
                  key={tag}
                  variant="secondary"
                  className="text-xs font-medium bg-gradient-to-r from-blue-500/20 to-purple-500/20 hover:from-blue-500/30 hover:to-purple-500/30"
                >
                  {tag}
                </Badge>
              ))}
            </div>
          </div>

          {/* Additional metadata - can be extended */}
          <h3 className="text-sm font-semibold text-foreground mb-3">
            Project Metadata
          </h3>
          <div className="bg-muted/50 rounded-lg p-4 space-y-3">
            <div>
              <h4 className="text-xs font-semibold text-muted-foreground uppercase mb-1">
                Project ID
              </h4>
              <p className="text-sm text-foreground font-mono">
                {project.id || "N/A"}
              </p>
            </div>

            <div>
              {project.metadata &&
                Object.entries(project.metadata).map(([key, value]) => (
                  <div key={key} className="mt-2">
                    <h4 className="text-xs font-semibold text-muted-foreground uppercase mb-1">
                      {key.replace(/_/g, " ")}
                    </h4>
                    <p className="text-sm text-foreground">{value}</p>
                  </div>
                ))}
            </div>
          </div>

          {/* Action buttons */}
          <div className="flex gap-3 pt-4">
            {project.url && (
              <Button asChild className="flex-1 gap-2">
                <a href={project.url} target="_blank" rel="noopener noreferrer">
                  <ExternalLink className="size-4" />
                  Visit Project
                </a>
              </Button>
            )}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
