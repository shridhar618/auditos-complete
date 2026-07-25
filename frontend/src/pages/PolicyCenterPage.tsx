import { useRef, useState } from "react";
import { Loader2, Search, ShieldCheck, Sparkles, Upload } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { Input } from "@/components/ui/input";
import { useAuth } from "@/context/AuthContext";
import { useDocuments } from "@/hooks/useDocuments";
import { useSearchPolicies, useUploadPolicyDocument } from "@/hooks/usePolicyCenter";

export default function PolicyCenterPage() {
  const { hasPermission } = useAuth();
  const [query, setQuery] = useState("");
  const fileInputRef = useRef<HTMLInputElement>(null);

  const { data: policyDocuments } = useDocuments("policy");
  const uploadPolicy = useUploadPolicyDocument();
  const search = useSearchPolicies();

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) uploadPolicy.mutate(file);
  };

  const handleSearch = () => {
    if (query.trim()) search.mutate(query.trim());
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Policy Center</h1>
        <p className="text-muted-foreground">
          Upload internal policies, RBI guidelines, SOX, or GST rules. Search them with citations — the same
          engine the Policy Agent uses when reviewing flagged transactions.
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <Card className="lg:col-span-1">
          <CardHeader>
            <CardTitle>Uploaded Policies ({policyDocuments?.length ?? 0})</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {hasPermission("policies:write") && (
              <>
                <Button className="w-full" onClick={() => fileInputRef.current?.click()} disabled={uploadPolicy.isPending}>
                  {uploadPolicy.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Upload className="h-4 w-4" />}
                  Upload Policy Document
                </Button>
                <input ref={fileInputRef} type="file" className="hidden" accept=".pdf,.docx,.txt,.md" onChange={handleFileChange} />
              </>
            )}
            {!policyDocuments || policyDocuments.length === 0 ? (
              <p className="text-sm text-muted-foreground">No policy documents uploaded yet.</p>
            ) : (
              <ul className="space-y-2">
                {policyDocuments.map((doc) => (
                  <li key={doc.id} className="flex items-center gap-2 text-sm">
                    <ShieldCheck className="h-3.5 w-3.5 shrink-0 text-muted-foreground" />
                    <span className="truncate">{doc.original_filename}</span>
                  </li>
                ))}
              </ul>
            )}
          </CardContent>
        </Card>

        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Search Policies</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex gap-2">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  placeholder="e.g. 'expense approval limits' or 'related party transactions'"
                  className="pl-9"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && handleSearch()}
                />
              </div>
              <Button onClick={handleSearch} disabled={search.isPending || !query.trim()}>
                {search.isPending && <Loader2 className="h-4 w-4 animate-spin" />}
                Search
              </Button>
            </div>

            {search.data && (
              <div className="space-y-3">
                <div className="flex items-center gap-2 text-xs text-muted-foreground">
                  {search.data.search_method_used === "semantic" ? (
                    <>
                      <Sparkles className="h-3.5 w-3.5 text-accent" /> Semantic search (embeddings)
                    </>
                  ) : (
                    <>Keyword search (no OPENAI_API_KEY configured, or no embedded matches)</>
                  )}
                </div>

                {search.data.results.length === 0 ? (
                  <EmptyState icon={Search} title="No matches found" description="Try a different phrase, or upload more policy documents." />
                ) : (
                  search.data.results.map((result, i) => (
                    <div key={i} className="rounded-md border border-border p-4">
                      <div className="mb-2 flex items-center gap-2">
                        <ShieldCheck className="h-3.5 w-3.5 text-primary" />
                        <p className="text-sm font-medium">{result.document_name}</p>
                      </div>
                      <p className="text-sm text-muted-foreground">{result.chunk_text}</p>
                    </div>
                  ))
                )}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
