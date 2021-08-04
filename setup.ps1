$commands = "npm", "conda", "git"
foreach ($command in $commands)
{
    if ((Get-Command $command -ErrorAction SilentlyContinue) -eq $null)
    {
        Write-Host "Unable to find " $command " in path"
        exit
    }
}


Write-Host "existing environments will be listed below:"
Invoke-Expression "conda env list"
$env = Read-Host -Prompt "If you have already defined a favorite conda environment (env), 
you can enter the environment's name now, otherwise enter a new one (default environment is 'Semi-ATE')"
if (!$env)
{
    $env = 'Semi-ATE'
}

$root_location = $(Get-Location)
$webui_location = "ATE/Tester/TES/ui/angular/mini-sct-gui"
$plugin_location = "Plugins/TDKMicronas"
$apps_location = "ATE/Tester/TES/apps"
$confirm = "y"

function Install-Dependencies {
    Write-Host "install spyder"
    Invoke-Expression "conda install -c conda-forge/label/beta spyder=5.0.0a5 -y"

    Write-Host "install Semi-ATE packages"
    Invoke-Expression "conda install --file requirements/run.txt -y"

    Write-Host "install ATE package"
    Rename-Item -Path ".\MANIFEST.in" -NewName ".\MANIFEST.in.abc"
    Invoke-Expression "python setup.py develop"
    Rename-Item -Path ".\MANIFEST.in.abc" -NewName ".\MANIFEST.in"

    Write-Host "install TDKMicronas plugin package"
    Invoke-Expression "cd $plugin_location"
    Invoke-Expression "python setup.py develop"
    Set-Location -Path $root_location

    Write-Host "install STDF-Package"
    Invoke-Expression "pip install Semi-ATE-STDF"
}


try
{
    Invoke-Expression "conda deactivate"
    Invoke-Expression "conda activate $env"
    Write-Host "conda environment: " $env " is activated"
}
catch
{
    Write-Host "new conda environment: " $env " will be generated"
    $confirmation = Read-Host "are you sure you want proceed and create the new environment [y/n]"

    if (($confirmation -eq $confirm) -or (!$confirmation))
    {
        Write-Host "create new conda environment: " $env
        Invoke-Expression "conda create -n $env python=3.8 -y"
        Invoke-Expression "conda config --append channels conda-forge"
        Invoke-Expression "conda deactivate $env"
        Invoke-Expression "conda activate $env"

        Install-Dependencies
    } else
    {
        exit
    }

    Set-Location -Path $root_location
}

Write-Host "new configuration file for master and control Apps will be generated"
$confirmation = Read-Host "are you sure you want proceed and create new configuration files [y/n]"
if (($confirmation -eq $confirm) -or (!$confirmation))
{
    Set-Location -Path $apps_location

    Write-Host "generate control_app configuration file"
    Invoke-Expression "python auto_script.py control SCT-82-1F -conf"
    Write-Host "done"

    Write-Host "generate master_app configuration file"
    Invoke-Expression "python auto_script.py master SCT-82-1F -conf"
    Write-Host "done"

    Invoke-Expression "cp le123456000_template.xml le123456000.xml"
    Set-Location -Path $root_location
}


Write-Host ""
Write-Host "                        !!!!!!!!!!!!!!!!!!!!!!! ATTENTION !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
Write-Host "                        please make sure you read the instruction from README.md file"
