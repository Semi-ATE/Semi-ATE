# -*- coding: utf-8 -*-
import os
import json
from pathlib import Path
from typing import Any, Dict, Iterable, Optional   # , Tuple
from graphviz import Digraph


class Flowchart():
    """
    Creates a graphical representation from a flow of Semi-Ate, with comments taken from the description of the individual tests.

    Various tags are available for formatting:
        “#Flow:”     Instead of the general description, the string after the tag is used.
                     If additional lines are used, they must be indented.
        "->"         The string is then displayed in a separate node, which is arranged horizontally to the previous box.
                     The Tag "#Flow:" must have been used previously.
        ":"          indicates a summary of tests. The 'test name' is the string between #flow and the :.
    """

    tags = ["#flow:", "#->"]

    def __init__(self, path, project, version, hardware="HW0", base="FT", target="DummyDevice", group="production", name="qdbflow"):
        kversion = version[1] + version[3]
        path = os.getcwd() if path is None else path+os.sep
        definitions = f"{path}/{project}{kversion}/definitions"
        sequence = f"sequence/sequence{project}{kversion}_{hardware}_{base}_{target}_{group}_{name}.json"

        with open(f"{definitions}/{sequence}", "r", encoding="utf-8") as f:
            data = json.load(f)

        names = [
            (item.get("definition") or {}).get("name")
            for item in data
            if (item.get("definition") or {}).get("name") is not None
        ]
        print(f'found:\n{names}')

        # now open the files and read the documentation
        folder = Path(definitions + "/test/")
        docs = self._collect_docstrings(names, folder, hardware, base)
        self.path = Path(definitions).parent.parent
        self.flowdict = self._docs2flow(docs)
        self.project = project
        self.kversion = kversion
        self.hardware = hardware
        self.base = base
        self.target = target
        self.group = group
        self.name = name

    def _extract_docstring_from_entry(self, entry: Dict[str, Any]) -> Optional[str]:
        """
        Extracts a docstring from an entry:
        - checks entry[“docstring”] and entry[‘definition’][“docstring”]
        - returns a string (list is concatenated with ‘\n’), or None if not present.
        """
        candidates = []
        # direkte docstring-Felder
        if "docstring" in entry:
            candidates.append(entry["docstring"])
        # docstring in definition
        if isinstance(entry.get("definition"), dict) and "docstring" in entry["definition"]:
            candidates.append(entry["definition"]["docstring"])

        for c in candidates:
            if isinstance(c, str):
                return c.strip()
            if isinstance(c, list):
                # join non-None items, konvertiere jedes Element zu str, entferne führende/trailing spaces
                # parts = [str(x).strip() for x in c if x is not None]
                # return "\n".join(parts).strip()
                return "\n".join(c).strip()
        return None

    def _find_hw_base_docstring(self, obj: Any, hardware: str = "HW0", base: str = "FT") -> Optional[str]:
        """
        Expects `obj` as a list of entries (dicts).
        Searches for the first entry with hardware==hardware and base==base
        (checks top-level and definition fields).
        """
        if not isinstance(obj, list):
            return None
        for entry in obj:
            if not isinstance(entry, dict):
                continue
            hw = entry.get("hardware") or (entry.get("definition") or {}).get("hardware")
            b = entry.get("base") or (entry.get("definition") or {}).get("base")
            if hw == hardware and b == base:
                return self._extract_docstring_from_entry(entry)
        return None

    def _collect_docstrings(self, names: Iterable[str], folder: Path = Path("."), hardware: str = "HW0", base: str = "FT") -> Dict[str, Optional[str]]:
        """
        Reads the file {name}.json in the folder `folder` for each name
        and returns a dict: name -> docstring (or None).
        """
        result: Dict[str, Optional[str]] = {'start': ""}
        for name in names:
            p = folder / f"test{name}.json"
            if not p.exists():
                result[name] = 'file not found'
                continue
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
            except Exception:
                result[name] = None
                continue
            doc = self._find_hw_base_docstring(data, hardware=hardware, base=base)
            result[name] = doc
        result['end'] = ''
        return result

    def _docs2flow(self, data):
        def createbranch(txt, id, color='white'):
            txt = list(txt.values())[0]
            flowdict["nodes"].append({"id": 'b'+str(id), "label": txt, "style": "filled", "fillcolor": color})
            flowdict["edges"].append({"from": str(id), "to": 'b'+str(id)})

        def createbox(id):
            flowdict["nodes"].append({"id": str(id), "label": flowlabel})
            if id+1 < length:
                flowdict["edges"].append({"from": str(id), "to": str(id+1)})
            if branchlabel:
                createbranch(branchlabel, id, 'yellow')
            return id+1

        flowdict = {"nodes": [], "edges": []}
        length = len(data.keys())
        id = 0
        summary = ''                                       # sets the heading of a summary of test
        samebox = False
        for key in data.keys():
            label = data[key].split('\n')
            if label == [""] and samebox:
                id = createbox(id)
                samebox = False
            if samebox:
                length -= 1
            else:
                flowlabel = f"{key}\n"
                branchlabel = ''
            fhash = []
            phash = 0
            ifnoflow = ""
            for line in label:
                if len(line) == 0:
                    continue
                if key in branchlabel and line[phash: phash+len("#->")].strip() == '':
                    branchlabel[key] += "\n" + line.strip()
                elif branchlabel and not samebox:
                    createbranch(branchlabel, id)
                for hash in self.tags:
                    phash = line.lower().find(hash)
                    if phash >= 0:
                        if hash == self.tags[0]:                                 # "#Flow:"
                            if summary in line and samebox:
                                flowlabel += f"{key} - {line.split(':')[-1]}\n"
                            elif not samebox:
                                flowlabel += line[phash + len(hash)+1:] + "\n"
                            else:
                                print("{hash} should not happen....")

                            if ":" in flowlabel.split("\n")[1]:
                                label_summary = flowlabel.split("\n")[1]
                                key_summary = label_summary[:label_summary.find(":")]
                                if key_summary not in summary:
                                    summary = key_summary
                                    flowlabel = f"{key_summary}:\n{key} - {label_summary[label_summary.find(':')+1:]}\n"
                                    samebox = True
                            fhash.append(0)
                            continue
                        elif hash == self.tags[1]:                                 # "#->"
                            if samebox and 0 not in fhash:
                                id = createbox(id)
                                length += 1
                                samebox = False
                                flowlabel = f"{key}\n{ifnoflow}\n"
                            branchlabel = {key: line[phash + len(hash)+1:]}
                            fhash.append(1)
                            continue
                ifnoflow += line + "\n"
            # flowlabel = f"{key}\n{data[key]}" if flowlabel == f"{key}\n" else flowlabel
            flowlabel = f"{key}\n{ifnoflow}" if flowlabel == f"{key}\n" else flowlabel
            if not samebox:
                id = createbox(id)
        return flowdict

    def create(self, output_file=None, format="png"):
        """Create a Flowdiagramm from a Dictionary."""
        output_file = output_file if output_file is not None else f"{self.project}{self.kversion}_{self.hardware}_{self.base}_{self.target}_{self.group}_{self.name}"
        dot = Digraph(comment="Flowchart", format=format)
        dot.attr(rankdir="TB", size="10")       # TB = Top to Bottom
        dot.attr(ranksep='0.4')
        dot.attr(nodesep='1.2')

        # Knoten hinzufügen
        for node in self.flowdict["nodes"]:
            node_id = node.get("id")
            label = node.get("label", node_id)
            color = node.get('fillcolor') if node.get('fillcolor') is not None else "white"
            if not node_id:
                raise ValueError("Each node requires an ‘id’ field.")
            if node_id[0] != 'b':
                dot.node(node_id, label, shape='box')
                last_label = label
            else:                                           # create horizontal plane
                with dot.subgraph() as s:
                    s.attr(rank='same')
                    s.node(node_id[1:], last_label)
                    s.node(node_id, label, style="filled", fillcolor=color)

        # Kanten hinzufügen
        for edge in self.flowdict["edges"]:
            src = edge.get("from")
            dst = edge.get("to")
            if not src or not dst:
                raise ValueError("Each Edge requires 'from' and 'to'.")
            dot.edge(src, dst)

        # Diagramm rendern
        output_path = dot.render(str(self.path) + os.sep + output_file, cleanup=True)
        print(f"create Flowchart: {output_path}")


def parse_args():
    import argparse

    parser = argparse.ArgumentParser(description="Script for creating a graphical representation from a flow of Semi-Ate, with comments taken from the description of the individual tests.")
    # Pflicht-Parameter
    parser.add_argument("--path", default=None, help=r'Pfad, z. B. "C:\\Users\\jung\\ATE\\packages"')
    parser.add_argument("--project", required=True, help="Projektname, z. B. CHIP")
    parser.add_argument("--version", required=True, help='Version, z. B. "0205"')

    # Optionale Parameter mit Defaults
    parser.add_argument("--hw", default="HW0", help="Hardware (default: HW0)")
    parser.add_argument("--base", default="FT", help="Base (default: FT)")
    parser.add_argument("--target", default="DummyDevice", help="Target (default: DummyDevice)")
    parser.add_argument("--group", default="production", help="Group (default: production)")
    parser.add_argument("--name", default="qdbflow", help="Name (default: qdbflow)")

    return parser.parse_args()


def main():
    args = parse_args()
    flow = Flowchart(args.path, args.project, args.version, args.hw, args.base, args.target, args.group, args.name)
    flow.create(format="png")
    flow.create(format="pdf")
