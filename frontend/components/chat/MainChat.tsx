"use client"

import { useEffect, useState, useRef } from "react"
import { Textarea } from "@/components/ui/textarea"
import { Button } from "@/components/ui/button"
import { chatApi, type ChatMessage } from "@/lib/api"
import { Loader2 } from "lucide-react"

interface MainChatProps {
  repositoryId: number
  repositoryName: string
  showWelcome?: boolean
  sidebarOpen?: boolean
}

export default function MainChat({ repositoryId, repositoryName, showWelcome = false, sidebarOpen = false }: MainChatProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState("")
  const [loading, setLoading] = useState(false)
  const [sending, setSending] = useState(false)
  const [typingMessages, setTypingMessages] = useState<Map<number, string>>(new Map())
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  useEffect(() => {
    if (repositoryId > 0) {
      loadMessages()
    } else {
      setMessages([])
      setLoading(false)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [repositoryId])

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  useEffect(() => {
    // Auto-focus textarea
    textareaRef.current?.focus()
  }, [repositoryId])

  const scrollToBottom = () => {
    try {
      messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
    } catch (error) {
      // Silently handle scroll errors
      if (messagesEndRef.current) {
        messagesEndRef.current.scrollIntoView()
      }
    }
  }

  const loadMessages = async () => {
    try {
      setLoading(true)
      const data = await chatApi.list(repositoryId)
      setMessages(data || [])
    } catch (error: any) {
      // Silently handle errors - don't crash UI if API is not available
      console.error("Failed to load messages:", error)
      setMessages([])
    } finally {
      setLoading(false)
    }
  }

  const handleSend = async () => {
    if (!input.trim() || sending) return

    const userMessage = input.trim()
    setInput("")
    
    // Add delay before sending
    await new Promise(resolve => setTimeout(resolve, 300))
    
    setSending(true)

    // If no repository selected, show a message
    if (repositoryId === 0) {
      const tempUserMessage: ChatMessage = {
        id: Date.now(),
        repository_id: 0,
        user_id: null,
        role: "user",
        content: userMessage,
        created_at: new Date().toISOString(),
      }
      const tempAssistantMessage: ChatMessage = {
        id: Date.now() + 1,
        repository_id: 0,
        user_id: null,
        role: "assistant",
        content: "Please select a repository from the sidebar to start chatting. You can also mention a GitHub repository in your message (e.g., 'microsoft/vscode') and I'll help you explore it.",
        created_at: new Date().toISOString(),
      }
      setMessages((prev) => [...prev, tempUserMessage, tempAssistantMessage])
      setSending(false)
      if (textareaRef.current) {
        textareaRef.current.style.height = "auto"
      }
      textareaRef.current?.focus()
      return
    }

    // Optimistically add user message
    const tempUserMessage: ChatMessage = {
      id: Date.now(),
      repository_id: repositoryId,
      user_id: null,
      role: "user",
      content: userMessage,
      created_at: new Date().toISOString(),
    }
    setMessages((prev) => [...prev, tempUserMessage])

    // Auto-resize textarea
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto"
    }

    try {
      const response = await chatApi.send(repositoryId, { content: userMessage })
      // Replace temp message and add response with empty content initially
      const responseWithEmptyContent = { ...response, content: "" }
      setMessages((prev) => {
        const filtered = prev.filter((m) => m.id !== tempUserMessage.id)
        return [...filtered, responseWithEmptyContent]
      })
      
      // Typewriter effect for assistant messages
      if (response.role === "assistant") {
        typewriterEffect(response.id, response.content || "")
      } else {
        setMessages((prev) => {
          return prev.map((m) =>
            m.id === response.id ? response : m
          )
        })
      }
    } catch (error: any) {
      // Silently handle errors - show user-friendly message instead of crashing
      console.error("Failed to send message:", error)
      // Remove temp message on error and show error message
      setMessages((prev) => {
        const filtered = prev.filter((m) => m.id !== tempUserMessage.id)
        const errorMessage: ChatMessage = {
          id: Date.now() + 1,
          repository_id: repositoryId,
          user_id: null,
          role: "assistant",
          content: "Sorry, I'm having trouble connecting to the server. Please check if the backend is running and try again.",
          created_at: new Date().toISOString(),
        }
        return [...filtered, errorMessage]
      })
    } finally {
      setSending(false)
      textareaRef.current?.focus()
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleTextareaChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(e.target.value)
    // Auto-resize
    e.target.style.height = "auto"
    e.target.style.height = `${Math.min(e.target.scrollHeight, 200)}px`
  }

  const typewriterEffect = (messageId: number, fullText: string) => {
    if (!fullText || fullText.length === 0) {
      // If no text, just remove from typing messages
      setTypingMessages((prev) => {
        const newMap = new Map(prev)
        newMap.delete(messageId)
        return newMap
      })
      return
    }

    let currentIndex = 0
    const typingSpeed = 20 // milliseconds per character
    
    const typeInterval = setInterval(() => {
      if (currentIndex <= fullText.length) {
        const displayedText = fullText.slice(0, currentIndex)
        setTypingMessages((prev) => {
          const newMap = new Map(prev)
          newMap.set(messageId, displayedText)
          return newMap
        })
        
        setMessages((prev) => {
          return prev.map((m) =>
            m.id === messageId ? { ...m, content: displayedText } : m
          )
        })
        
        currentIndex++
        scrollToBottom()
      } else {
        clearInterval(typeInterval)
        setTypingMessages((prev) => {
          const newMap = new Map(prev)
          newMap.delete(messageId)
          return newMap
        })
      }
    }, typingSpeed)
  }

  return (
    <div className="flex flex-col h-full relative">
     

      {/* Messages Area - Scrollable, adjusts for sidebar */}
      <div className="flex-1 overflow-y-auto pb-40">
        <div 
          className="mx-auto px-4 md:px-6 py-8 md:py-12 transition-all"
          style={{
            maxWidth: sidebarOpen ? 'calc(100vw - clamp(320px, 38vw, 480px) - 4rem)' : '56rem',
            transitionDuration: '650ms',
            transitionTimingFunction: 'cubic-bezier(0.25, 0.46, 0.45, 0.94)'
          }}
        >
          {loading ? (
            <div className="flex justify-center items-center min-h-[60vh]">
              <div className="flex flex-col items-center gap-4">
                <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
                <p className="text-sm text-muted-foreground">Loading messages...</p>
              </div>
            </div>
          ) : messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center min-h-[80vh] px-4">
              <div className="max-w-2xl w-full text-center space-y-8">
                <div className="space-y-4">
                  <h1 className="text-5xl md:text-6xl font-light text-foreground tracking-tight">
                    {repositoryId > 0 ? (
                      <>Collaborate on <span className="font-medium">{repositoryName}</span></>
                    ) : (
                      <>Meet Polonium</>
                    )}
                  </h1>
                </div>
                
                {repositoryId > 0 && (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-w-2xl mx-auto pt-8">
                    <button
                      onClick={() => setInput("@issue I found a bug in the authentication flow")}
                      className="p-4 text-left rounded-xl border border-border/50 bg-card/50 hover:bg-accent/50 hover:border-accent transition-all duration-200 text-sm backdrop-blur-sm"
                    >
                      @issue I found a bug in the authentication flow
                    </button>
                    <button
                      onClick={() => setInput("Can someone review this pull request? @team")}
                      className="p-4 text-left rounded-xl border border-border/50 bg-card/50 hover:bg-accent/50 hover:border-accent transition-all duration-200 text-sm backdrop-blur-sm"
                    >
                      Can someone review this pull request? @team
                    </button>
                    <button
                      onClick={() => setInput("Explain the architecture of this codebase")}
                      className="p-4 text-left rounded-xl border border-border/50 bg-card/50 hover:bg-accent/50 hover:border-accent transition-all duration-200 text-sm backdrop-blur-sm"
                    >
                      Explain the architecture of this codebase
                    </button>
                    <button
                      onClick={() => setInput("@discussion What's the best approach for handling API rate limits?")}
                      className="p-4 text-left rounded-xl border border-border/50 bg-card/50 hover:bg-accent/50 hover:border-accent transition-all duration-200 text-sm backdrop-blur-sm"
                    >
                      @discussion What's the best approach for handling API rate limits?
                    </button>
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="space-y-8 pb-24">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${
                    message.role === "user" ? "justify-end" : "justify-start"
                  }`}
                >
                  <div className="max-w-[85%] md:max-w-[75%]">
                    <div
                      className={`rounded-2xl px-5 py-4 shadow-sm ${
                        message.role === "user"
                          ? "bg-primary text-primary-foreground ml-auto"
                          : "bg-card border border-border/50"
                      }`}
                    >
                      <p className="text-[15px] leading-relaxed whitespace-pre-wrap">
                        {typingMessages.get(message.id) ?? message.content}
                        {typingMessages.has(message.id) && (
                          <span className="animate-pulse ml-1">|</span>
                        )}
                      </p>
                    </div>
                    <p
                      className={`text-xs mt-2 px-1 ${
                        message.role === "user"
                          ? "text-right text-muted-foreground"
                          : "text-muted-foreground"
                      }`}
                    >
                    </p>
                  </div>
                </div>
              ))}
              {sending && (
                <div className="flex justify-start">
                  <div className="bg-card border border-border/50 rounded-2xl px-5 py-4 shadow-sm">
                    <div className="flex items-center gap-2">
                      <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
                      <span className="text-sm text-muted-foreground">Thinking...</span>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>
      </div>

      {/* Input Area - Fixed at Bottom, adjusts for sidebar */}
      <div 
        className="absolute bottom-6 px-6 py-4 relative flex items-end gap-3 bg-card/80 backdrop-blur-xl rounded-2xl border border-border/50 shadow-2xl transition-all"
        style={{
          left: sidebarOpen ? '1.5rem' : '50%',
          transform: sidebarOpen ? 'translateX(0)' : 'translateX(-50%)',
          width: sidebarOpen ? 'calc(100% - 3rem)' : 'min(100vw - 3rem, 56rem)',
          maxWidth: sidebarOpen ? 'none' : '56rem',
          transitionDuration: '650ms',
          transitionTimingFunction: 'cubic-bezier(0.25, 0.46, 0.45, 0.94)'
        }}
      >
        <Textarea
          ref={textareaRef}
          placeholder={repositoryId > 0 ? "Mention issues, ask questions, or discuss code with your team..." : "Ask me to create a workspace for you..."}
          value={input}
          onChange={handleTextareaChange}
          onKeyPress={handleKeyPress}
          disabled={sending}
          rows={1}
          className="resize-none flex-1 min-h-[52px] max-h-[200px] pr-12 py-3.5 px-0 border-0 bg-transparent focus-visible:ring-0 focus-visible:ring-offset-0 text-base placeholder:text-muted-foreground/60"
        />
        <Button
          onClick={handleSend}
          disabled={sending || !input.trim()}
          size="icon"
          className="h-10 w-10 rounded-full bg-primary hover:bg-primary/90 disabled:opacity-40 disabled:cursor-not-allowed transition-all flex-shrink-0 shadow-lg"
        >
          {sending ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <svg 
              width="16" 
              height="16" 
              viewBox="0 0 24 24" 
              fill="none" 
              xmlns="http://www.w3.org/2000/svg"
              className="h-4 w-4"
            >
              <g clipPath="url(#clip0_403_3214)">
                <path 
                  d="M6.99985 24C6.86824 24.0008 6.73778 23.9756 6.61594 23.9258C6.4941 23.876 6.38329 23.8027 6.28985 23.71C6.19612 23.6171 6.12172 23.5065 6.07096 23.3846C6.02019 23.2628 5.99405 23.132 5.99405 23C5.99405 22.868 6.02019 22.7373 6.07096 22.6155C6.12172 22.4936 6.19612 22.383 6.28985 22.29L14.4598 14.12C15.0216 13.5575 15.3372 12.7951 15.3372 12C15.3372 11.205 15.0216 10.4426 14.4598 9.88005L6.28985 1.71006C6.10154 1.52176 5.99576 1.26636 5.99576 1.00006C5.99576 0.733761 6.10154 0.478366 6.28985 0.290063C6.47815 0.101759 6.73355 -0.00402832 6.99985 -0.00402832C7.26615 -0.00402832 7.52154 0.101759 7.70985 0.290063L15.8798 8.46005C16.3455 8.92451 16.7149 9.47626 16.967 10.0837C17.219 10.6912 17.3488 11.3424 17.3488 12C17.3488 12.6577 17.219 13.3089 16.967 13.9164C16.7149 14.5238 16.3455 15.0756 15.8798 15.54L7.70985 23.71C7.61641 23.8027 7.50559 23.876 7.38375 23.9258C7.26192 23.9756 7.13145 24.0008 6.99985 24Z" 
                  fill="currentColor"
                />
              </g>
              <defs>
                <clipPath id="clip0_403_3214">
                  <rect width="24" height="24" fill="white"/>
                </clipPath>
              </defs>
            </svg>
          )}
        </Button>
      </div>
    </div>
  )
}

