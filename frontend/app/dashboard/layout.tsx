"use client"

import { useState } from "react"
import Link from "next/link"
import Image from "next/image"
import { usePathname } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import {
  Sheet,
  SheetContent,
  SheetTrigger,
} from "@/components/ui/sheet"
import {
  Shield,
  LayoutDashboard,
  Bot,
  Plug,
  AlertCircle,
  FileSearch,
  CheckSquare,
  ScrollText,
  Settings,
  Search,
  Bell,
  ChevronDown,
  LogOut,
  Menu,
  Building2,
} from "lucide-react"
import { cn } from "@/lib/utils"

const navigation = [
  { name: "Overview", href: "/dashboard", icon: LayoutDashboard },
  { name: "Agents", href: "/dashboard/agents", icon: Bot },
  { name: "Integrations", href: "/dashboard/integrations", icon: Plug },
  { name: "Issues", href: "/dashboard/issues", icon: AlertCircle },
  { name: "Reviews", href: "/dashboard/reviews", icon: FileSearch },
  { name: "Approvals", href: "/dashboard/approvals", icon: CheckSquare },
  { name: "Policies", href: "/dashboard/policies", icon: ScrollText },
  { name: "Settings", href: "/dashboard/settings", icon: Settings },
]

function SidebarContent({ pathname }: { pathname: string }) {
  return (
    <div className="flex h-full flex-col">
      {/* Logo */}
      <div className="flex h-16 items-center border-b px-4">
        <Link href="/dashboard">
          <Image
            src="/images/logotype.png"
            alt="ContextSuite"
            width={150}
            height={38}
            className="h-8 w-auto"
          />
        </Link>
      </div>

      {/* Workspace Selector */}
      <div className="p-4 border-b">
        <Select defaultValue="acme">
          <SelectTrigger className="w-full">
            <div className="flex items-center gap-2">
              <Building2 className="h-4 w-4" />
              <SelectValue placeholder="Select workspace" />
            </div>
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="acme">Acme Corp</SelectItem>
            <SelectItem value="startup">My Startup</SelectItem>
            <SelectItem value="personal">Personal</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-1 p-4">
        {navigation.map((item) => {
          const isActive = pathname === item.href || 
            (item.href !== "/dashboard" && pathname.startsWith(item.href))
          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                isActive
                  ? "bg-primary text-primary-foreground"
                  : "text-muted-foreground hover:bg-muted hover:text-foreground"
              )}
            >
              <item.icon className="h-5 w-5" />
              {item.name}
              {item.name === "Approvals" && (
                <Badge variant="secondary" className="ml-auto text-xs">
                  3
                </Badge>
              )}
              {item.name === "Issues" && (
                <Badge variant="destructive" className="ml-auto text-xs">
                  5
                </Badge>
              )}
            </Link>
          )
        })}
      </nav>

      {/* Bottom section */}
      <div className="border-t p-4">
        <div className="rounded-lg bg-muted p-3">
          <p className="text-xs font-medium">Free Plan</p>
          <p className="text-xs text-muted-foreground mt-1">3 of 5 agents used</p>
          <Button size="sm" className="w-full mt-2">
            Upgrade to Pro
          </Button>
        </div>
      </div>
    </div>
  )
}

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const pathname = usePathname()
  const [searchQuery, setSearchQuery] = useState("")

  return (
    <div className="min-h-screen bg-background">
      {/* Mobile Header */}
      <header className="sticky top-0 z-50 flex h-16 items-center gap-4 border-b bg-background px-4 lg:hidden">
        <Sheet>
          <SheetTrigger asChild>
            <Button variant="ghost" size="icon">
              <Menu className="h-5 w-5" />
            </Button>
          </SheetTrigger>
          <SheetContent side="left" className="w-72 p-0">
            <SidebarContent pathname={pathname} />
          </SheetContent>
        </Sheet>
        <Link href="/dashboard">
          <Image
            src="/images/logotype.png"
            alt="ContextSuite"
            width={140}
            height={35}
            className="h-7 w-auto"
          />
        </Link>
      </header>

      <div className="flex">
        {/* Desktop Sidebar */}
        <aside className="hidden lg:flex h-screen w-64 flex-col border-r bg-background sticky top-0">
          <SidebarContent pathname={pathname} />
        </aside>

        {/* Main Content */}
        <div className="flex-1 flex flex-col min-h-screen">
          {/* Top Bar */}
          <header className="sticky top-0 z-40 h-16 border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
            <div className="flex h-full items-center justify-between px-6">
              {/* Global Search */}
              <div className="relative w-full max-w-md">
                <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  placeholder="Search agents, reviews, issues..."
                  className="pl-10"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </div>

              {/* Right Actions */}
              <div className="flex items-center gap-4">
                {/* Notifications */}
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="ghost" size="icon" className="relative">
                      <Bell className="h-5 w-5" />
                      <span className="absolute -top-1 -right-1 h-4 w-4 rounded-full bg-destructive text-[10px] font-medium text-destructive-foreground flex items-center justify-center">
                        3
                      </span>
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end" className="w-80">
                    <DropdownMenuLabel>Notifications</DropdownMenuLabel>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem className="flex flex-col items-start gap-1 py-3">
                      <div className="flex items-center gap-2">
                        <Badge variant="destructive" className="h-2 w-2 p-0 rounded-full" />
                        <span className="font-medium">Plan blocked by policy</span>
                      </div>
                      <span className="text-xs text-muted-foreground">Agent "cursor-main" attempted high-risk action</span>
                    </DropdownMenuItem>
                    <DropdownMenuItem className="flex flex-col items-start gap-1 py-3">
                      <div className="flex items-center gap-2">
                        <Badge className="h-2 w-2 p-0 rounded-full bg-[#F5A524]" />
                        <span className="font-medium">Approval required</span>
                      </div>
                      <span className="text-xs text-muted-foreground">Database migration needs review</span>
                    </DropdownMenuItem>
                    <DropdownMenuItem className="flex flex-col items-start gap-1 py-3">
                      <div className="flex items-center gap-2">
                        <Badge className="h-2 w-2 p-0 rounded-full bg-[#18C29C]" />
                        <span className="font-medium">GitHub connected</span>
                      </div>
                      <span className="text-xs text-muted-foreground">Successfully linked acme/webapp</span>
                    </DropdownMenuItem>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem className="justify-center text-primary">
                      View all notifications
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>

                {/* User Menu */}
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="ghost" className="flex items-center gap-2">
                      <Avatar className="h-8 w-8">
                        <AvatarFallback className="bg-primary text-primary-foreground">AD</AvatarFallback>
                      </Avatar>
                      <span className="hidden md:inline">Admin</span>
                      <ChevronDown className="h-4 w-4" />
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end" className="w-56">
                    <DropdownMenuLabel>My Account</DropdownMenuLabel>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem asChild>
                      <Link href="/dashboard/settings">
                        <Settings className="mr-2 h-4 w-4" />
                        Settings
                      </Link>
                    </DropdownMenuItem>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem asChild>
                      <Link href="/login" className="flex items-center text-destructive">
                        <LogOut className="mr-2 h-4 w-4" />
                        Log out
                      </Link>
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </div>
            </div>
          </header>

          {/* Page Content */}
          <main className="flex-1 p-6">
            {children}
          </main>
        </div>
      </div>
    </div>
  )
}
