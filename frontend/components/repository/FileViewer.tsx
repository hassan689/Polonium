"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Separator } from "@/components/ui/separator"
import { type File, type FileExplanation } from "@/lib/api"
import { Loader2, Code2, FileText } from "lucide-react"
import Editor from "@monaco-editor/react"

interface FileViewerProps {
  file: File
  explanation: FileExplanation | null
  loading: boolean
}

export default function FileViewer({ file, explanation, loading }: FileViewerProps) {
  const getLanguage = (extension: string | null) => {
    if (!extension) return "plaintext"
    const langMap: Record<string, string> = {
      ".py": "python",
      ".js": "javascript",
      ".ts": "typescript",
      ".jsx": "javascript",
      ".tsx": "typescript",
      ".java": "java",
      ".go": "go",
      ".rs": "rust",
      ".cpp": "cpp",
      ".c": "c",
      ".cs": "csharp",
      ".php": "php",
      ".rb": "ruby",
      ".swift": "swift",
      ".kt": "kotlin",
      ".html": "html",
      ".css": "css",
      ".sql": "sql",
      ".sh": "shell",
      ".yaml": "yaml",
      ".yml": "yaml",
      ".json": "json",
      ".md": "markdown",
    }
    return langMap[extension.toLowerCase()] || "plaintext"
  }

  return (
    <div className="h-full flex flex-col">
      <div className="p-4 border-b">
        <div className="flex items-center gap-2 mb-1">
          <FileText className="h-4 w-4" />
          <h3 className="font-semibold font-mono text-sm">{file.path}</h3>
        </div>
        <div className="text-xs text-muted-foreground">
          {file.language || "Unknown"} • {file.line_count?.toLocaleString() || 0} lines •{" "}
          {(file.size_bytes / 1024).toFixed(2)} KB
        </div>
      </div>

      <ScrollArea className="flex-1">
        <div className="p-4 space-y-4">
          {loading ? (
            <div className="flex justify-center items-center py-8">
              <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
            </div>
          ) : explanation ? (
            <>
              <Card>
                <CardHeader>
                  <CardTitle className="text-base">AI Explanation</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground whitespace-pre-wrap">
                    {explanation.explanation}
                  </p>
                </CardContent>
              </Card>

              {explanation.purpose && (
                <Card>
                  <CardHeader>
                    <CardTitle className="text-base">Purpose</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-muted-foreground">{explanation.purpose}</p>
                  </CardContent>
                </Card>
              )}

              {explanation.key_functions && explanation.key_functions.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle className="text-base">Key Functions</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ul className="space-y-1">
                      {explanation.key_functions.map((func, index) => (
                        <li key={index} className="text-sm font-mono text-muted-foreground">
                          • {func}
                        </li>
                      ))}
                    </ul>
                  </CardContent>
                </Card>
              )}

              {explanation.dependencies && explanation.dependencies.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle className="text-base">Dependencies</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ul className="space-y-1">
                      {explanation.dependencies.map((dep, index) => (
                        <li key={index} className="text-sm text-muted-foreground">
                          • {dep}
                        </li>
                      ))}
                    </ul>
                  </CardContent>
                </Card>
              )}
            </>
          ) : null}
        </div>
      </ScrollArea>
    </div>
  )
}

