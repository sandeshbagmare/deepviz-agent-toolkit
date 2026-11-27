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
$head = (& git -C $root rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0 -or $head -cne $ExpectedSha) { throw 'Exact candidate SHA mismatch' }
$dirty = & git -C $root status --porcelain --untracked-files=no
if ($LASTEXITCODE -ne 0 -or $dirty) { throw 'Candidate has tracked changes; use a clean isolated commit' }

$regression = 'packages/deepviz/test/test_r07_tool_spec_null.test.mjs'
$testHash = (Get-FileHash (Join-Path $root $regression) -Algorithm SHA256).Hash.ToLowerInvariant()
if ($testHash -ne '08be1d15661d6bd5bf87bdcec7db11ba3097d9eee294db654369564716e32227') {
    throw 'Immutable helper-null regression checksum mismatch'
}
foreach ($schema in @('schemas/chart-spec.schema.json', 'packages/deepviz/src/chart-spec.schema.json')) {
    $hash = (Get-FileHash (Join-Path $root $schema) -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($hash -ne '3bfc9e4e4351e1d51984a62dcc67ed42eda6a02d61eb718f511a5451d11c4a71') {
        throw 'Schema changed outside the helper-defaulting release; request explicit review'
    }
}
$renderHash = (Get-FileHash (Join-Path $root 'packages/deepviz/src/render.ts') -Algorithm SHA256).Hash.ToLowerInvariant()
$knownUnfixed = $renderHash -eq '7f0a69004d570e05b45b8c6ce10c73263652d2874362960af27baed82b3996e9'
$originCheck = "import {realpathSync} from 'node:fs';import {fileURLToPath} from 'node:url';import assert from 'node:assert/strict';const resolved=realpathSync(fileURLToPath(import.meta.resolve('@deepviz/agent-toolkit')));assert.equal(resolved,realpathSync(process.argv[1]));console.log(resolved);"
$steps = @(
    @{ name = 'build'; executable = 'npm.cmd'; arguments = @('run', 'build'); cwd = $root },
    @{ name = 'public-origin'; executable = 'node'; arguments = @('--input-type=module', '--eval', $originCheck, (Join-Path $root 'packages/deepviz/dist/index.js')); cwd = (Join-Path $root 'packages/deepviz') },
    @{ name = 'typecheck'; executable = 'npm.cmd'; arguments = @('run', 'typecheck'); cwd = $root },
    @{ name = 'immutable-regression'; executable = 'node'; arguments = @('--test', $regression); cwd = $root },
    @{ name = 'full-npm'; executable = 'npm.cmd'; arguments = @('test'); cwd = $root },
    @{ name = 'schema-check'; executable = 'npm.cmd'; arguments = @('run', 'schema:check'); cwd = $root },
    @{ name = 'python-schema-check'; executable = $Python; arguments = @('scripts/export_schema.py', '--check'); cwd = $root },
    @{ name = 'core-parity'; executable = $Python; arguments = @('-m', 'pytest', 'tests/test_models.py', 'tests/test_schema_contract.py', 'tests/test_cross_language_contract.py', 'tests/test_n12_authoritative_parity.py', '-q'); cwd = $root },
    @{ name = 'npm-pack-dry-run'; executable = 'npm.cmd'; arguments = @('pack', '--dry-run', '--workspace', '@deepviz/agent-toolkit'); cwd = $root }
)
$receipt = [ordered]@{
    status = 'PLAN_ONLY_NOT_EXECUTED'; source_sha = $head; candidate = $root
    immutable_test_sha256 = $testHash; render_source_sha256 = $renderHash
    known_unfixed_source = $knownUnfixed
    steps = @($steps | ForEach-Object { [ordered]@{ name = $_.name; executable = $_.executable; arguments = $_.arguments; cwd = $_.cwd; state = 'NOT_RUN' } })
}
if (-not $Run) { $receipt | ConvertTo-Json -Depth 6; exit 0 }
if ($knownUnfixed) { throw 'Known unfixed render.ts: do not repeat completed RED suites; wait for an eligible producer commit' }
if (-not (Test-Path -LiteralPath $Python -PathType Leaf)) { throw 'Explicit Python executable not found' }
if (-not (Test-Path -LiteralPath $ToolsBin -PathType Container)) { throw 'Explicit read-only tools directory not found' }
if (Test-Path -LiteralPath $EvidenceDirectory) { throw 'Evidence directory must be new; preserve earlier evidence' }

$evidence = (New-Item -ItemType Directory -Path $EvidenceDirectory).FullName
$old = @{ PATH = $env:PATH; PYTHONPATH = $env:PYTHONPATH; NPM_CONFIG_CACHE = $env:NPM_CONFIG_CACHE; NPM_CONFIG_UPDATE_NOTIFIER = $env:NPM_CONFIG_UPDATE_NOTIFIER }
$failed = $false
try {
    $env:PATH = $ToolsBin + [IO.Path]::PathSeparator + $env:PATH
    $env:PYTHONPATH = Join-Path $root 'python/deepviz/src'
    $env:NPM_CONFIG_CACHE = Join-Path $evidence 'npm-cache'
    $env:NPM_CONFIG_UPDATE_NOTIFIER = 'false'
    for ($index = 0; $index -lt $steps.Count; $index++) {
        $step = $steps[$index]
        $log = Join-Path $evidence ($step.name + '.log')
        Push-Location $step.cwd
        try {
            $executable = (Get-Command -Name $step.executable -CommandType Application -ErrorAction Stop).Source
            $arguments = $step.arguments
            $ErrorActionPreference = 'Continue'
            & $executable @arguments *> $log
            $code = $LASTEXITCODE
        } finally { $ErrorActionPreference = 'Stop'; Pop-Location }
        $receipt.steps[$index]['state'] = 'EXECUTED'
        $receipt.steps[$index]['exit'] = $code
        $receipt.steps[$index]['log'] = $log
        Write-Output ($step.name + ' exit=' + $code)
        if ($code -ne 0) { $failed = $true; break }
    }
    $receipt.status = if ($failed) { 'GATE_FAILURE_REMAINING_STEPS_NOT_RUN' } else { 'SCOPED_GATES_PASS_NOT_FINAL_APPROVAL' }
    if (Test-Path (Join-Path $root 'packages/deepviz/dist/render.js')) {
        $receipt['built_render_sha256'] = (Get-FileHash (Join-Path $root 'packages/deepviz/dist/render.js') -Algorithm SHA256).Hash.ToLowerInvariant()
    }
} catch {
    $failed = $true
    $receipt.status = 'HARNESS_ERROR_NOT_A_PRODUCT_PASS'
    Write-Error 'Retest harness failed; inspect the step log and do not infer acceptance' -ErrorAction Continue
} finally {
    $receipt | ConvertTo-Json -Depth 6 | Set-Content (Join-Path $evidence 'result.json') -Encoding UTF8
    foreach ($name in $old.Keys) { Set-Item -Path ('Env:' + $name) -Value $old[$name] }
}
if ($failed) { exit 1 }
exit 0
