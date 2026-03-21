"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
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
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog"
import {
  Bot,
  Plus,
  MoreVertical,
  Copy,
  RefreshCw,
  Trash2,
  Settings,
  CheckCircle,
  AlertTriangle,
  XCircle,
  Activity,
  Clock,
  Shield,
  Zap,
  Pause,
  Play,
} from "lucide-react"
import { toast } from "sonner"

const agents = [
  {
    id: "agent-001",
    name: "cursor-main",
    profile: "Safe Reviewer",
    repository: "acme/webapp",
    status: "healthy",
    riskMode: "medium",
    approvalMode: "Human-Gated",
    lastHeartbeat: "30s ago",
    reviewsToday: 24,
    blockedToday: 3,
    env: "prod",
    enabled: true,
    url: "https://api.contextsuite.io/v1/agents/cursor-main",
  },
  {
    id: "agent-002",
    name: "copilot-api",
    profile: "Coding Copilot",
    repository: "acme/api",
    status: "healthy",
    riskMode: "high",
    approvalMode: "Human-Gated",
    lastHeartbeat: "1m ago",
    reviewsToday: 18,
    blockedToday: 7,
    env: "staging",
    enabled: true,
    url: "https://api.contextsuite.io/v1/agents/copilot-api",
  },
  {
    id: "agent-003",
    name: "claude-docs",
    profile: "Research Assistant",
    repository: "acme/docs",
    status: "warning",
    riskMode: "low",
    approvalMode: "Auto",
    lastHeartbeat: "5m ago",
    reviewsToday: 8,
    blockedToday: 0,
    env: "dev",
    enabled: true,
    url: "https://api.contextsuite.io/v1/agents/claude-docs",
  },
  {
    id: "agent-004",
    name: "v0-frontend",
    profile: "Safe Reviewer",
    repository: "acme/mobile",
    status: "disabled",
    riskMode: "medium",
    approvalMode: "Human-Gated",
    lastHeartbeat: "2d ago",
    reviewsToday: 0,
    blockedToday: 0,
    env: "dev",
    enabled: false,
    url: "https://api.contextsuite.io/v1/agents/v0-frontend",
  },
]

