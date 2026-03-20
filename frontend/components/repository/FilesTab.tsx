"use client"

import { useEffect, useState } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Input } from "@/components/ui/input"
import { fileApi, type File, type FileExplanation } from "@/lib/api"
import { Loader2, FileText, Search } from "lucide-react"
import FileViewer from "./FileViewer"

interface FilesTabProps {
  repositoryId: number
}

export default function RepositoryFilesTab({ repositoryId }: FilesTabProps) {
  const [files, setFiles] = useState<File[]>([])
  const [filteredFiles, setFilteredFiles] = useState<File[]>([])
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [fileExplanation, setFileExplanation] = useState<FileExplanation | null>(null)
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState("")
  const [loadingExplanation, setLoadingExplanation] = useState(false)

  useEffect(() => {
    loadFiles()
  }, [repositoryId])

  useEffect(() => {
    if (searchQuery) {
      const filtered = files.filter(
        (file) =>
          file.path.toLowerCase().includes(searchQuery.toLowerCase()) ||
          file.name.toLowerCase().includes(searchQuery.toLowerCase())
      )
      setFilteredFiles(filtered)
    } else {
      setFilteredFiles(files)
    }
  }, [searchQuery, files])

  const loadFiles = async () => {
    try {
      setLoading(true)
      const data = await fileApi.list(repositoryId)
      setFiles(data)
      setFilteredFiles(data)
    } catch (error) {
      console.error("Failed to load files:", error)
    } finally {
      setLoading(false)
    }
  }

  const handleFileSelect = async (file: File) => {
    setSelectedFile(file)
    setFileExplanation(null)
    setLoadingExplanation(true)

    try {
      const explanation = await fileApi.explain(repositoryId, file.path)
      setFileExplanation(explanation)
    } catch (error) {
      console.error("Failed to load file explanation:", error)
    } finally {
      setLoadingExplanation(false)
    }
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    )
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-[600px]">
      <Card className="lg:col-span-1">
        <CardContent className="p-0 h-full flex flex-col">
          <div className="p-4 border-b">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search files..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-9"
              />
            </div>
          </div>
          <ScrollArea className="flex-1">
            <div className="p-2">
              {filteredFiles.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground text-sm">
                  No files found
                </div>
              ) : (
                <div className="space-y-1">
                  {filteredFiles.map((file) => (
                    <button
                      key={file.id}
                      onClick={() => handleFileSelect(file)}
                      className={`w-full text-left px-3 py-2 rounded-md text-sm hover:bg-accent transition-colors ${
                        selectedFile?.id === file.id ? "bg-accent" : ""
                      }`}
                    >
                      <div className="flex items-center gap-2">
                        <FileText className="h-4 w-4 text-muted-foreground" />
                        <span className="truncate font-mono text-xs">{file.name}</span>
                      </div>
                      <div className="text-xs text-muted-foreground truncate ml-6">
                        {file.path}
                      </div>
                    </button>
                  ))}
                </div>
              )}
            </div>
          </ScrollArea>
        </CardContent>
      </Card>

      <Card className="lg:col-span-2">
        <CardContent className="p-0 h-full">
          {selectedFile ? (
            <FileViewer
              file={selectedFile}
              explanation={fileExplanation}
              loading={loadingExplanation}
            />
          ) : (
            <div className="h-full flex items-center justify-center text-muted-foreground">
              Select a file to view its explanation
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}







