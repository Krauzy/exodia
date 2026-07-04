param(
  [string]$Query = "",
  [int]$Top = 5,
  [switch]$Json,
  [switch]$List
)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$AgentsRoot = Split-Path -Parent $ScriptDir
$ContextRoot = Join-Path $AgentsRoot "context"
$IndexPath = Join-Path $ContextRoot "index.json"

if (-not (Test-Path -LiteralPath $IndexPath)) {
  throw "Context index not found: $IndexPath"
}

$Index = Get-Content -LiteralPath $IndexPath -Raw | ConvertFrom-Json

function Normalize-Text {
  param([string]$Value)
  if ($null -eq $Value) {
    return ""
  }
  $normalized = $Value.ToLowerInvariant().Normalize([Text.NormalizationForm]::FormD)
  $builder = [Text.StringBuilder]::new()
  foreach ($char in $normalized.ToCharArray()) {
    $category = [Globalization.CharUnicodeInfo]::GetUnicodeCategory($char)
    if ($category -ne [Globalization.UnicodeCategory]::NonSpacingMark) {
      [void]$builder.Append($char)
    }
  }
  return $builder.ToString().Normalize([Text.NormalizationForm]::FormC)
}

function Expand-Query {
  param([string]$Value)
  $synonyms = @{
    "autenticacao" = @("auth", "authentication", "login", "token")
    "autorizacao" = @("authorization", "authorized", "ownership", "scope")
    "alvo" = @("target", "targets")
    "alvos" = @("target", "targets")
    "varredura" = @("scan", "scans")
    "varreduras" = @("scan", "scans")
    "modulo" = @("module", "modules")
    "modulos" = @("module", "modules")
    "relatorio" = @("report", "reports")
    "relatorios" = @("report", "reports")
    "seguranca" = @("security", "safe", "authorization")
    "implantacao" = @("deployment", "runtime", "vercel", "docker")
    "validacao" = @("validation", "tests", "build")
    "banco" = @("database", "sqlite", "sqlalchemy")
    "fila" = @("job", "eventbus", "sse")
    "historico" = @("history", "scans", "reports", "logs")
  }

  $expanded = [System.Collections.Generic.List[string]]::new()
  foreach ($token in (Get-Tokens $Value)) {
    $expanded.Add($token)
    if ($synonyms.ContainsKey($token)) {
      foreach ($synonym in $synonyms[$token]) {
        $expanded.Add((Normalize-Text $synonym))
      }
    }
  }
  return $expanded | Select-Object -Unique
}

function Get-Tokens {
  param([string]$Value)
  $normalized = Normalize-Text $Value
  return $normalized -split "[^a-z0-9_./:-]+" | Where-Object { $_.Length -gt 1 }
}

function Get-Snippet {
  param(
    [string]$Content,
    [string[]]$Tokens
  )
  $normalized = Normalize-Text $Content
  $position = -1
  foreach ($token in $Tokens) {
    $position = $normalized.IndexOf($token)
    if ($position -ge 0) {
      break
    }
  }
  if ($position -lt 0) {
    $position = 0
  }
  $start = [Math]::Max(0, $position - 140)
  $length = [Math]::Min(320, $Content.Length - $start)
  return ($Content.Substring($start, $length) -replace "\s+", " ").Trim()
}

if ($List) {
  $rows = foreach ($document in $Index.documents) {
    [pscustomobject]@{
      Id = $document.id
      Title = $document.title
      Path = Join-Path ".agents/context" $document.path
      Tags = ($document.tags -join ",")
    }
  }
  if ($Json) {
    $rows | ConvertTo-Json -Depth 5
  } else {
    $rows | Format-Table -AutoSize
  }
  exit 0
}

if ([string]::IsNullOrWhiteSpace($Query)) {
  Write-Host "Usage: .\.agents\scripts\search-context.ps1 -Query ""auth scans"" -Top 5"
  Write-Host "       .\.agents\scripts\search-context.ps1 -List"
  exit 0
}

$tokens = @(Expand-Query $Query)
$results = foreach ($document in $Index.documents) {
  $docPath = Join-Path $ContextRoot $document.path
  if (-not (Test-Path -LiteralPath $docPath)) {
    continue
  }

  $content = Get-Content -LiteralPath $docPath -Raw
  $haystack = Normalize-Text (($document.id, $document.title, ($document.tags -join " "), ($document.keywords -join " "), $content) -join " ")
  $score = 0

  foreach ($token in $tokens) {
    $matches = [regex]::Matches($haystack, [regex]::Escape($token)).Count
    if ($matches -gt 0) {
      $score += $matches
      if (($document.keywords | ForEach-Object { Normalize-Text $_ }) -contains $token) {
        $score += 5
      }
      if (($document.tags | ForEach-Object { Normalize-Text $_ }) -contains $token) {
        $score += 3
      }
    }
  }

  if ($score -gt 0) {
    [pscustomobject]@{
      Score = $score
      Id = $document.id
      Title = $document.title
      Path = Join-Path ".agents/context" $document.path
      Tags = $document.tags
      Snippet = Get-Snippet -Content $content -Tokens $tokens
    }
  }
}

$ranked = @($results | Sort-Object -Property Score, Id -Descending | Select-Object -First $Top)

if ($Json) {
  $ranked | ConvertTo-Json -Depth 6
  exit 0
}

if (-not $ranked) {
  Write-Host "No context matches found for query: $Query"
  exit 0
}

foreach ($item in $ranked) {
  Write-Host ("[{0}] {1} - {2}" -f $item.Score, $item.Id, $item.Title)
  Write-Host ("Path: {0}" -f $item.Path)
  Write-Host ("Tags: {0}" -f ($item.Tags -join ", "))
  Write-Host ("Snippet: {0}" -f $item.Snippet)
  Write-Host ""
}
