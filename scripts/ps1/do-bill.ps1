$Root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
python "$Root/scripts/python/devctl_core.py" do-bill $args
