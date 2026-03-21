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
} from "@/components/ui/dialog"
import {
  GitBranch,
  Zap,
  Shield,
  MessageSquare,
  Send,
  CheckCircle,
  AlertCircle,
  XCircle,
  RefreshCw,
  ExternalLink,
  Settings,
  Plus,
} from "lucide-react"
import { toast } from "sonner"

interface Integration {
  id: string
  name: string
  description: string
  icon: React.ReactNode
  status: "connected" | "needs-action" | "error" | "disconnected"
  lastSync?: string
  config?: Record<string, string>
}

const initialIntegrations: Integration[] = [
  {
    id: "github",
    name: "GitHub",
    description: "Connect organization/repository and configure webhook events for plan review triggers.",
    icon: <GitBranch className="h-6 w-6" />,
    status: "connected",
    lastSync: "2 minutes ago",
    config: { org: "acme", repos: "webapp, api, mobile" },
  },
  {
    id: "skills",
    name: "Skills",
    description: "Browse and attach skill packs. Toggle skill availability per agent.",
    icon: <Zap className="h-6 w-6" />,
    status: "connected",
    lastSync: "5 minutes ago",
    config: { activePacks: "3" },
  },
  {
    id: "mcp",
    name: "MCP",
    description: "Select tool profile. Set allowed command set and safety scope.",
    icon: <Shield className="h-6 w-6" />,
    status: "connected",
    lastSync: "1 hour ago",
    config: { profile: "standard", commands: "12 allowed" },
  },
  {
    id: "slack",
    name: "Slack",
    description: "Choose channel for approvals and alerts. Toggle blocked-plan notifications.",
    icon: <MessageSquare className="h-6 w-6" />,
    status: "disconnected",
  },
  {
    id: "telegram",
    name: "Telegram",
    description: "Connect bot/channel. Toggle alert severity thresholds.",
    icon: <Send className="h-6 w-6" />,
    status: "disconnected",
  },
]

const futureIntegrations = [
  { id: "jira", name: "Jira", description: "Issue tracking and project management", icon: <AlertCircle className="h-6 w-6" /> },
  { id: "gitlab", name: "GitLab", description: "Source control and CI/CD", icon: <GitBranch className="h-6 w-6" /> },
  { id: "teams", name: "Microsoft Teams", description: "Team communication and alerts", icon: <MessageSquare className="h-6 w-6" /> },
  { id: "linear", name: "Linear", description: "Issue tracking for modern teams", icon: <Zap className="h-6 w-6" /> },
]

