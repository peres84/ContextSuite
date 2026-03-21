"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Input } from "@/components/ui/input"
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
  Bot,
  CheckCircle,
  Clock,
  AlertTriangle,
  Shield,
  TrendingUp,
  Copy,
  ExternalLink,
  Plus,
  Zap,
  GitBranch,
  MessageSquare,
  Plug,
  Activity,
} from "lucide-react"
import { toast } from "sonner"

// Demo data
const recentActivity = [
  { timestamp: "2 min ago", agent: "cursor-main", event: "Plan reviewed", source: "GitHub", risk: "low", action: "Auto-approved", result: "Passed" },
  { timestamp: "15 min ago", agent: "copilot-api", event: "Plan blocked", source: "MCP", risk: "high", action: "Blocked", result: "Policy violation" },
  { timestamp: "32 min ago", agent: "claude-docs", event: "Slack alert sent", source: "Slack", risk: "medium", action: "Notified", result: "Delivered" },
  { timestamp: "1 hour ago", agent: "cursor-main", event: "Agent created", source: "Dashboard", risk: "low", action: "Created", result: "Success" },
  { timestamp: "2 hours ago", agent: "copilot-api", event: "MCP profile updated", source: "Dashboard", risk: "low", action: "Updated", result: "Success" },
  { timestamp: "3 hours ago", agent: "claude-docs", event: "Human approval granted", source: "Slack", risk: "high", action: "Approved", result: "Proceeded" },
]

const createdAgents = [
  { id: "agent-001", name: "cursor-main", url: "https://api.contextsuite.io/v1/agents/cursor-main", status: "healthy", lastHeartbeat: "30s ago", env: "prod" },
  { id: "agent-002", name: "copilot-api", url: "https://api.contextsuite.io/v1/agents/copilot-api", status: "healthy", lastHeartbeat: "1m ago", env: "staging" },
  { id: "agent-003", name: "claude-docs", url: "https://api.contextsuite.io/v1/agents/claude-docs", status: "warning", lastHeartbeat: "5m ago", env: "dev" },
]

