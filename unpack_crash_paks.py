from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

# Source folders
NST_SOURCE = Path(r"F:\Crash-modding\Crash-games\Crash Bandicoot - N Sane Trilogy\archives")
CRASH4_SOURCE = Path(r"F:\Crash-modding\Crash-games\Crash Bandicoot 4\Lava\Content\Paks")

# Tool paths: edit these values for your setup.
QUICKBMS_EXE = Path(r"F:\Crash-modding\tools\quickbms_win\quickbms.exe")
NST_BMS_SCRIPT = Path(r"F:\Crash-modding\tools\quickbms_win\marvel_ultimate_alliance_2.bms")
UNREALPAK_EXE: Path(r"F:\Crash-modding\tools\UnrealPakTool\UnrealPak.exe")

# Output folders
NST_OUTPUT = Path(r"F:\Crash-modding\paks\nst")
CRASH4_OUTPUT = Path(r"F:\Crash-modding\paks\c4")


def find_executable(explicit_path: str | None, name: str) -> Path:
    if explicit_path:
        executable = Path(explicit_path)
        if executable.is_file():
            return executable
        raise FileNotFoundError(f"{name} not found: {executable}")

    on_path = shutil.which(name)
    if on_path:
        return Path(on_path)

    raise FileNotFoundError(
        f"Could not find {name}. Pass its location with the matching command-line option."
    )


def find_nst_script(explicit_path: str | None) -> Path:
    if explicit_path:
        script = Path(explicit_path)
        if script.is_file():
            return script
        raise FileNotFoundError(f"NST QuickBMS script not found: {script}")

    raise FileNotFoundError(
        "Could not find the NST QuickBMS script. Pass the path to "
    )


def unpack_nst(source: Path, destination: Path, quickbms: Path, bms_script: Path) -> int:
    if not source.is_dir():
        print(f"NST source folder does not exist: {source}", file=sys.stderr)
        return 1

    pak_files = sorted(source.rglob("*.pak"))
    if not pak_files:
        print(f"No NST .pak files found in: {source}")
        return 0

    destination.mkdir(parents=True, exist_ok=True)
    failures = 0

    for pak_file in pak_files:
        # Keep each archive separate so identically named files do not overwrite.
        pak_output = destination / pak_file.stem
        pak_output.mkdir(parents=True, exist_ok=True)
        print(f"Unpacking NST archive with QuickBMS: {pak_file}")
        result = subprocess.run(
            [str(quickbms), "-o", str(bms_script), str(pak_file), str(pak_output)],
            check=False,
        )
        if result.returncode != 0:
            failures += 1
            print(f"Failed (exit {result.returncode}): {pak_file}", file=sys.stderr)

    print(f"NST finished: {len(pak_files) - failures}/{len(pak_files)} archives extracted to {destination}")
    return failures


def unpack_crash4(source: Path, destination: Path, unrealpak: Path) -> int:
    if not source.is_dir():
        print(f"Crash 4 source folder does not exist: {source}", file=sys.stderr)
        return 1

    pak_files = sorted(source.rglob("*.pak"))
    if not pak_files:
        print(f"No Crash 4 .pak files found in: {source}")
        return 0

    destination.mkdir(parents=True, exist_ok=True)
    failures = 0

    for pak_file in pak_files:
        pak_output = destination / pak_file.stem
        pak_output.mkdir(parents=True, exist_ok=True)
        print(f"Unpacking Crash 4 archive with UnrealPak: {pak_file}")
        result = subprocess.run(
            [str(unrealpak), str(pak_file), "-Extract", str(pak_output)],
            check=False,
        )
        if result.returncode != 0:
            failures += 1
            print(f"Failed (exit {result.returncode}): {pak_file}", file=sys.stderr)

    print(f"Crash 4 finished: {len(pak_files) - failures}/{len(pak_files)} archives extracted to {destination}")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Batch extract NST archives with QuickBMS and Crash 4 archives with UnrealPak."
    )
    parser.add_argument("--quickbms", help="Path to quickbms.exe.")
    parser.add_argument("--nst-script", help="Path to Aluigi's marvel_ultimate_alliance_2.bms script.")
    parser.add_argument("--unrealpak", help="Path to UnrealPak.exe (or add it to PATH).")
    args = parser.parse_args()

    try:
        quickbms = find_executable(args.quickbms or str(QUICKBMS_EXE), "quickbms.exe")
        nst_script = find_nst_script(args.nst_script or str(NST_BMS_SCRIPT))
        unrealpak = find_executable(args.unrealpak or (str(UNREALPAK_EXE) if UNREALPAK_EXE else None), "UnrealPak.exe")
    except FileNotFoundError as error:
        parser.error(str(error))

    failures = unpack_nst(NST_SOURCE, NST_OUTPUT, quickbms, nst_script)
    failures += unpack_crash4(CRASH4_SOURCE, CRASH4_OUTPUT, unrealpak)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())

