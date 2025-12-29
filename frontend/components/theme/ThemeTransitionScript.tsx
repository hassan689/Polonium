"use client"

import { useEffect } from "react"
import { useTheme } from "next-themes"

export function ThemeTransitionScript() {
  const { theme, resolvedTheme } = useTheme()

  useEffect(() => {
    const html = document.documentElement
    
    // Add transitioning class when theme changes
    html.classList.add("theme-transitioning")
    
    // Remove the class after transition completes
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

