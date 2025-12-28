# PyX12 837P to JSON Converter

A Python toolkit for converting X12 837P (Professional Healthcare Claims) EDI files to JSON format using the PyX12 library.

## Overview

This project provides two complementary approaches to convert X12 837P healthcare claim files to JSON:

1. **Structured Claims Parser** (`x12_837p_to_claims_json.py`) - Extracts healthcare claims with proper hierarchical structure
2. **Flat Segment Parser** (`x12_to_json_flat.py`) - Converts X12 files to a simple sequential list of segments

## Features

- Parse X12 837P professional healthcare claim files
- Extract claim-level and service line-level data
- Two output formats: structured (business logic applied) and flat (raw segments)
- Command-line interface for easy file conversion
- Python API for programmatic usage
- Sample data and outputs included for reference

## What is X12 837P?

The X12 837P (Healthcare Claim: Professional) is a HIPAA-compliant EDI transaction set used in the U.S. healthcare industry for submitting professional healthcare claim information from providers to insurance payers.

Key X12 837P concepts:
- **2300 Loop**: Claim Information - contains header info for a single claim
- **2400 Loop**: Service Line - contains details about individual services/procedures
- **CLM Segment**: Claim header with control number and total charge
- **SV1 Segment**: Professional service with procedure code and line charge

## Installation

### Prerequisites

- Python 3.8 or higher
- PyX12 library

### Install Dependencies

```bash
pip install pyx12
```

### Clone or Download

```bash
# Clone this repository or download the files
git clone <repository-url>
cd pyx12_837p_to_json
```

## Usage

### 1. Structured Claims Parser

Extracts claims with proper hierarchy (claims containing service lines):

#### Command Line

```bash
# Output to stdout
python x12_837p_to_claims_json.py x12_837p_data/sample_837p_minimal.txt

# Output to file
python x12_837p_to_claims_json.py x12_837p_data/sample_837p.txt -o output.json
```

#### Python API

```python
from x12_837p_to_claims_json import extract_claims_from_837p

# Extract claims from file
claims = extract_claims_from_837p("path/to/file.837")

# Process claims
for claim in claims:
    print(f"Claim ID: {claim['claim_id']}")
    print(f"Total Charge: {claim['total_charge']}")
    for line in claim['service_lines']:
        print(f"  - Procedure: {line['procedure_code']}, Charge: {line['line_charge']}")
```

#### Output Format

```json
[
  {
    "claim_id": "1001",
    "total_charge": "100",
    "service_lines": [
      {
        "procedure_code": "HC:99213",
        "line_charge": "100"
      }
    ]
  }
]
```

### 2. Flat Segment Parser

Converts X12 files to a flat list of segments (no business logic applied):

#### Command Line

```bash
# Output to stdout
python x12_to_json_flat.py x12_837p_data/sample_837p_minimal.txt

# Output to file
python x12_to_json_flat.py x12_837p_data/sample_837p.txt -o output_flat.json
```

#### Python API

```python
from x12_to_json_flat import x12_to_flat_json

# Parse X12 file to flat JSON
data = x12_to_flat_json("path/to/file.837")

# Access segments
print(f"File: {data['file']}")
for segment in data['segments']:
    print(f"Segment: {segment['segment_id']}, Elements: {segment['elements']}")
```

#### Output Format

```json
{
  "file": "path/to/file.837",
  "segments": [
    {
      "segment_id": "ISA",
      "elements": ["00", "          ", "00", "          ", ...]
    },
    {
      "segment_id": "CLM",
      "elements": ["1001", "100", "", "", "11:B:1", ...]
    }
  ]
}
```

## Project Structure

```
pyx12_837p_to_json/
├── x12_837p_to_claims_json.py    # Structured claims parser
├── x12_to_json_flat.py           # Flat segment parser
├── x12_837p_data/                # Sample X12 input files
│   ├── sample_837p.txt
│   └── sample_837p_minimal.txt
├── json_output/                  # Sample JSON output files
│   ├── sample_837p_flat.json
│   ├── sample_837p_minimal.json
│   └── sample_837p_minimal_flat.json
└── docs/                         # Documentation
    ├── pyx12_element_structure_explained.html
    └── pyx12.params.pdf
```

