# x12_837p_to_claims_json.py
"""
X12 837P Professional Healthcare Claims to JSON Converter

This module parses X12 837P files (professional healthcare claims) and converts
them to a simplified JSON format. The X12 837P format is a standard used in the
healthcare industry for submitting healthcare claim information from providers
to insurance payers.

Key X12 837P Concepts:
- 2300 Loop: Claim Information - contains header info for a single claim
- 2400 Loop: Service Line - contains details about individual services/procedures
- CLM Segment: Claim header with control number and total charge
- SV1 Segment: Professional service with procedure code and line charge
"""

from __future__ import annotations

from pathlib import Path
import json

# PyX12 library imports for parsing X12 EDI files
from pyx12.params import ParamsUnix
from pyx12.error_handler import errh_null
from pyx12.x12context import X12ContextReader


def extract_claims_from_837p(path: str | Path) -> list[dict]:
    """
    Extract claims from data in X12 837P file and convert to JSON-serializable format.

    This is a simplified extraction that focuses on core claim data:
    - Iterates over 2300 claim loops (each representing one claim)
    - Extracts basic claim header elements (claim ID, total charge)
    - Iterates over 2400 service line loops nested under each claim
    - Extracts procedure codes and charges for each service line.

    Agrs:
        path: File path to the X12 837P file (string or Path object)

    Returns:
        List of claims, each represented as a dictionary with claim header and service lines.
        Format:
        [
            {
                "claim_id": str,
                "total_charge": str,
                "service_lines": [
                    {
                        "procedure_code": str,
                        "line_charge": str,
                    },
                    ...
                ],
            },
            ...
        ]

    """
    path = Path(path)

    # ParamsUnix sets map_path and other defaults for you
    # [oai_citation:6‡PyX12](https://pyx12.sourceforge.net/doc/epydoc/pyx12.params-pysrc.html?utm_source=chatgpt.com)
    param = ParamsUnix()  # Configuration for X12 parsing (map files, delimiters, etc.)
    errh = errh_null()  # Null error handler (silently ignores errors)

    # List to accumulate all claims found in the file
    claims: list[dict] = []  #

    # Open and parse X12 837P file.
    with path.open("r") as f:
        # X12ContextReader provides hierarchial parsing of X12 segments and loops
        ctx = X12ContextReader(param, errh, f)
        # Iterate over 2300 loops (claims)
        # 2300 = Claim loop in 837P; README uses same pattern
        # [oai_citation:7‡GitHub](https://github.com/azoner/pyx12?utm_source=chatgpt.com)
        for claim_loop in ctx.iter_segments("2300"):
            # Claim header info (CLM segment inside 2300)
            claim_id = claim_loop.get_value("CLM01")  # Patient control number
            total_charge = claim_loop.get_value("CLM02")  # Total claim charge

            # FILTER: Skip entries that don't have claim data
            # iter_segments() returns both actual loops AND individual segments
            # Only process entries that have a CLM segment with data
            if claim_id is None and total_charge is None:
                continue

            # You can add more CLMxx / REF / HI / DTP etc. as needed:
            # service_location = claim_loop.get_value("CLM05-1")  # etc.

            service_lines = []
            # Iterate over 2400 loops (service lines) under this claim
            # [oai_citation:8‡GitHub](https://github.com/azoner/pyx12?utm_source=chatgpt.com)
            for sl_loop in claim_loop.select("2400"):
                # Extract service line details (SV1 segment inside 2400)
                procedure_code = sl_loop.get_value(
                    "SV101"
                )  # SV1-01: Procedure code (CPT/HCPCS) - composite field
                line_charge = sl_loop.get_value("SV102")  # SV1-02: Line item charge

                # Build service line dictionary
                service_lines.append(
                    {
                        "procedure_code": procedure_code,
                        "line_charge": line_charge,
                        # Additional  line-level data can be added:
                        # - SV103 Unit/basis for measurement code
                        # - SV104: Service unit count
                        # - Procedure modifiers (SV101-3, SV101-4, etc)
                        # - DTP segments for service dates
                        # - REF segments for line-level references
                    }
                )

            # Append the complete claim with all its service lines to the claims list.
            claims.append(
                {
                    "claim_id": claim_id,
                    "total_charge": total_charge,
                    "service_lines": service_lines,
                }
            )

    # Return all extracted claims.
    return claims


if __name__ == "__main__":
    import argparse

    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(description="X12 837P -> simple claims JSON")
    parser.add_argument("input", help="837P X12 file")
    parser.add_argument("-o", "--output", help="JSON output (default: stdout)")
    args = parser.parse_args()

    claims = extract_claims_from_837p(args.input)
    text = json.dumps(claims, indent=2)

    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
    else:
        print(text)
