# Using sammy
sammy is intended to be used as a standalone executable.

## Building sammy
sammy is build using pyinstaller. Pyinstaller will always attempt to capture the complete environment in which a given script
or application is running. This can result in huge binaries, if the venv contains too many packets (e.g. installing numpy will
add ~200 MiB to the executable size). A large executable will be very slow to load, which makes working with the IDE sluggish.

To avoid this problem always create a new venv before building sammy:

``` conda create --name sammybuild ```
``` conda activate sammybuild ```

Afterwards install *only* the packets needed for sammy into the environment
``` conda install --file requirements.txt ```

At last, build sammy (from the sammy root directory):
``` pyinstaller --onefile --console --clean --distpath .\ .\sammy.py ```

## Using sammy
The IDE uses sammy to generate code for all projects. For it to be able to find sammy, the executable must be on the path for the current user.
