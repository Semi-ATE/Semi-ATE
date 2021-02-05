from ATE.sammy.verbs.migrate import Migrate
from ATE.sammy.verbs.generate import Generate
from ATE.projectdatabase import __version__
import argparse
import os
import sys

parser = argparse.ArgumentParser(description="sammy - the Semi-ATE.org codegenerator")
parser.add_argument("verb", type=str)
parser.add_argument("noun", type=str, nargs="?", default="")
parser.add_argument("params", nargs="*")

allargs = parser.parse_args()
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
