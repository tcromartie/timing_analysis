import json
import re
import argparse
import sys

assignment = re.compile(r"^(\s*)(\w+)\s*=\s*(.*)\n$")

def transform_notebook(nb, transformations, verbose=False):
    subs = 0
    for cell in nb["cells"]:
        if cell["cell_type"]!="code":
            continue
        for i, l in enumerate(cell["source"]):
            m = assignment.match(l)
            if not m:
                continue
            try:
                val = transformations[m.group(2)]
            except KeyError:
                continue
            new_line = f"{m.group(1)}{m.group(2)} = {val}\n"
            if verbose:
                print(f"replacing line {repr(l)} by {repr(new_line)}")
            cell["source"][i] = new_line
            subs += 1
    return subs

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="""Substitute variables on a Jupyter notebook.
    
    This script allows you to substitute values into variable assignments in a notebook.
    The idea is that it allows you to have a variable, say 'write_results' that controls
    the notebook's behaviour. Then in a template notebook there will be a line that says
    'write_results = False'; this script lets you replace this with 'write_results = True'.
    """)
    def parse(s):
        key, value = s.split(",")
        return key, value
    parser.add_argument("-s", "--set-variable", type=parse, action="append", 
                        help="The variable to replace and its value, separated by a comma. "
                        "May require quotes to protect it from your shell; the value is "
                        "python source code (so strings need quotes in addition to whatever "
                        "the shell requires. Can be specified multiple times to have multiple "
                        "substitutions.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Describe all substitutions.")
    parser.add_argument("infile", help="Input file to transform")
    parser.add_argument("outfile", help="Output file to write")
    args = parser.parse_args()
    
    if not args.set_variable:
        print("No substitutions requested, no action will be taken.", file=sys.stderr)
        parser.print_help(sys.stderr)
        sys.exit(1)
    transformations = {k: v for (k,v) in args.set_variable}
    with open(args.infile) as f:
        nb = json.load(f)
    if not transform_notebook(nb, transformations, verbose=args.verbose):
        print(f"No substitutions performed; requested were {transformations}", file=sys.stderr)
    with open(args.outfile, "w") as f:
        nb = json.dump(nb, f)
    
    