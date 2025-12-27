#!/usr/bin/env python3
"""
Automated nameplate generator for multiple names
Generates properly sized nameplates - colors assigned manually in slicer
"""

import os
import subprocess
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

        # Output directories
        self.output_dir = "output"
        self.stl_dir = self.output_dir
        self.scad_dir = os.path.join(self.output_dir, "temp_scad")

        # Create directories if they don't exist
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

    def create_3mf_with_separate_objects(self, base_stl, text_stl, output_3mf, name):
        """Create 3MF with base and text as separate objects (not merged)"""
        try:
            import zipfile
            import xml.etree.ElementTree as ET
            from stl import mesh as stl_mesh

            # Load STL files
            base_mesh = stl_mesh.Mesh.from_file(base_stl)
            text_mesh = stl_mesh.Mesh.from_file(text_stl)

            # Create 3MF structure
            temp_dir = os.path.join(self.scad_dir, "temp_3mf")
            os.makedirs(temp_dir, exist_ok=True)
            model_dir = os.path.join(temp_dir, "3D")
            os.makedirs(model_dir, exist_ok=True)

            # Create XML structure
            model_root = ET.Element('model', {
                'unit': 'millimeter',
                'xml:lang': 'en-US',
                'xmlns': 'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'
            })

            resources = ET.SubElement(model_root, 'resources')
            build = ET.SubElement(model_root, 'build')

            # Add base object
            base_obj = ET.SubElement(resources, 'object', {
                'id': '1',
                'type': 'model',
                'name': f'{name} - Base'
            })
            base_mesh_elem = ET.SubElement(base_obj, 'mesh')
            base_vertices = ET.SubElement(base_mesh_elem, 'vertices')
            base_triangles = ET.SubElement(base_mesh_elem, 'triangles')

            # Add base vertices and triangles
            vertex_idx = 0
            for triangle in base_mesh.vectors:
                for vertex in triangle:
                    ET.SubElement(base_vertices, 'vertex', {
                        'x': str(vertex[0]),
                        'y': str(vertex[1]),
                        'z': str(vertex[2])
                    })
                ET.SubElement(base_triangles, 'triangle', {
                    'v1': str(vertex_idx),
                    'v2': str(vertex_idx + 1),
                    'v3': str(vertex_idx + 2)
                })
                vertex_idx += 3

            # Add text object
            text_obj = ET.SubElement(resources, 'object', {
                'id': '2',
                'type': 'model',
                'name': f'{name} - Text'
            })
            text_mesh_elem = ET.SubElement(text_obj, 'mesh')
            text_vertices = ET.SubElement(text_mesh_elem, 'vertices')
            text_triangles = ET.SubElement(text_mesh_elem, 'triangles')

            # Add text vertices and triangles (offset Z by base thickness)
            vertex_idx = 0
            for triangle in text_mesh.vectors:
                for vertex in triangle:
                    ET.SubElement(text_vertices, 'vertex', {
                        'x': str(vertex[0]),
                        'y': str(vertex[1]),
                        'z': str(vertex[2] + self.base_thickness)  # Offset text on top of base
                    })
                ET.SubElement(text_triangles, 'triangle', {
                    'v1': str(vertex_idx),
                    'v2': str(vertex_idx + 1),
                    'v3': str(vertex_idx + 2)
                })
                vertex_idx += 3

            # Add both objects to build plate
            ET.SubElement(build, 'item', {'objectid': '1'})
            ET.SubElement(build, 'item', {'objectid': '2'})

            # Write model file
            tree = ET.ElementTree(model_root)
            ET.indent(tree, space='  ')
            model_file = os.path.join(model_dir, '3dmodel.model')
            tree.write(model_file, encoding='UTF-8', xml_declaration=True)

            # Create [Content_Types].xml
            content_types = ET.Element('Types', {
                'xmlns': 'http://schemas.openxmlformats.org/package/2006/content-types'
            })
            ET.SubElement(content_types, 'Default', {
                'Extension': 'rels',
                'ContentType': 'application/vnd.openxmlformats-package.relationships+xml'
            })
            ET.SubElement(content_types, 'Default', {
                'Extension': 'model',
                'ContentType': 'application/vnd.ms-package.3dmanufacturing-3dmodel+xml'
            })
            content_tree = ET.ElementTree(content_types)
            ET.indent(content_tree, space='  ')
            content_tree.write(
                os.path.join(temp_dir, '[Content_Types].xml'),
                encoding='UTF-8',
                xml_declaration=True
            )

            # Create _rels/.rels
            rels_dir = os.path.join(temp_dir, '_rels')
            os.makedirs(rels_dir, exist_ok=True)
            rels = ET.Element('Relationships', {
                'xmlns': 'http://schemas.openxmlformats.org/package/2006/relationships'
            })
            ET.SubElement(rels, 'Relationship', {
                'Target': '/3D/3dmodel.model',
                'Id': 'rel0',
                'Type': 'http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel'
            })
            rels_tree = ET.ElementTree(rels)
            ET.indent(rels_tree, space='  ')
            rels_tree.write(
                os.path.join(rels_dir, '.rels'),
                encoding='UTF-8',
                xml_declaration=True
            )

            # Create ZIP (3MF file)
            with zipfile.ZipFile(output_3mf, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, temp_dir)
                        zipf.write(file_path, arcname)

            # Clean up
            import shutil
            shutil.rmtree(temp_dir)

            return True
        except Exception as e:
            print(f"  Warning: Could not create 3MF: {e}")
            import traceback
            traceback.print_exc()
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

        # Generate SCAD files in temp directory
        print(f"  Generating OpenSCAD files...")
        scad_base = os.path.join(self.scad_dir, f"{safe_name}_base.scad")
        scad_text = os.path.join(self.scad_dir, f"{safe_name}_text.scad")

        self.generate_scad_base_only(name, scad_base)
        self.generate_scad_text_only(name, scad_text)

        # Render to STL in temp directory
        print(f"  Rendering STL files...")
        stl_base = os.path.join(self.scad_dir, f"{safe_name}_base.stl")
        stl_text = os.path.join(self.scad_dir, f"{safe_name}_text.stl")

        success_base = self.render_stl(scad_base, stl_base)
        success_text = self.render_stl(scad_text, stl_text)

        # Create 3MF with separate objects
        threemf_file = os.path.join(self.stl_dir, f"{safe_name}.3mf")
        success_3mf = False
        if success_base and success_text:
            print(f"  Creating 3MF...")
            success_3mf = self.create_3mf_with_separate_objects(stl_base, stl_text, threemf_file, name)

        # Report result
        if success_3mf:
            print(f"  ✓ {safe_name}.3mf (base + text as separate objects)")
        else:
            print(f"  ✗ Failed to generate 3MF for {safe_name}")

        return {
            'name': name,
            'threemf': threemf_file if success_3mf else None,
            'width': plate_width,
            'success': success_3mf
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

        successful = [r for r in results if r['success']]
        failed = [r for r in results if not r['success']]

        print(f"\n✓ Successfully generated {len(successful)} nameplate(s):")
        for r in successful:
            print(f"  • {r['name']} ({r['width']}mm width)")

        if failed:
            print(f"\n✗ Failed to generate {len(failed)} nameplate(s):")
            for r in failed:
                print(f"  • {r['name']}")

        print(f"\n{'='*60}")
        print(f"FILES READY")
        print(f"{'='*60}")
        print(f"\n📁 output/ contains all your nameplate STL files")
        print(f"   Bulk import them into Bambu Studio!")

        print(f"\n📖 See README.md for instructions on bulk importing")
        print(f"   and setting up height range modifier in Bambu Studio")

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
