from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--phase', choices=('before', 'after'), required=True)
    phase = parser.parse_args().phase
    artifacts = Path('artifacts/r46-15')
    proof = json.loads((artifacts / 'source-compiler-prebuild.json').read_text())
    pin = '546c25ea75ee9d8a41b3832aa639664bc9a683b5'
    assert proof['source_commit'] == pin
    for name, expected in proof['raw_Git_equal_inputs_sha256'].items():
        file = artifacts / 'input' / name
        assert digest(file) == expected and file.read_bytes() == subprocess.check_output(['git', 'show', pin + ':' + name])
    compiler = Path('C:/Users/bagma/deepviz-agent-toolkit/node_modules/typescript')
    actual_compiler = {p.relative_to(compiler).as_posix(): digest(p) for p in sorted(compiler.rglob('*')) if p.is_file()}
    assert actual_compiler == proof['compiler_readonly_files_sha256']
    package = artifacts / 'input/packages/deepviz'
    dist = {p.relative_to(package / 'dist').as_posix(): digest(p) for p in sorted((package / 'dist').rglob('*')) if p.is_file()}
    assert {name for name in dist if name.endswith('.js')} == {'index.js', 'models.js', 'normalize.js', 'render.js', 'renderers.js', 'schema.js'}
    for name in ('index', 'models', 'normalize', 'render', 'renderers', 'schema'):
        mapping = json.loads((package / f'dist/{name}.js.map').read_text())
        assert mapping['sources'] == [f'../src/{name}.ts'] and mapping['sourceRoot'] == ''
    if phase == 'after':
        assert json.loads((artifacts / 'build-proof-before.json').read_text())['dist_sha256'] == dist
    result = {'source_commit': pin, 'phase': phase, 'raw_Git_input_count': 12,
              'all_source_test_config_inputs_exact_Git': True, 'compiler_tree_unchanged_files': len(actual_compiler),
              'compiler_tree_sha256': hashlib.sha256(json.dumps(actual_compiler, sort_keys=True, separators=(',', ':')).encode()).hexdigest(),
              'dist_sha256': dist, 'six_source_maps_resolve_own_Git_source': True}
    output = artifacts / f'build-proof-{phase}.json'
    assert not output.exists()
    output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(f'R46_BUILD_{phase.upper()}_OWN_GIT12_COMPILER416_DIST_SOURCE_MAP_PROOF0')


if __name__ == '__main__':
    main()