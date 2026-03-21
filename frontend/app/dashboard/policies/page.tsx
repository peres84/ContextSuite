"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Switch } from "@/components/ui/switch"
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
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import {
  ScrollText,
  Plus,
  MoreVertical,
  Edit,
  Trash2,
  Shield,
  AlertTriangle,
  CheckCircle,
  Copy,
} from "lucide-react"
import { toast } from "sonner"

const initialPolicies = [
  {
    id: "POL-001",
    name: "High-Risk Change Approval",
    description: "Require human approval for any changes classified as high-risk by the review system.",
    type: "approval",
    severity: "high",
    enabled: true,
    triggers: 47,
    lastTriggered: "2 hours ago",
    conditions: ["Risk level is HIGH", "OR change affects payment/auth modules"],
    actions: ["Block execution", "Request human approval", "Send Slack notification"],
  },
  {
    id: "POL-002",
    name: "Database Schema Protection",
    description: "Prevent direct schema modifications without proper migration scripts.",
    type: "protection",
    severity: "high",
    enabled: true,
    triggers: 12,
    lastTriggered: "1 day ago",
    conditions: ["Change type is DDL", "Target is production database"],
    actions: ["Block execution", "Log violation"],
  },
  {
    id: "POL-003",
    name: "API Breaking Change Alert",
    description: "Alert when changes may break existing API contracts.",
    type: "alert",
    severity: "medium",
    enabled: true,
    triggers: 23,
    lastTriggered: "5 hours ago",
    conditions: ["API endpoint signature changed", "Response schema modified"],
    actions: ["Send warning", "Continue with caution"],
  },
  {
    id: "POL-004",
    name: "Security Credential Check",
    description: "Block any code that appears to contain hardcoded credentials or secrets.",
    type: "protection",
    severity: "high",
    enabled: true,
    triggers: 8,
    lastTriggered: "3 days ago",
    conditions: ["Pattern matches credential format", "Not in allowed exceptions"],
    actions: ["Block execution", "Flag for security review"],
  },
  {
    id: "POL-005",
    name: "Dependency Vulnerability Scan",
    description: "Check new dependencies against known vulnerability databases.",
    type: "alert",
    severity: "medium",
    enabled: false,
    triggers: 0,
    lastTriggered: "Never",
    conditions: ["New dependency added", "Dependency version changed"],
    actions: ["Scan against CVE database", "Report findings"],
  },
]

