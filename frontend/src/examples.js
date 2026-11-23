export const examples = [
  {
    name: 'session_tokens.py',
    label: 'Weak randomness demo',
    source: `import random
import string

ALPHABET = string.ascii_letters + string.digits


def make_session_token():
    return "".join(random.choices(ALPHABET, k=24))
`,
  },
  {
    name: 'config_reader.py',
    label: 'Configuration reader',
    source: `import json

DEFAULT_CONFIG = '{"timeout": 30, "retries": 3}'


def load_config(text: str) -> dict:
    config = json.loads(text)
    if not isinstance(config, dict):
        raise ValueError("Expected a JSON object")
    return config


if __name__ == "__main__":
    settings = load_config(DEFAULT_CONFIG)
    print(settings["timeout"])
`,
  },
  {
    name: 'temperature.py',
    label: 'Temperature converter',
    source: `def to_celsius(fahrenheit: float) -> float:
    return (fahrenheit - 32) * 5 / 9


readings = [32, 68, 86]
converted = [round(to_celsius(value), 1) for value in readings]
print(converted)
`,
  },
  {
    name: 'yaml_config.py',
    label: 'YAML loader demo',
    source: `import yaml as y

def load_config(raw):
    return y.load(
        raw,  # Standard configuration data
    )
`,
  },
  {
    name: 'fixed_command.py',
    label: 'Fixed shell command demo',
    source: `import subprocess as sp

def show_message():
    return sp.run("/usr/bin/printf hello", shell=True, check=True)
`,
  },
  {
    name: 'file_and_connection_checks.py',
    label: 'File and connection checks demo',
    source: `import hashlib
import os
import requests
import tempfile

def review_settings(url, data, private_file):
    response = requests.get(url, verify=False)
    digest = hashlib.sha1(data).hexdigest()
    temporary_path = tempfile.mktemp()
    os.chmod(private_file, 0o666)
    return response.status_code, digest, temporary_path
`,
  },
  {
    name: 'syntax_error.py',
    label: 'Syntax error',
    source: `def greet(name)
    return f"Hello, {name}"
`,
  },
];
