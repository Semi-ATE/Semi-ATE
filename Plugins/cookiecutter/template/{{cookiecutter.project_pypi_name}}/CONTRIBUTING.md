# Contributing

Contributions are welcome, and they are greatly appreciated! Every little bit
helps, and credit will always be given.

You can contribute in many ways:

## Types of Contributions

### Report Bugs

Report bugs on the [issue tracker](https://github.com/{{ cookiecutter.github_org }}/{{ cookiecutter.project_pypi_name }}/issues).

If you are reporting a bug, please include:

* Your operating system name and version.
* Any details about your local setup that might be helpful in troubleshooting.
* Detailed steps to reproduce the bug.

### Fix Bugs

Look through the GitHub issues for bugs. Anything tagged with "bug" and "help
wanted" is open to whoever wants to implement it.

### Implement Features

Look through the GitHub issues for features. Anything tagged with "enhancement"
and "help wanted" is open to whoever wants to implement it.

### Write Documentation

{{ cookiecutter.project_name }} could always use more documentation, whether as part of the
official {{ cookiecutter.project_name }} docs, in docstrings, or even on the web in blog posts,
articles, and such.

### Submit Feedback

The best way to send feedback is to file an issue on the [issue tracker](https://github.com/{{ cookiecutter.github_org }}/{{ cookiecutter.project_pypi_name }}/issues).

If you are proposing a feature:

* Explain in detail how it would work.
* Keep the scope as narrow as possible, to make it easier to implement.
* Remember that this is a volunteer-driven project, and that contributions
  are welcome :)

## Get Started

Ready to contribute? Here's how to set up `{{ cookiecutter.project_name }}` for local development.

1. Fork the `{{ cookiecutter.project_pypi_name }}` repo on GitHub.
1. Clone your fork locally:

```bash
git clone git@github.com:your_name_here/{{ cookiecutter.project_pypi_name }}.git
```

1. Install your local copy into a conda environment.

```bash
conda create -n {{ cookiecutter.project_pypi_name }} python
cd {{ cookiecutter.project_pypi_name }}/
python setup.py develop
```

1. Create a branch for local development:

```bash
git checkout -b name-of-your-bugfix-or-feature
```

Now you can make your changes locally.

1. When you're done making changes, check that your changes pass flake8 and the
   tests, including testing other Python versions:

```bash
flake8 {{ cookiecutter.project_package_name }}
pytest {{ cookiecutter.project_package_name }}
```

1. Commit your changes and push your branch to GitHub:

```bash
git add .
git commit -m "Your detailed description of your changes."
git push origin name-of-your-bugfix-or-feature
```

1. Submit a pull request through the GitHub website.

## Pull Request Guidelines

Before you submit a pull request, check that it meets these guidelines:

1. The pull request should include tests.
1. If the pull request adds functionality, the docs should be updated. Put
   your new functionality into a function with a docstring, and add the
   feature to the list in README.rst.
1. The pull request should work for Python 3.6, 3.7 and 3.8. Check
   https://github.com/{{ cookiecutter.github_org }}/{{ cookiecutter.project_pypi_name }}/pull_requests
   and make sure that the tests pass for all supported Python versions.

## Tips

To run a subset of tests:

```bash
pytest tests/spyder/test_plugin.py
```

## Deploying

A reminder for the maintainers on how to deploy.
Make sure all your changes are committed (including an entry in HISTORY.rst).
Then run:

```bash
bump2version patch  # possible: major / minor / patch
git push
git push --tags
```

Github will then deploy to PyPI if tests pass.
