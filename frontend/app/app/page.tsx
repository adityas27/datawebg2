"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Search, Plus, BookOpen, Send, ChevronRight, Tag, Clock, Zap } from "lucide-react"

export default function AppPage() {
  const [rightPanelOpen, setRightPanelOpen] = useState(true)

  return (
    <div className="h-screen flex flex-col relative overflow-hidden">
      {/* Gradient Background */}
      <div className="absolute inset-0 bg-gradient-to-b from-black via-neutral-950 to-black" />
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,rgba(16,185,129,0.05),transparent_70%)]" />

      {/* Top Bar */}
      <header className="relative z-10 h-16 border-b border-white/10 flex items-center justify-between px-6 backdrop-blur-xl bg-neutral-950/80">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-emerald-500 to-emerald-600 flex items-center justify-center">
            <BookOpen className="w-5 h-5 text-white" />
          </div>
          <span className="font-semibold text-base">DataWeb</span>
        </div>
      </header>

      <div className="relative z-10 flex-1 flex overflow-hidden">
        {/* Left Sidebar - Sources */}
        <aside className="w-[260px] border-r border-white/10 flex flex-col backdrop-blur-xl bg-neutral-950/80">
          <div className="p-4 space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-sm font-semibold text-neutral-300 uppercase tracking-wider">
                Sources
              </h2>
              <Button size="sm" className="h-9 px-3 bg-emerald-600 hover:bg-emerald-700 text-base font-medium">
                <Plus className="w-4 h-4" />
              </Button>
            </div>

            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-400" />
              <Input
                placeholder="Search..."
                className="pl-10 h-12 bg-neutral-900/80 border-white/10 text-lg"
              />
            </div>
          </div>

          {/* Empty State */}
          <div className="flex-1 flex items-center justify-center p-6">
            <div className="text-center space-y-2">
              <div className="w-12 h-12 rounded-xl bg-neutral-900/80 border border-white/10 flex items-center justify-center mx-auto">
                <BookOpen className="w-6 h-6 text-neutral-500" />
              </div>
              <p className="text-sm text-neutral-500">
                No sources yet
              </p>
            </div>
          </div>
        </aside>

        {/* Main Panel */}
        <main className="flex-1 flex flex-col relative">
          {/* Radial Glow */}
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_40%,rgba(16,185,129,0.05),transparent_60%)] pointer-events-none" />
          
          {/* Empty State */}
          <div className="flex-1 flex items-center justify-center relative z-10">
            <div className="text-center space-y-6 max-w-2xl mx-auto px-6">
              <div className="w-20 h-20 rounded-3xl bg-gradient-to-br from-neutral-900/80 to-neutral-900/40 backdrop-blur-xl border border-white/10 flex items-center justify-center mx-auto shadow-2xl">
                <BookOpen className="w-10 h-10 text-emerald-500/60" />
              </div>
              <div className="space-y-2">
                <h3 className="text-3xl font-semibold tracking-tight">Start a conversation</h3>
                <p className="text-lg text-neutral-500">Ask anything or add sources to begin</p>
              </div>
              
              {/* Search Bar */}
              <div className="relative pt-4 w-full max-w-3xl">
                <div className="relative rounded-2xl bg-neutral-900/80 backdrop-blur-xl border border-emerald-500/50 shadow-[0_0_40px_rgba(16,185,129,0.2)] transition-all hover:border-emerald-500/70">
                  <Input
                    placeholder="Start typing..."
                    className="h-16 pr-36 bg-transparent border-0 text-lg placeholder:text-neutral-400"
                  />
                  <div className="absolute right-2 top-1/2 -translate-y-1/2 flex items-center gap-2">
                    <span className="text-sm text-neutral-400 px-2">0</span>
                    <Button size="sm" className="h-10 w-10 p-0 rounded-xl bg-emerald-600 hover:bg-emerald-700">
                      <Send className="w-5 h-5" />
                    </Button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </main>

        {/* Right Panel - Context */}
        {rightPanelOpen && (
          <aside className="w-[320px] border-l border-white/10 backdrop-blur-xl bg-neutral-900/80 flex flex-col">
            <div className="p-4 border-b border-white/10 flex items-center justify-between">
              <h2 className="text-sm font-semibold text-neutral-300 uppercase tracking-wider">
                Context
              </h2>
              <button 
                onClick={() => setRightPanelOpen(false)}
                className="p-1.5 hover:bg-white/10 rounded transition-colors"
              >
                <ChevronRight className="w-5 h-5 text-neutral-400" />
              </button>
            </div>

            <div className="flex-1 overflow-auto p-4 space-y-6">
              {/* Metadata */}
              <div className="space-y-2">
                <div className="text-sm text-neutral-300 uppercase tracking-wider">Metadata</div>
              </div>
            </div>
          </aside>
        )}

        {/* Collapsed Right Panel Toggle */}
        {!rightPanelOpen && (
          <button
            onClick={() => setRightPanelOpen(true)}
            className="absolute right-4 top-4 z-20 p-2.5 rounded-lg bg-neutral-900/80 backdrop-blur-xl border border-white/10 hover:border-emerald-500/50 transition-all"
          >
            <ChevronRight className="w-5 h-5 rotate-180" />
          </button>
        )}
      </div>
    </div>
  )
}
