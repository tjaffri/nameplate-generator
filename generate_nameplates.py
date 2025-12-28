#!/usr/bin/env python3
"""
Generate Bambu Labs compatible 3MF files for nameplates with proper color assignments.
This script generates 3MF files that can be directly imported into Bambu Studio with
the base and text already assigned to different extruders (colors).
"""

import os
import subprocess
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from stl import mesh as stl_mesh
from datetime import datetime


class BambuNameplateGenerator:
    def __init__(self):
        # Dimensions optimized for 0.2mm layer height printing (25% smaller for bulk printing)
        self.base_height = 13.5  # mm
        self.base_thickness = 2.0  # mm
        self.text_height = 1.2  # mm
        self.corner_radius = 1.0  # mm
        self.pin_hole_diameter = 1.0  # mm
        self.pin_hole_from_edge = 2.0  # mm
        self.font_size = 9  # points
        self.min_width = 40  # minimum plate width
        self.margin = 7  # margin on each side of text

        # Output directories
        self.output_dir = "output"
        self.temp_dir = os.path.join(self.output_dir, "temp_generation")

        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.temp_dir, exist_ok=True)

    def calculate_text_width(self, text, font_size):
        """Estimate text width in mm based on character count"""
        # Use conservative estimate to prevent text overflow
        char_width = font_size * 0.7
        return len(text) * char_width

    def calculate_plate_width(self, name):
        """Calculate appropriate plate width for the given name"""
        text_width = self.calculate_text_width(name, self.font_size)
        plate_width = text_width + (2 * self.margin)

        if plate_width < self.min_width:
            plate_width = self.min_width

        # Round to nearest 5mm
        plate_width = round(plate_width / 5) * 5
        return plate_width

    def generate_scad_combined(self, name, output_file):
        """Generate OpenSCAD file with base and text MERGED as single solid"""
        plate_width = self.calculate_plate_width(name)

        scad_content = f"""// Combined nameplate for {name} - MERGED geometry
plate_width = {plate_width};
plate_height = {self.base_height};
plate_thickness = {self.base_thickness};
text_height = {self.text_height};
corner_radius = {self.corner_radius};
pin_hole_diameter = {self.pin_hole_diameter};
pin_hole_from_edge = {self.pin_hole_from_edge};
font_size = {self.font_size};

$fn = 64;  // High resolution

module rounded_rectangle(width, height, thickness, radius) {{
    linear_extrude(height = thickness)
        offset(r = radius)
            offset(r = -radius)
                square([width, height], center = true);
}}

module nameplate_base() {{
    difference() {{
        rounded_rectangle(plate_width, plate_height, plate_thickness, corner_radius);
        translate([plate_width/2 - pin_hole_from_edge, plate_height/2 - pin_hole_from_edge, 0])
            cylinder(h = plate_thickness + 1, r = pin_hole_diameter/2, center = true);
        translate([-plate_width/2 + pin_hole_from_edge, plate_height/2 - pin_hole_from_edge, 0])
            cylinder(h = plate_thickness + 1, r = pin_hole_diameter/2, center = true);
    }}
}}

module nameplate_text() {{
    translate([0, 0, plate_thickness])
        linear_extrude(height = text_height, convexity = 10)
            text("{name}", size = font_size, font = "Liberation Sans:style=Bold", halign = "center", valign = "center");
}}

// UNION base and text into ONE solid mesh - no floating regions!
union() {{
    nameplate_base();
    nameplate_text();
}}
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

    def create_bambu_3mf(self, combined_stl, output_3mf, name):
        """
        Create a Bambu Labs compatible 3MF file with merged mesh and painted regions.
        Uses single STL to avoid floating regions, with color painting by Z-height.
        """
        try:
            # Load the single merged STL
            mesh = stl_mesh.Mesh.from_file(combined_stl)

            # Create temporary 3MF structure
            temp_3mf_dir = os.path.join(self.temp_dir, "3mf_structure")
            if os.path.exists(temp_3mf_dir):
                import shutil
                shutil.rmtree(temp_3mf_dir)

            os.makedirs(temp_3mf_dir, exist_ok=True)
            model_dir = os.path.join(temp_3mf_dir, "3D")
            metadata_dir = os.path.join(temp_3mf_dir, "Metadata")
            os.makedirs(model_dir, exist_ok=True)
            os.makedirs(metadata_dir, exist_ok=True)

            # Create 3dmodel.model file with single mesh
            self._create_model_file(mesh, model_dir, name)

            # Create model_settings.config (this is where color assignment happens!)
            self._create_model_settings(metadata_dir, name)

            # Create [Content_Types].xml
            self._create_content_types(temp_3mf_dir)

            # Create _rels/.rels (required for 3MF to be recognized!)
            self._create_rels(temp_3mf_dir)

            # Create ZIP (3MF file)
            with zipfile.ZipFile(output_3mf, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(temp_3mf_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, temp_3mf_dir)
                        zipf.write(file_path, arcname)

            # Clean up
            import shutil
            shutil.rmtree(temp_3mf_dir)

            return True
        except Exception as e:
            print(f"  Error creating 3MF: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _create_model_file(self, mesh, model_dir, name):
        """Create the 3D/3dmodel.model file with single merged mesh"""
        model_root = ET.Element('model', {
            'unit': 'millimeter',
            'xml:lang': 'en-US',
            'xmlns': 'http://schemas.microsoft.com/3dmanufacturing/core/2015/02',
            'xmlns:BambuStudio': 'http://schemas.bambulab.com/package/2021'
        })

        # Add metadata
        metadata_items = [
            ('Application', 'BambuStudio-02.04.00.70'),
            ('BambuStudio:3mfVersion', '1'),
            ('CreationDate', datetime.now().strftime('%Y-%m-%d')),
            ('ModificationDate', datetime.now().strftime('%Y-%m-%d')),
            ('Title', name)
        ]

        for key, value in metadata_items:
            meta = ET.SubElement(model_root, 'metadata', {'name': key})
            meta.text = value

        resources = ET.SubElement(model_root, 'resources')

        # Single object with merged geometry
        obj = ET.SubElement(resources, 'object', {
            'id': '1',
            'type': 'model'
        })
        self._add_mesh_to_object(obj, mesh)

        # Build plate
        build = ET.SubElement(model_root, 'build')
        ET.SubElement(build, 'item', {
            'objectid': '1',
            'printable': '1'
        })

        # Write file
        tree = ET.ElementTree(model_root)
        ET.indent(tree, space=' ')
        model_file = os.path.join(model_dir, '3dmodel.model')
        tree.write(model_file, encoding='UTF-8', xml_declaration=True)

    def _add_mesh_to_object(self, obj_element, mesh):
        """Add mesh vertices and triangles to an object element"""
        mesh_elem = ET.SubElement(obj_element, 'mesh')
        vertices_elem = ET.SubElement(mesh_elem, 'vertices')
        triangles_elem = ET.SubElement(mesh_elem, 'triangles')

        vertex_idx = 0
        for triangle in mesh.vectors:
            for vertex in triangle:
                ET.SubElement(vertices_elem, 'vertex', {
                    'x': str(vertex[0]),
                    'y': str(vertex[1]),
                    'z': str(vertex[2])
                })
            ET.SubElement(triangles_elem, 'triangle', {
                'v1': str(vertex_idx),
                'v2': str(vertex_idx + 1),
                'v3': str(vertex_idx + 2)
            })
            vertex_idx += 3

    def _create_model_settings(self, metadata_dir, name):
        """
        Create model_settings.config with painted regions for multi-color.
        Single mesh with facets painted by Z-height.
        """
        config_root = ET.Element('config')

        # Object definition
        obj = ET.SubElement(config_root, 'object', {'id': '1'})
        ET.SubElement(obj, 'metadata', {
            'key': 'name',
            'value': f'{name}.3mf'
        })

        # Single part representing the whole model
        part = ET.SubElement(obj, 'part', {
            'id': '1',
            'subtype': 'normal_part'
        })
        ET.SubElement(part, 'metadata', {
            'key': 'name',
            'value': name
        })
        ET.SubElement(part, 'metadata', {
            'key': 'matrix',
            'value': '1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1'
        })

        # Paint metadata - assign regions by height to different extruders
        # Base region (0 to base_thickness) -> extruder 1
        paint1 = ET.SubElement(part, 'paint')
        ET.SubElement(paint1, 'metadata', {
            'key': 'extruder',
            'value': '1'
        })
        ET.SubElement(paint1, 'metadata', {
            'key': 'height_range_low',
            'value': '0'
        })
        ET.SubElement(paint1, 'metadata', {
            'key': 'height_range_high',
            'value': str(self.base_thickness)
        })

        # Text region (base_thickness to base_thickness + text_height) -> extruder 2
        paint2 = ET.SubElement(part, 'paint')
        ET.SubElement(paint2, 'metadata', {
            'key': 'extruder',
            'value': '2'
        })
        ET.SubElement(paint2, 'metadata', {
            'key': 'height_range_low',
            'value': str(self.base_thickness)
        })
        ET.SubElement(paint2, 'metadata', {
            'key': 'height_range_high',
            'value': str(self.base_thickness + self.text_height)
        })

        # Plate info
        plate = ET.SubElement(config_root, 'plate')
        ET.SubElement(plate, 'metadata', {
            'key': 'plater_id',
            'value': '1'
        })

        # Model instance
        model_inst = ET.SubElement(plate, 'model_instance')
        ET.SubElement(model_inst, 'metadata', {
            'key': 'object_id',
            'value': '1'
        })
        ET.SubElement(model_inst, 'metadata', {
            'key': 'instance_id',
            'value': '0'
        })

        # Assemble section
        assemble = ET.SubElement(config_root, 'assemble')
        ET.SubElement(assemble, 'assemble_item', {
            'object_id': '1',
            'instance_id': '0',
            'transform': '1 0 0 0 1 0 0 0 1 0 0 0',
            'offset': '0 0 0'
        })

        # Write file
        tree = ET.ElementTree(config_root)
        ET.indent(tree, space=' ')
        config_file = os.path.join(metadata_dir, 'model_settings.config')
        tree.write(config_file, encoding='UTF-8', xml_declaration=True)

    def _create_content_types(self, temp_3mf_dir):
        """Create [Content_Types].xml"""
        types_root = ET.Element('Types', {
            'xmlns': 'http://schemas.openxmlformats.org/package/2006/content-types'
        })

        ET.SubElement(types_root, 'Default', {
            'Extension': 'rels',
            'ContentType': 'application/vnd.openxmlformats-package.relationships+xml'
        })
        ET.SubElement(types_root, 'Default', {
            'Extension': 'model',
            'ContentType': 'application/vnd.ms-package.3dmanufacturing-3dmodel+xml'
        })

        tree = ET.ElementTree(types_root)
        ET.indent(tree, space=' ')
        tree.write(
            os.path.join(temp_3mf_dir, '[Content_Types].xml'),
            encoding='UTF-8',
            xml_declaration=True
        )

    def _create_rels(self, temp_3mf_dir):
        """Create _rels/.rels file (required for 3MF validation)"""
        rels_dir = os.path.join(temp_3mf_dir, '_rels')
        os.makedirs(rels_dir, exist_ok=True)

        rels_root = ET.Element('Relationships', {
            'xmlns': 'http://schemas.openxmlformats.org/package/2006/relationships'
        })

        ET.SubElement(rels_root, 'Relationship', {
            'Target': '/3D/3dmodel.model',
            'Id': 'rel0',
            'Type': 'http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel'
        })

        tree = ET.ElementTree(rels_root)
        ET.indent(tree, space=' ')
        tree.write(
            os.path.join(rels_dir, '.rels'),
            encoding='UTF-8',
            xml_declaration=True
        )

    def generate_nameplate(self, name):
        """Generate a complete nameplate 3MF file ready for Bambu Studio"""
        safe_name = name.replace(" ", "_").replace("/", "_")

        print(f"\n{'='*60}")
        print(f"Generating: {name}")
        print(f"{'='*60}")

        # File paths
        scad_file = os.path.join(self.temp_dir, f"{safe_name}.scad")
        stl_file = os.path.join(self.output_dir, f"{safe_name}.stl")

        # Calculate dimensions
        plate_width = self.calculate_plate_width(name)
        print(f"  Plate dimensions: {plate_width}mm x {self.base_height}mm")

        # Generate single merged SCAD file
        print(f"  Generating OpenSCAD file...")
        self.generate_scad_combined(name, scad_file)

        # Render to STL - single solid piece
        print(f"  Rendering to STL...")
        if not self.render_stl(scad_file, stl_file):
            print(f"  Failed to render STL")
            return False

        print(f"  ✓ Success! Created: {safe_name}.stl")
        print(f"    Single solid piece - no floating regions, all letters complete")

        return True

    def generate_batch(self, names):
        """Generate nameplates for multiple names"""
        print(f"\n{'#'*60}")
        print(f"# BAMBU LABS NAMEPLATE GENERATOR")
        print(f"# Generating {len(names)} nameplate(s)")
        print(f"# Single-color STL files - no floating regions!")
        print(f"{'#'*60}")

        results = []
        for name in names:
            success = self.generate_nameplate(name)
            results.append({'name': name, 'success': success})

        # Summary
        print(f"\n{'='*60}")
        print(f"GENERATION COMPLETE")
        print(f"{'='*60}")

        successful = [r for r in results if r['success']]
        failed = [r for r in results if not r['success']]

        if successful:
            print(f"\nSuccessfully generated {len(successful)} nameplate(s):")
            for r in successful:
                print(f"  - {r['name']}.stl")

        if failed:
            print(f"\nFailed to generate {len(failed)} nameplate(s):")
            for r in failed:
                print(f"  - {r['name']}")

        print(f"\n{'='*60}")
        print(f"READY TO PRINT!")
        print(f"{'='*60}")
        print(f"\nYour STL files are in the output/ directory.")
        print(f"Import them into Bambu Studio and slice!")
        print(f"\nSingle-color solid pieces - no floating regions, all letters complete!")

        return results


def main():
    """Main entry point"""
    import sys

    generator = BambuNameplateGenerator()

    # Read names from file
    names_file = "names.txt"

    if os.path.exists(names_file):
        print(f"Reading names from {names_file}...")
        with open(names_file, 'r') as f:
            names = [line.strip() for line in f if line.strip()]
    elif len(sys.argv) > 1:
        names = sys.argv[1:]
    else:
        names = ["Hadi Jaffri", "Hussein Naqi"]
        print("No names.txt file found. Using default names.")

    generator.generate_batch(names)


if __name__ == "__main__":
    main()
