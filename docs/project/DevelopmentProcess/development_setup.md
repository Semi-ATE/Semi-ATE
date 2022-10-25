## Setup a conda environment
```
(base)~$ mamba create -n Semi-ATE python=3.9
(base)~$ conda activate Semi-ATE
(Semi-ATE)~$ mamba install spyder=5.3
(Semi-ATE)~$ mkdir ~/repos/Semi-ATE
(Semi-ATE)~$ cd ~/repos/Semi-ATE
(Semi-ATE)~/repos/Semi-ATE$ git clone https://github.com/Semi-ATE/Semi-ATE.git
(Semi-ATE)~/repos/Semi-ATE$ git clone https://github.com/Semi-ATE/TCC_actuators.git
(Semi-ATE)~/repos/Semi-ATE$ git clone https://github.com/Semi-ATE/SCT8-ML.git
(Semi-ATE)~/repos/Semi-ATE$ git clone https://github.com/Semi-ATE/STIL-Tools.git
(Semi-ATE)~/repos/Semi-ATE$ cd Semi-ATE
(Semi-ATE)~/repos/Semi-ATE/Semi-ATE$ python scripts/package_tool.py --change-env cicd
...
(Semi-ATE)~/repos/Semi-ATE/Semi-ATE$cd ../TCC_actuators
(Semi-ATE)~/repos/Semi-ATE/TCC_actuators$ pip install -e .
...
(Semi-ATE)~/repos/Semi-ATE/TCC_actuators$ cd ../SCT8-ML
(Semi-ATE)~/repos/Semi-ATE/SCT8-ML$ pip install -e .
...
(Semi-ATE)~/repos/Semi-ATE/SCT8-ML$ cd STIL-Tools
(Semi-ATE)~/repos/Semi-ATE/STIL-Tools$ pip install -e .
...
(Semi-ATE)~/repos/Semi-ATE/STIL-Tools$ mamba install h5py 

---> goto `https://github.com/Semi-ATE/STIL-Tools/releases` and download the latest `.deb` file (sct8-stil-loader_VERSION_arm64.deb)

(Semi-ATE)~/repos/Semi-ATE/STIL-Tools$ sudo dpkg -i sct8-stil-loader_VERSION_arm64.deb

```
