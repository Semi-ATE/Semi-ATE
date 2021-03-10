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
$stdf_location = "Semi-ATE-STDF"
$spyder_location = ".."
$spyder2_location = "../spyder"
$smoke_test_location = "tests/ATE/spyder/widgets/CI/qt/smoketest"
$apps_location = "ATE/Tester/TES/apps"
$package_is_uptodate = $False
$confirm = "y"

function Install-Dependencies {
    Write-Host "install requirements"
    Invoke-Expression "conda install --file requirements/run.txt -y"

    Write-Host "install test requirements"
    Invoke-Expression "conda install --file requirements/test.txt -y"
    
    Write-Host "install ATE package"
    Rename-Item -Path ".\MANIFEST.in" -NewName ".\MANIFEST.in.abc"
    Invoke-Expression "python setup.py develop"
    Rename-Item -Path ".\MANIFEST.in.abc" -NewName ".\MANIFEST.in"

    Set-Location -Path $root_location
    Write-Host "install TDKMicronas plugin package"
    Invoke-Expression "cd $plugin_location"
    Invoke-Expression "python setup.py develop"

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

        $package_is_uptodate = $True

        Install-Dependencies
    } else
    {
        exit
    }

    Set-Location -Path $root_location
}

$confirmation = Read-Host "do you want to build web-UI disctribution [y/n]"
if (($confirmation -eq $confirm) -or (!$confirmation))
{
    Write-Host "install angular cli dependencies"
    Invoke-Expression "npm i -g @angular/cli"

    Write-Host "install web-UI dependencies"
    Invoke-Expression "cd $webui_location"
    Invoke-Expression "npm install"
    Invoke-Expression "npm audit fix"

    Write-Host "generate web-UI distribution"
    Invoke-Expression "ng build"
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

    Write-Host "testprogram name must be adapted in ATE/Tester/TES/apps/le123456000.xml, therefore replace the 'PROGRAM_DIR#' field inside
                'STATION' section with the following:"
    $testprogram_location = "smoketest/smoke_test/src/HW0/PR/smoke_test_HW0_PR_Die1_Production_PR_1.py"
    Write-Host "(make sure you copy the absolut path!!) => test program path: " $testprogram_location

    Write-Host "now you should be able to start control, master and test-application"
}

Set-Location -Path $root_location
$confirmation = Read-Host "do you want to get spyder sources [y/n]"
if (($confirmation -eq $confirm) -or (!$confirmation))
{
    $spyder = $(Get-Location)
    Invoke-Expression "git clone https://github.com/spyder-ide/spyder.git"
    Set-Location -Path $spyder2_location
    Invoke-Expression "git checkout 06562dd073d3473c24e658849a09ab6266af3426"
    Write-Host "to run spyder-IDE use the following command, first change directroy to: " $spyder"/spyder"
    Write-Host "python bootstrap.py"
}

$confirmation = Read-Host "do you want to install spyder dependencies [y/n]"
if (($confirmation -eq $confirm) -or (!$confirmation))
{
    Set-Location -Path $root_location
    try
    {
        Set-Location -Path $spyder2_location
        Invoke-Expression "conda install --file requirements/conda.txt -y"
        Set-Location -Path $root_location
        Install-Dependencies
    } catch
    {
        Set-Location -Path $spyder_location
        Write-Host "spyder folder could not be found under: " $(Get-Location)
        exit
    }
}

Set-Location -Path $root_location
Write-Host "build test program"
Invoke-Expression "pytest $smoke_test_location"
Invoke-Expression "Copy-Item  -Path $smoke_test_location -Destination ./ -Recurse -force"

Set-Location -Path $root_location
if ($package_is_uptodate -ne $True)
{
    $confirmation = Read-Host "do you want to install packages again [y/n]"
    if (($confirmation -eq $confirm) -or (!$confirmation))
    {
        Install-Dependencies
    }
}

Set-Location -Path $root_location


Write-Host ""
Write-Host "                        !!!!!!!!!!!!!!!!!!!!!!! ATTENTION !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
Write-Host "                        please make sure you read the instruction from README.md file"
