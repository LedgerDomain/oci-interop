#!/bin/bash

# Check for arguments
if [ $# -ne 1 ]; then
    echo "Usage: $0 <test-specifier>"
    echo
    echo "    Run the OCI Interoperability tests, storing the results in a timestamped subdirectory"
    echo
    echo "<test-specifier> can be used to filter the tests to be run to the specified pattern."
    echo
    echo "    Example - run all tests:"
    echo "        $0 oci_interop"
    echo
    echo "    Example - run all tests under the VRS group:"
    echo "        $0 oci_interop.VRS"
    echo
    echo "    Example - run only the oci_interop.VRS.test_vrs_spherity_vp_generate_and_xatp_vp_verify test:"
    echo "        $0 oci_interop.VRS.test_vrs_spherity_vp_generate_and_xatp_vp_verify"
    exit 1
fi

TEST_SPECIFIER=$1

# See https://gist.github.com/mohanpedala/1e2ff5661761d3abd0385e8223e16425#set--e--u--x--o-pipefail
# Exit on error.
set -e
# Exit on undefined variables.
set -u
# Exit if any command in a piped command fails.
set -o pipefail
# Print commands and their arguments as they are executed.
set -x

# First, run the static type checker.
mypy oci_interop

# Create a subdirectory under 'results' directory with the current timestamp (UTC) for this run.
# A directory is created because in the future it may be useful to save other artifacts for
# each run, such as generated VPs, etc.
TIMESTAMP=$(date --iso-8601=seconds --utc)
RESULTS_DIR="results/$TIMESTAMP"
mkdir -p "$RESULTS_DIR"
LOG_FILE="$RESULTS_DIR/$TEST_SPECIFIER.log"

# Run the tests, saving the results to the timestamped results subdirectory.
python3 -m unittest $TEST_SPECIFIER -v 2>&1 | tee "$LOG_FILE"
