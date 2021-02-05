$root_location = $(Get-Location)
$sammy_path = "$root_location\ATE\sammy"
$sammy_exe = "sammy.exe"

Set-Location -Path $root_location
Set-Location -Path $sammy_path

if (Test-Path -Path $sammy_exe)
{}
else
{
    Invoke-Expression "conda create --name sammybuild"
    Invoke-Expression "conda activate sammybuild"
    Invoke-Expression "conda install --file run.txt"
    Invoke-Expression "pyinstaller --onefile --console --clean --distpath .\ sammy.py"
    Invoke-Expression "conda deactivate"
}

Set-Location -Path $root_location
Set-Item -Path Env:Path -Value ($Env:Path + ";$sammy_path")