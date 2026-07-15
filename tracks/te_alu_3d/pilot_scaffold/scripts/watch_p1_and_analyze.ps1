# Continuous watcher: re-run P1 desk whenever edit .hic files grow/complete
$ErrorActionPreference = "Continue"
$data = "D:\DNK - 2\data\HUDEP2_GSE160422"
$py = "D:\DNK - 2\DNA_TE_3DGenome_Context\pilot_scaffold\scripts\run_p1_3primeHS1_desk.py"
$log = "D:\DNK - 2\DNA_TE_3DGenome_Context\09_outputs\prospective\p1_watcher_log.txt"
function SizeMB($name) {
  $p = Join-Path $data $name
  if (Test-Path $p) { [math]::Round((Get-Item $p).Length/1MB, 1) } else { 0 }
}
$lastRun = 0
for ($i=0; $i -lt 200; $i++) {
  $w = SizeMB "GSM4873113_WT-HUDEP2-HiC_allValidPairs.hic"
  $d = SizeMB "GSM4873114_B6-HUDEP2-HiC_allValidPairs.hic"
  $v = SizeMB "GSM4873115_A2-HUDEP2-HiC_allValidPairs.hic"
  $cw = SizeMB "GSM4873116_WT-HUDEP2-captureHiC_allValidPairs.hic"
  $cd = SizeMB "GSM4873117_B6-HUDEP2-captureHiC_allValidPairs.hic"
  $ci = SizeMB "GSM4873118_A2-HUDEP2-captureHiC_allValidPairs.hic"
  $msg = "t=$i WT=$w DEL=$d INV=$v CAP_WT=$cw CAP_DEL=$cd CAP_INV=$ci"
  Add-Content $log $msg
  Write-Host $msg
  $readyGW = ($w -gt 6500 -and $d -gt 6500)
  $readyCap = ($cw -gt 2000 -and $cd -gt 2000)
  $should = $false
  if ($readyGW -or $readyCap) {
    $sig = [int]($d + $v + $cd + $ci)
    if ($sig -ne $lastRun) { $should = $true; $lastRun = $sig }
  }
  if ($should) {
    Write-Host "RUNNING_P1_DESK"
    python $py | Tee-Object -FilePath $log -Append
  }
  if ($readyGW -and $v -gt 6500 -and $readyCap -and $ci -gt 2000) {
    Write-Host "ALL_FILES_READY"
    python $py | Tee-Object -FilePath $log -Append
    break
  }
  Start-Sleep -Seconds 90
}
Write-Host "WATCHER_EXIT"
