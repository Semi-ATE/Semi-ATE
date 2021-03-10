from ATE.sammy.verbs.migrate import Migrate
from ATE.sammy.verbs.generate import Generate
from ATE.projectdatabase import __version__
import argparse
import os
import sys
import textwrap

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
    exit(0)

print("-- sammy --")
print(f"    for projectversion {__version__}")
cwd = os.getcwd()
print(f"    running in {cwd}")

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

if allargs.verb not in supported_verbs:
    print(f"    {allargs.verb} is an unknown verb.")
    sys.exit(-1)

# ensure CWD is a project directory, nouns that don't
# need a projectdirectory such as "new" will have to
# execute before this check.
if not os.path.exists(os.path.join(cwd, ".lastsettings")):
    print("    This is not a semi-ate.org project")

supported_verbs[allargs.verb].run(cwd, allargs)