export default function DashboardOverview() {
  const [isCreating, setIsCreating] = useState(false)
  const [newAgent, setNewAgent] = useState({
    name: "",
    repository: "",
    profile: "safe-reviewer",
    riskMode: "medium",
    approvalMode: "human-gated",
  })
  const [createdAgent, setCreatedAgent] = useState<{ id: string; name: string; url: string } | null>(null)
  const [showCreateDialog, setShowCreateDialog] = useState(false)

  const handleCreateAgent = () => {
    setIsCreating(true)
    // Simulate API call
    setTimeout(() => {
      const agentId = `agent-${Date.now()}`
      const agent = {
        id: agentId,
        name: newAgent.name || "new-agent",
        url: `https://api.contextsuite.io/v1/agents/${newAgent.name || "new-agent"}`,
      }
      setCreatedAgent(agent)
      setIsCreating(false)
      toast.success("Agent created successfully!")
    }, 1500)
  }

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
    toast.success("Copied to clipboard!")
  }

  const getRiskBadge = (risk: string) => {
    switch (risk) {
      case "high":
        return <Badge variant="destructive">High</Badge>
      case "medium":
        return <Badge className="bg-[#F5A524]/10 text-[#F5A524] hover:bg-[#F5A524]/20">Medium</Badge>
      case "low":
        return <Badge className="bg-[#18C29C]/10 text-[#18C29C] hover:bg-[#18C29C]/20">Low</Badge>
      default:
        return <Badge variant="secondary">Unknown</Badge>
    }
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "healthy":
        return <Badge className="bg-[#18C29C]/10 text-[#18C29C]"><CheckCircle className="mr-1 h-3 w-3" />Healthy</Badge>
      case "warning":
        return <Badge className="bg-[#F5A524]/10 text-[#F5A524]"><AlertTriangle className="mr-1 h-3 w-3" />Warning</Badge>
      case "error":
        return <Badge variant="destructive"><AlertTriangle className="mr-1 h-3 w-3" />Error</Badge>
      default:
        return <Badge variant="secondary">Unknown</Badge>
    }
  }

  return (
    <div className="mx-auto max-w-7xl space-y-6">
      {/* Page Header */}
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Overview</h1>
          <p className="text-muted-foreground">Create agents, manage connections, and monitor activity.</p>
        </div>
        <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              Create Agent
            </Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-lg">
            {!createdAgent ? (
              <>
                <DialogHeader>
                  <DialogTitle>Create your first agent in seconds</DialogTitle>
                  <DialogDescription>
                    Configure your agent and get a connection link for your workflow.
                  </DialogDescription>
                </DialogHeader>
                <div className="space-y-4 py-4">
                  <div className="space-y-2">
                    <Label htmlFor="agent-name">Agent Name *</Label>
                    <Input
                      id="agent-name"
                      placeholder="e.g., cursor-main"
                      value={newAgent.name}
                      onChange={(e) => setNewAgent({ ...newAgent, name: e.target.value })}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="repository">Project / Repository</Label>
                    <Select
                      value={newAgent.repository}
                      onValueChange={(value) => setNewAgent({ ...newAgent, repository: value })}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select repository" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="acme/webapp">acme/webapp</SelectItem>
                        <SelectItem value="acme/api">acme/api</SelectItem>
                        <SelectItem value="acme/mobile">acme/mobile</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="profile">Agent Profile</Label>
                    <Select
                      value={newAgent.profile}
                      onValueChange={(value) => setNewAgent({ ...newAgent, profile: value })}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="safe-reviewer">Safe Reviewer</SelectItem>
                        <SelectItem value="coding-copilot">Coding Copilot</SelectItem>
                        <SelectItem value="research-assistant">Research Assistant</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label>Risk Mode</Label>
                      <Select
                        value={newAgent.riskMode}
                        onValueChange={(value) => setNewAgent({ ...newAgent, riskMode: value })}
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="low">Low</SelectItem>
                          <SelectItem value="medium">Medium</SelectItem>
                          <SelectItem value="high">High</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="space-y-2">
                      <Label>Approval Mode</Label>
                      <Select
                        value={newAgent.approvalMode}
                        onValueChange={(value) => setNewAgent({ ...newAgent, approvalMode: value })}
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="auto">Auto (Low Risk)</SelectItem>
                          <SelectItem value="human-gated">Human-Gated</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                </div>
                <DialogFooter className="flex-col gap-2 sm:flex-row">
                  <Button variant="outline" onClick={() => setShowCreateDialog(false)}>
                    Cancel
                  </Button>
                  <Button onClick={handleCreateAgent} disabled={!newAgent.name || isCreating}>
                    {isCreating ? (
                      <>Creating...</>
                    ) : (
                      <>
                        <Zap className="mr-2 h-4 w-4" />
                        Create Agent
                      </>
                    )}
                  </Button>
                </DialogFooter>
              </>
            ) : (
              <>
                <DialogHeader>
                  <DialogTitle className="flex items-center gap-2 text-[#18C29C]">
                    <CheckCircle className="h-5 w-5" />
                    Agent Created Successfully
                  </DialogTitle>
                  <DialogDescription>
                    Your agent is ready. Copy the connection URL to integrate with your workflow.
                  </DialogDescription>
                </DialogHeader>
                <div className="space-y-4 py-4">
                  <div className="rounded-lg border bg-muted/50 p-4 space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-muted-foreground">Agent ID</span>
                      <code className="text-sm font-mono">{createdAgent.id}</code>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-muted-foreground">Name</span>
                      <span className="font-medium">{createdAgent.name}</span>
                    </div>
                  </div>
                  <div className="space-y-2">
                    <Label>Agent Connection URL</Label>
                    <div className="flex gap-2">
                      <Input
                        value={createdAgent.url}
                        readOnly
                        className="font-mono text-sm"
                      />
                      <Button
                        variant="outline"
                        size="icon"
                        onClick={() => copyToClipboard(createdAgent.url)}
                      >
                        <Copy className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                  <div className="space-y-2">
                    <Label>API Token (Demo)</Label>
                    <div className="flex gap-2">
                      <Input
                        value="ctx_demo_xxxxxxxxxxxxxxxxxxxx"
                        readOnly
                        className="font-mono text-sm"
                      />
                      <Button
                        variant="outline"
                        size="icon"
                        onClick={() => copyToClipboard("ctx_demo_xxxxxxxxxxxxxxxxxxxx")}
                      >
                        <Copy className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </div>
                <DialogFooter className="flex-col gap-2 sm:flex-row">
                  <Button
                    variant="outline"
                    onClick={() => {
                      setCreatedAgent(null)
                      setNewAgent({ name: "", repository: "", profile: "safe-reviewer", riskMode: "medium", approvalMode: "human-gated" })
                      setShowCreateDialog(false)
                    }}
                  >
                    Close
                  </Button>
                  <Button asChild>
                    <a href="/dashboard/integrations">
                      <Plug className="mr-2 h-4 w-4" />
                      Open in Integrations
                    </a>
                  </Button>
                </DialogFooter>
              </>
            )}
          </DialogContent>
        </Dialog>
      </div>

      {/* Operational Insights */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Active Agents</CardTitle>
            <Bot className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">3</div>
            <p className="text-xs text-muted-foreground">2 healthy, 1 warning</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Pending Approvals</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-[#F5A524]">3</div>
            <p className="text-xs text-muted-foreground">Awaiting review</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Blocked (24h)</CardTitle>
            <AlertTriangle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-destructive">7</div>
            <p className="text-xs text-muted-foreground">Policy violations</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Memory Match</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">87%</div>
            <Progress value={87} className="mt-2 h-1.5" />
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Trust Score</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-[#18C29C]">92</div>
            <p className="text-xs text-muted-foreground"><span className="text-[#18C29C]">+3</span> this week</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Violations</CardTitle>
            <Shield className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Badge variant="destructive" className="text-xs">2 High</Badge>
              <Badge className="bg-[#F5A524]/10 text-[#F5A524] text-xs">5 Med</Badge>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Agent Link & Access Panel */}
      <Card>
        <CardHeader>
          <CardTitle>Agent Connections</CardTitle>
          <CardDescription>Get your agent link and plug it into your workflow</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {createdAgents.map((agent) => (
              <div
                key={agent.id}
                className="flex flex-col gap-4 rounded-lg border p-4 sm:flex-row sm:items-center sm:justify-between"
              >
                <div className="flex items-center gap-4">
                  <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary/10">
                    <Bot className="h-5 w-5 text-primary" />
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <p className="font-medium">{agent.name}</p>
                      {getStatusBadge(agent.status)}
                      <Badge variant="outline" className="text-xs">{agent.env}</Badge>
                    </div>
                    <p className="text-sm text-muted-foreground">Last heartbeat: {agent.lastHeartbeat}</p>
                  </div>
                </div>
                <div className="flex flex-col gap-2 sm:flex-row sm:items-center">
                  <code className="rounded bg-muted px-2 py-1 text-xs font-mono truncate max-w-[300px]">
                    {agent.url}
                  </code>
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => copyToClipboard(agent.url)}
                    >
                      <Copy className="mr-2 h-3 w-3" />
                      Copy
                    </Button>
                    <Button variant="ghost" size="sm">
                      <ExternalLink className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Integration Quick Access */}
      <div className="grid gap-4 md:grid-cols-5">
        <Card className="cursor-pointer transition-colors hover:bg-muted/50" onClick={() => window.location.href = "/dashboard/integrations"}>
          <CardContent className="flex flex-col items-center justify-center p-6 text-center">
            <GitBranch className="h-8 w-8 text-primary mb-2" />
            <p className="font-medium">GitHub</p>
            <Badge className="mt-2 bg-[#18C29C]/10 text-[#18C29C]">Connected</Badge>
          </CardContent>
        </Card>
        <Card className="cursor-pointer transition-colors hover:bg-muted/50" onClick={() => window.location.href = "/dashboard/integrations"}>
          <CardContent className="flex flex-col items-center justify-center p-6 text-center">
            <Zap className="h-8 w-8 text-primary mb-2" />
            <p className="font-medium">Skills</p>
            <Badge className="mt-2 bg-[#18C29C]/10 text-[#18C29C]">3 Active</Badge>
          </CardContent>
        </Card>
        <Card className="cursor-pointer transition-colors hover:bg-muted/50" onClick={() => window.location.href = "/dashboard/integrations"}>
          <CardContent className="flex flex-col items-center justify-center p-6 text-center">
            <Shield className="h-8 w-8 text-primary mb-2" />
            <p className="font-medium">MCP</p>
            <Badge className="mt-2 bg-[#18C29C]/10 text-[#18C29C]">Connected</Badge>
          </CardContent>
        </Card>
        <Card className="cursor-pointer transition-colors hover:bg-muted/50" onClick={() => window.location.href = "/dashboard/integrations"}>
          <CardContent className="flex flex-col items-center justify-center p-6 text-center">
            <MessageSquare className="h-8 w-8 text-primary mb-2" />
            <p className="font-medium">Slack</p>
            <Badge className="mt-2" variant="outline">Not Connected</Badge>
          </CardContent>
        </Card>
        <Card className="cursor-pointer transition-colors hover:bg-muted/50" onClick={() => window.location.href = "/dashboard/integrations"}>
          <CardContent className="flex flex-col items-center justify-center p-6 text-center">
            <MessageSquare className="h-8 w-8 text-primary mb-2" />
            <p className="font-medium">Telegram</p>
            <Badge className="mt-2" variant="outline">Not Connected</Badge>
          </CardContent>
        </Card>
      </div>

      {/* Recent Activity */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Activity</CardTitle>
          <CardDescription>Review risks before execution, not after incidents</CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Timestamp</TableHead>
                <TableHead>Agent</TableHead>
                <TableHead>Event</TableHead>
                <TableHead>Source</TableHead>
                <TableHead>Risk</TableHead>
                <TableHead>Action</TableHead>
                <TableHead>Result</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {recentActivity.map((activity, index) => (
                <TableRow key={index} className="cursor-pointer hover:bg-muted/50">
                  <TableCell className="text-muted-foreground">{activity.timestamp}</TableCell>
                  <TableCell className="font-medium">{activity.agent}</TableCell>
                  <TableCell>{activity.event}</TableCell>
                  <TableCell>
                    <Badge variant="outline">{activity.source}</Badge>
                  </TableCell>
                  <TableCell>{getRiskBadge(activity.risk)}</TableCell>
                  <TableCell>{activity.action}</TableCell>
                  <TableCell>
                    {activity.result === "Passed" || activity.result === "Success" || activity.result === "Delivered" || activity.result === "Proceeded" ? (
                      <span className="text-[#18C29C]">{activity.result}</span>
                    ) : (
                      <span className="text-destructive">{activity.result}</span>
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  )
}
