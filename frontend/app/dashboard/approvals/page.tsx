"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Textarea } from "@/components/ui/textarea"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import {
  CheckSquare,
  Clock,
  CheckCircle,
  XCircle,
  AlertTriangle,
  GitBranch,
  User,
  MessageSquare,
} from "lucide-react"
import { toast } from "sonner"

const initialApprovals = [
  {
    id: "APR-001",
    title: "Database migration for user table",
    agent: "cursor-main",
    riskLevel: "high",
    status: "pending",
    requestedAt: "10 minutes ago",
    requestedBy: "cursor-main",
    reason: "High-risk schema change affecting user data",
    changes: ["Add new column 'last_login' to users table", "Create index on email column", "Update existing records with default values"],
  },
  {
    id: "APR-002",
    title: "Payment gateway integration update",
    agent: "copilot-api",
    riskLevel: "high",
    status: "pending",
    requestedAt: "25 minutes ago",
    requestedBy: "copilot-api",
    reason: "Changes to payment processing logic require approval",
    changes: ["Update Stripe API version", "Modify payment intent creation flow", "Add new webhook handlers"],
  },
  {
    id: "APR-003",
    title: "User permissions refactor",
    agent: "claude-docs",
    riskLevel: "medium",
    status: "pending",
    requestedAt: "1 hour ago",
    requestedBy: "claude-docs",
    reason: "Medium-risk change affecting access control",
    changes: ["Refactor role-based access control", "Add new permission types", "Update admin dashboard"],
  },
  {
    id: "APR-004",
    title: "API rate limiting changes",
    agent: "cursor-main",
    riskLevel: "medium",
    status: "approved",
    requestedAt: "2 hours ago",
    requestedBy: "cursor-main",
    approvedAt: "1 hour ago",
    approvedBy: "Admin",
    reason: "Rate limit threshold changes",
    changes: ["Increase rate limit to 1000 req/min", "Add burst allowance"],
  },
  {
    id: "APR-005",
    title: "Third-party SDK update",
    agent: "copilot-api",
    riskLevel: "low",
    status: "rejected",
    requestedAt: "3 hours ago",
    requestedBy: "copilot-api",
    rejectedAt: "2 hours ago",
    rejectedBy: "Admin",
    rejectionReason: "SDK version has known security vulnerabilities",
    reason: "Dependency update",
    changes: ["Update analytics SDK to v3.0"],
  },
]