export default function AgentsPage() {
  const [agentList, setAgentList] = useState(agents)
  const [showCreateDialog, setShowCreateDialog] = useState(false)
  const [showDeleteDialog, setShowDeleteDialog] = useState(false)
  const [selectedAgent, setSelectedAgent] = useState<typeof agents[0] | null>(null)
  const [isCreating, setIsCreating] = useState(false)
  const [newAgent, setNewAgent] = useState({
    name: "",
    repository: "",
    profile: "safe-reviewer",
    riskMode: "medium",
    approvalMode: "human-gated",
  })

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "healthy":
        return <CheckCircle className="h-4 w-4 text-[#18C29C]" />
      case "warning":
        return <AlertTriangle className="h-4 w-4 text-[#F5A524]" />
      case "error":
        return <XCircle className="h-4 w-4 text-destructive" />
      case "disabled":
        return <Pause className="h-4 w-4 text-muted-foreground" />
      default:
        return <Activity className="h-4 w-4 text-muted-foreground" />
    }
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "healthy":
        return <Badge className="bg-[#18C29C]/10 text-[#18C29C]">Healthy</Badge>
      case "warning":
        return <Badge className="bg-[#F5A524]/10 text-[#F5A524]">Warning</Badge>
      case "error":
        return <Badge variant="destructive">Error</Badge>
      case "disabled":
        return <Badge variant="secondary">Disabled</Badge>
      default:
        return <Badge variant="outline">Unknown</Badge>
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

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
    toast.success("Copied to clipboard!")
  }

  const toggleAgent = (agentId: string) => {
    setAgentList(agentList.map(agent => {
      if (agent.id === agentId) {
        const newEnabled = !agent.enabled
        toast.success(newEnabled ? "Agent enabled" : "Agent disabled")
        return {
          ...agent,
          enabled: newEnabled,
          status: newEnabled ? "healthy" : "disabled"
        }
      }
      return agent
    }))
  }

  const regenerateLink = (agentId: string) => {
    toast.success("Agent link regenerated")
  }

  const deleteAgent = () => {
    if (selectedAgent) {
      setAgentList(agentList.filter(a => a.id !== selectedAgent.id))
      toast.success("Agent deleted")
      setShowDeleteDialog(false)
      setSelectedAgent(null)
    }
  }

  const handleCreateAgent = () => {
    setIsCreating(true)
    setTimeout(() => {
      const newAgentData = {
        id: `agent-${Date.now()}`,
        name: newAgent.name,
        profile: newAgent.profile === "safe-reviewer" ? "Safe Reviewer" : newAgent.profile === "coding-copilot" ? "Coding Copilot" : "Research Assistant",
        repository: newAgent.repository,
        status: "healthy",
        riskMode: newAgent.riskMode,
        approvalMode: newAgent.approvalMode === "human-gated" ? "Human-Gated" : "Auto",
        lastHeartbeat: "Just now",
        reviewsToday: 0,
        blockedToday: 0,
        env: "dev",
        enabled: true,
        url: `https://api.contextsuite.io/v1/agents/${newAgent.name}`,
      }
      setAgentList([newAgentData, ...agentList])
      setIsCreating(false)
      setShowCreateDialog(false)
      setNewAgent({ name: "", repository: "", profile: "safe-reviewer", riskMode: "medium", approvalMode: "human-gated" })
      toast.success("Agent created successfully!")
    }, 1500)
  }

  return (
    <div className="mx-auto max-w-7xl space-y-6">
      {/* Page Header */}
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Agents</h1>
          <p className="text-muted-foreground">Manage your AI coding agents and their configurations.</p>
        </div>
        <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              Create Agent
            </Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-lg">
            <DialogHeader>
              <DialogTitle>Create New Agent</DialogTitle>
              <DialogDescription>
                Configure your agent settings and deployment options.
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
                <Label>Project / Repository</Label>
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
                    <SelectItem value="acme/docs">acme/docs</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label>Agent Profile</Label>
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
            <DialogFooter>
              <Button variant="outline" onClick={() => setShowCreateDialog(false)}>
                Cancel
              </Button>
              <Button onClick={handleCreateAgent} disabled={!newAgent.name || isCreating}>
                {isCreating ? "Creating..." : "Create Agent"}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      {/* Stats */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Total Agents</CardTitle>
            <Bot className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{agentList.length}</div>
            <p className="text-xs text-muted-foreground">{agentList.filter(a => a.enabled).length} active</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Reviews Today</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{agentList.reduce((sum, a) => sum + a.reviewsToday, 0)}</div>
            <p className="text-xs text-muted-foreground">Across all agents</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Blocked Today</CardTitle>
            <Shield className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-destructive">{agentList.reduce((sum, a) => sum + a.blockedToday, 0)}</div>
            <p className="text-xs text-muted-foreground">Regressions prevented</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Health Score</CardTitle>
            <Zap className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-[#18C29C]">
              {Math.round((agentList.filter(a => a.status === "healthy").length / agentList.filter(a => a.enabled).length) * 100)}%
            </div>
            <p className="text-xs text-muted-foreground">Agents healthy</p>
          </CardContent>
        </Card>
      </div>

      {/* Agent List */}
      <div className="grid gap-4">
        {agentList.map((agent) => (
          <Card key={agent.id} className={!agent.enabled ? "opacity-60" : ""}>
            <CardContent className="p-6">
              <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
                <div className="flex items-start gap-4">
                  <div className={`flex h-12 w-12 items-center justify-center rounded-full ${agent.enabled ? "bg-primary/10" : "bg-muted"}`}>
                    <Bot className={`h-6 w-6 ${agent.enabled ? "text-primary" : "text-muted-foreground"}`} />
                  </div>
                  <div className="space-y-1">
                    <div className="flex items-center gap-2 flex-wrap">
                      <h3 className="font-semibold text-lg">{agent.name}</h3>
                      {getStatusBadge(agent.status)}
                      <Badge variant="outline">{agent.env}</Badge>
                      <Badge variant="secondary">{agent.profile}</Badge>
                    </div>
                    <div className="flex items-center gap-4 text-sm text-muted-foreground">
                      <span>{agent.repository}</span>
                      <span className="flex items-center gap-1">
                        <Clock className="h-3 w-3" />
                        {agent.lastHeartbeat}
                      </span>
                    </div>
                    <div className="flex items-center gap-4 text-sm">
                      <span>Risk: {getRiskBadge(agent.riskMode)}</span>
                      <span>Approval: <Badge variant="outline">{agent.approvalMode}</Badge></span>
                    </div>
                  </div>
                </div>

                <div className="flex flex-col gap-4 lg:flex-row lg:items-center">
                  <div className="flex gap-6 text-center">
                    <div>
                      <p className="text-2xl font-bold">{agent.reviewsToday}</p>
                      <p className="text-xs text-muted-foreground">Reviews</p>
                    </div>
                    <div>
                      <p className="text-2xl font-bold text-destructive">{agent.blockedToday}</p>
                      <p className="text-xs text-muted-foreground">Blocked</p>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => copyToClipboard(agent.url)}
                    >
                      <Copy className="mr-2 h-3 w-3" />
                      Copy URL
                    </Button>
                    <div className="flex items-center gap-2 px-3">
                      <Switch
                        checked={agent.enabled}
                        onCheckedChange={() => toggleAgent(agent.id)}
                      />
                      <span className="text-sm text-muted-foreground">
                        {agent.enabled ? "Enabled" : "Disabled"}
                      </span>
                    </div>
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button variant="ghost" size="icon">
                          <MoreVertical className="h-4 w-4" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuItem>
                          <Settings className="mr-2 h-4 w-4" />
                          Configure
                        </DropdownMenuItem>
                        <DropdownMenuItem onClick={() => regenerateLink(agent.id)}>
                          <RefreshCw className="mr-2 h-4 w-4" />
                          Regenerate Link
                        </DropdownMenuItem>
                        <DropdownMenuSeparator />
                        <DropdownMenuItem
                          className="text-destructive"
                          onClick={() => {
                            setSelectedAgent(agent)
                            setShowDeleteDialog(true)
                          }}
                        >
                          <Trash2 className="mr-2 h-4 w-4" />
                          Delete Agent
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Delete Confirmation */}
      <AlertDialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Agent</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete {selectedAgent?.name}? This action cannot be undone and will remove all associated data.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={deleteAgent} className="bg-destructive text-destructive-foreground hover:bg-destructive/90">
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
}
