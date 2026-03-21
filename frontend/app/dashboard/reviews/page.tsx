"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
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
  FileSearch,
  Search,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Clock,
  GitBranch,
  Eye,
  RefreshCw,
  Filter,
  TrendingUp,
} from "lucide-react"

const reviews = [
  { id: "REV-001", title: "Add user authentication flow", status: "passed", riskLevel: "low", agent: "cursor-main", time: "2 min ago", duration: "0.8s", matchedIssues: 0, matchedConstraints: 2 },
  { id: "REV-002", title: "Refactor payment processing", status: "blocked", riskLevel: "high", agent: "copilot-api", time: "15 min ago", duration: "1.2s", matchedIssues: 3, matchedConstraints: 5 },
  { id: "REV-003", title: "Update API rate limiting", status: "warning", riskLevel: "medium", agent: "claude-docs", time: "1 hour ago", duration: "0.9s", matchedIssues: 1, matchedConstraints: 3 },
  { id: "REV-004", title: "Fix database connection pooling", status: "passed", riskLevel: "low", agent: "cursor-main", time: "2 hours ago", duration: "0.7s", matchedIssues: 0, matchedConstraints: 1 },
  { id: "REV-005", title: "Implement caching layer", status: "passed", riskLevel: "low", agent: "v0-frontend", time: "3 hours ago", duration: "1.1s", matchedIssues: 0, matchedConstraints: 4 },
  { id: "REV-006", title: "Add email notification service", status: "passed", riskLevel: "medium", agent: "cursor-main", time: "4 hours ago", duration: "0.6s", matchedIssues: 0, matchedConstraints: 2 },
  { id: "REV-007", title: "Migrate to new auth provider", status: "blocked", riskLevel: "high", agent: "copilot-api", time: "5 hours ago", duration: "1.5s", matchedIssues: 2, matchedConstraints: 6 },
  { id: "REV-008", title: "Update user permissions", status: "warning", riskLevel: "medium", agent: "claude-docs", time: "6 hours ago", duration: "0.8s", matchedIssues: 1, matchedConstraints: 3 },
  { id: "REV-009", title: "Add analytics tracking", status: "passed", riskLevel: "low", agent: "v0-frontend", time: "8 hours ago", duration: "0.5s", matchedIssues: 0, matchedConstraints: 1 },
  { id: "REV-010", title: "Refactor API endpoints", status: "passed", riskLevel: "low", agent: "cursor-main", time: "10 hours ago", duration: "0.9s", matchedIssues: 0, matchedConstraints: 2 },
]

