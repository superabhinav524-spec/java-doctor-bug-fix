$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
python -m javadoctor.cli.main $args
