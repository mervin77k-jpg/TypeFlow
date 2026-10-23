$ErrorActionPreference = 'Stop'
$PythonVersion = '3.14.9'
function Test-Python([string]$exe) {
    if (-not $exe -or -not (Test-Path -LiteralPath $exe -PathType Leaf)) { return $false }
    try {
        & $exe -I -c 'import sys, tkinter; assert sys.version_info >= (3,10); r=tkinter.Tk(); r.withdraw(); r.destroy()' 2>$null | Out-Null
        return ($LASTEXITCODE -eq 0)
    } catch { return $false }
}
function Find-Python([string]$preferred) {
    $candidates = @($preferred)
    foreach ($name in @('python.exe','python3.exe')) {
        $cmd = Get-Command $name -CommandType Application -ErrorAction SilentlyContinue
        if ($cmd -and $cmd.Source -notlike '*\Microsoft\WindowsApps\*') { $candidates += $cmd.Source }
    }
    foreach ($root in @('HKCU:\Software\Python\PythonCore','HKLM:\Software\Python\PythonCore','HKLM:\Software\WOW6432Node\Python\PythonCore')) {
        foreach ($version in @(Get-ChildItem $root -ErrorAction SilentlyContinue)) {
            $key = Get-Item ($version.PSPath + '\InstallPath') -ErrorAction SilentlyContinue
            if ($key) {
                $exe = $key.GetValue('ExecutablePath')
                if (-not $exe -and $key.GetValue('')) { $exe = Join-Path $key.GetValue('') 'python.exe' }
                $candidates += $exe
            }
        }
    }
    foreach ($exe in ($candidates | Select-Object -Unique)) { if (Test-Python $exe) { return $exe } }
}
function Assert-Publisher([string]$installer) {
    $signature = Get-AuthenticodeSignature -LiteralPath $installer
    if ($signature.Status -ne 'Valid' -or $signature.SignerCertificate.Subject -notmatch '(^|,\s*)O="?Python Software Foundation"?(,|$)') {
        throw 'Python publisher verification failed. Nothing was installed. Check your connection and Windows date, then retry.'
    }
}
function Start-TypeFlow([string]$Directory = $PSScriptRoot) {
    $companion = Join-Path $Directory 'typeflow_companion.py'
    if (-not (Test-Path -LiteralPath $companion)) { throw 'Extract ALL files from the ZIP first, then open Start-TypeFlow.cmd from the extracted folder.' }
    $target = Join-Path $env:LOCALAPPDATA 'Programs\TypeFlow\Python314'
    $preferred = Join-Path $target 'python.exe'
    Write-Host 'TypeFlow: checking Python and window components...'
    $python = Find-Python $preferred
    if (-not $python) {
        $architecture = $env:PROCESSOR_ARCHITEW6432
        if (-not $architecture) { $architecture = $env:PROCESSOR_ARCHITECTURE }
        $suffix = switch ($architecture.ToUpperInvariant()) {
            'ARM64' { '-arm64' }
            'AMD64' { '-amd64' }
            'X86' { '' }
            default { throw 'Unsupported processor. TypeFlow needs Windows 10 or 11.' }
        }
        $cache = Join-Path $env:LOCALAPPDATA 'TypeFlow\Setup'
        New-Item -ItemType Directory -Force -Path $cache | Out-Null
        $installer = Join-Path $cache "python-$PythonVersion$suffix.exe"
        $log = Join-Path $cache 'python-install.log'
        try {
            Write-Host 'Downloading Python from python.org. Keep this window open...'
            [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
            Invoke-WebRequest -UseBasicParsing -Uri "https://www.python.org/ftp/python/$PythonVersion/python-$PythonVersion$suffix.exe" -OutFile $installer -TimeoutSec 300
            Write-Host 'Verifying the Python Software Foundation publisher...'
            $hashes = @{
                '-amd64' = 'a247a0b612244a803f507b39fb7121e3602e4160d59c3b99d98e735289c53394'
                '' = '55616c5b63219f66aeb79d3053dc8a8d770c29da8a15ab6ff8cb36412fda654b'
                '-arm64' = '4508e6a54c69566b8faec461d84d85eebee65c39a15eb910bc2ad873d09b022b'
            }
            if ((Get-FileHash -LiteralPath $installer -Algorithm SHA256).Hash -ne $hashes[$suffix]) { throw 'Python download verification failed. Please retry.' }
            Assert-Publisher $installer
            Write-Host 'Installing Python and Tkinter for your account. Please wait...'
            $arguments = @('/passive','/norestart','InstallAllUsers=0','Include_launcher=0','Include_tcltk=1','Include_pip=0','Include_test=0','Include_doc=0','Shortcuts=0','AssociateFiles=0','PrependPath=0',('TargetDir="' + $target + '"'),'/log',('"' + $log + '"'))
            $process = Start-Process -FilePath $installer -ArgumentList $arguments -Wait -PassThru -WindowStyle Hidden
            if ($process.ExitCode -notin @(0,3010)) { throw "Python setup failed (code $($process.ExitCode)). Details: $log. Retry, or install Python with Tcl/Tk from https://www.python.org/downloads/windows/ ." }
            $python = Find-Python $preferred
            if (-not $python) { throw "Python window components are unavailable. Restart Windows and retry. Details: $log" }
        } finally {
            if (Test-Path -LiteralPath $installer) { Remove-Item -LiteralPath $installer -Force }
        }
    }
    Write-Host 'Opening TypeFlow. Keep the companion window open while typing.'
    & $python -I $companion
    if ($LASTEXITCODE -ne 0) { throw 'The companion closed with an error. Close any other TypeFlow companion and retry.' }
}
# Dot sourcing is for tests: no downloads or installations.
if ($MyInvocation.InvocationName -ne '.') {
    try { Start-TypeFlow; exit 0 } catch {
        Write-Host ('TypeFlow: ' + $_.Exception.Message) -ForegroundColor Red
        Write-Host 'For download problems, check your connection and run Start-TypeFlow.cmd again.'
        exit 1
    }
}
