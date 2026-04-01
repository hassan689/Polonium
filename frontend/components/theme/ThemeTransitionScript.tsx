"use client"

import { useEffect } from "react"
import { useTheme } from "next-themes"

export function ThemeTransitionScript() {
  const { theme, resolvedTheme } = useTheme()

  useEffect(() => {
    const html = document.documentElement
    html.classList.add("theme-transitioning")
    const timeout = setTimeout(() => {
    html.classList.remove("theme-transitioning")
    }, 800)
    
    return () => {
      clearTimeout(timeout)
      html.classList.remove("theme-transitioning")
    }
  }, [resolvedTheme])

  return null
}






