"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import {
  AlertCircle,
  Plus,
  Filter,
  Search,
  MoreVertical,
  Eye,
  CheckCircle,
  XCircle,
  Clock,
  AlertTriangle,
} from "lucide-react"
import { toast } from "sonner"

const initialIssues = [
  { id: "ISS-001", title: "Auth token exposed in logs", severity: "high", status: "open", agent: "cursor-main", detected: "2 hours ago", category: "Security" },
  { id: "ISS-002", title: "Database connection leak", severity: "high", status: "open", agent: "copilot-api", detected: "4 hours ago", category: "Performance" },
  { id: "ISS-003", title: "Missing input validation", severity: "medium", status: "investigating", agent: "cursor-main", detected: "1 day ago", category: "Security" },
  { id: "ISS-004", title: "Deprecated API usage", severity: "low", status: "resolved", agent: "claude-docs", detected: "2 days ago", category: "Compatibility" },
  { id: "ISS-005", title: "Race condition in payment flow", severity: "high", status: "open", agent: "copilot-api", detected: "3 hours ago", category: "Logic" },
  { id: "ISS-006", title: "Memory leak in worker", severity: "medium", status: "investigating", agent: "cursor-main", detected: "5 hours ago", category: "Performance" },
  { id: "ISS-007", title: "SQL injection vulnerability", severity: "high", status: "resolved", agent: "copilot-api", detected: "3 days ago", category: "Security" },
  { id: "ISS-008", title: "Incorrect error handling", severity: "low", status: "open", agent: "claude-docs", detected: "1 day ago", category: "Error Handling" },
]

