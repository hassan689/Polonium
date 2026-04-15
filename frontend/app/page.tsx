"use client"
import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Input } from "@/components/ui/input"
import { repositoryApi, type Repository } from "@/lib/api"
import { Plus, MessageSquare, GitBranch, Loader2, LogIn, User } from "lucide-react"
import Link from "next/link"
import MainChat from "@/components/chat/MainChat"
import { ThemeToggle } from "@/components/theme/ThemeToggle"
import StaggeredMenu from "@/components/StaggeredMenu"

export default function HomePage() {
  const router = useRouter()
  const [repositories, setRepositories] = useState<Repository[]>([])
  const [selectedRepo, setSelectedRepo] = useState<Repository | null>(null)
  const [loading, setLoading] = useState(true)
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [showConnectForm, setShowConnectForm] = useState(false)
  const [repoOwner, setRepoOwner] = useState("")
  const [repoName, setRepoName] = useState("")
  const [connectingRepo, setConnectingRepo] = useState(false)
  const [connectError, setConnectError] = useState<string | null>(null)

  useEffect(() => {
    loadRepositories()
  }, [])

  const loadRepositories = async () => {
    try {
      setLoading(true)
      const data = await repositoryApi.list()
      setRepositories(data || [])
      // Auto-select first completed repository
      const completed = data?.find(r => r.status === "completed")
      if (completed) {
        setSelectedRepo(completed)
      }
    } catch (error: any) {
      // Silently handle errors - don't show error to user if API is not available
      console.error("Failed to load repositories:", error)
      setRepositories([])
    } finally {
      setLoading(false)
    }
  }

  const getStatusColor = (status: Repository["status"]) => {
    switch (status) {
      case "completed":
        return "text-green-600 dark:text-green-400"
      case "in_progress":
        return "text-blue-600 dark:text-blue-400"
      case "failed":
        return "text-red-600 dark:text-red-400"
      default:
        return "text-gray-600 dark:text-gray-400"
    }
  }

  const handleConnectRepository = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!repoOwner.trim() || !repoName.trim() || connectingRepo) return

    setConnectError(null)
    setConnectingRepo(true)
    try {
      const created = await repositoryApi.create({
        owner: repoOwner.trim(),
        name: repoName.trim(),
      })
      setRepositories((prev) => [created, ...prev])
      setRepoOwner("")
      setRepoName("")
      setShowConnectForm(false)
      router.push(`/repositories/${created.id}`)
    } catch (error: any) {
      setConnectError(error?.response?.data?.detail || "Failed to connect repository.")
    } finally {
      setConnectingRepo(false)
    }
  }

  return (
    <div className="relative h-screen bg-gradient-to-br from-background via-background to-muted/20 overflow-hidden">
      {/* Top Right Sign In Button */}
      <div className="absolute top-5 right-8 z-50">
        <Button
          variant="ghost"
          size="lg"
          className="bg-card/80 backdrop-blur-sm hover:bg-accent/50 hover:text-accent-foreground border border-border/50 shadow-sm transition-colors"
          onClick={() => {
            const authUrl = `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/auth/github`
            window.location.href = authUrl
          }}
        >
          Sign in
        </Button>
      </div>

      {/* Staggered Menu - Hidden by default, opens on Polonium click */}
      <StaggeredMenu
        position="left"
        isFixed={true}
        menuButtonColor="#fff"
        openMenuButtonColor="#000"
        changeMenuColorOnOpen={true}
        accentColor="#5227FF"
        closeOnClickAway={true}
        displayItemNumbering={false}
        displaySocials={false}
        onOpenChange={setSidebarOpen}
      >
        {/* Sidebar Content */}
        <div className="w-full h-full flex flex-col bg-white dark:bg-gray-900">
          <div className="p-4 border-b border-gray-200 dark:border-gray-700 flex-shrink-0">
            <div className="flex items-center gap-2 mb-4">
              <h1 className="font-semibold text-lg text-black dark:text-white">Polonium</h1>
            </div>
            <Button 
              className="w-full bg-transparent hover:bg-gray-100 dark:hover:bg-gray-800 text-black dark:text-white border-0 shadow-none" 
              size="sm"
              variant="ghost"
              onClick={() => {
                setShowConnectForm((prev) => !prev)
                setConnectError(null)
              }}
            >
              <Plus className="mr-2 h-4 w-4" />
              Connect Repository
            </Button>
            {showConnectForm && (
              <form onSubmit={handleConnectRepository} className="mt-3 space-y-2">
                <Input
                  placeholder="Owner / org (e.g. vercel)"
                  value={repoOwner}
                  onChange={(e) => setRepoOwner(e.target.value)}
                  disabled={connectingRepo}
                />
                <Input
                  placeholder="Repository name (e.g. next.js)"
                  value={repoName}
                  onChange={(e) => setRepoName(e.target.value)}
                  disabled={connectingRepo}
                />
                {connectError && (
                  <p className="text-xs text-red-600 dark:text-red-400">{connectError}</p>
                )}
                <div className="flex gap-2">
                  <Button
                    type="submit"
                    size="sm"
                    disabled={connectingRepo || !repoOwner.trim() || !repoName.trim()}
                  >
                    {connectingRepo ? <Loader2 className="h-4 w-4 animate-spin" /> : "Add"}
                  </Button>
                  <Button
                    type="button"
                    size="sm"
                    variant="ghost"
                    onClick={() => {
                      setShowConnectForm(false)
                      setConnectError(null)
                    }}
                    disabled={connectingRepo}
                  >
                    Cancel
                  </Button>
                </div>
              </form>
            )}
          </div>

          <ScrollArea className="flex-1 min-h-0">
            <div className="p-3">
              <div className="text-xs font-semibold text-muted-foreground px-2 mb-2 uppercase tracking-wider">
                Repositories
              </div>
              {loading ? (
                <div className="flex justify-center py-8">
                  <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />
                </div>
              ) : repositories.length === 0 ? (
                <div className="text-center py-8 text-sm text-muted-foreground px-2">
                  <GitBranch className="h-8 w-8 mx-auto mb-2 opacity-50" />
                  <p>No repositories yet</p>
                  <p className="text-xs mt-1">Connect one to get started</p>
                </div>
              ) : (
                <div className="space-y-1">
                  {repositories.map((repo) => (
                    <button
                      key={repo.id}
                      onClick={() => {
                        if (repo.status === "completed") {
                          setSelectedRepo(repo)
                        }
                      }}
                      className={`w-full text-left px-3 py-2 rounded-md text-sm transition-colors ${
                        selectedRepo?.id === repo.id
                          ? "bg-gray-100 dark:bg-gray-800 text-black dark:text-white"
                          : "bg-transparent hover:bg-gray-100 dark:hover:bg-gray-800"
                      } ${
                        repo.status !== "completed" ? "opacity-60 cursor-not-allowed" : ""
                      }`}
                      disabled={repo.status !== "completed"}
                    >
                      <div className="flex items-center justify-between mb-1">
                        <span className="font-medium truncate text-black dark:text-white">{repo.github_name}</span>
                        {repo.status === "completed" && (
                          <MessageSquare className="h-3 w-3 flex-shrink-0" />
                        )}
                      </div>
                      <div className="flex items-center gap-2 text-xs text-muted-foreground">
                        <span className="truncate">{repo.github_owner}</span>
                        <span className={getStatusColor(repo.status)}>•</span>
                      </div>
                    </button>
                  ))}
                </div>
              )}
            </div>
          </ScrollArea>

          <div className="p-4 border-t border-gray-200 dark:border-gray-700 space-y-3 flex-shrink-0">
            <Link
              href="/repositories"
              className="text-xs text-muted-foreground hover:text-foreground transition-colors block"
            >
              View all repositories →
            </Link>
            
            {/* Theme Toggle */}
            <ThemeToggle />
            
            {/* Authentication Section */}
            <div className="pt-2 border-t border-gray-200 dark:border-gray-700 space-y-2">
              <Button 
                className="w-full bg-transparent hover:bg-gray-100 dark:hover:bg-gray-800 text-black dark:text-white border-0 shadow-none" 
                size="sm" 
                variant="ghost"
                onClick={() => {
                  const authUrl = `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/auth/github`
                  window.location.href = authUrl
                }}
              >
                <svg className="mr-2 h-4 w-4" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M20.317 4.37a19.791 19.791 0 0 0-4.885-1.515.074.074 0 0 0-.079.037c-.21.375-.444.864-.608 1.25a18.27 18.27 0 0 0-5.487 0 12.64 12.64 0 0 0-.617-1.25.077.077 0 0 0-.079-.037A19.736 19.736 0 0 0 3.677 4.37a.07.07 0 0 0-.032.027C.533 9.046-.32 13.58.099 18.057a.082.082 0 0 0 .031.057 19.9 19.9 0 0 0 5.993 3.03.078.078 0 0 0 .084-.028c.462-.63.874-1.295 1.226-1.994a.076.076 0 0 0-.041-.106 13.107 13.107 0 0 1-1.872-.892.077.077 0 0 1-.008-.128 10.2 10.2 0 0 0 .372-.292.074.074 0 0 1 .077-.01c3.928 1.793 8.18 1.793 12.062 0a.074.074 0 0 1 .078.01c.12.098.246.198.373.292a.077.077 0 0 1-.006.127 12.299 12.299 0 0 1-1.873.892.077.077 0 0 0-.041.107c.36.698.772 1.362 1.225 1.993a.076.076 0 0 0 .084.028 19.839 19.839 0 0 0 6.002-3.03.077.077 0 0 0 .032-.054c.5-5.177-.838-9.674-3.549-13.66a.061.061 0 0 0-.031-.03zM8.02 15.33c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.956-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.956 2.418-2.157 2.418zm7.975 0c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.955-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.946 2.418-2.157 2.418z"/>
                </svg>
                Login with GitHub
              </Button>
              
              {/* User Profile Section (when logged in) */}
              <div className="flex items-center gap-2 text-xs pt-1">
                <div className="w-6 h-6 rounded-full bg-muted flex items-center justify-center">
                  <User className="h-3 w-3" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="font-medium truncate text-black dark:text-white">Not logged in</p>
                  <p className="text-muted-foreground text-[10px]">Click GitHub to login</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </StaggeredMenu>

      {/* Main Chat Area - Adjusts when sidebar opens */}
      <div 
        className="h-full flex flex-col relative z-[5] transition-all"
        style={{
          marginLeft: sidebarOpen ? 'clamp(320px, 38vw, 480px)' : '0',
          transitionDuration: '650ms',
          transitionTimingFunction: 'cubic-bezier(0.25, 0.46, 0.45, 0.94)'
        }}
      >
        {selectedRepo ? (
          <MainChat repositoryId={selectedRepo.id} repositoryName={selectedRepo.github_full_name} sidebarOpen={sidebarOpen} />
        ) : (
          <MainChat 
            repositoryId={0} 
            repositoryName="Polonium" 
            showWelcome={true}
            sidebarOpen={sidebarOpen}
          />
        )}
      </div>
    </div>
  )
}

