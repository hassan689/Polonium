"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { repositoryApi } from "@/lib/api"
import { Loader2, ArrowLeft } from "lucide-react"
import Link from "next/link"

export default function NewRepositoryPage() {
  const router = useRouter()
  const [owner, setOwner] = useState("")
  const [name, setName] = useState("")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setLoading(true)

    try {
      const repo = await repositoryApi.create({ owner, name })
      router.push(`/repositories/${repo.id}`)
    } catch (err: any) {
      setError(
        err.response?.data?.detail || "Failed to connect repository. Please check the owner and name."
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-2xl">
      <Link href="/repositories" className="inline-flex items-center text-sm text-muted-foreground hover:text-foreground mb-6">
        <ArrowLeft className="mr-2 h-4 w-4" />
        Back to repositories
      </Link>

      <Card>
        <CardHeader>
          <CardTitle>Connect GitHub Repository</CardTitle>
          <CardDescription>
            Enter the owner and name of the GitHub repository you want to connect.
            The repository will be analyzed and indexed for AI-powered exploration.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-2">
              <Label htmlFor="owner">Owner / Organization</Label>
              <Input
                id="owner"
                placeholder="e.g., microsoft, facebook, vercel"
                value={owner}
                onChange={(e) => setOwner(e.target.value)}
                required
                disabled={loading}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="name">Repository Name</Label>
              <Input
                id="name"
                placeholder="e.g., vscode, react, next.js"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
                disabled={loading}
              />
            </div>

            {error && (
              <div className="p-3 rounded-md bg-destructive/10 text-destructive text-sm">
                {error}
              </div>
            )}

            <div className="flex gap-4">
              <Button type="submit" disabled={loading || !owner || !name}>
                {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                Connect Repository
              </Button>
              <Link href="/repositories">
                <Button type="button" variant="outline" disabled={loading}>
                  Cancel
                </Button>
              </Link>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}

