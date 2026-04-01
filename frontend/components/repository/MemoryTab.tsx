"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { memoryApi, type RepositoryMemory } from "@/lib/api"
import { Loader2, Brain, Lightbulb } from "lucide-react"
import { format } from "date-fns"

interface MemoryTabProps {
  repositoryId: number
}

export default function RepositoryMemoryTab({ repositoryId }: MemoryTabProps) {
  const [memories, setMemories] = useState<RepositoryMemory[]>([])
  const [loading, setLoading] = useState(true)
  const [endpointAvailable, setEndpointAvailable] = useState(true)

  useEffect(() => {
    loadMemories()
  }, [repositoryId])

  const loadMemories = async () => {
    try {
      setLoading(true)
      const data = await memoryApi.list(repositoryId)
      setMemories(data || [])
      setEndpointAvailable(true)
    } catch (error: any) {
      // Keep UI usable even if backend memory endpoint is not implemented yet.
      if (error?.response?.status === 404) {
        setEndpointAvailable(false)
      }
      setMemories([])
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

  if (!endpointAvailable) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Brain className="h-5 w-5" />
            Repository Memory
          </CardTitle>
          <CardDescription>
            Persistent memory UI is ready. Backend memory endpoints can be enabled next.
          </CardDescription>
        </CardHeader>
      </Card>
    )
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Brain className="h-5 w-5" />
            Repository Memory
          </CardTitle>
          <CardDescription>
            Important insights, decisions, and context preserved for this repository.
          </CardDescription>
        </CardHeader>
      </Card>

      {memories.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center">
            <Lightbulb className="h-10 w-10 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-1">No memory entries yet</h3>
            <p className="text-muted-foreground text-sm">
              As the team chats and explores code, useful insights can be stored here.
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4">
          {memories.map((memory) => (
            <Card key={memory.id}>
              <CardHeader className="pb-2">
                <div className="flex items-start justify-between gap-4">
                  <CardTitle className="text-base">{memory.title}</CardTitle>
                  <span className="text-xs text-muted-foreground whitespace-nowrap">
                    {format(new Date(memory.created_at), "MMM d, yyyy")}
                  </span>
                </div>
                {memory.memory_type && (
                  <CardDescription className="capitalize">{memory.memory_type}</CardDescription>
                )}
              </CardHeader>
              <CardContent>
                <p className="text-sm whitespace-pre-wrap text-muted-foreground">{memory.content}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
