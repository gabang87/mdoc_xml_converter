# Author: Gabriella Angiulli
# Date: 2026-04-27
# Description: Convert MDOC files to BeamShift XML format cryosparc compatible

import os
import sys
import mdocfile
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom

# ---------------- XLM NAMESPACES ----------------
NS_MAIN = "http://schemas.datacontract.org/2004/07/Fei.SharedObjects"
NS_A = "http://schemas.datacontract.org/2004/07/Fei.Types"

# ---------------- XLM FORMAT ----------------
ET.register_namespace("", NS_MAIN)
ET.register_namespace("a", NS_A)

# ---------------- PRETTY PRINT ----------------
def prettify(elem):
    rough = ET.tostring(elem, encoding="utf-8")
    reparsed = minidom.parseString(rough)
    return reparsed.toprettyxml(indent="    ")

# ---------------- CORE FUNCTION ----------------
def convert_mdoc_to_xml(input_folder, output_folder):
    if not os.path.exists(input_folder):
        print(f"Input folder does not exist: {input_folder}")
        return

    os.makedirs(output_folder, exist_ok=True) 

    for filename in os.listdir(input_folder):
        if not filename.endswith(".mdoc"):
            continue

        try:
            filepath = os.path.join(input_folder, filename)
            print(f"Processing: {filename}")

            df = mdocfile.read(filepath)

            if df.empty:
                print(f"Empty file: {filename}")
                continue

            if "ImageShift" not in df.columns:
                print(f"Skipping {filename}: no ImageShift")
                continue

            row = df.iloc[0]
            shift = row["ImageShift"]

            # Handle different formats
            if isinstance(shift, (list, tuple)):
                x, y = shift
            else:
                parts = str(shift).split()
                x = parts[0]
                y = parts[1] if len(parts) > 1 else 0

            # ---- XML ----
            root = ET.Element(f"{{{NS_MAIN}}}MicroscopeImage", {
                "xmlns:i": "http://www.w3.org/2001/XMLSchema-instance"
            })

            microscopeData = ET.SubElement(root, "microscopeData")
            optics = ET.SubElement(microscopeData, "optics")
            beamshift = ET.SubElement(optics, "BeamShift")

            ET.SubElement(beamshift, f"{{{NS_A}}}_x").text = str(x)
            ET.SubElement(beamshift, f"{{{NS_A}}}_y").text = str(y)

            # ---- SAVE ----
            base_name = os.path.splitext(filename)[0]
            output_file = os.path.join(output_folder, base_name + ".xml")

            xml_string = prettify(root)

            with open(output_file, "w", encoding="utf-8") as f:
                f.write(xml_string)

            print(f"Saved: {output_file}")

        except Exception as e:
            print(f"Error in {filename}: {e}")


# ---------------- ENTRY POINT ----------------
if __name__ == "__main__":
    # If arguments are provided → use them
    if len(sys.argv) == 3:
        input_folder = sys.argv[1]
        output_folder = sys.argv[2]
    else:
        # Otherwise, ask the user
        print("No folders provided. Please enter them below:\n")

        input_folder = input("Enter input folder path: ").strip()
        output_folder = input("Enter output folder path: ").strip()

    convert_mdoc_to_xml(input_folder, output_folder)