export default function ReviewsPage() {
  const [filterStatus, setFilterStatus] = useState("all")
  const [filterRisk, setFilterRisk] = useState("all")
  const [searchQuery, setSearchQuery] = useState("")
  const [showDetailDialog, setShowDetailDialog] = useState<typeof reviews[0] | null>(null)

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "passed":
        return <CheckCircle className="h-4 w-4 text-[#18C29C]" />
      case "blocked":
        return <XCircle className="h-4 w-4 text-destructive" />
      case "warning":
        return <AlertTriangle className="h-4 w-4 text-[#F5A524]" />
      default:
        return <Clock className="h-4 w-4 text-muted-foreground" />
    }
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "passed":
        return <Badge className="bg-[#18C29C]/10 text-[#18C29C]">Passed</Badge>
      case "blocked":
        return <Badge variant="destructive">Blocked</Badge>
      case "warning":
        return <Badge className="bg-[#F5A524]/10 text-[#F5A524]">Warning</Badge>
      default:
        return <Badge variant="secondary">Pending</Badge>
    }
  }

  const getRiskBadge = (level: string) => {
    switch (level) {
      case "high":
        return <Badge variant="outline" className="border-destructive text-destructive">High</Badge>
      case "medium":
        return <Badge variant="outline" className="border-[#F5A524] text-[#F5A524]">Medium</Badge>
      case "low":
        return <Badge variant="outline" className="border-[#18C29C] text-[#18C29C]">Low</Badge>
      default:
        return <Badge variant="outline">Unknown</Badge>
    }
  }

  const filteredReviews = reviews.filter(review => {
    if (filterStatus !== "all" && review.status !== filterStatus) return false
    if (filterRisk !== "all" && review.riskLevel !== filterRisk) return false
    if (searchQuery && !review.title.toLowerCase().includes(searchQuery.toLowerCase())) return false
    return true
  })

  return (
    <div className="mx-auto max-w-7xl space-y-6">
      {/* Page Header */}
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Reviews</h1>
          <p className="text-muted-foreground">AI code plan reviews and regression checks.</p>
        </div>
        <Button variant="outline">
          <RefreshCw className="mr-2 h-4 w-4" />
          Refresh
        </Button>
      </div>

      {/* Stats */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Total Reviews</CardTitle>
            <FileSearch className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{reviews.length}</div>
            <p className="text-xs text-muted-foreground">Last 24 hours</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Pass Rate</CardTitle>
            <TrendingUp className="h-4 w-4 text-[#18C29C]" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-[#18C29C]">
              {Math.round((reviews.filter(r => r.status === "passed").length / reviews.length) * 100)}%
            </div>
            <p className="text-xs text-muted-foreground">Reviews passing</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Blocked</CardTitle>
            <XCircle className="h-4 w-4 text-destructive" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-destructive">{reviews.filter(r => r.status === "blocked").length}</div>
            <p className="text-xs text-muted-foreground">Regressions prevented</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Avg. Time</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">0.9s</div>
            <p className="text-xs text-muted-foreground">Per review</p>
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
                placeholder="Search reviews..."
                className="pl-10"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
            <div className="flex gap-2">
              <Select value={filterStatus} onValueChange={setFilterStatus}>
                <SelectTrigger className="w-[130px]">
                  <SelectValue placeholder="Status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Status</SelectItem>
                  <SelectItem value="passed">Passed</SelectItem>
                  <SelectItem value="warning">Warning</SelectItem>
                  <SelectItem value="blocked">Blocked</SelectItem>
                </SelectContent>
              </Select>
              <Select value={filterRisk} onValueChange={setFilterRisk}>
                <SelectTrigger className="w-[130px]">
                  <SelectValue placeholder="Risk" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Risk</SelectItem>
                  <SelectItem value="low">Low</SelectItem>
                  <SelectItem value="medium">Medium</SelectItem>
                  <SelectItem value="high">High</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Reviews Table */}
      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-[50px]"></TableHead>
                <TableHead>Review</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Risk</TableHead>
                <TableHead>Agent</TableHead>
                <TableHead>Matches</TableHead>
                <TableHead>Duration</TableHead>
                <TableHead>Time</TableHead>
                <TableHead className="w-[50px]"></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredReviews.map((review) => (
                <TableRow key={review.id} className="cursor-pointer hover:bg-muted/50" onClick={() => setShowDetailDialog(review)}>
                  <TableCell>{getStatusIcon(review.status)}</TableCell>
                  <TableCell>
                    <div>
                      <p className="font-medium">{review.title}</p>
                      <p className="text-xs text-muted-foreground font-mono">{review.id}</p>
                    </div>
                  </TableCell>
                  <TableCell>{getStatusBadge(review.status)}</TableCell>
                  <TableCell>{getRiskBadge(review.riskLevel)}</TableCell>
                  <TableCell>
                    <div className="flex items-center gap-1">
                      <GitBranch className="h-3 w-3 text-muted-foreground" />
                      {review.agent}
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="text-sm">
                      <span className={review.matchedIssues > 0 ? "text-destructive" : "text-muted-foreground"}>
                        {review.matchedIssues} issues
                      </span>
                      <span className="text-muted-foreground"> / </span>
                      <span className="text-muted-foreground">{review.matchedConstraints} constraints</span>
                    </div>
                  </TableCell>
                  <TableCell className="font-mono text-sm">{review.duration}</TableCell>
                  <TableCell className="text-muted-foreground">{review.time}</TableCell>
                  <TableCell>
                    <Button variant="ghost" size="icon" onClick={(e) => { e.stopPropagation(); setShowDetailDialog(review); }}>
                      <Eye className="h-4 w-4" />
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Detail Dialog */}
      <Dialog open={!!showDetailDialog} onOpenChange={() => setShowDetailDialog(null)}>
        <DialogContent className="sm:max-w-2xl">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              {showDetailDialog && getStatusIcon(showDetailDialog.status)}
              {showDetailDialog?.title}
            </DialogTitle>
            <DialogDescription className="font-mono">{showDetailDialog?.id}</DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="flex flex-wrap gap-2">
              {showDetailDialog && getStatusBadge(showDetailDialog.status)}
              {showDetailDialog && getRiskBadge(showDetailDialog.riskLevel)}
              <Badge variant="outline">{showDetailDialog?.agent}</Badge>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="rounded-lg border p-4">
                <p className="text-sm text-muted-foreground mb-1">Review Duration</p>
                <p className="text-2xl font-bold">{showDetailDialog?.duration}</p>
              </div>
              <div className="rounded-lg border p-4">
                <p className="text-sm text-muted-foreground mb-1">Memory Matches</p>
                <p className="text-2xl font-bold">
                  <span className={showDetailDialog?.matchedIssues ? "text-destructive" : ""}>{showDetailDialog?.matchedIssues}</span>
                  <span className="text-muted-foreground text-base"> issues</span>
                  <span className="text-muted-foreground text-base"> / </span>
                  <span>{showDetailDialog?.matchedConstraints}</span>
                  <span className="text-muted-foreground text-base"> constraints</span>
                </p>
              </div>
            </div>

            {showDetailDialog?.status === "blocked" && (
              <div className="rounded-lg border border-destructive/50 bg-destructive/5 p-4">
                <h4 className="font-medium text-destructive mb-2">Blocking Issues</h4>
                <ul className="text-sm space-y-1 text-muted-foreground">
                  <li>- Historical issue #ISS-005: Similar payment flow caused race condition</li>
                  <li>- Constraint violation: "No direct database writes in payment module"</li>
                  <li>- Policy: High-risk changes require human approval</li>
                </ul>
              </div>
            )}

            {showDetailDialog?.status === "warning" && (
              <div className="rounded-lg border border-[#F5A524]/50 bg-[#F5A524]/5 p-4">
                <h4 className="font-medium text-[#F5A524] mb-2">Warnings</h4>
                <ul className="text-sm space-y-1 text-muted-foreground">
                  <li>- Medium risk: Changes affect shared utilities</li>
                  <li>- 1 similar issue found in memory (resolved)</li>
                </ul>
              </div>
            )}

            <div>
              <h4 className="font-medium mb-2">Review Summary</h4>
              <p className="text-sm text-muted-foreground">
                This plan was reviewed against {showDetailDialog?.matchedConstraints} active constraints and checked for similarity with {showDetailDialog?.matchedIssues} historical issues. 
                {showDetailDialog?.status === "passed" && " No blocking issues were found."}
                {showDetailDialog?.status === "blocked" && " The review was blocked due to policy violations."}
                {showDetailDialog?.status === "warning" && " Some concerns were identified but the plan can proceed with caution."}
              </p>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowDetailDialog(null)}>Close</Button>
            <Button variant="outline">View Full Report</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
