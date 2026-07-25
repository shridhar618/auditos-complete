import { Loader2, Upload } from "lucide-react";
import { useRef, useState } from "react";

import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { NativeSelect } from "@/components/ui/native-select";
import { useUploadDocument } from "@/hooks/useDocuments";
import type { DocumentCategory } from "@/types/document";

const CATEGORY_OPTIONS: { value: DocumentCategory; label: string }[] = [
  { value: "invoice", label: "Invoice" },
  { value: "purchase_order", label: "Purchase Order" },
  { value: "contract", label: "Contract" },
  { value: "bank_statement", label: "Bank Statement" },
  { value: "email", label: "Email" },
  { value: "other", label: "Other" },
];

export function UploadDocumentDialog() {
  const [open, setOpen] = useState(false);
  const [category, setCategory] = useState<DocumentCategory>("invoice");
  const [file, setFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const upload = useUploadDocument();

  const handleSubmit = async () => {
    if (!file) return;
    await upload.mutateAsync({ file, category });
    setFile(null);
    setOpen(false);
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button>
          <Upload className="h-4 w-4" />
          Upload Document
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Upload a document</DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
          <div className="space-y-2">
            <Label>Document type</Label>
            <NativeSelect value={category} onChange={(e) => setCategory(e.target.value as DocumentCategory)}>
              {CATEGORY_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </NativeSelect>
          </div>

          <div className="space-y-2">
            <Label>File (PDF, DOCX, TXT, or CSV)</Label>
            <button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              className="flex w-full flex-col items-center justify-center rounded-md border-2 border-dashed border-border p-6 text-sm text-muted-foreground transition-colors hover:border-primary hover:text-primary"
            >
              <Upload className="mb-2 h-5 w-5" />
              {file ? file.name : "Click to choose a file"}
            </button>
            <input
              ref={fileInputRef}
              type="file"
              className="hidden"
              accept=".pdf,.docx,.txt,.csv,.md"
              onChange={(e) => setFile(e.target.files?.[0] ?? null)}
            />
          </div>

          {upload.isError && <p className="text-sm text-destructive">Upload failed. Please try again.</p>}

          <Button className="w-full" onClick={handleSubmit} disabled={!file || upload.isPending}>
            {upload.isPending && <Loader2 className="h-4 w-4 animate-spin" />}
            Upload
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
