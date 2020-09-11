# Release process

* Ensure you have the latest version from upstream and update your fork

  ```bash
  git pull upstream master
  git push origin master
  ```

* Clean the repo

  ```bash
  git clean -xfdi
  ```

* Update CHANGELOG.md (if any):

* Update version in `__init__.py`

* Commit changes

  ```bash
  git add .
  git commit -m "Set release version"
  ```

* Create distributions

  ```bash
  python setup.py sdist bdist_wheel
  ```

* Upload distributions

  ```bash
  twine upload dist/* -u <username> -p <password>
  ```

* Add release tag

  ```bash
  git tag -a vX.X.X -m 'Release version'
  ```

* Update `__init__.py`

* Commint changes

  ```bash
  git add .
  git commit -m "Restore dev version"
  ```

* Push changes

  ```bash
  git push upstream master
  git push origin master
  git push --tags
  ```

## To release a new version of on conda-forge:

* Update recipe on the conda forge feedstock: https://github.com/conda-forge/semi-ate-feedstock
