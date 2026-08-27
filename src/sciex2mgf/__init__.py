#!/usr/bin/env python3

# PGK FILE DESCRIPTION
# 2026 (c) YOUR NAME
# https://github.com/username/
# your.mail@mail.com

r"""An example python package with a script that battles two characters.

.. code-block:: text
   :caption: Example Usage

   usage: battle [-h] -f FILE [-c1 CHARACTER_1] [-c2 CHARACTER_2] [-hp HEALTH] [--version]

   Battles two characters.

   options:
     -h, --help            show this help message and exit
     -f, --file FILE       character file to read characters from (str).
     -c1, --character-1 CHARACTER_1
                           index of the first character to use (int).
     -c2, --character-2 CHARACTER_2
                           index of the second character to use (int).
     -hp, --hit-points HEALTH
                           health of all characters (int).
     --version             show program's version number and exit

   (c) Micha Birklbauer, 2026

Examples
--------
>>> from python_pkg_template import character_factory, battle
>>> characters = character_factory("data/characters.csv")
>>> winner = battle(characters[0], characters[1], health=10000)
>>> winner.name
'Shadowheart'
"""

__all__ = ["main"]
__version__ = "0.1.0"
__author__ = "Your Name"

import os
import sys
import argparse
from tqdm import tqdm
from pyteomics import mzml

def try_float(maybe_float) -> float:
    try:
        return float(maybe_float)
    except ValueError as e:
        return float(str(maybe_float).replace(",", "."))

def read_mzml(filename) -> None:
    mgf = list()
    i = 0
    ms2 = list()
    print("Reading mzML file...")
    with mzml.read(filename) as reader:
        for spectrum in reader:
            if int(spectrum["ms level"]) == 2:
                ms2.append(spectrum)
    for spectrum in tqdm(ms2, total=len(ms2), desc="Converting MS2 spectra..."):
        title = f"TITLE={os.path.basename(filename)}.{i} File:\"{os.path.basename(filename)}\" NativeID:\"{spectrum['id']}\""
        if (
            "scanList" not in spectrum
            or "scan" not in spectrum["scanList"]
            or len(spectrum["scanList"]["scan"]) != 1
        ):
            raise RuntimeError(f"Can't get retention time for spectrum: {spectrum}")
        rt_in_min = try_float(spectrum["scanList"]["scan"][0]["scan start time"])
        rt_in_sec = rt_in_min * 60.0
        rtinseconds = f"RTINSECONDS={rt_in_sec}"
        if "precursorList" not in spectrum:
            raise RuntimeError(
                f"[precursorList] No precursor for MS2 spectrum found: {spectrum}"
            )
        if (
            "precursor" not in spectrum["precursorList"]
            or len(spectrum["precursorList"]["precursor"]) < 1
        ):
            raise RuntimeError(
                f"[precursor] No precursor for MS2 spectrum found: {spectrum}"
            )
        for precursor in spectrum["precursorList"]["precursor"]:
            if "selectedIonList" not in precursor:
                raise RuntimeError(
                    f"[selectedIonList] No precursor for MS2 spectrum found: {spectrum}"
                )
            if (
                "selectedIon" not in precursor["selectedIonList"]
                or len(precursor["selectedIonList"]["selectedIon"]) < 1
            ):
                raise RuntimeError(
                    f"[selectedIon] No precursor for MS2 spectrum found: {spectrum}"
                )
            for ion in precursor["selectedIonList"]["selectedIon"]:
                pepmass = f"PEPMASS={try_float(ion['selected ion m/z'])}"
                charge = f"CHARGE={int(ion['charge state'])}+"
                mz_array = spectrum["m/z array"]
                intensity_array = spectrum["intensity array"]
                mgf.append(f"BEGIN IONS\n{title}\n{rtinseconds}\n{pepmass}\n{charge}\n")
                for mz in range(len(mz_array)):
                    mgf.append(f"{float(mz_array[mz])} {float(intensity_array[mz])}\n")
                mgf.append("END IONS\n")
                i += 1
    with open(f"{filename}.mgf", "w", encoding="utf-8") as f:
        f.writelines(mgf)
    print("Finished!")
    return

def main() -> None:
    if len(sys.argv) == 1:
        return stats()
    return read_mzml(str(sys.argv[1]).strip())
