"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Search, Filter, Plus, BookOpen, Send, MoreVertical, Menu, X } from "lucide-react"

export default function AppPage() {
  const [sidebarOpen, setSidebarOpen] = useState(true)

  return (
    <div className="h-screen flex flex-col bg-neutral-950">
      {/* Top Bar */}
      <header className="h-14 border-b border-neutral-800 flex items-center justify-between px-4">
        <button
          onClick={() => setSidebarOpen(!sidebarOpen)}
          className="lg:hidden p-2 hover:bg-neutral-900 rounded-lg"
        >
          {sidebarOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
        </button>
        <div className="flex-1" />
        <button className="p-2 hover:bg-neutral-900 rounded-lg transition-colors">
          <MoreVertical className="w-5 h-5" />
        </button>
      </header>

      <div className="flex-1 flex overflow-hidden">
        {/* Left Sidebar */}
        <aside
          className={`${
            sidebarOpen ? "translate-x-0" : "-translate-x-full"
          } lg:translate-x-0 fixed lg:relative z-20 w-80 h-full bg-neutral-900 border-r border-neutral-800 flex flex-col transition-transform duration-300`}
        >
          <div className="p-4 space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-sm font-semibold text-neutral-400 uppercase tracking-wider">
                Sources
              </h2>
              <Button size="sm" className="h-8 px-3">
                <Plus className="w-4 h-4" />
                Add
              </Button>
            </div>

            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-500" />
              <Input
                placeholder="Search sources..."
                className="pl-9 h-9"
              />
            </div>

            <div className="flex gap-2">
              <Button variant="outline" size="sm" className="flex-1 h-9">
                <Filter className="w-4 h-4" />
                Web
              </Button>
              <Button variant="outline" size="sm" className="flex-1 h-9">
                <Filter className="w-4 h-4" />
                Research
              </Button>
            </div>
          </div>

          {/* Empty State */}
          <div className="flex-1 flex items-center justify-center p-8">
            <div className="text-center space-y-3">
              <div className="w-12 h-12 rounded-full bg-neutral-800 flex items-center justify-center mx-auto">
                <BookOpen className="w-6 h-6 text-neutral-500" />
              </div>
              <p className="text-sm text-neutral-500">
                Saved sources will appear here
              </p>
            </div>
          </div>
        </aside>

        {/* Main Panel */}
        <main className="flex-1 flex flex-col">
          {/* Empty State */}
          <div className="flex-1 flex items-center justify-center p-8">
            <div className="text-center space-y-4">
              <div className="w-16 h-16 rounded-2xl bg-neutral-900 border border-neutral-800 flex items-center justify-center mx-auto">
                <BookOpen className="w-8 h-8 text-neutral-500" />
              </div>
              <div>
                <h3 className="text-xl font-semibold mb-1">Untitled notebook</h3>
                <p className="text-sm text-neutral-500">0 sources</p>
              </div>
            </div>
          </div>

          {/* Bottom Input Bar */}
          <div className="p-4 border-t border-neutral-800">
            <div className="max-w-4xl mx-auto">
              <div className="relative">
                <Input
                  placeholder="Start typing..."
                  className="pr-24 h-12 rounded-2xl bg-neutral-900"
                />
                <div className="absolute right-2 top-1/2 -translate-y-1/2 flex items-center gap-2">
                  <span className="text-xs text-neutral-500">0 sources</span>
                  <Button size="sm" className="h-8 w-8 p-0 rounded-full">
                    <Send className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  )
}
