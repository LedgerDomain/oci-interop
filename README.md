# oci-interop

Interoperability test automation for OCI Digital Wallet Providers

If you just want to run the tests, skip to the section "How To Run Tests".

## Proposed Structure

### Goal(s)

The initial goal of this repository is to have a single, shared point of control for specifying and running a well-defined, uniform, and comprehensive set of interoperability tests for Wallet Providers (which are currently Spherity and XATP).

It should be possible for any party that has access to at least one Wallet Provider's system to run these tests to validate the functioning of the various APIs specified in the [OCI spec](https://open-credentialing-initiative.github.io/Digital-Wallet-Conformance-Criteria/v3.0.0/).

### Intended Use

However, the intended use of this test suite is for each OCI Wallet Provider, having access to their own and each of the other Wallet Providers' API, to run all of the tests in all directions.  For example, in testing the VRS VP generate and VRS VP verify API endpoints, X VP generate then Y VP verify should be run for X in {Spherity, XATP} and for Y in {Spherity, XATP}.

Proposal: Let's create the test suite as a Python script that can be run by any party supplying appropriate API keys/etc via env vars (env vars so no API keys end up in this repository itself).

Included in this repository is a start on such a script.

### Visibility of Test Results

Suggestion: We schedule these tests to run periodically (say once per day by each Wallet Provider) and post the results in a shared medium (e.g. shared Slack channel, or potentially in this repository) for total visibility.

### Alignment on Usage of Trusted Issuer Lists

