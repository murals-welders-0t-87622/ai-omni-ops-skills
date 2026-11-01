#!/usr/bin/env python3
"""Check resolved Compose ASR settings without printing the resolved config."""
import json
import subprocess
import sys


def check(config):
    try:
        server = config['services']['server']
        args = server['build']['args']
        env = server['environment']
        enabled = str(args['INSTALL_LOCAL_ASR'])
        build_model = args['LOCAL_ASR_PRELOAD_WHISPER_MODEL']
        runtime_model = env['WHISPER_MODEL_NAME']
        if not isinstance(build_model, str) or not isinstance(runtime_model, str):
            return {'state': 'configuration_unavailable'}
        build_model = build_model.strip()
        runtime_model = runtime_model.strip()
    except (KeyError, TypeError):
        return {'state': 'configuration_unavailable'}
    if enabled != '1':
        return {'state': 'asr_not_built'}
    if not build_model or not runtime_model:
        return {'state': 'configuration_unavailable'}
    if build_model != runtime_model:
        return {'state': 'model_mismatch', 'build_model': build_model, 'runtime_model': runtime_model}
    return {'state': 'models_match', 'model': build_model}


def main(argv):
    if not argv or argv[0] != '--' or len(argv) == 1:
        print('Usage: check-compose-asr.py -- <docker compose project, env-file and -f arguments>', file=sys.stderr)
        return 2
    try:
        proc = subprocess.run(['docker', 'compose', *argv[1:], 'config', '--format', 'json'],
                              capture_output=True, text=True, encoding='utf-8', timeout=60, check=False)
        if proc.returncode:
            raise ValueError('compose config failed')
        result = check(json.loads(proc.stdout))
    except (OSError, UnicodeError, ValueError, subprocess.TimeoutExpired):
        result = {'state': 'configuration_unavailable'}
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result['state'] == 'models_match' else 2


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
