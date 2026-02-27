import Link from "next/link"
import { Sparkles, ArrowRight, Database, Zap, Shield } from "lucide-react"
import { Button } from "@/components/ui/button"

export default function Home() {
  return (
    <div className="min-h-screen bg-black relative overflow-hidden">
      {/* Background gradient */}
      <div className="absolute inset-0 bg-gradient-to-b from-black via-neutral-950 to-green-950/20" />
      
      {/* Bottom glow */}
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_120%,rgba(16,185,129,0.15),transparent_55%)]" />
      
      {/* Dotted grid */}
      <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAiIGhlaWdodD0iNDAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PGNpcmNsZSBjeD0iMSIgY3k9IjEiIHI9IjEiIGZpbGw9InJnYmEoMjU1LDI1NSwyNTUsMC4wNCkiLz48L3N2Zz4=')] opacity-40" />

      <div className="relative z-10">
        {/* Header */}
        <header className="flex items-center justify-between px-6 py-6 max-w-7xl mx-auto">
          <div className="flex items-center gap-2">
            <Sparkles className="w-6 h-6 text-green-500" />
            <span className="text-xl font-bold">DataWeb</span>
          </div>
          <Link href="/login">
            <Button variant="outline" className="border-neutral-800 hover:border-green-500">
              Login
            </Button>
          </Link>
        </header>

        {/* Hero */}
        <div className="max-w-6xl mx-auto px-6 py-24 text-center space-y-8">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-green-950/30 border border-green-900/50 text-sm text-green-400">
            <Sparkles className="w-4 h-4" />
            Modern Research Platform
          </div>
          
          <h1 className="text-5xl md:text-7xl font-bold tracking-tight leading-tight">
            Your Data,{" "}
            <span className="text-green-500 drop-shadow-[0_0_30px_rgba(16,185,129,0.5)]">
              Simplified
            </span>
          </h1>

          <p className="text-xl text-neutral-400 max-w-2xl mx-auto">
            Organize, analyze, and collaborate on your research with our intuitive notebook-style interface.
          </p>

          <div className="flex flex-wrap gap-4 justify-center pt-4">
            <Link href="/login">
              <Button size="lg" className="h-12 px-8 bg-green-600 hover:bg-green-700 text-base">
                Get Started
                <ArrowRight className="w-5 h-5 ml-2" />
              </Button>
            </Link>
            <Link href="/signup">
              <Button size="lg" variant="outline" className="h-12 px-8 border-neutral-800 hover:border-green-500 text-base">
                Sign Up Free
              </Button>
            </Link>
          </div>
        </div>

        {/* Features */}
        <div className="max-w-6xl mx-auto px-6 py-16 grid md:grid-cols-3 gap-8">
          <div className="p-6 rounded-2xl bg-neutral-900/50 border border-neutral-800 hover:border-green-900/50 transition-colors">
            <div className="w-12 h-12 rounded-xl bg-green-950/50 flex items-center justify-center mb-4">
              <Database className="w-6 h-6 text-green-500" />
            </div>
            <h3 className="text-lg font-semibold mb-2">Organized Research</h3>
            <p className="text-neutral-400 text-sm">Keep all your sources and notes in one place with our notebook interface.</p>
          </div>
          
          <div className="p-6 rounded-2xl bg-neutral-900/50 border border-neutral-800 hover:border-green-900/50 transition-colors">
            <div className="w-12 h-12 rounded-xl bg-green-950/50 flex items-center justify-center mb-4">
              <Zap className="w-6 h-6 text-green-500" />
            </div>
            <h3 className="text-lg font-semibold mb-2">Lightning Fast</h3>
            <p className="text-neutral-400 text-sm">Built with modern tech for instant search and seamless performance.</p>
          </div>
          
          <div className="p-6 rounded-2xl bg-neutral-900/50 border border-neutral-800 hover:border-green-900/50 transition-colors">
            <div className="w-12 h-12 rounded-xl bg-green-950/50 flex items-center justify-center mb-4">
              <Shield className="w-6 h-6 text-green-500" />
            </div>
            <h3 className="text-lg font-semibold mb-2">Secure & Private</h3>
            <p className="text-neutral-400 text-sm">Your data is encrypted and protected with enterprise-grade security.</p>
          </div>
        </div>
      </div>
    </div>
  )
}