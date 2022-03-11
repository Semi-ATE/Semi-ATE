from ate_sammy.verbs.migrate import Migrate
from ate_sammy.verbs.generate import Generate
from ate_projectdatabase import __version__
import argparse
import os
import sys
import textwrap


def main() -> int:
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description=textwrap.dedent('''\
                                                 sammy - the Semi-ATE.org codegenerator

                                                 all commands must be executed in a testproject root directory, except for 'generate new <project>'

                                                 To generate files:
                                                 > sammy generate all                 --> generates everything
                                                 > sammy generate sequence            --> generates testprograms
                                                 > sammy generate test                --> generates tests
                                                 > sammy generate test_target         --> generates test_targets
                                                 > sammy generate new <project name>  --> generates new project
                                                 To Migrate to the newest release:
                                                 > sammy migrate
                                                 '''))
    parser.add_argument("verb", type=str)
    parser.add_argument("noun", type=str, nargs="?", default="")
    parser.add_argument("params", nargs="*")

    try:
        allargs = parser.parse_args()
    except BaseException:
        parser.print_help()
        return 0

    cwd = os.getcwd()
    run(allargs, cwd)


def run(args: argparse.Namespace, project_dir: str) -> int:
    print("-- sammy --")
    print(f"    for projectversion {__version__}")
    print(f"    running in {project_dir}")

    # To make things run either as standalone exe or script,
    # we need to detect the basedirectory correctly, either,
    # where the standalone exe is or where __file__ is located
    template_base_path = os.path.dirname(__file__)
    if "python" not in sys.executable:
        template_base_path = os.path.dirname(sys.executable)

    template_base_path = os.path.join(template_base_path, "templates")

    supported_verbs = {
        "migrate": Migrate(),
        "generate": Generate(template_base_path),
    }

    if args.verb not in supported_verbs:
        print(f"    {args.verb} is an unknown verb.")
        return -1

    # ensure CWD is a project directory, nouns that don't
    # need a projectdirectory such as "new" will have to
    # execute before this check.
    if args.verb == 'migrate':
        if not os.path.exists(os.path.join(project_dir, ".lastsettings")):
            print("    This is not a semi-ate.org project.")
            print("    In order to migrate some project you have to execute this command inside some project folder.")
            return -1


    supported_verbs[args.verb].run(project_dir, args)

    return 0

if __name__ == '__main__':
    sys.exit(main())