Alex has suggested the following, which I support because of its simplicity and usefulness.
-   Production systems use ONLY the production trusted issuer list (as far as I know, this ethereum contract hasn't been deployed yet, but is meant to be deployed on Mainnet).
-   Test systems use as their trusted issuer list the union of the following trusted issuer lists.  This makes it so that real credentials can be checked in test systems, but not the other way around.  These test systems are the ones that are accessible and usable by other parties in test/demo capacity.
    -   Production (presumably on Mainnet)
    -   STK-INT (on Goerli)
-   Development systems use as their trusted issuer list the union of the following trusted issuer lists.  This makes it so that real credentials and test credentials can be checked in development systems, but not the other way around.  These systems are the ones used in internal development/testing, and aren't meant for anyone but Wallet Providers.  This level is potentially useful when dealing with inter-Wallet-Provider development on amendments to the OCI spec, or other features that require interop testing.
    -   Production (presumably on Mainnet)
    -   STK-INT (on Goerli)
    -   WLT-INT (on Goerli)
-   Single-engineer systems (i.e. an engineer is working on a feature branch) use as their trusted issuer list the union of the following trusted issuer lists.  The purpose of this level is to allow an engineer (e.g. who is working on a new feature) to run their own test issuer to produce credentials for testing in their own workflows.  This includes the higher-level trusted issuer lists so that it's still possible to check credentials from the higher levels, but not the other way around.
    -   Production (presumably on Mainnet)
    -   STK-INT (on Goerli)
    -   WLT-INT (on Goerli)
    -   PUB-INT (on Goerli)

## Interoperability Testing

In order for an interoperability test to be run, the party that is running the tests (call this party the Test Runner) must have API access to each of the Wallet Providers' systems that are to be tested.  For example, the Test Runner would need API access to each of Spherity and XATP's systems, and would supply those to the test script via env var (as mentioned previously).

Note that the details of authentication and specific usage of API keys is currently different between Spherity and XATP, but this can be accounted for in the construction of the test scripts.

### Most Basic Happy-Path Interop Test

-   Most basic happy path interop test:
    -   For X in [Spherity, XATP]:
        -   For Y in [Spherity, XATP]:
            -   X VP generate, Y VP verify.

### Comprehensive VP Sad-Path Interop Test

There needs to be a way to generate purposefully-invalid VPs to cover all the error codes.

Suggestion:
-   We add an optional argument to the VRS VP generate endpoint, call it "testCaseErrorCode".
-   If "testCaseErrorCode" is not present, then a normal, valid VP should be generated.
-   If "testCaseErrorCode" is present, then
    -   If it's equal to one of those defined in
        https://open-credentialing-initiative.github.io/Digital-Wallet-Conformance-Criteria/v3.0.0/#api-specific-error-codes
        then a VP is generated such that it produces that error code.  Note that some error codes pertain to the VC, some pertain to the VP, and some pertain to the relationship between the VC and the VP.
    -   If it's an unknown error code, then an error is returned.

## Notes

For comments or questions, please post in the Discussions section of this Github repo.  For bug reports and other issues, please post in the Issues section of this Github repo.

## How To Run Tests

### Environment Variable Setup

Environment variables are used to define access to each Wallet Provider's API.  They can be placed in a `.env` file in the root of this github repo and they will be automatically loaded into the environment when the tests are run.  Note that `.env` is in the `.gitignore` file, as it contains API keys/secrets, and should never be committed to any repository!  Here is a template:

    SPHERITY_CLIENT_ID=...
    SPHERITY_CLIENT_SECRET=...
    SPHERITY_VRS_API_URL=...
    SPHERITY_VRS_HOLDER_DID=...

    XATP_API_KEY=...
    XATP_VRS_API_URL=...
    XATP_VRS_HOLDER_DID=...

The environment variables are as follows.
-   Spherity:  The script will try to read an access token from disk first.  If that succeeds, then it will be checked for expiration.  If expired, or if not present on disk, a new access token will be retrieved from Spherity (via `https://auth.caro.vc/oauth/token`), and written to disk.  The reason for all of this caching is because Spherity rate-limits new access tokens to 150 per 24 hours.  Access to Spherity's APIs are via the `Authorization: Bearer <access_token>` header in HTTP requests.  The relevant environment variables are:
    -   SPHERITY_CLIENT_ID - specifies the `client_id` field of the request.
    -   SPHERITY_CLIENT_SECRET - specifies the `client_secret` field of the request.
    -   SPHERITY_VRS_API_URL - the base URL under which the [VRS endpoints](https://open-credentialing-initiative.github.io/api-specifications/v2.0.0/) are found for the Spherity system.
    -   SPHERITY_VRS_HOLDER_DID - the value for the holderDID (and verifierDID) parameter of the VRS VP Generate (and Verify) endpoint(s) in the Spherity system.
-   XATP:  Uses an API Key, which is specified by the following environment variable:
    -   XATP_API_KEY - specifies the value for the `X-API-Key` header in HTTP requests to XATP APIs.
    -   XATP_VRS_API_URL - the base URL under which the [VRS endpoints](https://open-credentialing-initiative.github.io/api-specifications/v2.0.0/) are found for the XATP system.
    -   XATP_VRS_HOLDER_DID - the value for the holderDID (and verifierDID) parameter of the VRS VP Generate (and Verify) endpoint(s) in the XATP system.

Additionally, the LOG_LEVEL environment variable can be set, as is [standard in Python](https://docs.python.org/3/howto/logging.html), in order to get more information during the test runs.  If not set, it will default to `WARNING`.

### Commandline Execution

Ensure that you are using Python 3.6 or later.

Ensure that all the necessary Python packages are installed;

    pip install --upgrade PyJWT python-dotenv requests

Running the tests is easy, simply run

    ./run-tests.sh

There will be an indicator of each test running, as well as results for each test, saved into a UTC-timestamped subdirectory under the `results` directory.

If it's desired to run a subgroup of tests or even a single test, for example the VRS grouping of tests, run

    python -m unittest oci_interop.VRS -v

### Static Type Checking

Run

    mypy .

to run the `mypy` static type checker on the codebase.  This will catch a large class of bugs that can be detected statically, as if it were a compiled language.  This will be done automatically in the `run-tests.sh` script.
