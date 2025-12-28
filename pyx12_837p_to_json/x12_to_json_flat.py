"""
x12_to_json_flat.py

Converts X12 EDI files (particularly 837P healthcare claims) to a flat JSON representation
using the pyx12 library.

WHAT IS "FLAT" REPRESENTATION?
"Flat" means the output is a simple sequential list of segments without any hierarchical
nesting or structure. Specifically:

- NO hierarchical loops: X12 files have nested loops (e.g., 2000A Billing Provider Loop,
  2300 Claim Loop, 2400 Service Line Loop), but this converter ignores that structure
- NO business logic: Doesn't group related segments (e.g., CLM with its service lines)
- NO relationships: Each segment stands alone without understanding its context
- JUST a linear list: Segments appear in file order as a flat list

This is useful for:
- Debugging: See exactly what's in the file without interpretation
- Initial exploration: Understand raw file contents before applying business logic
- Simple data extraction: When you just need specific segment values

For a hierarchical/structured output that groups claims, service lines, etc., you would
need a different parser that understands X12 loop structures.

The output JSON contains:
- File path/name
- List of segments, each with:
  - segment_id: The segment identifier (e.g., 'ISA', 'GS', 'ST', 'CLM', 'SV1')
  - elements: Ordered list of element values from that segment

Usage:
    As a module:
        from x12_to_json_flat import x12_to_flat_json
        data = x12_to_flat_json("path/to/file.837")

    As a command-line tool:
        python x12_to_json_flat.py input.837 -o output.json
"""

from pathlib import Path
import json

import pyx12.x12file as x12file
import pyx12.errors as x12errors

def x12_to_flat_json(path: str | Path) -> dict:
    """
    Parse an X12 file and convert it to a flat JSON representation.

    This function reads an X12 EDI file segment by segment and extracts each segment's
    identifier and element values into a simple list structure. No hierarchical parsing
    or business logic is applied - segments are simply read in sequential order.

    "Flat" means segments are returned as a linear list in file order, without any
    hierarchical nesting to represent X12 loops (like 2000A, 2300, 2400) or grouping
    of related segments. Each segment is independent and unaware of its context within
    the larger X12 structure.

    Args:
        path: File path to the X12 file (string or Path object)

    Returns:
        Dictionary with structure:
        {
            "file": "path/to/file.x12",
            "segments": [
                {
                    "segment_id": "ISA",
                    "elements": ["00", "          ", "00", ...]
                },
                {
                    "segment_id": "GS",
                    "elements": ["HC", "SENDER", "RECEIVER", ...]
                },
                {
                    "segment_id": "CLM",
                    "elements": ["CLAIM123", "100.00", ...]
                },
                ...
            ]
        }

        Note: All segments appear sequentially - there's no nesting to show that
        certain segments belong to a specific claim or service line.

    Raises:
        FileNotFoundError: If the specified file doesn't exist
        RuntimeError: If the file is not valid X12 format
    """
    # Convert path to Path object for consistent handling
    path = Path(path)

    # Validate that the file exists
    if not path.is_file():
        raise FileNotFoundError(path)

    # Initialize list to store all segments from the X12 file
    segments = []

    # Open and parse the X12 file
    # IMPORTANT: pyx12.X12Reader requires an open file object, not a string path
    with path.open("r") as f:
        # Create X12 reader and handle any parsing errors
        try:
            reader = x12file.X12Reader(f)
        except x12errors.X12Error as e:
            raise RuntimeError(f"{path} does not look like X12: {e}")

        # Iterate through each segment in the X12 file
        for seg in reader:
            # Extract the segment identifier (e.g., 'ISA', 'GS', 'ST', 'CLM', 'SV1')
            seg_id = seg.get_seg_id()

            # Extract all element values from the segment in order
            # values_iterator() provides each element from the segment sequentially
            elements = [v for v in seg.values_iterator()]

            # Add this segment to our list with its ID and element values
            segments.append(
                {
                    "segment_id": seg_id,
                    "elements": elements,
                }
            )

    # Return the complete data structure with filename and all segments
    return {"file": str(path), "segments": segments}


if __name__ == "__main__":
    # Command-line interface for converting X12 files to JSON
    import argparse

    # Set up command-line argument parser
    parser = argparse.ArgumentParser(description="Flat X12 -> JSON")
    parser.add_argument("input", help="X12 837P file")
    parser.add_argument("-o", "--output", help="JSON output file (default: stdout)")
    args = parser.parse_args()

    # Parse the X12 file to JSON data structure
    data = x12_to_flat_json(args.input)

    # Convert to formatted JSON string with 2-space indentation
    text = json.dumps(data, indent=2)
data_d
    # Write output to file or print to stdout
    if args.output:
        # Write to specified output file
        Path(args.output).write_text(text, encoding="utf-8")
    else:
        # Print to stdout (console)
        print(text)
