param([string]$EngineRoot='', [switch]$Launch)
$ErrorActionPreference='Stop'
try {
 $root=Split-Path -Parent $PSScriptRoot
 $manifest=Join-Path $root 'MANIFEST_SHA256.csv'
 if(-not (Test-Path -LiteralPath $manifest)){throw '请先全部解压整个ZIP，不能从压缩包内直接启动。'}
 Write-Host '正在核对交付文件是否完整（会读取全部文件，不修改文件）...'
 $rows=Import-Csv -LiteralPath $manifest
 $bad=@();$count=0
 foreach($row in $rows){
  $file=Join-Path $root $row.relative_path
  if(-not(Test-Path -LiteralPath $file -PathType Leaf)){$bad+=$row.relative_path+' [缺失]';continue}
  if((Get-Item -LiteralPath $file).Length -ne [long]$row.bytes){$bad+=$row.relative_path+' [大小不同]';continue}
  $stream=[System.IO.File]::OpenRead($file)
  $hasher=[System.Security.Cryptography.SHA256]::Create()
  try {$hash=[BitConverter]::ToString($hasher.ComputeHash($stream)).Replace('-','')}finally{$stream.Dispose();$hasher.Dispose()}
  if($hash -ne $row.sha256){$bad+=$row.relative_path+' [内容不同]'}
  $count++
 }
 if($bad.Count){$bad|ForEach-Object{Write-Host $_ -ForegroundColor Red};throw '交付文件缺失或已被修改。请重新完整解压原包到一个新目录；不会覆盖现有工作。'}
 Write-Host ('文件校验通过：'+$count+' 项。') -ForegroundColor Green
 $requirements=Get-Content -Raw -Encoding UTF8 -LiteralPath (Join-Path $root 'Docs/EngineRequirements.json')|ConvertFrom-Json
 if(-not $EngineRoot){
  $candidates=@()
  foreach($key in @('HKLM:\SOFTWARE\EpicGames\Unreal Engine\5.8','HKLM:\SOFTWARE\WOW6432Node\EpicGames\Unreal Engine\5.8')){
   $value=Get-ItemProperty -LiteralPath $key -ErrorAction SilentlyContinue
   if($value.InstalledDirectory){$candidates+=$value.InstalledDirectory}
  }
  $launcher=Join-Path $env:ProgramData 'Epic/UnrealEngineLauncher/LauncherInstalled.dat'
  if(Test-Path -LiteralPath $launcher){
   $installed=Get-Content -Raw -LiteralPath $launcher|ConvertFrom-Json
   $candidates+=@($installed.InstallationList|Where-Object{$_.AppName -eq 'UE_5.8'}|ForEach-Object{$_.InstallLocation})
  }
  foreach($candidate in $candidates|Select-Object -Unique){
   if(Test-Path -LiteralPath (Join-Path $candidate 'Engine/Build/Build.version')){$EngineRoot=$candidate;break}
  }
 }
 if(-not $EngineRoot){$EngineRoot=Read-Host '请输入UE 5.8.2安装目录（例如 D:\Epic Games\UE_5.8）'}
 $EngineRoot=$EngineRoot.Trim('"')
 if(Test-Path -LiteralPath (Join-Path $EngineRoot 'Engine/Build/Build.version')){$engine=Join-Path $EngineRoot 'Engine'}else{$engine=$EngineRoot}
 $versionFile=Join-Path $engine 'Build/Build.version'
 if(-not(Test-Path -LiteralPath $versionFile)){throw '此目录不是有效的UE引擎目录。'}
 $v=Get-Content -Raw -LiteralPath $versionFile|ConvertFrom-Json
 if($v.MajorVersion -ne 5 -or $v.MinorVersion -ne 8 -or $v.PatchVersion -ne 2){throw ('当前引擎为 '+$v.MajorVersion+'.'+$v.MinorVersion+'.'+$v.PatchVersion+'。本包验收版本为UE 5.8.2，请使用相同版本，避免蓝图/组件无法识别。')}
 $engineMissing=@()
 foreach($item in $requirements.engine_files){if(-not(Test-Path -LiteralPath (Join-Path $engine $item.relative) -PathType Leaf)){$engineMissing+=$item.relative}}
 if($engineMissing.Count){$engineMissing|ForEach-Object{Write-Host $_ -ForegroundColor Red};throw '当前UE安装缺少上述内置模块或资源。请核对UE安装；本脚本不会安装或修改引擎。'}
 Write-Host '工程文件和引擎依赖检查通过。' -ForegroundColor Green
 if($Launch){
  $exe=Join-Path $engine 'Binaries/Win64/UnrealEditor.exe'
  $project=Join-Path $root 'DSH_Standalone.uproject'
  Start-Process -FilePath $exe -ArgumentList ('"'+$project+'"')
 }
 exit 0
}catch{Write-Host $_.Exception.Message -ForegroundColor Red;exit 1}