export default function IssuesPage() {
  const [issues, setIssues] = useState(initialIssues)
  const [showCreateDialog, setShowCreateDialog] = useState(false)
  const [showDetailDialog, setShowDetailDialog] = useState<typeof initialIssues[0] | null>(null)
  const [filterSeverity, setFilterSeverity] = useState("all")
  const [filterStatus, setFilterStatus] = useState("all")
  const [searchQuery, setSearchQuery] = useState("")

  const [newIssue, setNewIssue] = useState({
    title: "",
    description: "",
    severity: "medium",
    category: "Security",
  })

  const getSeverityBadge = (severity: string) => {
    switch (severity) {
      case "high":
        return <Badge variant="destructive">High</Badge>
      case "medium":
        return <Badge className="bg-[#F5A524]/10 text-[#F5A524]">Medium</Badge>
      case "low":
        return <Badge className="bg-[#18C29C]/10 text-[#18C29C]">Low</Badge>
      default:
        return <Badge variant="outline">Unknown</Badge>
    }
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "open":
        return <Badge variant="outline" className="border-destructive text-destructive"><AlertCircle className="mr-1 h-3 w-3" />Open</Badge>
      case "investigating":
        return <Badge variant="outline" className="border-[#F5A524] text-[#F5A524]"><Clock className="mr-1 h-3 w-3" />Investigating</Badge>
      case "resolved":
        return <Badge variant="outline" className="border-[#18C29C] text-[#18C29C]"><CheckCircle className="mr-1 h-3 w-3" />Resolved</Badge>
      default:
        return <Badge variant="outline">Unknown</Badge>
    }
  }

  const filteredIssues = issues.filter(issue => {
    if (filterSeverity !== "all" && issue.severity !== filterSeverity) return false
    if (filterStatus !== "all" && issue.status !== filterStatus) return false
    if (searchQuery && !issue.title.toLowerCase().includes(searchQuery.toLowerCase())) return false
    return true
  })

  const handleCreateIssue = () => {
    const issue = {
      id: `ISS-${String(issues.length + 1).padStart(3, "0")}`,
      title: newIssue.title,
      severity: newIssue.severity,
      status: "open" as const,
      agent: "Manual",
      detected: "Just now",
      category: newIssue.category,
    }
    setIssues([issue, ...issues])
    setShowCreateDialog(false)
    setNewIssue({ title: "", description: "", severity: "medium", category: "Security" })
    toast.success("Issue logged successfully")
  }

  const updateIssueStatus = (issueId: string, newStatus: string) => {
    setIssues(issues.map(i => i.id === issueId ? { ...i, status: newStatus } : i))
    toast.success(`Issue marked as ${newStatus}`)
    setShowDetailDialog(null)
  }

  return (
    <div className="mx-auto max-w-7xl space-y-6">
      {/* Page Header */}
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Issues</h1>
          <p className="text-muted-foreground">Track and manage detected issues across your agents.</p>
        </div>
        <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              Log Issue
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Log New Issue</DialogTitle>
              <DialogDescription>Manually log an issue for tracking.</DialogDescription>
            </DialogHeader>
            <div className="space-y-4 py-4">
              <div className="space-y-2">
                <Label>Title *</Label>
                <Input
                  placeholder="Brief description of the issue"
                  value={newIssue.title}
                  onChange={(e) => setNewIssue({ ...newIssue, title: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label>Description</Label>
                <Textarea
                  placeholder="Detailed description..."
                  value={newIssue.description}
                  onChange={(e) => setNewIssue({ ...newIssue, description: e.target.value })}
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Severity</Label>
                  <Select value={newIssue.severity} onValueChange={(v) => setNewIssue({ ...newIssue, severity: v })}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="high">High</SelectItem>
                      <SelectItem value="medium">Medium</SelectItem>
                      <SelectItem value="low">Low</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label>Category</Label>
                  <Select value={newIssue.category} onValueChange={(v) => setNewIssue({ ...newIssue, category: v })}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="Security">Security</SelectItem>
                      <SelectItem value="Performance">Performance</SelectItem>
                      <SelectItem value="Logic">Logic</SelectItem>
                      <SelectItem value="Compatibility">Compatibility</SelectItem>
                      <SelectItem value="Error Handling">Error Handling</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setShowCreateDialog(false)}>Cancel</Button>
              <Button onClick={handleCreateIssue} disabled={!newIssue.title}>Log Issue</Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      {/* Stats */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Open Issues</CardTitle>
            <AlertCircle className="h-4 w-4 text-destructive" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-destructive">{issues.filter(i => i.status === "open").length}</div>
            <p className="text-xs text-muted-foreground">Requiring attention</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Investigating</CardTitle>
            <Clock className="h-4 w-4 text-[#F5A524]" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-[#F5A524]">{issues.filter(i => i.status === "investigating").length}</div>
            <p className="text-xs text-muted-foreground">In progress</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Resolved</CardTitle>
            <CheckCircle className="h-4 w-4 text-[#18C29C]" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-[#18C29C]">{issues.filter(i => i.status === "resolved").length}</div>
            <p className="text-xs text-muted-foreground">Fixed this week</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">High Severity</CardTitle>
            <AlertTriangle className="h-4 w-4 text-destructive" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{issues.filter(i => i.severity === "high" && i.status !== "resolved").length}</div>
            <p className="text-xs text-muted-foreground">Active critical issues</p>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="p-4">
          <div className="flex flex-col gap-4 md:flex-row md:items-center">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                placeholder="Search issues..."
                className="pl-10"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
            <div className="flex gap-2">
              <Select value={filterSeverity} onValueChange={setFilterSeverity}>
                <SelectTrigger className="w-[140px]">
                  <SelectValue placeholder="Severity" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Severity</SelectItem>
                  <SelectItem value="high">High</SelectItem>
                  <SelectItem value="medium">Medium</SelectItem>
                  <SelectItem value="low">Low</SelectItem>
                </SelectContent>
              </Select>
              <Select value={filterStatus} onValueChange={setFilterStatus}>
                <SelectTrigger className="w-[140px]">
                  <SelectValue placeholder="Status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Status</SelectItem>
                  <SelectItem value="open">Open</SelectItem>
                  <SelectItem value="investigating">Investigating</SelectItem>
                  <SelectItem value="resolved">Resolved</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Issues Table */}
      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>ID</TableHead>
                <TableHead>Title</TableHead>
                <TableHead>Severity</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Agent</TableHead>
                <TableHead>Category</TableHead>
                <TableHead>Detected</TableHead>
                <TableHead className="w-[50px]"></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredIssues.map((issue) => (
                <TableRow key={issue.id} className="cursor-pointer hover:bg-muted/50" onClick={() => setShowDetailDialog(issue)}>
                  <TableCell className="font-mono text-sm">{issue.id}</TableCell>
                  <TableCell className="font-medium">{issue.title}</TableCell>
                  <TableCell>{getSeverityBadge(issue.severity)}</TableCell>
                  <TableCell>{getStatusBadge(issue.status)}</TableCell>
                  <TableCell>{issue.agent}</TableCell>
                  <TableCell><Badge variant="outline">{issue.category}</Badge></TableCell>
                  <TableCell className="text-muted-foreground">{issue.detected}</TableCell>
                  <TableCell>
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild onClick={(e) => e.stopPropagation()}>
                        <Button variant="ghost" size="icon">
                          <MoreVertical className="h-4 w-4" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuItem onClick={(e) => { e.stopPropagation(); setShowDetailDialog(issue); }}>
                          <Eye className="mr-2 h-4 w-4" />
                          View Details
                        </DropdownMenuItem>
                        <DropdownMenuItem onClick={(e) => { e.stopPropagation(); updateIssueStatus(issue.id, "resolved"); }}>
                          <CheckCircle className="mr-2 h-4 w-4" />
                          Mark Resolved
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Detail Dialog */}
      <Dialog open={!!showDetailDialog} onOpenChange={() => setShowDetailDialog(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <span className="font-mono text-sm text-muted-foreground">{showDetailDialog?.id}</span>
              {showDetailDialog?.title}
            </DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="flex gap-4">
              {showDetailDialog && getSeverityBadge(showDetailDialog.severity)}
              {showDetailDialog && getStatusBadge(showDetailDialog.status)}
              <Badge variant="outline">{showDetailDialog?.category}</Badge>
            </div>
            <div className="rounded-lg bg-muted p-4 space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Detected by:</span>
                <span className="font-medium">{showDetailDialog?.agent}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Detected:</span>
                <span>{showDetailDialog?.detected}</span>
              </div>
            </div>
            <div>
              <h4 className="font-medium mb-2">Description</h4>
              <p className="text-sm text-muted-foreground">
                This issue was automatically detected during a code plan review. The agent identified a potential {showDetailDialog?.category.toLowerCase()} concern that could impact the application.
              </p>
            </div>
          </div>
          <DialogFooter className="flex-col gap-2 sm:flex-row">
            <Button variant="outline" onClick={() => setShowDetailDialog(null)}>Close</Button>
            {showDetailDialog?.status !== "resolved" && (
              <>
                <Button variant="outline" onClick={() => updateIssueStatus(showDetailDialog?.id || "", "investigating")}>
                  <Clock className="mr-2 h-4 w-4" />
                  Mark Investigating
                </Button>
                <Button onClick={() => updateIssueStatus(showDetailDialog?.id || "", "resolved")}>
                  <CheckCircle className="mr-2 h-4 w-4" />
                  Mark Resolved
                </Button>
              </>
            )}
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
