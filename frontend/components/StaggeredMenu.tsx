"use client"

import React, { useCallback, useLayoutEffect, useRef, useState } from 'react'
import { gsap } from 'gsap'

export interface StaggeredMenuItem {
  label: string
  ariaLabel: string
  link: string
  onClick?: () => void
}

export interface StaggeredMenuSocialItem {
  label: string
  link: string
}

export interface StaggeredMenuProps {
  position?: 'left' | 'right'
  items?: StaggeredMenuItem[]
  socialItems?: StaggeredMenuSocialItem[]
  displaySocials?: boolean
  displayItemNumbering?: boolean
  className?: string
  logoUrl?: string
  menuButtonColor?: string
  openMenuButtonColor?: string
  accentColor?: string
  isFixed?: boolean
  changeMenuColorOnOpen?: boolean
  closeOnClickAway?: boolean
  onMenuOpen?: () => void
  onMenuClose?: () => void
  onOpenChange?: (open: boolean) => void
  children?: React.ReactNode
}

export const StaggeredMenu: React.FC<StaggeredMenuProps> = ({
  position = 'left',
  items = [],
  socialItems = [],
  displaySocials = true,
  displayItemNumbering = true,
  className,
  logoUrl,
  menuButtonColor = '#fff',
  openMenuButtonColor = '#000',
  changeMenuColorOnOpen = true,
  accentColor = '#5227FF',
  isFixed = true,
  closeOnClickAway = true,
  onMenuOpen,
  onMenuClose,
  onOpenChange,
  children
}: StaggeredMenuProps) => {
  const [open, setOpen] = useState(false)
  const openRef = useRef(false)

  const panelRef = useRef<HTMLDivElement | null>(null)
  const plusHRef = useRef<HTMLSpanElement | null>(null)
  const plusVRef = useRef<HTMLSpanElement | null>(null)
  const iconRef = useRef<HTMLSpanElement | null>(null)
  const textInnerRef = useRef<HTMLSpanElement | null>(null)
  const toggleBtnRef = useRef<HTMLButtonElement | null>(null)
  const busyRef = useRef(false)

  const openTlRef = useRef<gsap.core.Timeline | null>(null)
  const closeTweenRef = useRef<gsap.core.Tween | null>(null)
  const spinTweenRef = useRef<gsap.core.Timeline | null>(null)
  const textCycleAnimRef = useRef<gsap.core.Tween | null>(null)
  const colorTweenRef = useRef<gsap.core.Tween | null>(null)
  const itemEntranceTweenRef = useRef<gsap.core.Tween | null>(null)

  useLayoutEffect(() => {
    const ctx = gsap.context(() => {
      const panel = panelRef.current
      const plusH = plusHRef.current
      const plusV = plusVRef.current
      const icon = iconRef.current
      const textInner = textInnerRef.current

      if (!panel) return

      // For fixed positioning, use x transform instead of xPercent
      // Use fixed width (matches CSS clamp(320px, 38vw, 480px) max value)
      const panelWidth = 480
      const offscreen = position === 'left' ? -panelWidth : panelWidth
      gsap.set(panel, { x: offscreen, opacity: 0, pointerEvents: 'none' })

      if (plusH && plusV) {
        gsap.set(plusH, { transformOrigin: '50% 50%', rotate: 0 })
        gsap.set(plusV, { transformOrigin: '50% 50%', rotate: 90 })
      }
      if (icon) {
        gsap.set(icon, { rotate: 0, transformOrigin: '50% 50%' })
      }
      if (textInner) {
        gsap.set(textInner, { yPercent: 0 })
      }
      if (toggleBtnRef.current) {
        gsap.set(toggleBtnRef.current, { color: menuButtonColor })
      }
    })
    return () => ctx.revert()
  }, [menuButtonColor, position])

  const buildOpenTimeline = useCallback(() => {
    const panel = panelRef.current
    if (!panel) return null

    openTlRef.current?.kill()
    if (closeTweenRef.current) {
      closeTweenRef.current.kill()
      closeTweenRef.current = null
    }
    itemEntranceTweenRef.current?.kill()

    const itemEls = Array.from(panel.querySelectorAll('.sm-panel-itemLabel')) as HTMLElement[]
    const numberEls = Array.from(
      panel.querySelectorAll('.sm-panel-list[data-numbering] .sm-panel-item')
    ) as HTMLElement[]
    const socialTitle = panel.querySelector('.sm-socials-title') as HTMLElement | null
    const socialLinks = Array.from(panel.querySelectorAll('.sm-socials-link')) as HTMLElement[]

    // Use fixed width calculation (matches CSS clamp(320px, 38vw, 480px))
    const panelWidth = 480
    const offscreen = position === 'left' ? -panelWidth : panelWidth
    const panelStart = Number(gsap.getProperty(panel, 'x')) || offscreen

    if (itemEls.length) gsap.set(itemEls, { yPercent: 140, rotate: 10 })
    if (numberEls.length) gsap.set(numberEls, { ['--sm-num-opacity' as any]: 0 })
    if (socialTitle) gsap.set(socialTitle, { opacity: 0 })
    if (socialLinks.length) gsap.set(socialLinks, { y: 25, opacity: 0 })

    const tl = gsap.timeline({ paused: true })

    // Slide in panel (overlay removed - no blur)
    const panelDuration = 0.65
    gsap.set(panel, { opacity: 1, pointerEvents: 'auto' })
    tl.fromTo(
      panel,
      { x: panelStart, opacity: 0 },
      { x: 0, opacity: 1, duration: panelDuration, ease: 'power4.out' },
      0.1
    )

    // Animate items
    if (itemEls.length) {
      const itemsStart = 0.2
      tl.to(
        itemEls,
        {
          yPercent: 0,
          rotate: 0,
          duration: 1,
          ease: 'power4.out',
          stagger: { each: 0.1, from: 'start' }
        },
        itemsStart
      )

      if (numberEls.length) {
        tl.to(
          numberEls,
          {
            duration: 0.6,
            ease: 'power2.out',
            ['--sm-num-opacity' as any]: 1,
            stagger: { each: 0.08, from: 'start' }
          },
          itemsStart + 0.1
        )
      }
    }

    // Animate socials
    if (socialTitle || socialLinks.length) {
      const socialsStart = 0.4
      if (socialTitle) {
        tl.to(socialTitle, { opacity: 1, duration: 0.5, ease: 'power2.out' }, socialsStart)
      }
      if (socialLinks.length) {
        tl.to(
          socialLinks,
          {
            y: 0,
            opacity: 1,
            duration: 0.55,
            ease: 'power3.out',
            stagger: { each: 0.08, from: 'start' },
            onComplete: () => {
              gsap.set(socialLinks, { clearProps: 'opacity' })
            }
          },
          socialsStart + 0.04
        )
      }
    }

    openTlRef.current = tl
    return tl
  }, [position])

  const playOpen = useCallback(() => {
    if (busyRef.current) return
    busyRef.current = true
    const tl = buildOpenTimeline()
    if (tl) {
      tl.eventCallback('onComplete', () => {
        busyRef.current = false
      })
      tl.play(0)
    } else {
      busyRef.current = false
    }
  }, [buildOpenTimeline])

  const playClose = useCallback(() => {
    openTlRef.current?.kill()
    openTlRef.current = null
    itemEntranceTweenRef.current?.kill()

    const panel = panelRef.current
    if (!panel) return

    closeTweenRef.current?.kill()

    // Use fixed width calculation (matches CSS clamp(320px, 38vw, 480px))
    const panelWidth = 480
    const offscreen = position === 'left' ? -panelWidth : panelWidth

    // Slide out panel
    closeTweenRef.current = gsap.to(panel, {
      x: offscreen,
      opacity: 0,
      pointerEvents: 'none',
      duration: 0.32,
      ease: 'power3.in',
      overwrite: 'auto',
      onComplete: () => {
        const itemEls = Array.from(panel.querySelectorAll('.sm-panel-itemLabel')) as HTMLElement[]
        if (itemEls.length) gsap.set(itemEls, { yPercent: 140, rotate: 10 })

        const numberEls = Array.from(
          panel.querySelectorAll('.sm-panel-list[data-numbering] .sm-panel-item')
        ) as HTMLElement[]
        if (numberEls.length) gsap.set(numberEls, { ['--sm-num-opacity' as any]: 0 })

        const socialTitle = panel.querySelector('.sm-socials-title') as HTMLElement | null
        const socialLinks = Array.from(panel.querySelectorAll('.sm-socials-link')) as HTMLElement[]
        if (socialTitle) gsap.set(socialTitle, { opacity: 0 })
        if (socialLinks.length) gsap.set(socialLinks, { y: 25, opacity: 0 })

        busyRef.current = false
      }
    })
  }, [position])

  const animateIcon = useCallback((opening: boolean) => {
    const icon = iconRef.current
    const h = plusHRef.current
    const v = plusVRef.current
    if (!icon || !h || !v) return

    spinTweenRef.current?.kill()

    if (opening) {
      gsap.set(icon, { rotate: 0, transformOrigin: '50% 50%' })
      spinTweenRef.current = gsap
        .timeline({ defaults: { ease: 'power4.out' } })
        .to(h, { rotate: 45, duration: 0.5 }, 0)
        .to(v, { rotate: -45, duration: 0.5 }, 0)
    } else {
      spinTweenRef.current = gsap
        .timeline({ defaults: { ease: 'power3.inOut' } })
        .to(h, { rotate: 0, duration: 0.35 }, 0)
        .to(v, { rotate: 90, duration: 0.35 }, 0)
        .to(icon, { rotate: 0, duration: 0.001 }, 0)
    }
  }, [])

  const animateColor = useCallback(
    (opening: boolean) => {
      const btn = toggleBtnRef.current
      if (!btn) return
      colorTweenRef.current?.kill()
      if (changeMenuColorOnOpen) {
        const targetColor = opening ? openMenuButtonColor : menuButtonColor
        colorTweenRef.current = gsap.to(btn, {
          color: targetColor,
          delay: 0.18,
          duration: 0.3,
          ease: 'power2.out'
        })
      } else {
        gsap.set(btn, { color: menuButtonColor })
      }
    },
    [openMenuButtonColor, menuButtonColor, changeMenuColorOnOpen]
  )

  const animateText = useCallback((opening: boolean) => {
    const inner = textInnerRef.current
    if (!inner) return

    textCycleAnimRef.current?.kill()

    const currentLabel = opening ? 'Menu' : 'Close'
    const targetLabel = opening ? 'Close' : 'Menu'
    const cycles = 3

    const seq: string[] = [currentLabel]
    let last = currentLabel
    for (let i = 0; i < cycles; i++) {
      last = last === 'Menu' ? 'Close' : 'Menu'
      seq.push(last)
    }
    if (last !== targetLabel) seq.push(targetLabel)
    seq.push(targetLabel)

    gsap.set(inner, { yPercent: 0 })

    const lineCount = seq.length
    const finalShift = ((lineCount - 1) / lineCount) * 100

    textCycleAnimRef.current = gsap.to(inner, {
      yPercent: -finalShift,
      duration: 0.5 + lineCount * 0.07,
      ease: 'power4.out'
    })
  }, [])

  const toggleMenu = useCallback(() => {
    const target = !openRef.current
    openRef.current = target
    setOpen(target)
    onOpenChange?.(target)

    if (target) {
      onMenuOpen?.()
      playOpen()
    } else {
      onMenuClose?.()
      playClose()
    }

    animateIcon(target)
    animateColor(target)
    animateText(target)
  }, [playOpen, playClose, animateIcon, animateColor, animateText, onMenuOpen, onMenuClose, onOpenChange])

  const closeMenu = useCallback(() => {
    if (openRef.current) {
      openRef.current = false
      setOpen(false)
      onOpenChange?.(false)
      onMenuClose?.()
      playClose()
      animateIcon(false)
      animateColor(false)
      animateText(false)
    }
  }, [playClose, animateIcon, animateColor, animateText, onMenuClose, onOpenChange])

  // Removed click-away close functionality - menu stays open until Polonium is clicked again

  const [textLines, setTextLines] = useState<string[]>(['Menu', 'Close'])

  React.useEffect(() => {
    const currentLabel = open ? 'Close' : 'Menu'
    const targetLabel = open ? 'Menu' : 'Close'
    const cycles = 3

    const seq: string[] = [currentLabel]
    let last = currentLabel
    for (let i = 0; i < cycles; i++) {
      last = last === 'Menu' ? 'Close' : 'Menu'
      seq.push(last)
    }
    if (last !== targetLabel) seq.push(targetLabel)
    seq.push(targetLabel)

    setTextLines(seq)
  }, [open])

  // Inject styles only on client side to prevent hydration mismatch
  React.useEffect(() => {
    const styleId = 'staggered-menu-styles'
    if (document.getElementById(styleId)) return

    const style = document.createElement('style')
    style.id = styleId
    style.textContent = `
        .sm-scope .staggered-menu-wrapper {
          position: relative;
          width: 100%;
          height: 100%;
          z-index: 40;
          pointer-events: none;
        }
        .sm-scope .staggered-menu-header {
          position: absolute;
          top: 0;
          left: 0;
          width: 100%;
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 2em;
          background: transparent;
          pointer-events: none;
          z-index: 20;
        }
        .sm-scope .staggered-menu-header > * {
          pointer-events: auto;
        }
        .sm-scope .sm-logo {
          display: flex;
          align-items: center;
          user-select: none;
        }
        .sm-scope .sm-logo-img {
          display: block;
          height: 32px;
          width: auto;
          object-fit: contain;
        }
        .sm-scope .sm-toggle {
          position: relative;
          display: inline-flex;
          align-items: center;
          gap: 0.3rem;
          background: transparent;
          border: none;
          cursor: pointer;
          font-weight: 500;
          line-height: 1;
          overflow: visible;
        }
        .sm-scope .sm-toggle:focus-visible {
          outline: 2px solid rgba(255, 255, 255, 0.7);
          outline-offset: 4px;
          border-radius: 4px;
        }
        .sm-scope .sm-toggle-textWrap {
          position: relative;
          margin-right: 0.5em;
          display: inline-block;
          height: 1em;
          overflow: hidden;
          white-space: nowrap;
          width: var(--sm-toggle-width, auto);
          min-width: var(--sm-toggle-width, auto);
        }
        .sm-scope .sm-toggle-textInner {
          display: flex;
          flex-direction: column;
          line-height: 1;
        }
        .sm-scope .sm-toggle-line {
          display: block;
          height: 1em;
          line-height: 1;
        }
        .sm-scope .sm-icon {
          position: relative;
          width: 14px;
          height: 14px;
          flex: 0 0 14px;
          display: inline-flex;
          align-items: center;
          justify-content: center;
          will-change: transform;
        }
        .sm-scope .sm-icon-line {
          position: absolute;
          left: 50%;
          top: 50%;
          width: 100%;
          height: 2px;
          background: currentColor;
          border-radius: 2px;
          transform: translate(-50%, -50%);
          will-change: transform;
        }
        .sm-scope .staggered-menu-panel {
          position: fixed;
          top: 0;
          left: 0;
          width: clamp(320px, 38vw, 480px);
          height: 100vh;
          background: white;
          display: flex;
          flex-direction: column;
          overflow-y: auto;
          z-index: 50;
          pointer-events: auto;
          box-shadow: 4px 0 24px rgba(0, 0, 0, 0.15);
        }
        .dark .sm-scope .staggered-menu-panel {
          background: #1a1a1a;
        }
        .sm-scope [data-position='right'] .staggered-menu-panel {
          right: 0;
          left: auto;
        }
        .sm-scope .sm-panel-inner {
          flex: 1;
          display: flex;
          flex-direction: column;
          gap: 1.25rem;
        }
        .sm-scope .sm-socials {
          margin-top: auto;
          padding-top: 2rem;
          display: flex;
          flex-direction: column;
          gap: 0.75rem;
        }
        .sm-scope .sm-socials-title {
          margin: 0;
          font-size: 1rem;
          font-weight: 500;
          color: var(--sm-accent, #5227FF);
        }
        .sm-scope .sm-socials-list {
          list-style: none;
          margin: 0;
          padding: 0;
          display: flex;
          flex-direction: row;
          align-items: center;
          gap: 1rem;
          flex-wrap: wrap;
        }
        .sm-scope .sm-socials-list .sm-socials-link {
          opacity: 1;
          transition: opacity 0.3s ease;
        }
        .sm-scope .sm-socials-list:hover .sm-socials-link:not(:hover) {
          opacity: 0.35;
        }
        .sm-scope .sm-socials-list:focus-within .sm-socials-link:not(:focus-visible) {
          opacity: 0.35;
        }
        .sm-scope .sm-socials-list .sm-socials-link:hover,
        .sm-scope .sm-socials-list .sm-socials-link:focus-visible {
          opacity: 1;
        }
        .sm-scope .sm-socials-link:focus-visible {
          outline: 2px solid var(--sm-accent, #5227FF);
          outline-offset: 3px;
        }
        .sm-scope .sm-socials-link {
          font-size: 1.2rem;
          font-weight: 500;
          color: #111;
          text-decoration: none;
          position: relative;
          padding: 2px 0;
          display: inline-block;
          transition: color 0.3s ease, opacity 0.3s ease;
        }
        .sm-scope .sm-socials-link:hover {
          color: var(--sm-accent, #5227FF);
        }
        .sm-scope .sm-panel-list {
          list-style: none;
          margin: 0;
          padding: 0;
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
        }
        .sm-scope .sm-panel-item {
          position: relative;
          color: #000;
          font-weight: 600;
          font-size: 4rem;
          cursor: pointer;
          line-height: 1;
          letter-spacing: -2px;
          text-transform: uppercase;
          transition: background 0.25s, color 0.25s;
          display: inline-block;
          text-decoration: none;
          padding-right: 1.4em;
        }
        .sm-scope .sm-panel-itemLabel {
          display: inline-block;
          will-change: transform;
          transform-origin: 50% 100%;
        }
        .sm-scope .sm-panel-item:hover {
          color: var(--sm-accent, #5227FF);
        }
        .sm-scope .sm-panel-list[data-numbering] {
          counter-reset: smItem;
        }
        .sm-scope .sm-panel-list[data-numbering] .sm-panel-item::after {
          counter-increment: smItem;
          content: counter(smItem, decimal-leading-zero);
          position: absolute;
          top: 0.1em;
          right: 3.2em;
          font-size: 18px;
          font-weight: 400;
          color: var(--sm-accent, #5227FF);
          letter-spacing: 0;
          pointer-events: none;
          user-select: none;
          opacity: var(--sm-num-opacity, 0);
        }
        @media (max-width: 1024px) {
          .sm-scope .staggered-menu-panel {
            width: 100%;
            left: 0;
            right: 0;
          }
        }
        @media (max-width: 640px) {
          .sm-scope .staggered-menu-panel {
            width: 100%;
            left: 0;
            right: 0;
          }
        }
      `
    document.head.appendChild(style)

    return () => {
      const existingStyle = document.getElementById(styleId)
      if (existingStyle) {
        existingStyle.remove()
      }
    }
  }, [])

  return (
    <div
      className={`sm-scope ${isFixed ? 'fixed top-0 left-0 w-screen h-screen' : 'w-full h-full'}`}
      style={{ pointerEvents: 'none', zIndex: 40 }}
    >
      <div
        className={
          (className ? className + ' ' : '') +
          'staggered-menu-wrapper pointer-events-none relative w-full h-full'
        }
        style={accentColor ? ({ ['--sm-accent' as any]: accentColor } as React.CSSProperties) : undefined}
        data-position={position}
        data-open={open || undefined}
      >
        {/* Overlay - removed blur and click-to-close */}

        {/* Header with logo button */}
        <header
          className="staggered-menu-header absolute top-0 left-0 w-full flex items-center p-8 bg-transparent pointer-events-none z-20"
          aria-label="Main navigation header"
        >
          <button
            onClick={toggleMenu}
            className="sm-logo flex items-center select-none pointer-events-auto cursor-pointer bg-transparent border-0 p-0 hover:opacity-80 transition-opacity"
            aria-label="Toggle menu"
            type="button"
          >
            {logoUrl ? (
              <img
                src={logoUrl}
                alt="Logo"
                className="sm-logo-img block h-8 w-auto object-contain"
                draggable={false}
              />
            ) : (
              <span className="text-xl font-semibold text-white">Polonium</span>
            )}
          </button>
        </header>

        {/* Sidebar Panel */}
        <aside
          id="staggered-menu-panel"
          ref={panelRef}
          className="staggered-menu-panel fixed top-0 left-0 h-full bg-white dark:bg-gray-900 flex flex-col overflow-y-auto z-[50] shadow-2xl"
          style={{ 
            pointerEvents: open ? 'auto' : 'none',
            opacity: open ? 1 : 0
          }}
          aria-hidden={!open}
        >
          <div className="sm-panel-inner flex-1 flex flex-col h-full">
            {/* Custom children content */}
            {children && <div className="sm-panel-custom w-full h-full flex flex-col">{children}</div>}

            {/* Menu items */}
            {items && items.length > 0 && (
              <ul
                className="sm-panel-list list-none m-0 p-0 flex flex-col gap-2"
                role="list"
                data-numbering={displayItemNumbering || undefined}
              >
                {items.map((it, idx) => (
                  <li className="sm-panel-itemWrap relative overflow-hidden leading-none" key={it.label + idx}>
                    <a
                      className="sm-panel-item relative text-black dark:text-white font-semibold text-[4rem] cursor-pointer leading-none tracking-[-2px] uppercase transition-[background,color] duration-150 ease-linear inline-block no-underline pr-[1.4em]"
                      href={it.link}
                      onClick={(e) => {
                        if (it.onClick) {
                          e.preventDefault()
                          it.onClick()
                          closeMenu()
                        }
                      }}
                      aria-label={it.ariaLabel}
                      data-index={idx + 1}
                    >
                      <span className="sm-panel-itemLabel inline-block [transform-origin:50%_100%] will-change-transform">
                        {it.label}
                      </span>
                    </a>
                  </li>
                ))}
              </ul>
            )}

            {/* Social links */}
            {displaySocials && socialItems && socialItems.length > 0 && (
              <div className="sm-socials mt-auto pt-8 flex flex-col gap-3" aria-label="Social links">
                <h3 className="sm-socials-title m-0 text-base font-medium [color:var(--sm-accent,#5227FF)]">
                  Socials
                </h3>
                <ul
                  className="sm-socials-list list-none m-0 p-0 flex flex-row items-center gap-4 flex-wrap"
                  role="list"
                >
                  {socialItems.map((s, i) => (
                    <li key={s.label + i} className="sm-socials-item">
                      <a
                        href={s.link}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="sm-socials-link text-[1.2rem] font-medium text-[#111] dark:text-white no-underline relative inline-block py-[2px] transition-[color,opacity] duration-300 ease-linear"
                      >
                        {s.label}
                      </a>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </aside>
      </div>
    </div>
  )
}

export default StaggeredMenu