export default function PoliciesPage() {
  const [policies, setPolicies] = useState(initialPolicies)
  const [showCreateDialog, setShowCreateDialog] = useState(false)
  const [showDetailDialog, setShowDetailDialog] = useState<typeof initialPolicies[0] | null>(null)
  const [newPolicy, setNewPolicy] = useState({
    name: "",
    description: "",
    type: "approval",
    severity: "medium",
  })

  const getSeverityBadge = (severity: string) => {
    switch (severity) {
      case "high":
        return <Badge variant="destructive">High Severity</Badge>
      case "medium":
        return <Badge className="bg-[#F5A524]/10 text-[#F5A524]">Medium Severity</Badge>
      case "low":
        return <Badge className="bg-[#18C29C]/10 text-[#18C29C]">Low Severity</Badge>
      default:
        return <Badge variant="outline">Unknown</Badge>
    }
  }

  const getTypeBadge = (type: string) => {
    switch (type) {
      case "approval":
        return <Badge variant="outline"><CheckCircle className="mr-1 h-3 w-3" />Approval</Badge>
      case "protection":
        return <Badge variant="outline"><Shield className="mr-1 h-3 w-3" />Protection</Badge>
      case "alert":
        return <Badge variant="outline"><AlertTriangle className="mr-1 h-3 w-3" />Alert</Badge>
      default:
        return <Badge variant="outline">Unknown</Badge>
    }
  }

  const togglePolicy = (policyId: string) => {
    setPolicies(policies.map(p => {
      if (p.id === policyId) {
        const newEnabled = !p.enabled
        toast.success(newEnabled ? "Policy enabled" : "Policy disabled")
        return { ...p, enabled: newEnabled }
      }
      return p
    }))
  }

  const deletePolicy = (policyId: string) => {
    setPolicies(policies.filter(p => p.id !== policyId))
    toast.success("Policy deleted")
  }

  const duplicatePolicy = (policy: typeof initialPolicies[0]) => {
    const newPol = {
      ...policy,
      id: `POL-${String(policies.length + 1).padStart(3, "0")}`,
      name: `${policy.name} (Copy)`,
      triggers: 0,
      lastTriggered: "Never",
    }
    setPolicies([...policies, newPol])
    toast.success("Policy duplicated")
  }

  const handleCreatePolicy = () => {
    const policy = {
      id: `POL-${String(policies.length + 1).padStart(3, "0")}`,
      name: newPolicy.name,
      description: newPolicy.description,
      type: newPolicy.type,
      severity: newPolicy.severity,
      enabled: true,
      triggers: 0,
      lastTriggered: "Never",
      conditions: ["Custom condition"],
      actions: ["Custom action"],
    }
    setPolicies([...policies, policy])
    setShowCreateDialog(false)
    setNewPolicy({ name: "", description: "", type: "approval", severity: "medium" })
    toast.success("Policy created")
  }

  return (
    <div className="mx-auto max-w-7xl space-y-6">
      {/* Page Header */}
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Policies</h1>
          <p className="text-muted-foreground">Define rules and constraints for AI agent behavior.</p>
        </div>
        <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              Create Policy
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Create New Policy</DialogTitle>
              <DialogDescription>Define a new policy for agent behavior control.</DialogDescription>
            </DialogHeader>
            <div className="space-y-4 py-4">
              <div className="space-y-2">
                <Label>Policy Name *</Label>
                <Input
                  placeholder="e.g., Block Unsafe Operations"
                  value={newPolicy.name}
                  onChange={(e) => setNewPolicy({ ...newPolicy, name: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label>Description</Label>
                <Textarea
                  placeholder="Describe what this policy does..."
                  value={newPolicy.description}
                  onChange={(e) => setNewPolicy({ ...newPolicy, description: e.target.value })}
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Type</Label>
                  <Select value={newPolicy.type} onValueChange={(v) => setNewPolicy({ ...newPolicy, type: v })}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="approval">Approval Required</SelectItem>
                      <SelectItem value="protection">Protection Rule</SelectItem>
                      <SelectItem value="alert">Alert Only</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label>Severity</Label>
                  <Select value={newPolicy.severity} onValueChange={(v) => setNewPolicy({ ...newPolicy, severity: v })}>
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
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setShowCreateDialog(false)}>Cancel</Button>
              <Button onClick={handleCreatePolicy} disabled={!newPolicy.name}>Create Policy</Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      {/* Stats */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Total Policies</CardTitle>
            <ScrollText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{policies.length}</div>
            <p className="text-xs text-muted-foreground">{policies.filter(p => p.enabled).length} active</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Total Triggers</CardTitle>
            <AlertTriangle className="h-4 w-4 text-[#F5A524]" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{policies.reduce((sum, p) => sum + p.triggers, 0)}</div>
            <p className="text-xs text-muted-foreground">All time</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Protection Rules</CardTitle>
            <Shield className="h-4 w-4 text-primary" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{policies.filter(p => p.type === "protection").length}</div>
            <p className="text-xs text-muted-foreground">Blocking policies</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">High Severity</CardTitle>
            <AlertTriangle className="h-4 w-4 text-destructive" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-destructive">{policies.filter(p => p.severity === "high").length}</div>
            <p className="text-xs text-muted-foreground">Critical policies</p>
          </CardContent>
        </Card>
      </div>

      {/* Policy List */}
      <div className="space-y-4">
        {policies.map((policy) => (
          <Card key={policy.id} className={!policy.enabled ? "opacity-60" : ""}>
            <CardContent className="p-6">
              <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
                <div className="space-y-2 flex-1">
                  <div className="flex items-center gap-2 flex-wrap">
                    <h3 className="font-semibold text-lg">{policy.name}</h3>
                    {getSeverityBadge(policy.severity)}
                    {getTypeBadge(policy.type)}
                    {!policy.enabled && <Badge variant="secondary">Disabled</Badge>}
                  </div>
                  <p className="text-sm text-muted-foreground">{policy.description}</p>
                  <div className="flex items-center gap-4 text-sm text-muted-foreground">
                    <span>Triggered {policy.triggers} times</span>
                    <span>Last: {policy.lastTriggered}</span>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <div className="flex items-center gap-2 px-3">
                    <Switch checked={policy.enabled} onCheckedChange={() => togglePolicy(policy.id)} />
                    <span className="text-sm text-muted-foreground">{policy.enabled ? "Enabled" : "Disabled"}</span>
                  </div>
                  <Button variant="outline" onClick={() => setShowDetailDialog(policy)}>
                    View Details
                  </Button>
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button variant="ghost" size="icon">
                        <MoreVertical className="h-4 w-4" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                      <DropdownMenuItem onClick={() => setShowDetailDialog(policy)}>
                        <Edit className="mr-2 h-4 w-4" />
                        Edit
                      </DropdownMenuItem>
                      <DropdownMenuItem onClick={() => duplicatePolicy(policy)}>
                        <Copy className="mr-2 h-4 w-4" />
                        Duplicate
                      </DropdownMenuItem>
                      <DropdownMenuItem className="text-destructive" onClick={() => deletePolicy(policy.id)}>
                        <Trash2 className="mr-2 h-4 w-4" />
                        Delete
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Detail Dialog */}
      <Dialog open={!!showDetailDialog} onOpenChange={() => setShowDetailDialog(null)}>
        <DialogContent className="sm:max-w-lg">
          <DialogHeader>
            <DialogTitle>{showDetailDialog?.name}</DialogTitle>
            <DialogDescription className="font-mono">{showDetailDialog?.id}</DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="flex gap-2 flex-wrap">
              {showDetailDialog && getSeverityBadge(showDetailDialog.severity)}
              {showDetailDialog && getTypeBadge(showDetailDialog.type)}
            </div>

            <p className="text-sm text-muted-foreground">{showDetailDialog?.description}</p>

            <div className="rounded-lg bg-muted p-4 space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Total Triggers:</span>
                <span className="font-medium">{showDetailDialog?.triggers}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Last Triggered:</span>
                <span>{showDetailDialog?.lastTriggered}</span>
              </div>
            </div>

            <div>
              <h4 className="font-medium mb-2">Conditions</h4>
              <ul className="text-sm space-y-1 text-muted-foreground">
                {showDetailDialog?.conditions.map((condition, i) => (
                  <li key={i} className="flex items-start gap-2">
                    <span className="text-primary">IF</span>
                    {condition}
                  </li>
                ))}
              </ul>
            </div>

            <div>
              <h4 className="font-medium mb-2">Actions</h4>
              <ul className="text-sm space-y-1 text-muted-foreground">
                {showDetailDialog?.actions.map((action, i) => (
                  <li key={i} className="flex items-start gap-2">
                    <span className="text-primary">THEN</span>
                    {action}
                  </li>
                ))}
              </ul>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowDetailDialog(null)}>Close</Button>
            <Button>Edit Policy</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
