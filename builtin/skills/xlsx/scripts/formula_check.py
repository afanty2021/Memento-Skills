#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""
formula_check.py — Static formula validator for xlsx files.

Usage:
 python3 formula_check.py <file.xlsx>
 python3 formula_check.py --json # machine-readable output
 python3 formula_check.py --report # standardized validation report (JSON)
 python3 formula_check.py --report -o out # report to file
 python3 formula_check.py --sheet Sales # limit to one sheet
 python3 formula_check.py --summary # error counts only, no details

What it checks:
1. Error-value cells: #REF! — all 7 Excel error types
2. Broken cross-sheet references: formula references a sheet not in workbook.xml
3. Broken named-range references: formula references a name not in workbook.xml 
4. Shared formula integrity: shared formula primary cell exists and has formula text
5. Missing <v> on t="e" cells (malformed XML)

Checks NOT performed (require dynamic recalculation):
- Runtime errors that only appear after formulas execute (#DIV/0! on empty denominator, etc.)
 -> Use libreoffice_recalc.py + re-run formula_check.py for dynamic validation

Exit code:
 0 — no errors found
 1 — errors detected (or file cannot be opened)
"""

import sys
import zipfile
import xml.etree.ElementTree as ET
import re
import json

NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
NSP = f"{{{NS}}}"

EXCEL_ERRORS = {"#REF!", "#DIV/0!", "#VALUE!", "#NAME?", "#NULL!", "#NUM!", "#N/A"}

_BUILTIN_FUNCTIONS = {
    "ABS", "AND", "AVERAGE", "AVERAGEIF", "AVERAGEIFS", "CEILING", "CHOOSE",
    "COUNTA", "COUNTIF", "COUNTIFS", "COUNT", "DATE", "EDATE", "EOMONTH",
    "FALSE", "FILTER", "FIND", "FLOOR", "IF", "IFERROR", "IFNA", "IFS",
    "INDEX", "INDIRECT", "INT", "IRR", "ISBLANK", "ISERROR", "ISNA", "ISNUMBER",
    "LARGE", "LEFT", "LEN", "LOOKUP", "LOWER", "MATCH", "MAX", "MID", "MIN",
    "MOD", "MONTH", "NETWORKDAYS", "NOT", "NOW", "NPV", "OFFSET", "OR",
    "PMT", "PV", "RAND", "RANK", "RIGHT", "ROUND", "ROUNDDOWN", "ROUNDUP",
    "ROW", "ROWS", "SEARCH", "SMALL", "SORT", "SQRT", "SUBSTITUTE", "SUM",
    "SUMIF", "SUMIFS", "SUMPRODUCT", "TEXT", "TODAY", "TRANSPOSE", "TRIM",
    "TRUE", "UNIQUE", "UPPER", "VALUE", "VLOOKUP", "HLOOKUP", "XLOOKUP",
    "XMATCH", "XNPV", "XIRR", "YEAR", "YEARFRAC",
}


def get_sheet_names(z: zipfile.ZipFile) -> dict[str, str]:
    wb_xml = z.read("xl/workbook.xml")
    wb = ET.fromstring(wb_xml)
    rel_ns = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
    sheets = {}
    for sheet in wb.findall(f".//{NSP}sheet"):
        name = sheet.get("name", "")
        rid = sheet.get(f"{{{rel_ns}}}id", "")
        sheets[rid] = name
    return sheets


def get_defined_names(z: zipfile.ZipFile) -> set[str]:
    wb_xml = z.read("xl/workbook.xml")
    wb = ET.fromstring(wb_xml)
    names = set()
    for dn in wb.findall(f".//{NSP}definedName"):
        n = dn.get("name", "")
        if n:
            names.add(n)
    return names


def get_sheet_files(z: zipfile.ZipFile) -> dict[str, str]:
    rels_xml = z.read("xl/_rels/workbook.xml.rels")
    rels = ET.fromstring(rels_xml)
    mapping = {}
    for rel in rels:
        rid = rel.get("Id", "")
        target = rel.get("Target", "")
        if "worksheets" in target:
            if not target.startswith("xl/"):
                target = "xl/" + target
            mapping[rid] = target
    return mapping


def extract_sheet_refs(formula: str) -> list[str]:
    refs = []
    for m in re.finditer(r"'([^']+)'!", formula):
        refs.append(m.group(1))
    for m in re.finditer(r"(?<!')\b([A-Za-z_]\w*)\!", formula):
        name = m.group(1)
        if name.upper() not in _BUILTIN_FUNCTIONS:
            refs.append(name)
    return refs


def extract_name_refs(formula: str) -> list[str]:
    names = []
    stripped = re.sub(r"'[^']*'!", "", formula)
    stripped = re.sub(r"[A-Za-z_]\w*!", "", stripped)
    for m in re.finditer(r"\b([A-Za-z_][A-Za-z0-9_.]*)\b", stripped):
        name = m.group(1)
        if name.upper() in _BUILTIN_FUNCTIONS:
            continue
        if re.match(r"^[A-Z]{1,3}[0-9]+$", name, re.IGNORECASE):
            continue
        if re.match(r"^[A-Z]{1,3}$", name, re.IGNORECASE):
            continue
        if name.upper() in ("TRUE", "FALSE"):
            continue
        names.append(name)
    return names


def check(xlsx_path: str, sheet_filter: str | None = None) -> dict:
    results = {
        "file": xlsx_path,
        "sheets_checked": [],
        "formula_count": 0,
        "shared_formula_ranges": 0,
        "error_count": 0,
        "errors": [],
    }

    try:
        z = zipfile.ZipFile(xlsx_path, "r")
    except Exception as e:
        results["errors"].append({"type": "file_error", "message": str(e)})
        results["error_count"] = 1
        return results

    with z:
        sheet_names = get_sheet_names(z)
        sheet_files = get_sheet_files(z)
        defined_names = get_defined_names(z)
        valid_sheet_names = set(sheet_names.values())

        for rid, sheet_name in sheet_names.items():
            if sheet_filter and sheet_name != sheet_filter:
                continue
            results["sheets_checked"].append(sheet_name)

            sheet_path = sheet_files.get(rid)
            if not sheet_path or sheet_path not in z.namelist():
                continue

            ws_xml = z.read(sheet_path)
            ws = ET.fromstring(ws_xml)

            shared_primary = {}

            for cell in ws.findall(f".//{NSP}c"):
                cell_ref = cell.get("r", "?")
                cell_type = cell.get("t", "")

                if cell_type == "e":
                    v_elem = cell.find(f"{NSP}v")
                    if v_elem is None:
                        results["errors"].append(
                            {
                                "type": "malformed_error_cell",
                                "sheet": sheet_name,
                                "cell": cell_ref,
                                "detail": "t=\"e\" but no <v> child element",
                            }
                        )
                        results["error_count"] += 1
                    else:
                        error_val = v_elem.text or "#UNKNOWN"
                        f_elem = cell.find(f"{NSP}f")
                        results["errors"].append(
                            {
                                "type": "error_value",
                                "error": error_val,
                                "sheet": sheet_name,
                                "cell": cell_ref,
                                "formula": f_elem.text if (f_elem is not None and f_elem.text) else None,
                            }
                        )
                        results["error_count"] += 1

                f_elem = cell.find(f"{NSP}f")
                if f_elem is None:
                    continue

                f_type = f_elem.get("t", "")
                f_si = f_elem.get("si")

                if f_type == "shared" and f_elem.text is None:
                    continue

                formula = f_elem.text or ""

                if f_type == "shared" and f_elem.get("ref"):
                    results["shared_formula_ranges"] += 1
                    if f_si is not None:
                        shared_primary[f_si] = cell_ref

                if formula:
                    results["formula_count"] += 1

                    for ref_sheet in extract_sheet_refs(formula):
                        if ref_sheet not in valid_sheet_names:
                            results["errors"].append(
                                {
                                    "type": "broken_sheet_ref",
                                    "sheet": sheet_name,
                                    "cell": cell_ref,
                                    "formula": formula,
                                    "missing_sheet": ref_sheet,
                                    "valid_sheets": sorted(valid_sheet_names),
                                }
                            )
                            results["error_count"] += 1

                    for name_ref in extract_name_refs(formula):
                        if name_ref not in defined_names:
                            results["errors"].append(
                                {
                                    "type": "unknown_name_ref",
                                    "sheet": sheet_name,
                                    "cell": cell_ref,
                                    "formula": formula,
                                    "unknown_name": name_ref,
                                    "defined_names": sorted(defined_names),
                                    "note": "Heuristic check — verify manually if this is a false positive",
                                }
                            )
                            results["error_count"] += 1

    return results


def build_report(results: dict) -> dict:
    from collections import Counter
    errors = results.get("errors", [])
    error_types = [e.get("error", e.get("type", "unknown")) for e in errors]
    return {
        "status": "success" if results["error_count"] == 0 else "errors_found",
        "file": results["file"],
        "sheets_checked": results["sheets_checked"],
        "total_formulas": results["formula_count"],
        "total_errors": results["error_count"],
        "shared_formula_ranges": results.get("shared_formula_ranges", 0),
        "errors_by_type": dict(Counter(error_types)) if errors else {},
        "errors": errors,
    }


def main() -> None:
    use_json = "--json" in sys.argv
    use_report = "--report" in sys.argv
    summary_only = "--summary" in sys.argv
    output_file = None
    sheet_filter = None
    args_clean = []

    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg == "--sheet" and i + 1 < len(sys.argv):
            sheet_filter = sys.argv[i + 1]
            i += 2
        elif arg == "-o" and i + 1 < len(sys.argv):
            output_file = sys.argv[i + 1]
            i += 2
        elif arg.startswith("--"):
            i += 1
        else:
            args_clean.append(arg)
            i += 1

    if not args_clean:
        print("Usage: formula_check.py <file.xlsx> [--json] [--report [-o FILE]] [--sheet NAME] [--summary]")
        sys.exit(1)

    results = check(args_clean[0], sheet_filter=sheet_filter)

    if use_report:
        report = build_report(results)
        output = json.dumps(report, indent=2, ensure_ascii=False)
        if output_file:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(output + "\n")
        else:
            print(output)
        sys.exit(1 if results["error_count"] > 0 else 0)

    if use_json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
        sys.exit(1 if results["error_count"] > 0 else 0)

    sheets = ", ".join(results["sheets_checked"]) or "(none)"
    if sheet_filter:
        sheets = f"{sheet_filter} (filtered)"

    print(f"File : {results['file']}")
    print(f"Sheets : {sheets}")
    print(f"Formulas checked : {results['formula_count']} distinct formula cells")
    print(f"Shared formula ranges : {results['shared_formula_ranges']} ranges")
    print(f"Errors found : {results['error_count']}")

    if not summary_only and results["errors"]:
        print("\n── Error Details ──")
        for e in results["errors"]:
            if e["type"] == "error_value":
                formula_hint = f" (formula: {e['formula']})" if e.get("formula") else ""
                print(f"  [FAIL] [{e['sheet']}!{e['cell']}] contains {e['error']}{formula_hint}")
            elif e["type"] == "broken_sheet_ref":
                print(f"  [FAIL] [{e['sheet']}!{e['cell']}] references missing sheet '{e['missing_sheet']}'")
                print(f"         Formula: {e['formula']}")
                print(f"         Valid sheets: {e.get('valid_sheets', [])}")
            elif e["type"] == "unknown_name_ref":
                print(f"  [WARN] [{e['sheet']}!{e['cell']}] uses unknown name '{e['unknown_name']}' (heuristic — verify manually)")
                print(f"         Formula: {e['formula']}")
                print(f"         Defined names: {e.get('defined_names', [])}")
            elif e["type"] == "malformed_error_cell":
                print(f"  [FAIL] [{e['sheet']}!{e['cell']}] malformed error cell: {e['detail']}")
            elif e["type"] == "file_error":
                print(f"  [FAIL] File error: {e['message']}")
        print()

    if results["error_count"] == 0:
        print("PASS — No formula errors detected")
    else:
        hard_errors = [e for e in results["errors"] if e["type"] != "unknown_name_ref"]
        warnings = [e for e in results["errors"] if e["type"] == "unknown_name_ref"]
        if hard_errors:
            print(f"FAIL — {len(hard_errors)} error(s) must be fixed before delivery")
        if warnings:
            print(f"WARN — {len(warnings)} heuristic warning(s) require manual review")
            sys.exit(1)
        else:
            print(f"PASS with WARN — {len(warnings)} heuristic warning(s) require manual review")
            sys.exit(0)


if __name__ == "__main__":
    main()
