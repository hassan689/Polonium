"use client"

import { useEffect, useState } from "react"
import { useParams } from "next/navigation"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { repositoryApi, fileApi, type Repository, type RepositoryOverview, type File } from "@/lib/api"
import { Loader2, FileText, MessageSquare, Code } from "lucide-react"
import Link from "next/link"
import RepositoryOverviewTab from "@/components/repository/OverviewTab"
import RepositoryFilesTab from "@/components/repository/FilesTab"
import RepositoryChatTab from "@/components/repository/ChatTab"

export default function RepositoryDetailPage() {
  const params = useParams()
  const repositoryId = parseInt(params.id as string)

  const [repository, setRepository] = useState<Repository | null>(null)
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState("overview")

  useEffect(() => {
    loadRepository()
    // Poll for status updates if in progress
    const interval = setInterval(() => {
      if (repository?.status === "in_progress" || repository?.status === "pending") {
        loadRepository()
      }
    }, 3000)
    return () => clearInterval(interval)
  }, [repositoryId])

  const loadRepository = async () => {
    try {
      const data = await repositoryApi.get(repositoryId)
      setRepository(data)
      if (data.status === "completed" && activeTab === "overview") {
        // Auto-load overview when ready
      }
    } catch (error) {
      console.error("Failed to load repository:", error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex justify-center items-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        </div>
      </div>
    )
  }

  if (!repository) {
    return (
      <div className="container mx-auto px-4 py-8">
        <Card>
          <CardContent className="py-12 text-center">
            <p className="text-muted-foreground">Repository not found</p>
            <Link href="/repositories" className="text-primary hover:underline mt-4 inline-block">
              Back to repositories
            </Link>
          </CardContent>
        </Card>
      </div>
    )
  }

  const getStatusColor = (status: Repository["status"]) => {
    switch (status) {
      case "completed":
        return "text-green-600"
      case "in_progress":
        return "text-blue-600"
      case "failed":
        return "text-red-600"
      default:
        return "text-gray-600"
    }
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-6">
        <Link href="/repositories" className="text-sm text-muted-foreground hover:text-foreground mb-2 inline-block">
          ← Back to repositories
        </Link>
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold mb-2">{repository.github_full_name}</h1>
            {repository.github_description && (
              <p className="text-muted-foreground">{repository.github_description}</p>
            )}
          </div>
          <div className="text-right">
            <div className={`text-sm font-medium ${getStatusColor(repository.status)}`}>
              {repository.status === "completed" ? "Ready" : 
               repository.status === "in_progress" ? "Processing..." :
               repository.status === "failed" ? "Failed" : "Pending"}
            </div>
            {repository.status === "completed" && (
              <div className="text-xs text-muted-foreground mt-1">
                {repository.total_files} files
              </div>
            )}
          </div>
        </div>
      </div>

      {repository.status === "completed" ? (
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="overview">
              <FileText className="mr-2 h-4 w-4" />
              Overview
            </TabsTrigger>
            <TabsTrigger value="files">
              <Code className="mr-2 h-4 w-4" />
              Files
            </TabsTrigger>
            <TabsTrigger value="chat">
              <MessageSquare className="mr-2 h-4 w-4" />
              Chat
            </TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="mt-6">
            <RepositoryOverviewTab repositoryId={repositoryId} />
          </TabsContent>

          <TabsContent value="files" className="mt-6">
            <RepositoryFilesTab repositoryId={repositoryId} />
          </TabsContent>

          <TabsContent value="chat" className="mt-6">
            <RepositoryChatTab repositoryId={repositoryId} />
          </TabsContent>
        </Tabs>
      ) : repository.status === "in_progress" ? (
        <Card>
          <CardContent className="py-12 text-center">
            <Loader2 className="h-8 w-8 animate-spin text-muted-foreground mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">Processing Repository</h3>
            <p className="text-muted-foreground">
              Fetching files, generating embeddings, and creating AI overview...
              This may take a few minutes.
            </p>
          </CardContent>
        </Card>
      ) : (
        <Card>
          <CardContent className="py-12 text-center">
            <p className="text-muted-foreground">
              {repository.status === "failed" 
                ? "Repository processing failed. Please try again."
                : "Repository is pending processing."}
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  )
}