export default function ApprovalsPage() {
  const [approvals, setApprovals] = useState(initialApprovals)
  const [showDetailDialog, setShowDetailDialog] = useState<typeof initialApprovals[0] | null>(null)
  const [rejectionReason, setRejectionReason] = useState("")
  const [showRejectDialog, setShowRejectDialog] = useState(false)

  const getRiskBadge = (level: string) => {
    switch (level) {
      case "high":
        return <Badge variant="destructive">High Risk</Badge>
      case "medium":
        return <Badge className="bg-[#F5A524]/10 text-[#F5A524]">Medium Risk</Badge>
      case "low":
        return <Badge className="bg-[#18C29C]/10 text-[#18C29C]">Low Risk</Badge>
      default:
        return <Badge variant="outline">Unknown</Badge>
    }
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "pending":
        return <Badge variant="outline" className="border-[#F5A524] text-[#F5A524]"><Clock className="mr-1 h-3 w-3" />Pending</Badge>
      case "approved":
        return <Badge className="bg-[#18C29C]/10 text-[#18C29C]"><CheckCircle className="mr-1 h-3 w-3" />Approved</Badge>
      case "rejected":
        return <Badge variant="destructive"><XCircle className="mr-1 h-3 w-3" />Rejected</Badge>
      default:
        return <Badge variant="outline">Unknown</Badge>
    }
  }

  const handleApprove = (approvalId: string) => {
    setApprovals(approvals.map(a => 
      a.id === approvalId 
        ? { ...a, status: "approved", approvedAt: "Just now", approvedBy: "Admin" }
        : a
    ))
    toast.success("Approval granted")
    setShowDetailDialog(null)
  }

  const handleReject = () => {
    if (showDetailDialog) {
      setApprovals(approvals.map(a => 
        a.id === showDetailDialog.id 
          ? { ...a, status: "rejected", rejectedAt: "Just now", rejectedBy: "Admin", rejectionReason }
          : a
      ))
      toast.success("Approval rejected")
      setShowRejectDialog(false)
      setShowDetailDialog(null)
      setRejectionReason("")
    }
  }

  const pendingApprovals = approvals.filter(a => a.status === "pending")
  const processedApprovals = approvals.filter(a => a.status !== "pending")

  return (
    <div className="mx-auto max-w-7xl space-y-6">
      {/* Page Header */}
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Approvals</h1>
          <p className="text-muted-foreground">Review and approve high-risk agent actions.</p>
        </div>
        <Badge variant="outline" className="text-lg px-4 py-2">
          <Clock className="mr-2 h-4 w-4" />
          {pendingApprovals.length} Pending
        </Badge>
      </div>

      {/* Stats */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Pending</CardTitle>
            <Clock className="h-4 w-4 text-[#F5A524]" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-[#F5A524]">{pendingApprovals.length}</div>
            <p className="text-xs text-muted-foreground">Awaiting review</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Approved Today</CardTitle>
            <CheckCircle className="h-4 w-4 text-[#18C29C]" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-[#18C29C]">{approvals.filter(a => a.status === "approved").length}</div>
            <p className="text-xs text-muted-foreground">Actions approved</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Rejected</CardTitle>
            <XCircle className="h-4 w-4 text-destructive" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-destructive">{approvals.filter(a => a.status === "rejected").length}</div>
            <p className="text-xs text-muted-foreground">Actions blocked</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Avg. Response</CardTitle>
            <CheckSquare className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">12m</div>
            <p className="text-xs text-muted-foreground">Response time</p>
          </CardContent>
        </Card>
      </div>

      {/* Pending Approvals */}
      {pendingApprovals.length > 0 && (
        <div>
          <h2 className="text-xl font-semibold mb-4">Pending Approvals</h2>
          <div className="space-y-4">
            {pendingApprovals.map((approval) => (
              <Card key={approval.id} className="border-l-4 border-l-[#F5A524]">
                <CardContent className="p-6">
                  <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
                    <div className="space-y-2">
                      <div className="flex items-center gap-2 flex-wrap">
                        <h3 className="font-semibold text-lg">{approval.title}</h3>
                        {getRiskBadge(approval.riskLevel)}
                        {getStatusBadge(approval.status)}
                      </div>
                      <p className="text-sm text-muted-foreground">{approval.reason}</p>
                      <div className="flex items-center gap-4 text-sm text-muted-foreground">
                        <span className="flex items-center gap-1">
                          <GitBranch className="h-3 w-3" />
                          {approval.agent}
                        </span>
                        <span className="flex items-center gap-1">
                          <Clock className="h-3 w-3" />
                          {approval.requestedAt}
                        </span>
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <Button variant="outline" onClick={() => setShowDetailDialog(approval)}>
                        View Details
                      </Button>
                      <Button variant="outline" className="text-destructive" onClick={() => { setShowDetailDialog(approval); setShowRejectDialog(true); }}>
                        <XCircle className="mr-2 h-4 w-4" />
                        Reject
                      </Button>
                      <Button onClick={() => handleApprove(approval.id)}>
                        <CheckCircle className="mr-2 h-4 w-4" />
                        Approve
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}

      {/* Processed Approvals */}
      <div>
        <h2 className="text-xl font-semibold mb-4">Recent History</h2>
        <div className="space-y-4">
          {processedApprovals.map((approval) => (
            <Card key={approval.id} className={`border-l-4 ${approval.status === "approved" ? "border-l-[#18C29C]" : "border-l-destructive"}`}>
              <CardContent className="p-6">
                <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
                  <div className="space-y-2">
                    <div className="flex items-center gap-2 flex-wrap">
                      <h3 className="font-semibold">{approval.title}</h3>
                      {getRiskBadge(approval.riskLevel)}
                      {getStatusBadge(approval.status)}
                    </div>
                    <div className="flex items-center gap-4 text-sm text-muted-foreground">
                      <span className="flex items-center gap-1">
                        <GitBranch className="h-3 w-3" />
                        {approval.agent}
                      </span>
                      <span className="flex items-center gap-1">
                        <User className="h-3 w-3" />
                        {approval.status === "approved" ? `Approved by ${approval.approvedBy}` : `Rejected by ${approval.rejectedBy}`}
                      </span>
                      <span className="flex items-center gap-1">
                        <Clock className="h-3 w-3" />
                        {approval.status === "approved" ? approval.approvedAt : approval.rejectedAt}
                      </span>
                    </div>
                    {approval.rejectionReason && (
                      <p className="text-sm text-destructive flex items-center gap-1">
                        <MessageSquare className="h-3 w-3" />
                        {approval.rejectionReason}
                      </p>
                    )}
                  </div>
                  <Button variant="ghost" onClick={() => setShowDetailDialog(approval)}>
                    View Details
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      {/* Detail Dialog */}
      <Dialog open={!!showDetailDialog && !showRejectDialog} onOpenChange={() => setShowDetailDialog(null)}>
        <DialogContent className="sm:max-w-lg">
          <DialogHeader>
            <DialogTitle>{showDetailDialog?.title}</DialogTitle>
            <DialogDescription className="font-mono">{showDetailDialog?.id}</DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="flex gap-2 flex-wrap">
              {showDetailDialog && getRiskBadge(showDetailDialog.riskLevel)}
              {showDetailDialog && getStatusBadge(showDetailDialog.status)}
            </div>

            <div className="rounded-lg bg-muted p-4 space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Agent:</span>
                <span className="font-medium">{showDetailDialog?.agent}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Requested:</span>
                <span>{showDetailDialog?.requestedAt}</span>
              </div>
              {showDetailDialog?.approvedBy && (
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Approved by:</span>
                  <span>{showDetailDialog.approvedBy}</span>
                </div>
              )}
              {showDetailDialog?.rejectedBy && (
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Rejected by:</span>
                  <span>{showDetailDialog.rejectedBy}</span>
                </div>
              )}
            </div>

            <div>
              <h4 className="font-medium mb-2">Reason for Approval</h4>
              <p className="text-sm text-muted-foreground">{showDetailDialog?.reason}</p>
            </div>

            <div>
              <h4 className="font-medium mb-2">Proposed Changes</h4>
              <ul className="text-sm space-y-1 text-muted-foreground">
                {showDetailDialog?.changes.map((change, i) => (
                  <li key={i} className="flex items-start gap-2">
                    <span className="text-primary">-</span>
                    {change}
                  </li>
                ))}
              </ul>
            </div>

            {showDetailDialog?.rejectionReason && (
              <div className="rounded-lg border border-destructive/50 bg-destructive/5 p-4">
                <h4 className="font-medium text-destructive mb-1">Rejection Reason</h4>
                <p className="text-sm text-muted-foreground">{showDetailDialog.rejectionReason}</p>
              </div>
            )}
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowDetailDialog(null)}>Close</Button>
            {showDetailDialog?.status === "pending" && (
              <>
                <Button variant="outline" className="text-destructive" onClick={() => setShowRejectDialog(true)}>
                  Reject
                </Button>
                <Button onClick={() => handleApprove(showDetailDialog.id)}>
                  Approve
                </Button>
              </>
            )}
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Reject Dialog */}
      <Dialog open={showRejectDialog} onOpenChange={setShowRejectDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Reject Approval</DialogTitle>
            <DialogDescription>Provide a reason for rejecting this approval request.</DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <Textarea
              placeholder="Enter rejection reason..."
              value={rejectionReason}
              onChange={(e) => setRejectionReason(e.target.value)}
              rows={4}
            />
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => { setShowRejectDialog(false); setRejectionReason(""); }}>
              Cancel
            </Button>
            <Button variant="destructive" onClick={handleReject} disabled={!rejectionReason}>
              Reject
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
