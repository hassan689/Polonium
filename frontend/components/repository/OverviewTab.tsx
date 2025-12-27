"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { repositoryApi, type RepositoryOverview } from "@/lib/api"
import { Loader2, Code2, FileText, Layers } from "lucide-react"

interface OverviewTabProps {
  repositoryId: number
}

export default function RepositoryOverviewTab({ repositoryId }: OverviewTabProps) {
  const [overview, setOverview] = useState<RepositoryOverview | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadOverview()
  }, [repositoryId])

  const loadOverview = async () => {
    try {
      setLoading(true)
      const data = await repositoryApi.getOverview(repositoryId)
      setOverview(data)
    } catch (error) {
      console.error("Failed to load overview:", error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    )
  }

  if (!overview) {
    return (
      <Card>
        <CardContent className="py-12 text-center">
          <p className="text-muted-foreground">Failed to load overview</p>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5" />
            Overview
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground whitespace-pre-wrap">{overview.overview}</p>
        </CardContent>
      </Card>

      {overview.architecture && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Layers className="h-5 w-5" />
              Architecture
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-muted-foreground whitespace-pre-wrap">{overview.architecture}</p>
          </CardContent>
        </Card>
      )}

      {overview.tech_stack && overview.tech_stack.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Code2 className="h-5 w-5" />
              Technology Stack
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              {overview.tech_stack.map((tech, index) => (
                <span
                  key={index}
                  className="px-3 py-1 rounded-full bg-secondary text-secondary-foreground text-sm"
                >
                  {tech}
                </span>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {overview.key_files && overview.key_files.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Key Files</CardTitle>
            <CardDescription>Important files to understand the codebase</CardDescription>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2">
              {overview.key_files.map((file, index) => (
                <li key={index} className="text-sm font-mono text-muted-foreground">
                  {file}
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

