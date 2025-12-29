"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { repositoryApi, type Repository } from "@/lib/api"
import { Loader2, Plus, GitBranch } from "lucide-react"

export default function RepositoriesPage() {
  const [repositories, setRepositories] = useState<Repository[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadRepositories()
  }, [])

  const loadRepositories = async () => {
    try {
      setLoading(true)
      const data = await repositoryApi.list()
      setRepositories(data)
    } catch (error) {
      console.error("Failed to load repositories:", error)
    } finally {
      setLoading(false)
    }
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

  const getStatusLabel = (status: Repository["status"]) => {
    switch (status) {
      case "completed":
        return "Ready"
      case "in_progress":
        return "Processing"
      case "failed":
        return "Failed"
      default:
        return "Pending"
    }
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold mb-2">Repositories</h1>
          <p className="text-muted-foreground">
            Connect and explore GitHub repositories with AI
          </p>
        </div>
        <Link href="/repositories/new">
          <Button>
            <Plus className="mr-2 h-4 w-4" />
            Connect Repository
          </Button>
        </Link>
      </div>

      {loading ? (
        <div className="flex justify-center items-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        </div>
      ) : repositories.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <GitBranch className="h-12 w-12 text-muted-foreground mb-4" />
            <h3 className="text-lg font-semibold mb-2">No repositories yet</h3>
            <p className="text-muted-foreground mb-4">
              Connect your first GitHub repository to get started
            </p>
            <Link href="/repositories/new">
              <Button>Connect Repository</Button>
            </Link>
          </CardContent>
        </Card>
      ) : (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {repositories.map((repo) => (
            <Link key={repo.id} href={`/repositories/${repo.id}`}>
              <Card className="hover:shadow-lg transition-shadow cursor-pointer h-full">
                <CardHeader>
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <CardTitle className="text-lg mb-1">
                        {repo.github_full_name}
                      </CardTitle>
                      <CardDescription className="line-clamp-2">
                        {repo.github_description || "No description"}
                      </CardDescription>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-muted-foreground">Status</span>
                      <span className={getStatusColor(repo.status)}>
                        {getStatusLabel(repo.status)}
                      </span>
                    </div>
                    {repo.status === "completed" && (
                      <>
                        <div className="flex items-center justify-between text-sm">
                          <span className="text-muted-foreground">Files</span>
                          <span>{repo.total_files.toLocaleString()}</span>
                        </div>
                        <div className="flex items-center justify-between text-sm">
                          <span className="text-muted-foreground">Size</span>
                          <span>
                            {(repo.total_size_bytes / 1024 / 1024).toFixed(2)} MB
                          </span>
                        </div>
                      </>
                    )}
                  </div>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}


