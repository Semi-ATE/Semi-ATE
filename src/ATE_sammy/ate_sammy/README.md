# Sammy

Sammy is part of the Semi-ATE project. It provides some command line tool and also a library. Sammy's purpose is to generate python-code. This is done by the help of the jinja2 template engine. Further it is used for updating/changing Semi-ATE projects databases form the `semi-ate-project-database` package.

Sammy is a required by the `semi-ate-spyder` plugin of the Semi-ATE project.

## Using the CLI

The sammy cli is used for generating new test program projects or for the migration of some former projects

1. Generating New Projects

   ```Console
   > sammy generate new <project-name>
   ```

   The above command will generate some empty project called \<project-name\\>
2. Migrating some project

   ```Console
   > cd /path/to-existing/project-name/
   > sammy migrate
   ```
