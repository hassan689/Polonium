"use client"

import { useEffect, useState, useRef } from "react"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Textarea } from "@/components/ui/textarea"
import { Button } from "@/components/ui/button"
import { chatApi, type ChatMessage } from "@/lib/api"
import { Loader2, Send, User, Bot } from "lucide-react"
import { format } from "date-fns"

interface MainChatProps {
  repositoryId: number
  repositoryName: string
  showWelcome?: boolean
}

export default function MainChat({ repositoryId, repositoryName, showWelcome = false }: MainChatProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState("")
  const [loading, setLoading] = useState(false)
  const [sending, setSending] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  useEffect(() => {
    if (repositoryId > 0) {
      loadMessages()
    } else {
      setMessages([])
      setLoading(false)
    }
  }, [repositoryId])

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  useEffect(() => {
    // Auto-focus textarea
    textareaRef.current?.focus()
  }, [repositoryId])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  const loadMessages = async () => {
    try {
      setLoading(true)
      const data = await chatApi.list(repositoryId)
      setMessages(data)
    } catch (error) {
      console.error("Failed to load messages:", error)
    } finally {
      setLoading(false)
    }
  }

  const handleSend = async () => {
    if (!input.trim() || sending) return

    const userMessage = input.trim()
    setInput("")
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
      // Replace temp message and add response
      setMessages((prev) => {
        const filtered = prev.filter((m) => m.id !== tempUserMessage.id)
        return [...filtered, response]
      })
    } catch (error) {
      console.error("Failed to send message:", error)
      // Remove temp message on error
      setMessages((prev) => prev.filter((m) => m.id !== tempUserMessage.id))
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

  return (
    <div className="flex flex-col h-full relative">
     

      {/* Messages Area - Scrollable */}
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-3xl mx-auto px-4 py-8">
          {loading ? (
            <div className="flex justify-center items-center py-12">
              <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
            </div>
          ) : messages.length === 0 ? (
            <div className="text-center py-12">
              {repositoryId > 0 && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-w-lg mx-auto">
                  <button
                    onClick={() => setInput("What is the main purpose of this repository?")}
                    className="p-3 text-left rounded-lg border hover:bg-accent transition-colors text-sm"
                  >
                    What is the main purpose of this repository?
                  </button>
                  <button
                    onClick={() => setInput("Explain the architecture of this codebase")}
                    className="p-3 text-left rounded-lg border hover:bg-accent transition-colors text-sm"
                  >
                    Explain the architecture of this codebase
                  </button>
                  <button
                    onClick={() => setInput("What are the key technologies used?")}
                    className="p-3 text-left rounded-lg border hover:bg-accent transition-colors text-sm"
                  >
                    What are the key technologies used?
                  </button>
                  <button
                    onClick={() => setInput("How do I get started with this project?")}
                    className="p-3 text-left rounded-lg border hover:bg-accent transition-colors text-sm"
                  >
                    How do I get started with this project?
                  </button>
                </div>
              )}
            </div>
          ) : (
            <div className="space-y-6 pb-24">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex gap-4 ${
                    message.role === "user" ? "justify-end" : "justify-start"
                  }`}
                >
                  {message.role === "assistant" && (
                    <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
                      <Bot className="h-4 w-4 text-primary" />
                    </div>
                  )}
                  <div
                    className={`max-w-[85%] ${
                      message.role === "user" ? "order-2" : ""
                    }`}
                  >
                    <div
                      className={`rounded-lg border px-4 py-3 ${
                        message.role === "user"
                          ? "bg-primary text-primary-foreground border-primary/20"
                          : "bg-muted border-border"
                      }`}
                    >
                      <p className="text-sm whitespace-pre-wrap leading-relaxed">
                        {message.content}
                      </p>
                    </div>
                    <p
                      className={`text-xs mt-2 px-1 ${
                        message.role === "user"
                          ? "text-right text-muted-foreground"
                          : "text-muted-foreground"
                      }`}
                    >
                      {format(new Date(message.created_at), "MMM d, HH:mm")}
                    </p>
                  </div>
                  {message.role === "user" && (
                    <div className="flex-shrink-0 w-8 h-8 rounded-full bg-secondary flex items-center justify-center order-1">
                      <User className="h-4 w-4" />
                    </div>
                  )}
                </div>
              ))}
              {sending && (
                <div className="flex gap-4 justify-start">
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
                    <Bot className="h-4 w-4 text-primary" />
                  </div>
                  <div className="bg-muted border border-border rounded-lg px-4 py-3">
                    <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>
      </div>

      {/* Input Area - Fixed at Bottom */}
      <div className="absolute bottom-0 left-0 right-0 border-t bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="max-w-5xl mx-auto h-full px-4 py-3">
          <div className="relative">
            <div className="flex items-end gap-2 bg-background rounded-lg border shadow-lg">
              <Textarea
                ref={textareaRef}
                placeholder="Message Polonium..."
                value={input}
                onChange={handleTextareaChange}
                onKeyPress={handleKeyPress}
                disabled={sending}
                rows={1}
                className="resize-none min-h-[52px] max-h-[200px] pr-14 py-3.5 px-4 border-0 focus-visible:ring-0 focus-visible:ring-offset-0"
              />
              <Button
                onClick={handleSend}
                disabled={sending || !input.trim()}
                size="icon"
                className="absolute right-2 bottom-2 h-8 w-8 rounded-lg disabled:opacity-50"
              >
                {sending ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Send className="h-4 w-4" />
                )}
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

