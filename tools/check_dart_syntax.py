#!/usr/bin/env python3
"""Optional static syntax check; never label this as a Flutter analyzer/build."""
import json,sys
from pathlib import Path
try:
    from tree_sitter import Language,Parser
    import tree_sitter_dart
except ImportError:
    raise SystemExit('Install tree-sitter and tree-sitter-dart, or use the actual flutter analyze command.')
root=Path(__file__).resolve().parents[1]
parser=Parser(Language(tree_sitter_dart.language()));result=[]
for path in sorted((root/'mobile_flutter').rglob('*.dart')):
    tree=parser.parse(path.read_bytes());errors=[]
    def visit(node):
        if node.type=='ERROR' or node.is_missing:
            errors.append({'type':node.type,'line':node.start_point.row+1,'column':node.start_point.column+1})
        for child in node.children:visit(child)
    visit(tree.root_node)
    result.append({'file':str(path.relative_to(root)),'status':'failed' if errors else 'passed','errors':errors})
    print('FAIL' if errors else 'PASS',path.name,errors or '')
target=root/'tests/results/dart-syntax.json';target.parent.mkdir(parents=True,exist_ok=True)
target.write_text(json.dumps({'scope':'tree-sitter syntax only; NOT dart analyze or flutter test','files':result},indent=2)+'\n')
sys.exit(any(item['errors'] for item in result))
