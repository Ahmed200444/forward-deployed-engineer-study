# Serves this folder at http://localhost:8765/ and opens it in your browser.
# Uses only PowerShell, which comes with Windows. Nothing is installed.
# Only this computer can reach it (localhost). Close this window to stop.
$ErrorActionPreference = 'Stop'
$root = [System.IO.Path]::GetFullPath($PSScriptRoot).TrimEnd('\', '/') + [System.IO.Path]::DirectorySeparatorChar
$port = 8765
$url = "http://localhost:$port/"

# Already running (another window)? Just open the browser.
try {
  $probe = [System.Net.WebRequest]::Create($url + 'py/pyodide-lock.json')
  $probe.Timeout = 1500
  $resp = $probe.GetResponse(); $resp.Close()
  Write-Host "FDE Study is already running. Opening $url"
  Start-Process $url
  exit 0
} catch { }

$types = @{
  '.html' = 'text/html; charset=utf-8'; '.js' = 'text/javascript; charset=utf-8'; '.mjs' = 'text/javascript; charset=utf-8'
  '.json' = 'application/json; charset=utf-8'; '.wasm' = 'application/wasm'; '.css' = 'text/css; charset=utf-8'
  '.txt' = 'text/plain; charset=utf-8'; '.png' = 'image/png'; '.svg' = 'image/svg+xml'; '.ico' = 'image/x-icon'
  '.zip' = 'application/zip'; '.whl' = 'application/zip'; '.tar' = 'application/x-tar'
}

$listener = New-Object System.Net.HttpListener
$listener.Prefixes.Add($url)
try { $listener.Start() } catch {
  Write-Host "Could not start on port $port. Another program may be using it." -ForegroundColor Red
  Write-Host $_.Exception.Message
  Read-Host 'Press Enter to close'
  exit 1
}
Write-Host ''
Write-Host "FDE Study is running at $url" -ForegroundColor Green
Write-Host 'Keep this window open while you study. Close it to stop.'
Write-Host ''
Start-Process $url

while ($listener.IsListening) {
  try { $ctx = $listener.GetContext() } catch { break }
  $res = $ctx.Response
  try {
    $rel = [System.Uri]::UnescapeDataString($ctx.Request.Url.AbsolutePath).TrimStart('/')
    if ($rel -eq '') { $rel = 'index.html' }
    $path = [System.IO.Path]::GetFullPath([System.IO.Path]::Combine($root, $rel))
    if (-not $path.StartsWith($root, [System.StringComparison]::OrdinalIgnoreCase) -or -not [System.IO.File]::Exists($path)) {
      $res.StatusCode = 404
      $msg = [System.Text.Encoding]::UTF8.GetBytes('Not found')
      $res.ContentType = 'text/plain; charset=utf-8'
      $res.OutputStream.Write($msg, 0, $msg.Length)
    } else {
      $ext = [System.IO.Path]::GetExtension($path).ToLowerInvariant()
      $res.ContentType = if ($types.ContainsKey($ext)) { $types[$ext] } else { 'application/octet-stream' }
      $res.Headers.Add('X-Content-Type-Options', 'nosniff')
      $res.Headers.Add('Cache-Control', 'no-cache')
      $fs = [System.IO.File]::OpenRead($path)
      try { $res.ContentLength64 = $fs.Length; $fs.CopyTo($res.OutputStream) } finally { $fs.Close() }
    }
  } catch {
    try { $res.StatusCode = 500 } catch { }
  } finally {
    try { $res.OutputStream.Close() } catch { }
  }
}
