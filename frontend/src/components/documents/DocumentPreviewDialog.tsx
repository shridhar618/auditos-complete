import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Skeleton } from "@/components/ui/skeleton";
import { useDocument } from "@/hooks/useDocuments";

export function DocumentPreviewDialog({ id, open, onOpenChange }: { id: string | null; open: boolean; onOpenChange: (open: boolean) => void }) {
  const { data, isLoading } = useDocument(open ? id ?? undefined : undefined);

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>{data?.original_filename ?? "Document preview"}</DialogTitle>
        </DialogHeader>
        <div className="max-h-[60vh] overflow-y-auto rounded-md bg-muted p-4 text-sm scrollbar-thin">
          {isLoading ? (
            <div className="space-y-2">
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-3/4" />
            </div>
          ) : data?.processing_error ? (
            <p className="text-muted-foreground">{data.processing_error}</p>
          ) : (
            <pre className="whitespace-pre-wrap font-sans text-sm">{data?.extracted_text || "No text extracted."}</pre>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}
