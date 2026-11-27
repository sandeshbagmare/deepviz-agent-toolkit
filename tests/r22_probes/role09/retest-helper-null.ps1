[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$Candidate,
    [Parameter(Mandatory = $true)][ValidatePattern('^[0-9a-f]{40}$')][string]$ExpectedSha,
    [Parameter(Mandatory = $true)][string]$EvidenceDirectory,
    [Parameter(Mandatory = $true)][string]$Python,
    [Parameter(Mandatory = $true)][string]$ToolsBin,
    [switch]$Run
)
$ErrorActionPreference = 'Stop'
$root = (Resolve-Path -LiteralPath $Candidate).Path
$pythonExe = (Resolve-Path -LiteralPath $Python).Path
$guard = Join-Path $PSScriptRoot 'recipe_guard.py'
function Get-Snapshot([string]$Mode='snapshot-after') {
    $text = & $pythonExe $guard $Mode $root
    if ($LASTEXITCODE -ne 0) { throw 'Source/runner identity check failed' }
    return ($text -join "`n")
}
function Resolve-OneTool([string[]]$Names) {
    foreach ($name in $Names) {
        $path = Join-Path $ToolsBin $name
        if (Test-Path -LiteralPath $path -PathType Leaf) { return (Resolve-Path -LiteralPath $path).Path }
    }
    throw 'Expected explicit tool missing from ToolsBin; PATH fallback forbidden'
}
$before = Get-Snapshot 'snapshot'
$identity = $before | ConvertFrom-Json
if ($identity.head -cne $ExpectedSha) { throw 'Exact candidate SHA mismatch' }
$regression = 'packages/deepviz/test/test_r07_tool_spec_null.test.mjs'
if ($identity.tracked_sha256.$regression -ne '08be1d15661d6bd5bf87bdcec7db11ba3097d9eee294db654369564716e32227') { throw 'Immutable regression checksum mismatch' }
foreach ($schema in @('schemas/chart-spec.schema.json', 'packages/deepviz/src/chart-spec.schema.json')) {
    if ($identity.tracked_sha256.$schema -ne '3bfc9e4e4351e1d51984a62dcc67ed42eda6a02d61eb718f511a5451d11c4a71') { throw 'Schema changed outside helper release' }
}
$npmExe = Resolve-OneTool @('npm.cmd')
$nodeExe = Resolve-OneTool @('node.exe', 'node.cmd')
$knownUnfixed = $identity.tracked_sha256.'packages/deepviz/src/render.ts' -eq '7f0a69004d570e05b45b8c6ce10c73263652d2874362960af27baed82b3996e9'
$steps = @(
    @{ name='build'; executable=$npmExe; arguments=@('run','build'); cwd=$root },
    @{ name='public-origin'; executable=$nodeExe; arguments=@('--conditions=import',(Join-Path $PSScriptRoot 'public-origin.mjs'), (Join-Path $root 'packages/deepviz')); cwd=(Join-Path $root 'packages/deepviz') },
    @{ name='typecheck'; executable=$npmExe; arguments=@('run','typecheck'); cwd=$root },
    @{ name='immutable-regression'; executable=$nodeExe; arguments=@('--test','--test-reporter=tap',$regression); cwd=$root; minimum=36 },
    @{ name='full-npm'; executable=$npmExe; arguments=@('test'); cwd=$root; minimum=282 },
    @{ name='schema-check'; executable=$npmExe; arguments=@('run','schema:check'); cwd=$root },
    @{ name='python-schema-check'; executable=$pythonExe; arguments=@('scripts/export_schema.py','--check'); cwd=$root },
    @{ name='core-parity'; executable=$pythonExe; arguments=@($guard,'pytest',$root,(Join-Path $EvidenceDirectory 'source-before.json'),$EvidenceDirectory); cwd=$root },
    @{ name='npm-pack-dry-run'; executable=$npmExe; arguments=@('pack','--dry-run','--workspace','@deepviz/agent-toolkit'); cwd=$root }
)
$receipt = [ordered]@{
    status='PLAN_ONLY_NOT_EXECUTED'; source_sha=$identity.head; candidate=$root; known_unfixed_source=$knownUnfixed
    skip_policy='ZERO_ALLOWED'; minimum_tests=@{ immutable_regression=36; full_npm=282; core_parity=4; core_selected_files=4 }
    steps=@($steps | ForEach-Object { [ordered]@{ name=$_.name; executable=$_.executable; arguments=$_.arguments; cwd=$_.cwd; state='NOT_RUN' } })
}
if (-not $Run) { $receipt | ConvertTo-Json -Depth 8; exit 0 }
if ($knownUnfixed) { throw 'Known unfixed source: do not repeat old RED product suites' }
$evidenceFull = [IO.Path]::GetFullPath($EvidenceDirectory)
if ($evidenceFull.StartsWith($root + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase) -or $evidenceFull -eq $root) { throw 'Evidence must be external to candidate' }
if (Test-Path -LiteralPath $EvidenceDirectory) { throw 'Evidence directory must be new' }
$evidence = (New-Item -ItemType Directory -Path $EvidenceDirectory).FullName
$before | Set-Content (Join-Path $evidence 'source-before.json') -Encoding UTF8
$old = @{}
foreach ($name in @('PATH','PYTHONPATH','PYTEST_ADDOPTS','PYTEST_DISABLE_PLUGIN_AUTOLOAD','NODE_OPTIONS','NPM_CONFIG_CACHE','NPM_CONFIG_UPDATE_NOTIFIER')) { $old[$name]=[Environment]::GetEnvironmentVariable($name) }
$failed = $false
$toolsBefore = @($npmExe,$nodeExe,$pythonExe) | ForEach-Object { (Get-FileHash -LiteralPath $_ -Algorithm SHA256).Hash }
try {
    $env:PATH = $ToolsBin + [IO.Path]::PathSeparator + $env:PATH
    $env:PYTHONPATH = Join-Path $root 'python/deepviz/src'
    $env:PYTEST_ADDOPTS = ''
    $env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = '1'
    $env:NODE_OPTIONS = '--test-reporter=tap'
    $env:NPM_CONFIG_CACHE = Join-Path $evidence 'npm-cache'
    $env:NPM_CONFIG_UPDATE_NOTIFIER = 'false'
    for ($index=0; $index -lt $steps.Count; $index++) {
        if ((Get-Snapshot) -cne $before) { throw 'Source/runner/HEAD identity changed before gate' }
        $step=$steps[$index]; $log=Join-Path $evidence ($step.name+'.log')
        Push-Location $step.cwd
        try {
            $arguments=$step.arguments; $executable=$step.executable
            $ErrorActionPreference='Continue'
            & $executable @arguments *> $log
            $code=$LASTEXITCODE
        } finally { $ErrorActionPreference='Stop'; Pop-Location }
        $receipt.steps[$index]['state']='EXECUTED'; $receipt.steps[$index]['exit']=$code; $receipt.steps[$index]['log']=$log
        $after=Get-Snapshot
        if ($after -cne $before) { throw 'Source/runner/test/config/HEAD identity changed after gate' }
        $toolsAfter=@($npmExe,$nodeExe,$pythonExe) | ForEach-Object { (Get-FileHash -LiteralPath $_ -Algorithm SHA256).Hash }
        if (($toolsAfter -join ',') -cne ($toolsBefore -join ',')) { throw 'Explicit tool bytes changed' }
        if ($code -ne 0) { throw ('Gate failed: '+$step.name) }
        if ($step.ContainsKey('minimum')) {
            $totals = & $pythonExe $guard tap $log $step.minimum
            if ($LASTEXITCODE -ne 0) { throw ('Structured TAP rejected: '+$step.name) }
            $receipt.steps[$index]['totals']=($totals | ConvertFrom-Json)
        }
        if ($step.name -eq 'core-parity') {
            $origin=Get-Content -Raw (Join-Path $evidence 'python-origin.json') | ConvertFrom-Json
            if ($origin.status -ne 'SAME_PROCESS_ORIGIN_AND_COUNTS_VERIFIED') { throw 'Actual Python origin/count receipt missing' }
            $receipt.steps[$index]['provenance']=$origin
        }
    }
    if ((Get-Snapshot) -cne $before) { throw 'Final source identity changed' }
    $receipt.status='SCOPED_GATES_PASS_NOT_FINAL_APPROVAL'
} catch {
    $failed=$true; $receipt.status='GATE_OR_PROVENANCE_FAILURE_NOT_PRODUCT_PASS'; $receipt['failure']=$_.Exception.Message
} finally {
    try { $receipt['source_after']=(Get-Snapshot | ConvertFrom-Json) } catch { $receipt['source_after_error']=$_.Exception.Message; $failed=$true; $receipt.status='GATE_OR_PROVENANCE_FAILURE_NOT_PRODUCT_PASS' }
    $receipt | ConvertTo-Json -Depth 12 | Set-Content (Join-Path $evidence 'result.json') -Encoding UTF8
    foreach ($name in $old.Keys) { [Environment]::SetEnvironmentVariable($name,$old[$name]) }
}
if ($failed) { exit 1 }; exit 0
