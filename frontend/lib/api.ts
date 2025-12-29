import axios from "axios"

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

const api = axios.create({
  baseURL: `${API_URL}/api/v1`,
  headers: {
    "Content-Type": "application/json",
  },
})

// Repository types
export interface Repository {
  id: number
  github_owner: string
  github_name: string
  github_full_name: string
  github_url: string
  github_description: string | null
  status: "pending" | "in_progress" | "completed" | "failed"
  total_files: number
  total_size_bytes: number
  created_at: string
  updated_at: string
}

export interface RepositoryCreate {
  owner: string
  name: string
}

export interface RepositoryOverview {
  overview: string
  architecture: string | null
  tech_stack: string[] | null
  key_files: string[] | null
  generated_at: string
}

// File types
export interface File {
  id: number
  repository_id: number
  path: string
  name: string
  extension: string | null
  language: string | null
  size_bytes: number
  line_count: number | null
  created_at: string
}

export interface FileExplanation {
  file_path: string
  explanation: string
  purpose: string | null
  key_functions: string[] | null
  dependencies: string[] | null
  generated_at: string
}

// Chat types
export interface ChatMessage {
  id: number
  repository_id: number
  user_id: number | null
  role: "user" | "assistant" | "system"
  content: string
  created_at: string
}

export interface ChatMessageCreate {
  content: string
}

// API functions
export const repositoryApi = {
  list: async (): Promise<Repository[]> => {
    const response = await api.get("/repositories")
    return response.data
  },

  get: async (id: number): Promise<Repository> => {
    const response = await api.get(`/repositories/${id}`)
    return response.data
  },

  create: async (data: RepositoryCreate): Promise<Repository> => {
    const response = await api.post("/repositories", data)
    return response.data
  },

  getOverview: async (id: number): Promise<RepositoryOverview> => {
    const response = await api.get(`/repositories/${id}/overview`)
    return response.data
  },
}

export const fileApi = {
  list: async (repositoryId: number, pathPrefix?: string): Promise<File[]> => {
    const params = pathPrefix ? { path_prefix: pathPrefix } : {}
    const response = await api.get(`/repositories/${repositoryId}/files`, { params })
    return response.data
  },

  get: async (repositoryId: number, filePath: string): Promise<File> => {
    const response = await api.get(`/repositories/${repositoryId}/files/${filePath}`)
    return response.data
  },

  explain: async (repositoryId: number, filePath: string): Promise<FileExplanation> => {
    const response = await api.get(`/repositories/${repositoryId}/files/${filePath}/explain`)
    return response.data
  },
}

export const chatApi = {
  list: async (repositoryId: number): Promise<ChatMessage[]> => {
    const response = await api.get(`/repositories/${repositoryId}/chat`)
    return response.data
  },

  send: async (repositoryId: number, message: ChatMessageCreate): Promise<ChatMessage> => {
    const response = await api.post(`/repositories/${repositoryId}/chat`, message)
    return response.data
  },
}

export default api


