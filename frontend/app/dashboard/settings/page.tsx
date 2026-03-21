"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Switch } from "@/components/ui/switch"
import { Separator } from "@/components/ui/separator"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog"
import {
  Settings,
  User,
  Building2,
  Bell,
  Shield,
  Key,
  Trash2,
  Copy,
  RefreshCw,
  Users,
  CreditCard,
  Download,
} from "lucide-react"
import { toast } from "sonner"

export default function SettingsPage() {
  // Profile settings
  const [profile, setProfile] = useState({
    name: "Admin User",
    email: "admin@acme.com",
    role: "Owner",
  })

  // Workspace settings
  const [workspace, setWorkspace] = useState({
    name: "Acme Corp",
    plan: "Pro",
    teamSize: "5",
    defaultRiskMode: "medium",
    defaultApprovalMode: "human-gated",
  })

  // Notification settings
  const [notifications, setNotifications] = useState({
    emailAlerts: true,
    slackNotifications: true,
    browserNotifications: false,
    digestFrequency: "daily",
    alertOnBlocked: true,
    alertOnHighRisk: true,
    alertOnApprovalRequired: true,
  })

  // Security settings
  const [security, setSecurity] = useState({
    twoFactorEnabled: true,
    sessionTimeout: "24",
    ipWhitelist: false,
    auditLogging: true,
  })

  // API Key (demo)
  const [apiKey] = useState("ctx_live_xxxxxxxxxxxxxxxxxxxxxxxxxxxx")
  const [showApiKey, setShowApiKey] = useState(false)

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
    toast.success("Copied to clipboard!")
  }

  const saveSettings = () => {
    toast.success("Settings saved successfully")
  }

  const regenerateApiKey = () => {
    toast.success("API key regenerated")
  }

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Settings</h1>
        <p className="text-muted-foreground">Manage your account and workspace preferences.</p>
      </div>

      <Tabs defaultValue="profile" className="space-y-6">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="profile" className="flex items-center gap-2">
            <User className="h-4 w-4" />
            <span className="hidden sm:inline">Profile</span>
          </TabsTrigger>
          <TabsTrigger value="workspace" className="flex items-center gap-2">
            <Building2 className="h-4 w-4" />
            <span className="hidden sm:inline">Workspace</span>
          </TabsTrigger>
          <TabsTrigger value="notifications" className="flex items-center gap-2">
            <Bell className="h-4 w-4" />
            <span className="hidden sm:inline">Notifications</span>
          </TabsTrigger>
          <TabsTrigger value="security" className="flex items-center gap-2">
            <Shield className="h-4 w-4" />
            <span className="hidden sm:inline">Security</span>
          </TabsTrigger>
          <TabsTrigger value="api" className="flex items-center gap-2">
            <Key className="h-4 w-4" />
            <span className="hidden sm:inline">API</span>
          </TabsTrigger>
        </TabsList>

        {/* Profile Tab */}
        <TabsContent value="profile" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Profile Information</CardTitle>
              <CardDescription>Update your account details and preferences.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Full Name</Label>
                  <Input
                    value={profile.name}
                    onChange={(e) => setProfile({ ...profile, name: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <Label>Email</Label>
                  <Input
                    type="email"
                    value={profile.email}
                    onChange={(e) => setProfile({ ...profile, email: e.target.value })}
                  />
                </div>
              </div>
              <div className="space-y-2">
                <Label>Role</Label>
                <div className="flex items-center gap-2">
                  <Badge variant="secondary">{profile.role}</Badge>
                  <span className="text-sm text-muted-foreground">Contact workspace admin to change roles</span>
                </div>
              </div>
              <Button onClick={saveSettings}>Save Changes</Button>
            </CardContent>
          </Card>

          <Card className="border-destructive">
            <CardHeader>
              <CardTitle className="text-destructive">Danger Zone</CardTitle>
              <CardDescription>Irreversible actions for your account.</CardDescription>
            </CardHeader>
            <CardContent>
              <AlertDialog>
                <AlertDialogTrigger asChild>
                  <Button variant="destructive">
                    <Trash2 className="mr-2 h-4 w-4" />
                    Delete Account
                  </Button>
                </AlertDialogTrigger>
                <AlertDialogContent>
                  <AlertDialogHeader>
                    <AlertDialogTitle>Delete Account</AlertDialogTitle>
                    <AlertDialogDescription>
                      This action cannot be undone. This will permanently delete your account and remove all associated data.
                    </AlertDialogDescription>
                  </AlertDialogHeader>
                  <AlertDialogFooter>
                    <AlertDialogCancel>Cancel</AlertDialogCancel>
                    <AlertDialogAction className="bg-destructive text-destructive-foreground hover:bg-destructive/90">
                      Delete Account
                    </AlertDialogAction>
                  </AlertDialogFooter>
                </AlertDialogContent>
              </AlertDialog>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Workspace Tab */}
        <TabsContent value="workspace" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Workspace Settings</CardTitle>
              <CardDescription>Configure your workspace preferences and defaults.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Workspace Name</Label>
                  <Input
                    value={workspace.name}
                    onChange={(e) => setWorkspace({ ...workspace, name: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <Label>Team Size</Label>
                  <Select value={workspace.teamSize} onValueChange={(v) => setWorkspace({ ...workspace, teamSize: v })}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="1">Solo</SelectItem>
                      <SelectItem value="5">Small Team (2-5)</SelectItem>
                      <SelectItem value="20">Medium Team (6-20)</SelectItem>
                      <SelectItem value="100">Large Team (21+)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <Separator />

              <h4 className="font-medium">Default Agent Settings</h4>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Default Risk Mode</Label>
                  <Select value={workspace.defaultRiskMode} onValueChange={(v) => setWorkspace({ ...workspace, defaultRiskMode: v })}>
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
                  <Label>Default Approval Mode</Label>
                  <Select value={workspace.defaultApprovalMode} onValueChange={(v) => setWorkspace({ ...workspace, defaultApprovalMode: v })}>
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

              <Button onClick={saveSettings}>Save Changes</Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Plan & Billing</CardTitle>
              <CardDescription>Manage your subscription and billing details.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between rounded-lg border p-4">
                <div>
                  <div className="flex items-center gap-2">
                    <h4 className="font-semibold">Pro Plan</h4>
                    <Badge className="bg-primary">Current</Badge>
                  </div>
                  <p className="text-sm text-muted-foreground">Unlimited agents, priority support, advanced analytics</p>
                </div>
                <div className="text-right">
                  <p className="text-2xl font-bold">$49</p>
                  <p className="text-sm text-muted-foreground">/month</p>
                </div>
              </div>
              <div className="flex gap-2">
                <Button variant="outline">
                  <CreditCard className="mr-2 h-4 w-4" />
                  Manage Billing
                </Button>
                <Button variant="outline">
                  <Download className="mr-2 h-4 w-4" />
                  Download Invoices
                </Button>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Team Members</CardTitle>
              <CardDescription>Manage who has access to this workspace.</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {[
                  { name: "Admin User", email: "admin@acme.com", role: "Owner" },
                  { name: "Dev Lead", email: "dev@acme.com", role: "Admin" },
                  { name: "Engineer", email: "engineer@acme.com", role: "Member" },
                ].map((member) => (
                  <div key={member.email} className="flex items-center justify-between rounded-lg border p-4">
                    <div>
                      <p className="font-medium">{member.name}</p>
                      <p className="text-sm text-muted-foreground">{member.email}</p>
                    </div>
                    <Badge variant="outline">{member.role}</Badge>
                  </div>
                ))}
              </div>
              <Button className="mt-4" variant="outline">
                <Users className="mr-2 h-4 w-4" />
                Invite Team Member
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Notifications Tab */}
        <TabsContent value="notifications" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Notification Preferences</CardTitle>
              <CardDescription>Choose how and when you receive notifications.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <h4 className="font-medium">Channels</h4>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium">Email Alerts</p>
                      <p className="text-sm text-muted-foreground">Receive notifications via email</p>
                    </div>
                    <Switch
                      checked={notifications.emailAlerts}
                      onCheckedChange={(v) => setNotifications({ ...notifications, emailAlerts: v })}
                    />
                  </div>
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium">Slack Notifications</p>
                      <p className="text-sm text-muted-foreground">Send alerts to connected Slack channel</p>
                    </div>
                    <Switch
                      checked={notifications.slackNotifications}
                      onCheckedChange={(v) => setNotifications({ ...notifications, slackNotifications: v })}
                    />
                  </div>
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium">Browser Notifications</p>
                      <p className="text-sm text-muted-foreground">Show desktop notifications</p>
                    </div>
                    <Switch
                      checked={notifications.browserNotifications}
                      onCheckedChange={(v) => setNotifications({ ...notifications, browserNotifications: v })}
                    />
                  </div>
                </div>
              </div>

              <Separator />

              <div className="space-y-4">
                <h4 className="font-medium">Alert Types</h4>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium">Blocked Plans</p>
                      <p className="text-sm text-muted-foreground">When a plan is blocked by policy</p>
                    </div>
                    <Switch
                      checked={notifications.alertOnBlocked}
                      onCheckedChange={(v) => setNotifications({ ...notifications, alertOnBlocked: v })}
                    />
                  </div>
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium">High Risk Reviews</p>
                      <p className="text-sm text-muted-foreground">When a high-risk review is processed</p>
                    </div>
                    <Switch
                      checked={notifications.alertOnHighRisk}
                      onCheckedChange={(v) => setNotifications({ ...notifications, alertOnHighRisk: v })}
                    />
                  </div>
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium">Approval Required</p>
                      <p className="text-sm text-muted-foreground">When human approval is needed</p>
                    </div>
                    <Switch
                      checked={notifications.alertOnApprovalRequired}
                      onCheckedChange={(v) => setNotifications({ ...notifications, alertOnApprovalRequired: v })}
                    />
                  </div>
                </div>
              </div>

              <Separator />

              <div className="space-y-2">
                <Label>Digest Frequency</Label>
                <Select
                  value={notifications.digestFrequency}
                  onValueChange={(v) => setNotifications({ ...notifications, digestFrequency: v })}
                >
                  <SelectTrigger className="w-[200px]">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="realtime">Real-time</SelectItem>
                    <SelectItem value="hourly">Hourly Digest</SelectItem>
                    <SelectItem value="daily">Daily Digest</SelectItem>
                    <SelectItem value="weekly">Weekly Digest</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <Button onClick={saveSettings}>Save Preferences</Button>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Security Tab */}
        <TabsContent value="security" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Security Settings</CardTitle>
              <CardDescription>Protect your account and workspace.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">Two-Factor Authentication</p>
                    <p className="text-sm text-muted-foreground">Add an extra layer of security</p>
                  </div>
                  <Switch
                    checked={security.twoFactorEnabled}
                    onCheckedChange={(v) => setSecurity({ ...security, twoFactorEnabled: v })}
                  />
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">IP Whitelist</p>
                    <p className="text-sm text-muted-foreground">Restrict access to specific IPs</p>
                  </div>
                  <Switch
                    checked={security.ipWhitelist}
                    onCheckedChange={(v) => setSecurity({ ...security, ipWhitelist: v })}
                  />
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">Audit Logging</p>
                    <p className="text-sm text-muted-foreground">Log all account activity</p>
                  </div>
                  <Switch
                    checked={security.auditLogging}
                    onCheckedChange={(v) => setSecurity({ ...security, auditLogging: v })}
                  />
                </div>
              </div>

              <Separator />

              <div className="space-y-2">
                <Label>Session Timeout (hours)</Label>
                <Select
                  value={security.sessionTimeout}
                  onValueChange={(v) => setSecurity({ ...security, sessionTimeout: v })}
                >
                  <SelectTrigger className="w-[200px]">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="1">1 hour</SelectItem>
                    <SelectItem value="8">8 hours</SelectItem>
                    <SelectItem value="24">24 hours</SelectItem>
                    <SelectItem value="168">1 week</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <Button onClick={saveSettings}>Save Security Settings</Button>
            </CardContent>
          </Card>
        </TabsContent>

        {/* API Tab */}
        <TabsContent value="api" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>API Access</CardTitle>
              <CardDescription>Manage your API keys for programmatic access.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label>API Key</Label>
                <div className="flex gap-2">
                  <Input
                    type={showApiKey ? "text" : "password"}
                    value={apiKey}
                    readOnly
                    className="font-mono"
                  />
                  <Button variant="outline" onClick={() => setShowApiKey(!showApiKey)}>
                    {showApiKey ? "Hide" : "Show"}
                  </Button>
                  <Button variant="outline" size="icon" onClick={() => copyToClipboard(apiKey)}>
                    <Copy className="h-4 w-4" />
                  </Button>
                </div>
                <p className="text-xs text-muted-foreground">
                  Keep this key secret. Do not share it or expose it in client-side code.
                </p>
              </div>

              <AlertDialog>
                <AlertDialogTrigger asChild>
                  <Button variant="outline">
                    <RefreshCw className="mr-2 h-4 w-4" />
                    Regenerate Key
                  </Button>
                </AlertDialogTrigger>
                <AlertDialogContent>
                  <AlertDialogHeader>
                    <AlertDialogTitle>Regenerate API Key</AlertDialogTitle>
                    <AlertDialogDescription>
                      This will invalidate your current API key. Any applications using the current key will need to be updated.
                    </AlertDialogDescription>
                  </AlertDialogHeader>
                  <AlertDialogFooter>
                    <AlertDialogCancel>Cancel</AlertDialogCancel>
                    <AlertDialogAction onClick={regenerateApiKey}>Regenerate</AlertDialogAction>
                  </AlertDialogFooter>
                </AlertDialogContent>
              </AlertDialog>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Webhooks</CardTitle>
              <CardDescription>Receive real-time notifications for events.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label>Webhook URL</Label>
                <Input placeholder="https://your-server.com/webhook" />
              </div>
              <div className="space-y-2">
                <Label>Events to Send</Label>
                <div className="space-y-2">
                  {["review.completed", "review.blocked", "approval.required", "agent.created"].map((event) => (
                    <div key={event} className="flex items-center gap-2">
                      <Switch defaultChecked />
                      <code className="text-sm">{event}</code>
                    </div>
                  ))}
                </div>
              </div>
              <Button onClick={saveSettings}>Save Webhook Settings</Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>API Documentation</CardTitle>
              <CardDescription>Learn how to integrate with ContextSuite.</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="rounded-lg bg-muted p-4">
                <p className="text-sm text-muted-foreground mb-2">Quick Start Example:</p>
                <pre className="text-sm overflow-x-auto">
{`curl -X POST https://api.contextsuite.io/v1/reviews \\
  -H "Authorization: Bearer $API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{"plan": "Add user authentication"}'`}
                </pre>
              </div>
              <Button className="mt-4" variant="outline" asChild>
                <a href="#">View Full Documentation</a>
              </Button>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
