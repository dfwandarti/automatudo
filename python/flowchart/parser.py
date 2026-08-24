# python/flowchart/parser.py
from __future__ import annotations

import logging
import re
import sys
from collections import deque
from dataclasses import dataclass, field
from pathlib import Path

MERMAID_BLOCK_RE = re.compile(r"```mermaid\s*\n(?P<body>.*?)```", re.DOTALL)
DIRECTION_RE = re.compile(r"^flowchart\s+\w+$", re.IGNORECASE)
COMMENT_RE = re.compile(r"^%%")

NODE_TOKEN_RE = re.compile(r'^(?P<id>[A-Za-z0-9_]+)\s*(?:\[\s*"?(?P<label>[^"\]]*)"?\s*\])?$')
EDGE_WITH_LABEL_RE = re.compile(r"^(?P<src>.+?)--(?P<label>[^-]*?)-->\s*(?P<dst>.+)$")
EDGE_NO_LABEL_RE = re.compile(r"^(?P<src>.+?)-->\s*(?P<dst>.+)$")
BARE_NODE_RE = re.compile(r"^[A-Za-z0-9_]+(\s*\[.*\])?$")


class FlowchartParseError(Exception):
    """Raised when a flowchart file/line cannot be parsed."""


@dataclass
class Transition:
    label: str
    node: "Node"


@dataclass
class Node:
    id: str
    label: str = ""
    successors: list[Transition] = field(default_factory=list)
    predecessors: list[Transition] = field(default_factory=list)


@dataclass
class FlowchartTree:
    nodes: dict[str, Node] = field(default_factory=dict)

    @classmethod
    def from_file(cls, path: str | Path) -> "FlowchartTree":
        path = Path(path)
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as e:
            raise FlowchartParseError(f"Não foi possível ler o arquivo '{path}': {e}")
        return cls.from_text(text)

    @classmethod
    def from_text(cls, text: str) -> "FlowchartTree":
        match = MERMAID_BLOCK_RE.search(text)
        if match is None:
            raise FlowchartParseError("Nenhum bloco ```mermaid encontrado no arquivo")

        tree = cls()
        for line_number, raw_line in enumerate(match.group("body").splitlines(), start=1):
            line = raw_line.strip()
            if not line or COMMENT_RE.match(line) or DIRECTION_RE.match(line):
                continue
            tree._parse_line(line, line_number)
        return tree

    def _parse_line(self, line: str, line_number: int) -> None:
        edge_match = EDGE_WITH_LABEL_RE.match(line) or EDGE_NO_LABEL_RE.match(line)
        if edge_match is not None:
            src_node = self._resolve_node(edge_match.group("src"), line_number)
            dst_node = self._resolve_node(edge_match.group("dst"), line_number)
            label = edge_match.groupdict().get("label", "") or ""
            src_node.successors.append(Transition(label, dst_node))
            dst_node.predecessors.append(Transition(label, src_node))
            return

        if BARE_NODE_RE.match(line):
            self._resolve_node(line, line_number)
            return

        raise FlowchartParseError(f"Linha {line_number}: sintaxe não reconhecida: '{line}'")

    def _resolve_node(self, token: str, line_number: int) -> Node:
        token = token.strip()
        token_match = NODE_TOKEN_RE.match(token)
        if token_match is None:
            raise FlowchartParseError(f"Linha {line_number}: nó inválido: '{token}'")

        node_id = token_match.group("id")
        label = token_match.group("label")

        node = self.nodes.get(node_id)
        if node is None:
            node = Node(id=node_id, label=label if label is not None else node_id)
            self.nodes[node_id] = node
        elif label is not None and not node.label:
            node.label = label

        return node

    def find_by_label(self, label: str) -> Node | None:
        for node in self.nodes.values():
            if node.label == label:
                return node
        return None

    def root(self) -> Node:
        roots = [node for node in self.nodes.values() if not node.predecessors]
        if len(roots) != 1:
            raise FlowchartParseError(
                f"Esperava exatamente 1 nó raiz (sem predecessors), encontrado {len(roots)}"
            )
        return roots[0]

    def path(self, source: Node, target: Node) -> list[Transition]:
        if source is target:
            return []

        visited = {source.id}
        queue: deque[tuple[Node, list[Transition]]] = deque([(source, [])])
        while queue:
            node, transitions = queue.popleft()
            for transition in node.successors:
                if transition.node.id in visited:
                    continue
                new_transitions = transitions + [transition]
                if transition.node is target:
                    return new_transitions
                visited.add(transition.node.id)
                queue.append((transition.node, new_transitions))

        raise FlowchartParseError(f"Não há caminho de '{source.label}' até '{target.label}' no flowchart")


def _print_tree(tree: FlowchartTree) -> None:
    for node in tree.nodes.values():
        print(f"{node.id} [\"{node.label}\"]")
        for transition in node.successors:
            label = transition.label or "(sem rótulo)"
            print(f"  -- {label} --> {transition.node.id}")
        for transition in node.predecessors:
            label = transition.label or "(sem rótulo)"
            print(f"  <-- {label} -- {transition.node.id}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    flowchart_path = sys.argv[1] if len(sys.argv) > 1 else "LOGIN_FLOW.md"
    try:
        flowchart_tree = FlowchartTree.from_file(flowchart_path)
    except FlowchartParseError as e:
        logging.error("Abortado ao parsear '%s': %s", flowchart_path, e)
        sys.exit(1)

    _print_tree(flowchart_tree)
