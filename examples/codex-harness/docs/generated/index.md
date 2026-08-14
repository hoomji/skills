# Generated documentation

Machine-produced documentation. Nothing in this directory is edited by hand: change the
producer, then regenerate. Every file here appears in the table below.

| Artifact | Describes | Producing command | Producer source | Last generated |
| --- | --- | --- | --- | --- |

This example has no generated documentation yet. The store exists so that the first
generated artifact has an index and a provenance contract to land in.

## Entry contract

Every generated file starts with a provenance header, using the comment syntax of its
format, containing both markers verbatim:

    <!-- Do not edit. Generated file. -->
    <!-- Producing command: `python scripts/check.py` -->

The producing command must be a real repository entrypoint, so a broken producer is
detectable rather than merely stale. Regeneration is part of the change that alters the
source, not a separate cleanup.
