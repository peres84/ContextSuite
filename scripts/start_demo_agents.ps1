param(
    [ValidateSet("codex", "claude", "cursor")]
    [string]$Assistant = "claude",
    [int]$ContextPort = 8000,
    [int]$CliPort = 8001,
    [switch]$OpenDemoSite,
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$PowerShellExe = (Get-Command powershell.exe).Source
$CleanupPorts = @($ContextPort, $CliPort, 8010, 8011, 8012, 8013, 8014) | Sort-Object -Unique

function Write-Step {
    param(
        [string]$Message,
        [ConsoleColor]$Color = [ConsoleColor]::Cyan
    )

    Write-Host "==> $Message" -ForegroundColor $Color
}

function New-AgentTerminal {
    param(
        [string]$Title,
        [string]$TitleColor = "Green",
        [string[]]$Lines
    )

    $safeTitle = $Title.Replace("'", "''")
    $safeRoot = $RepoRoot.Replace("'", "''")
    $safeTitleColor = $TitleColor.Replace("'", "''")
    $scriptLines = @(
        '$ErrorActionPreference = ''Stop'''
        "`$Host.UI.RawUI.WindowTitle = '$safeTitle'"
        "Set-Location '$safeRoot'"
        "Clear-Host"
        "Write-Host '$safeTitle' -ForegroundColor $safeTitleColor"
        "Write-Host ('Repo: ' + (Get-Location)) -ForegroundColor DarkGray"
    ) + $Lines

    $command = "& {`n" + ($scriptLines -join "`n") + "`n}"

    if ($DryRun) {
        Write-Step "Dry run: would open terminal '$Title'" "DarkYellow"
        Write-Host $command -ForegroundColor DarkGray
        return
    }

    Start-Process `
        -FilePath $PowerShellExe `
        -WorkingDirectory $RepoRoot `
        -ArgumentList @("-NoExit", "-ExecutionPolicy", "Bypass", "-Command", $command) | Out-Null
}

function Stop-AgentProcesses {
    $processes = Get-CimInstance Win32_Process -ErrorAction SilentlyContinue | Where-Object {
        $_.ProcessId -ne $PID -and
        $_.CommandLine -and
        (
            $_.CommandLine -match 'context-agent' -or
            $_.CommandLine -match 'cli-agent' -or
            $_.CommandLine -match 'contextsuite_agent\.server:app' -or
            $_.CommandLine -match 'contextsuite_cli\.server:app'
        )
    }

    foreach ($process in $processes) {
        Write-Step "Stopping stale process $($process.ProcessId) ($($process.Name))" "DarkYellow"
        Stop-Process -Id $process.ProcessId -Force -ErrorAction SilentlyContinue
    }
}

function Stop-ListeningPorts {
    param([int[]]$Ports)

    $listeners = Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue |
        Where-Object { $_.LocalPort -in $Ports }

    $processIds = $listeners | Select-Object -ExpandProperty OwningProcess -Unique
    foreach ($processId in $processIds) {
        if ($processId -and $processId -gt 0) {
            Write-Step "Freeing port owner PID $processId" "DarkYellow"
            Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
        }
    }
}

function Wait-ForPortsFree {
    param(
        [int[]]$Ports,
        [int]$TimeoutSec = 15
    )

    $deadline = (Get-Date).AddSeconds($TimeoutSec)
    while ((Get-Date) -lt $deadline) {
        $listeners = Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue |
            Where-Object { $_.LocalPort -in $Ports }
        if (-not $listeners) {
            return $true
        }
        Start-Sleep -Seconds 1
    }

    return $false
}

function Wait-ForHealth {
    param(
        [string]$Name,
        [string]$Url,
        [int]$TimeoutSec = 30
    )

    if ($DryRun) {
        Write-Step "Dry run: would wait for $Name at $Url" "DarkYellow"
        return $true
    }

    $deadline = (Get-Date).AddSeconds($TimeoutSec)
    while ((Get-Date) -lt $deadline) {
        try {
            Invoke-RestMethod -Method Get -Uri $Url -TimeoutSec 2 | Out-Null
            Write-Step "$Name is ready at $Url" "Green"
            return $true
        }
        catch {
            Start-Sleep -Seconds 1
        }
    }

    Write-Step "$Name did not become ready within $TimeoutSec seconds" "Yellow"
    return $false
}

Write-Step "Repo root: $RepoRoot"
Write-Step "Cleaning stale agent processes and ports: $($CleanupPorts -join ', ')"

Stop-AgentProcesses
Stop-ListeningPorts -Ports $CleanupPorts

if (-not (Wait-ForPortsFree -Ports $CleanupPorts)) {
    Write-Step "Some ports are still busy. You may need to rerun the launcher." "Red"
}

New-AgentTerminal -Title "ContextSuite CLI Agent" -TitleColor "Blue" -Lines @(
    "`$env:CLI_AGENT_PORT = '$CliPort'"
    "Write-Host 'Starting CLI Agent on http://127.0.0.1:$CliPort' -ForegroundColor Cyan"
    "uv run cli-agent"
)

New-AgentTerminal -Title "ContextSuite Context Agent" -TitleColor "DarkYellow" -Lines @(
    "`$env:CONTEXT_AGENT_PORT = '$ContextPort'"
    "`$env:CLI_AGENT_PORT = '$CliPort'"
    "Write-Host 'Starting Context Agent on http://127.0.0.1:$ContextPort' -ForegroundColor Cyan"
    "Write-Host 'Dispatch target: http://127.0.0.1:$CliPort' -ForegroundColor DarkCyan"
    "uv run context-agent"
)

if ($OpenDemoSite) {
    New-AgentTerminal -Title "ContextSuite Demo Site" -TitleColor "Green" -Lines @(
        "Set-Location 'demo'"
        "Write-Host 'Starting demo site in ./demo' -ForegroundColor Cyan"
        "if (-not (Test-Path 'node_modules')) { npm install }"
        "npm run dev"
    )
}

Wait-ForHealth -Name "CLI Agent" -Url "http://127.0.0.1:$CliPort/health" | Out-Null
Wait-ForHealth -Name "Context Agent" -Url "http://127.0.0.1:$ContextPort/health" | Out-Null

New-AgentTerminal -Title "ContextSuite Demo Prompt" -TitleColor "Yellow" -Lines @(
    "Write-Host 'Initializing ./demo for assistant: $Assistant' -ForegroundColor Cyan"
    "uv run contextsuite -p ./demo init -r 'demo/green-brand-site' -a $Assistant"
    "Write-Host ''"
    "Write-Host 'Ready. Run one of these next:' -ForegroundColor Green"
    'Write-Host ''uv run contextsuite -p ./demo chat "Improve the layout spacing, make the testimonials section clearer, and keep the primary green theme."'' -ForegroundColor White'
    'Write-Host ''uv run contextsuite -p ./demo chat "Change the primary site color from green to red across the landing page. If constraints prevent that, explain why in one short paragraph and do not edit files."'' -ForegroundColor White'
    "Write-Host ''"
    "Write-Host 'You can type the chat command directly in this terminal.' -ForegroundColor DarkGray"
)

Write-Step "Launcher finished. Fresh agent terminals are open." "Green"
