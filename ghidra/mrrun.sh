#!/bin/bash
# headless Ghidra on the MotorRaid2 project. usage: mrrun.sh <log> [headless args after project name]
# Set GHIDRA_HEADLESS (path to analyzeHeadless) and MR_GHIDRA (folder holding MotorRaid2.gpr); scripts in ./scripts.
log="$1"; shift
"$GHIDRA_HEADLESS" "$MR_GHIDRA" MotorRaid2 "$@" -scriptPath "$(dirname "$0")/scripts" > "$log" 2>&1
tail -3 "$log"
