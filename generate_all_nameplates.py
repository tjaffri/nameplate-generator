#!/usr/bin/env python3
"""
Automated nameplate generator for multiple names
Generates properly sized nameplates with color support for Bambu Studio
"""

import os
import subprocess
import json
import zipfile
import shutil
import uuid
from pathlib import Path


class NameplateGenerator:
    def __init__(self):
        # Default dimensions (can be overridden)
        self.base_height = 22  # mm
        self.base_thickness = 2.5  # mm
        self.text_height = 1.2  # mm (raised above base)
        self.corner_radius = 2  # mm
        self.pin_hole_diameter = 1.5  # mm
        self.pin_hole_from_edge = 4  # mm
        self.font_size = 10  # points
        self.min_width = 60  # minimum plate width
        self.margin = 8  # margin on each side of text

        # Colors (for 3MF export)
        self.base_color = "#87CEEB"  # Light blue (Sky Blue)
        self.text_color = "#000000"  # Black

        # Output directories
        self.output_dir = "output"
        self.final_dir = os.path.join(self.output_dir, "final")
        self.stl_dir = os.path.join(self.output_dir, "stl")
        self.scad_dir = os.path.join(self.output_dir, "scad")

        # Create directories if they don't exist
        os.makedirs(self.final_dir, exist_ok=True)
        os.makedirs(self.stl_dir, exist_ok=True)
        os.makedirs(self.scad_dir, exist_ok=True)

    def calculate_text_width(self, text, font_size):
        """Estimate text width in mm based on character count"""
        # Average character width for Arial Bold at size 10 is ~6mm
        # This is an approximation
        char_width = font_size * 0.6
        return len(text) * char_width

    def calculate_plate_width(self, name):
        """Calculate appropriate plate width for the given name"""
        text_width = self.calculate_text_width(name, self.font_size)
        plate_width = text_width + (2 * self.margin)

        # Ensure minimum width
        if plate_width < self.min_width:
            plate_width = self.min_width

        # Round to nearest 5mm for nice numbers
        plate_width = round(plate_width / 5) * 5

        return plate_width

    def generate_scad_file(self, name, output_file):
        """Generate OpenSCAD file for a nameplate"""
        plate_width = self.calculate_plate_width(name)

        scad_content = f"""// Nameplate for {name}
// Auto-generated - dimensions calculated based on text length

// Parameters
plate_width = {plate_width};
plate_height = {self.base_height};
plate_thickness = {self.base_thickness};
text_height = {self.text_height};
corner_radius = {self.corner_radius};
pin_hole_diameter = {self.pin_hole_diameter};
pin_hole_from_edge = {self.pin_hole_from_edge};
font_size = {self.font_size};

module rounded_rectangle(width, height, thickness, radius) {{
    linear_extrude(height = thickness)
        offset(r = radius)
            offset(r = -radius)
                square([width, height], center = true);
}}

module nameplate_base() {{
    difference() {{
        // Base plate
        rounded_rectangle(plate_width, plate_height, plate_thickness, corner_radius);

        // Pin holes at top corners
        translate([plate_width/2 - pin_hole_from_edge, plate_height/2 - pin_hole_from_edge, 0])
            cylinder(h = plate_thickness + 1, r = pin_hole_diameter/2, center = true, $fn = 20);
        translate([-plate_width/2 + pin_hole_from_edge, plate_height/2 - pin_hole_from_edge, 0])
            cylinder(h = plate_thickness + 1, r = pin_hole_diameter/2, center = true, $fn = 20);
    }}
}}

module nameplate_text() {{
    translate([0, 0, plate_thickness])
        linear_extrude(height = text_height)
            text("{name}", size = font_size, font = "Arial:style=Bold", halign = "center", valign = "center");
}}

// Render base and text together
nameplate_base();
nameplate_text();
"""

        with open(output_file, 'w') as f:
            f.write(scad_content)

        return plate_width

    def generate_scad_base_only(self, name, output_file):
        """Generate OpenSCAD file for base only"""
        plate_width = self.calculate_plate_width(name)

        scad_content = f"""// Base plate only for {name}
plate_width = {plate_width};
plate_height = {self.base_height};
plate_thickness = {self.base_thickness};
corner_radius = {self.corner_radius};
pin_hole_diameter = {self.pin_hole_diameter};
pin_hole_from_edge = {self.pin_hole_from_edge};

module rounded_rectangle(width, height, thickness, radius) {{
    linear_extrude(height = thickness)
        offset(r = radius)
            offset(r = -radius)
                square([width, height], center = true);
}}

difference() {{
    rounded_rectangle(plate_width, plate_height, plate_thickness, corner_radius);
    translate([plate_width/2 - pin_hole_from_edge, plate_height/2 - pin_hole_from_edge, 0])
        cylinder(h = plate_thickness + 1, r = pin_hole_diameter/2, center = true, $fn = 20);
    translate([-plate_width/2 + pin_hole_from_edge, plate_height/2 - pin_hole_from_edge, 0])
        cylinder(h = plate_thickness + 1, r = pin_hole_diameter/2, center = true, $fn = 20);
}}
"""

        with open(output_file, 'w') as f:
            f.write(scad_content)

    def generate_scad_text_only(self, name, output_file):
        """Generate OpenSCAD file for text only"""
        scad_content = f"""// Text only for {name}
plate_thickness = {self.base_thickness};
text_height = {self.text_height};
font_size = {self.font_size};

translate([0, 0, plate_thickness])
    linear_extrude(height = text_height)
        text("{name}", size = font_size, font = "Arial:style=Bold", halign = "center", valign = "center");
"""

        with open(output_file, 'w') as f:
            f.write(scad_content)

    def render_stl(self, scad_file, stl_file):
        """Render SCAD file to STL using OpenSCAD"""
        try:
            result = subprocess.run(
                ['openscad', '-o', stl_file, scad_file],
                capture_output=True,
                text=True,
                timeout=60
            )
            return result.returncode == 0
        except Exception as e:
            print(f"  Error rendering {scad_file}: {e}")
            return False

    def hex_to_rgb(self, hex_color):
        """Convert hex color to RGB values (0-1 range)"""
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        return r/255.0, g/255.0, b/255.0

    def create_3mf(self, base_stl, text_stl, output_3mf, name):
        """Create a 3MF file optimized for Bambu Studio with merged geometry and painting"""
        try:
            import trimesh
            from stl import mesh as stl_mesh
            import numpy as np

            print(f"    Loading and parsing STL files...")

            # Load and merge meshes using trimesh for better handling
            base_trimesh = trimesh.load(base_stl)
            text_trimesh = trimesh.load(text_stl)

            print(f"    Merging and painting geometry...")

            # Merge the meshes into a single mesh
            combined = trimesh.util.concatenate([base_trimesh, text_trimesh])

            # Assign face colors based on Z-height
            # Base faces (z < 2.5) get light blue, text faces (z >= 2.5) get black
            face_colors = np.zeros((len(combined.faces), 4), dtype=np.uint8)

            for i, face in enumerate(combined.faces):
                # Get the vertices of this face
                vertices = combined.vertices[face]
                # Check average Z position
                avg_z = np.mean(vertices[:, 2])

                if avg_z < 2.5:  # Base plate
                    # Light blue: #87CEEB
                    face_colors[i] = [135, 206, 235, 255]
                else:  # Text
                    # Black: #000000
                    face_colors[i] = [0, 0, 0, 255]

            # Apply the face colors
            combined.visual.face_colors = face_colors

            # Create temporary directory for 3MF contents
            temp_dir = f"temp_3mf_{name.replace(' ', '_')}"
            os.makedirs(temp_dir, exist_ok=True)
            os.makedirs(os.path.join(temp_dir, "3D"), exist_ok=True)

            print(f"    Exporting to 3MF format...")

            # Export using trimesh's 3MF exporter
            # Save to temp directory first
            temp_3mf = os.path.join(temp_dir, "temp.3mf")
            combined.export(temp_3mf, file_type='3mf')

            # Extract the temp 3MF to modify it
            import zipfile as zf
            with zf.ZipFile(temp_3mf, 'r') as zip_in:
                zip_in.extractall(temp_dir)

            # Remove the temp file
            os.remove(temp_3mf)

            # Read and modify the model XML to add Bambu Studio metadata
            model_file = os.path.join(temp_dir, "3D", "3dmodel.model")
            with open(model_file, 'r', encoding='utf-8') as f:
                model_xml = f.read()

            # Add Bambu Studio metadata after the opening model tag
            model_xml = model_xml.replace(
                '<model ',
                '<model xmlns:slic3rpe="http://schemas.slic3r.org/3mf/2017/06" '
            )
            model_xml = model_xml.replace(
                '</model>',
                f'''    <metadata name="Application">Bambu Studio</metadata>
    <metadata name="BambuStudio:3mfVersion">1</metadata>
    <metadata name="Title">{name} Nameplate</metadata>
</model>'''
            )

            # Write modified model back
            with open(model_file, 'w', encoding='utf-8') as f:
                f.write(model_xml)

            print(f"    Creating final 3MF archive...")
            # Create final 3MF archive
            with zipfile.ZipFile(output_3mf, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        if file.endswith('.3mf'):
                            continue
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, temp_dir)
                        zipf.write(file_path, arcname)

            # Clean up temp directory
            shutil.rmtree(temp_dir)

            return True
        except Exception as e:
            print(f"  Error creating 3MF: {e}")
            import traceback
            traceback.print_exc()
            if 'temp_dir' in locals() and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            return False

    def generate_nameplate(self, name):
        """Generate complete nameplate for a single name"""
        # Clean name for filename
        safe_name = name.lower().replace(" ", "_")

        print(f"\n{'='*60}")
        print(f"Generating nameplate: {name}")
        print(f"{'='*60}")

        # Calculate dimensions
        plate_width = self.calculate_plate_width(name)
        text_width = self.calculate_text_width(name, self.font_size)
        print(f"  Text width: {text_width:.1f}mm")
        print(f"  Plate width: {plate_width}mm")
        print(f"  Plate height: {self.base_height}mm")

        # Generate SCAD files in scad directory (temporary)
        print(f"  Generating OpenSCAD files...")
        scad_base = os.path.join(self.scad_dir, f"{safe_name}_base.scad")
        scad_text = os.path.join(self.scad_dir, f"{safe_name}_text.scad")
        scad_combined = os.path.join(self.scad_dir, f"{safe_name}.scad")

        self.generate_scad_base_only(name, scad_base)
        self.generate_scad_text_only(name, scad_text)
        self.generate_scad_file(name, scad_combined)

        # Render to STL in stl directory
        print(f"  Rendering STL files...")
        stl_base = os.path.join(self.stl_dir, f"{safe_name}_base.stl")
        stl_text = os.path.join(self.stl_dir, f"{safe_name}_text.stl")
        stl_combined = os.path.join(self.stl_dir, f"{safe_name}.stl")

        success_base = self.render_stl(scad_base, stl_base)
        success_text = self.render_stl(scad_text, stl_text)
        success_combined = self.render_stl(scad_combined, stl_combined)

        # Generate 3MF with colors in final directory
        threemf_file = os.path.join(self.final_dir, f"{safe_name}.3mf")
        success_3mf = False
        if success_base and success_text:
            print(f"  Creating 3MF with colors...")
            success_3mf = self.create_3mf(stl_base, stl_text, threemf_file, name)

        # Report results
        if success_base and success_text:
            print(f"  ✓ STL Base: output/stl/{safe_name}_base.stl")
            print(f"  ✓ STL Text: output/stl/{safe_name}_text.stl")
        if success_combined:
            print(f"  ✓ STL Combined: output/stl/{safe_name}.stl")
        if success_3mf:
            print(f"  ✓ 3MF (READY TO PRINT): output/final/{safe_name}.3mf")

        # Clean up temporary SCAD files (keep only the combined one)
        for f in [scad_base, scad_text]:
            if os.path.exists(f):
                os.remove(f)

        return {
            'name': name,
            'base_stl': stl_base if success_base else None,
            'text_stl': stl_text if success_text else None,
            'combined_stl': stl_combined if success_combined else None,
            'threemf': threemf_file if success_3mf else None,
            'scad': scad_combined,
            'width': plate_width
        }

    def generate_batch(self, names):
        """Generate nameplates for multiple names"""
        print(f"\n{'#'*60}")
        print(f"# NAMEPLATE BATCH GENERATOR")
        print(f"# Generating {len(names)} nameplate(s)")
        print(f"{'#'*60}")

        results = []
        for name in names:
            result = self.generate_nameplate(name)
            results.append(result)

        # Summary
        print(f"\n{'='*60}")
        print(f"GENERATION COMPLETE")
        print(f"{'='*60}")
        print(f"\nGenerated {len(results)} nameplate(s):")
        for r in results:
            print(f"  • {r['name']} ({r['width']}mm width)")

        print(f"\n{'='*60}")
        print(f"FILE ORGANIZATION")
        print(f"{'='*60}")
        print(f"\n📁 output/")
        print(f"  ├── final/        ← 3MF files (READY TO PRINT)")
        print(f"  ├── stl/          ← Individual STL parts")
        print(f"  └── scad/         ← OpenSCAD source files")

        print(f"\n{'='*60}")
        print(f"HOW TO USE IN BAMBU STUDIO")
        print(f"{'='*60}")

        print(f"\n🎯 RECOMMENDED: Use the 3MF files")
        print(f"  1. Go to output/final/")
        print(f"  2. Import the .3mf file for your nameplate")
        print(f"  3. Colors are pre-assigned (Light Blue base + Black text)")
        print(f"  4. Slice and print!")

        print(f"\nAlternative: Use separate STL files from output/stl/")
        print(f"  1. Import *_base.stl → Set to LIGHT BLUE")
        print(f"  2. Import *_text.stl → Set to BLACK")
        print(f"  3. They should align automatically")

        return results


def main():
    """Main entry point"""
    import sys

    generator = NameplateGenerator()

    # Check if names.txt exists
    names_file = "names.txt"

    if os.path.exists(names_file):
        print(f"Reading names from {names_file}...")
        with open(names_file, 'r') as f:
            names = [line.strip() for line in f if line.strip()]
    elif len(sys.argv) > 1:
        # Names provided as command line arguments
        names = sys.argv[1:]
    else:
        # Default names
        names = ["Hadi Jaffri", "Hussein Naqi"]
        print("No names.txt file found and no arguments provided.")
        print("Using default names. Create a names.txt file with one name per line to customize.")

    generator.generate_batch(names)

    print(f"\n{'='*60}")
    print(f"TIP: Create 'names.txt' with one name per line, then run:")
    print(f"     python3 generate_all_nameplates.py")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
