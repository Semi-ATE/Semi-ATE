param (
    [Parameter(Mandatory=$true)][String]$env='ATE_TEMP'
)

$commands = "npm", "conda"
foreach ($command in $commands)
{
    if ((Get-Command $command -ErrorAction SilentlyContinue) -eq $null)
    {
        Write-Host "Unable to find " $command " in path"
        exit
    }
}

$root_location = $(Get-Location)
$webui_location = "ATE/Tester/TES/ui/angular/mini-sct-gui"
$plugin_location = "Plugins/TDKMicronas"
$spyder_location = ".."
$smoke_test_location = "tests/ATE/spyder/widgets/CI/qt/smoketest"
$apps_location = "ATE/Tester/TES/apps"

Write-Host "install angular cli dependencies"
Invoke-Expression "npm i -g @angular/cli"

Write-Host "install web-UI dependencies"
Invoke-Expression "cd $webui_location"
Invoke-Expression "npm install"

Write-Host "generate web-UI distribution"
Invoke-Expression "ng build"
Set-Location -Path $root_location

try
{
    Invoke-Expression "conda activate $env"
    Write-Host "conda environment: " $env " is activated"
}
catch
{
    Write-Host "new conda environment: " $env " will be generated"
    $confirmation = Read-Host "are you sure you want proceed and create the new environment [y/n]"

    if ($confirmation -eq 'y')
    {
        Write-Host "create new conda environment: " $env
        Invoke-Expression "conda create -n $env python=3.7 -y"
        Invoke-Expression "conda config --append channels conda-forge"
        Invoke-Expression "conda activate $env"

        Write-Host "install requirements"
        Invoke-Expression "conda install --file requirements/run.txt -y"

        Write-Host "install test requirements"
        Invoke-Expression "conda install --file requirements/test.txt -y"

        Write-Host "install ATE package"
        Invoke-Expression "python setup.py develop"

        Write-Host "install TDKMicronas plugin package"
        Invoke-Expression "cd $plugin_location"
        Invoke-Expression "python setup.py develop"

        Set-Location -Path $root_location

        Write-Host "build test program"
        Invoke-Expression "pytest $smoke_test_location"

        Invoke-Expression "conda install spyder -y"
    }

    if ((Get-Command "git" -ErrorAction SilentlyContinue) -eq $null)
    {
        Write-Host "Unable to find git in path, spyder sources cannot be imported"
    } else
    {
        $confirmation = Read-Host "do you want to get spyder sources [y/n]"
        if ($confirmation -eq 'y')
        {
            Set-Location -Path $spyder_location
            $spyder = $(Get-Location)
            Invoke-Expression "git clone https://github.com/spyder-ide/spyder.git"
            Invoke-Expression "git checkout 9b2aa14"
            Write-Host "to run spyder-IDE use the following command, first change directroy to: " $spyder
            Write-Host "python bootstrap.py"
        }
    }
    Set-Location -Path $root_location
}


Write-Host "new configuration file for master and control Apps will be generated"
$confirmation = Read-Host "are you sure you want proceed and create new configuration files [y/n]"
if (-Not ($confirmation -eq 'y'))
{
    exit
}

Set-Location -Path $apps_location

Write-Host "generate control_app configuration file"
Invoke-Expression "python auto_script.py control SCT-81-1F -conf"
Write-Host "done"

Write-Host "generate master_app configuration file"
Invoke-Expression "python auto_script.py master SCT-81-1F -conf"
Write-Host "done"

Invoke-Expression "cp le306426001_template.xml le306426001.xml"

Write-Host "testprogram name must be adapted in ATE/Tester/TES/apps/le306426000.xml, therefore replace the 'PROGRAM_DIR#' field inside
            'STATION' section with the following:"
$testprogram_location = "tests/ATE/spyder/widgets/CI/qt/smoketest/smoke_test/src/HW0/PR/smoke_test_HW0_PR_Die1_Production_PR_1.py"
Write-Host "(make sure you copy the absolut path!!) => test program path: " $testprogram_location

Write-Host "now you should be able to start control, master and test-application"