## Understanding the Two Approaches

### Structured Parser (x12_837p_to_claims_json.py)

**Best for:**
- Processing healthcare claims for business applications
- Extracting specific claim and service line data
- When you need claims grouped with their service lines

**Features:**
- Understands X12 loop hierarchy (2300 claim loops, 2400 service line loops)
- Groups related data (each claim with its service lines)
- Filters out non-claim segments
- Applies business logic to extract meaningful data

### Flat Parser (x12_to_json_flat.py)

**Best for:**
- Debugging X12 files
- Initial exploration of file contents
- When you need all segments without interpretation
- Building custom parsers with your own business logic

**Features:**
- No hierarchical structure - just sequential segments
- No filtering - all segments included
- No business logic applied
- Shows exact file contents in order

## Extending the Parsers

### Adding More Claim Fields

In `x12_837p_to_claims_json.py`, you can extract additional claim-level data:

```python
# Inside the claim_loop iteration
service_location = claim_loop.get_value("CLM05-1")  # Service location
diagnosis_code = claim_loop.get_value("HI01-2")     # Primary diagnosis
service_date = claim_loop.get_value("DTP03")        # Service date
```

### Adding More Service Line Fields

```python
# Inside the sl_loop iteration
unit_count = sl_loop.get_value("SV104")             # Service unit count
procedure_modifier = sl_loop.get_value("SV101-3")   # Procedure modifier
service_date = sl_loop.get_value("DTP03")           # Service date
```

## Common X12 Segment References

| Segment | Description |
|---------|-------------|
| ISA | Interchange Control Header |
| GS | Functional Group Header |
| ST | Transaction Set Header |
| BHT | Beginning of Hierarchical Transaction |
| NM1 | Individual or Organizational Name |
| HL | Hierarchical Level |
| SBR | Subscriber Information |
| CLM | Claim Information |
| HI | Health Care Diagnosis Code |
| LX | Service Line Number |
| SV1 | Professional Service |
| DTP | Date or Time or Period |
| SE | Transaction Set Trailer |
| GE | Functional Group Trailer |
| IEA | Interchange Control Trailer |

## Troubleshooting

### PyX12 Import Errors

If you encounter import errors with PyX12:

```bash
pip install --upgrade pyx12
```

### Invalid X12 Format

The flat parser will raise a `RuntimeError` if the file is not valid X12 format. Check that:
- File uses proper X12 delimiters (typically `*` for elements, `~` for segments)
- File contains valid X12 segments (ISA, GS, ST, etc.)
- File encoding is correct (typically ASCII or UTF-8)

### Empty Claims Output

If the structured parser returns empty claims, verify:
- The file contains 2300 loops with CLM segments
- CLM01 (claim ID) and CLM02 (total charge) have values
- The X12 map files for PyX12 are properly configured

## Resources

### Documentation Files

- `docs/pyx12_element_structure_explained.html` - Detailed explanation of PyX12 element structure
- `docs/pyx12.params.pdf` - PyX12 parameters documentation

### External Resources

- [PyX12 Library](https://github.com/azoner/pyx12) - Official PyX12 repository
- [X12 Standards](https://x12.org/) - Official X12 EDI standards organization
- [HIPAA 837P Guide](https://www.cms.gov/regulations-and-guidance/administrative-simplification/hipaa-aba/downloads/claims837p.pdf) - CMS implementation guide

## License

This project is provided as-is for educational and development purposes. Please ensure compliance with HIPAA and other relevant regulations when handling healthcare data.

## Contributing

Contributions are welcome! Areas for improvement:

- Add support for additional X12 transaction sets (835, 270/271, etc.)
- Enhance error handling and validation
- Add unit tests
- Support for batch processing multiple files
- Add data validation against X12 specifications
- Extract additional claim and service line fields

## Contact

For questions, issues, or suggestions, please open an issue in the repository.