export default function IntegrationsPage() {
  const [integrations, setIntegrations] = useState(initialIntegrations)
  const [configDialog, setConfigDialog] = useState<Integration | null>(null)
  const [connectDialog, setConnectDialog] = useState<Integration | null>(null)

  // Config form states
  const [slackChannel, setSlackChannel] = useState("#approvals")
  const [slackNotifications, setSlackNotifications] = useState(true)
  const [telegramBotToken, setTelegramBotToken] = useState("")
  const [telegramChatId, setTelegramChatId] = useState("")
  const [githubOrg, setGithubOrg] = useState("acme")
  const [githubRepos, setGithubRepos] = useState("webapp, api")
  const [mcpProfile, setMcpProfile] = useState("standard")
  const [skillPacks, setSkillPacks] = useState(["code-review", "security", "testing"])

  const getStatusBadge = (status: Integration["status"]) => {
    switch (status) {
      case "connected":
        return <Badge className="bg-[#18C29C]/10 text-[#18C29C]"><CheckCircle className="mr-1 h-3 w-3" />Connected</Badge>
      case "needs-action":
        return <Badge className="bg-[#F5A524]/10 text-[#F5A524]"><AlertCircle className="mr-1 h-3 w-3" />Needs Action</Badge>
      case "error":
        return <Badge variant="destructive"><XCircle className="mr-1 h-3 w-3" />Error</Badge>
      case "disconnected":
        return <Badge variant="outline">Not Connected</Badge>
    }
  }

  const handleConnect = (integration: Integration) => {
    setConnectDialog(integration)
  }

  const handleConfigure = (integration: Integration) => {
    setConfigDialog(integration)
  }

  const handleDisconnect = (integrationId: string) => {
    setIntegrations(integrations.map(i =>
      i.id === integrationId ? { ...i, status: "disconnected" as const, lastSync: undefined } : i
    ))
    toast.success("Integration disconnected")
  }

  const completeConnection = (integrationId: string) => {
    setIntegrations(integrations.map(i =>
      i.id === integrationId ? { ...i, status: "connected" as const, lastSync: "Just now" } : i
    ))
    setConnectDialog(null)
    toast.success("Integration connected successfully!")
  }

  const saveConfig = () => {
    toast.success("Configuration saved")
    setConfigDialog(null)
  }

  return (
    <div className="mx-auto max-w-7xl space-y-6">
      {/* Page Header */}
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Integrations</h1>
          <p className="text-muted-foreground">Connect GitHub, Skills, MCP, Slack, and Telegram from one place.</p>
        </div>
        <Button variant="outline">
          <RefreshCw className="mr-2 h-4 w-4" />
          Sync All
        </Button>
      </div>

      {/* Stats */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Connected</CardTitle>
            <CheckCircle className="h-4 w-4 text-[#18C29C]" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{integrations.filter(i => i.status === "connected").length}</div>
            <p className="text-xs text-muted-foreground">Active integrations</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Pending</CardTitle>
            <AlertCircle className="h-4 w-4 text-[#F5A524]" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{integrations.filter(i => i.status === "needs-action").length}</div>
            <p className="text-xs text-muted-foreground">Need attention</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Available</CardTitle>
            <Plus className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{integrations.filter(i => i.status === "disconnected").length}</div>
            <p className="text-xs text-muted-foreground">Ready to connect</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Coming Soon</CardTitle>
            <Zap className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{futureIntegrations.length}</div>
            <p className="text-xs text-muted-foreground">More integrations</p>
          </CardContent>
        </Card>
      </div>

      {/* Active Integrations */}
      <div>
        <h2 className="text-xl font-semibold mb-4">Active Integrations</h2>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {integrations.map((integration) => (
            <Card key={integration.id}>
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <div className={`flex h-10 w-10 items-center justify-center rounded-lg ${integration.status === "connected" ? "bg-primary/10 text-primary" : "bg-muted text-muted-foreground"}`}>
                      {integration.icon}
                    </div>
                    <div>
                      <CardTitle className="text-lg">{integration.name}</CardTitle>
                      {integration.lastSync && (
                        <p className="text-xs text-muted-foreground">Synced {integration.lastSync}</p>
                      )}
                    </div>
                  </div>
                  {getStatusBadge(integration.status)}
                </div>
              </CardHeader>
              <CardContent>
                <CardDescription className="mb-4">{integration.description}</CardDescription>
                {integration.config && (
                  <div className="mb-4 rounded-lg bg-muted p-3 text-sm">
                    {Object.entries(integration.config).map(([key, value]) => (
                      <div key={key} className="flex justify-between">
                        <span className="text-muted-foreground capitalize">{key}:</span>
                        <span className="font-medium">{value}</span>
                      </div>
                    ))}
                  </div>
                )}
                <div className="flex gap-2">
                  {integration.status === "connected" ? (
                    <>
                      <Button
                        variant="outline"
                        className="flex-1"
                        onClick={() => handleConfigure(integration)}
                      >
                        <Settings className="mr-2 h-4 w-4" />
                        Configure
                      </Button>
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => handleDisconnect(integration.id)}
                      >
                        <XCircle className="h-4 w-4 text-destructive" />
                      </Button>
                    </>
                  ) : (
                    <Button className="w-full" onClick={() => handleConnect(integration)}>
                      <Plus className="mr-2 h-4 w-4" />
                      Connect
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      {/* Coming Soon */}
      <div>
        <h2 className="text-xl font-semibold mb-4">Coming Soon</h2>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {futureIntegrations.map((integration) => (
            <Card key={integration.id} className="opacity-60">
              <CardContent className="p-6">
                <div className="flex flex-col items-center text-center gap-3">
                  <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-muted text-muted-foreground">
                    {integration.icon}
                  </div>
                  <div>
                    <h3 className="font-semibold">{integration.name}</h3>
                    <p className="text-sm text-muted-foreground">{integration.description}</p>
                  </div>
                  <Badge variant="secondary">Coming Soon</Badge>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      {/* Connect Dialog */}
      <Dialog open={!!connectDialog} onOpenChange={() => setConnectDialog(null)}>
        <DialogContent className="sm:max-w-lg">
          <DialogHeader>
            <DialogTitle>Connect {connectDialog?.name}</DialogTitle>
            <DialogDescription>{connectDialog?.description}</DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            {connectDialog?.id === "slack" && (
              <>
                <div className="space-y-2">
                  <Label>Slack Channel</Label>
                  <Select value={slackChannel} onValueChange={setSlackChannel}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="#approvals">#approvals</SelectItem>
                      <SelectItem value="#alerts">#alerts</SelectItem>
                      <SelectItem value="#engineering">#engineering</SelectItem>
                      <SelectItem value="#general">#general</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="flex items-center justify-between rounded-lg border p-4">
                  <div>
                    <p className="font-medium">Blocked Plan Notifications</p>
                    <p className="text-sm text-muted-foreground">Send alerts when plans are blocked</p>
                  </div>
                  <Switch checked={slackNotifications} onCheckedChange={setSlackNotifications} />
                </div>
              </>
            )}
            {connectDialog?.id === "telegram" && (
              <>
                <div className="space-y-2">
                  <Label>Bot Token</Label>
                  <Input
                    placeholder="Enter your Telegram bot token"
                    value={telegramBotToken}
                    onChange={(e) => setTelegramBotToken(e.target.value)}
                  />
                </div>
                <div className="space-y-2">
                  <Label>Chat ID</Label>
                  <Input
                    placeholder="Enter channel or chat ID"
                    value={telegramChatId}
                    onChange={(e) => setTelegramChatId(e.target.value)}
                  />
                </div>
                <div className="space-y-2">
                  <Label>Alert Severity Threshold</Label>
                  <Select defaultValue="medium">
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="low">All alerts (Low and above)</SelectItem>
                      <SelectItem value="medium">Medium and above</SelectItem>
                      <SelectItem value="high">High severity only</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </>
            )}
            {connectDialog?.id === "github" && (
              <>
                <div className="space-y-2">
                  <Label>Organization</Label>
                  <Input value={githubOrg} onChange={(e) => setGithubOrg(e.target.value)} />
                </div>
                <div className="space-y-2">
                  <Label>Repositories (comma-separated)</Label>
                  <Input value={githubRepos} onChange={(e) => setGithubRepos(e.target.value)} />
                </div>
                <div className="space-y-2">
                  <Label>Webhook Events</Label>
                  <div className="space-y-2">
                    {["Push events", "Pull request events", "Issue events"].map((event) => (
                      <div key={event} className="flex items-center gap-2">
                        <Switch defaultChecked />
                        <span className="text-sm">{event}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </>
            )}
            {connectDialog?.id === "mcp" && (
              <>
                <div className="space-y-2">
                  <Label>Tool Profile</Label>
                  <Select value={mcpProfile} onValueChange={setMcpProfile}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="minimal">Minimal - Basic read operations</SelectItem>
                      <SelectItem value="standard">Standard - Read and limited write</SelectItem>
                      <SelectItem value="full">Full - All operations with approval</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label>Safety Scope</Label>
                  <Select defaultValue="strict">
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="strict">Strict - Maximum safety checks</SelectItem>
                      <SelectItem value="balanced">Balanced - Standard safety</SelectItem>
                      <SelectItem value="permissive">Permissive - Minimal restrictions</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </>
            )}
            {connectDialog?.id === "skills" && (
              <>
                <div className="space-y-2">
                  <Label>Available Skill Packs</Label>
                  <div className="space-y-2">
                    {["Code Review", "Security Analysis", "Testing", "Documentation", "Performance"].map((skill) => (
                      <div key={skill} className="flex items-center justify-between rounded-lg border p-3">
                        <span className="text-sm font-medium">{skill}</span>
                        <Switch defaultChecked={skillPacks.includes(skill.toLowerCase().replace(" ", "-"))} />
                      </div>
                    ))}
                  </div>
                </div>
              </>
            )}
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setConnectDialog(null)}>
              Cancel
            </Button>
            <Button onClick={() => completeConnection(connectDialog?.id || "")}>
              Connect
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Configure Dialog */}
      <Dialog open={!!configDialog} onOpenChange={() => setConfigDialog(null)}>
        <DialogContent className="sm:max-w-lg">
          <DialogHeader>
            <DialogTitle>Configure {configDialog?.name}</DialogTitle>
            <DialogDescription>Update your {configDialog?.name} integration settings.</DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            {configDialog?.id === "github" && (
              <>
                <div className="space-y-2">
                  <Label>Organization</Label>
                  <Input value={githubOrg} onChange={(e) => setGithubOrg(e.target.value)} />
                </div>
                <div className="space-y-2">
                  <Label>Repositories</Label>
                  <Input value={githubRepos} onChange={(e) => setGithubRepos(e.target.value)} />
                </div>
              </>
            )}
            {configDialog?.id === "skills" && (
              <div className="space-y-2">
                {["Code Review", "Security Analysis", "Testing", "Documentation", "Performance"].map((skill) => (
                  <div key={skill} className="flex items-center justify-between rounded-lg border p-3">
                    <span className="text-sm font-medium">{skill}</span>
                    <Switch defaultChecked={skill !== "Performance"} />
                  </div>
                ))}
              </div>
            )}
            {configDialog?.id === "mcp" && (
              <>
                <div className="space-y-2">
                  <Label>Tool Profile</Label>
                  <Select value={mcpProfile} onValueChange={setMcpProfile}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="minimal">Minimal</SelectItem>
                      <SelectItem value="standard">Standard</SelectItem>
                      <SelectItem value="full">Full</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </>
            )}
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setConfigDialog(null)}>
              Cancel
            </Button>
            <Button onClick={saveConfig}>
              Save Changes
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
