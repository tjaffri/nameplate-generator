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
        # Default dimensions (reduced to ~50% for smaller nameplates)
        self.base_height = 11  # mm
        self.base_thickness = 1.25  # mm
        self.text_height = 0.6  # mm (raised above base)
        self.corner_radius = 1  # mm
        self.pin_hole_diameter = 1.0  # mm
        self.pin_hole_from_edge = 2  # mm
        self.font_size = 5  # points
        self.min_width = 30  # minimum plate width
        self.margin = 5  # margin on each side of text (increased for safety)

        # Output directories
        self.output_dir = "output"
        self.temp_dir = os.path.join(self.output_dir, "temp_generation")

        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.temp_dir, exist_ok=True)

    def calculate_text_width(self, text, font_size):
        """Estimate text width in mm based on character count"""
        # Use more conservative estimate (0.75 instead of 0.6) to prevent overflow
        char_width = font_size * 0.75
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

    def generate_scad_base(self, name, output_file):
        """Generate OpenSCAD file for base only"""
        plate_width = self.calculate_plate_width(name)

        scad_content = f"""// Base plate for {name}
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

    def generate_scad_text(self, name, output_file):
        """Generate OpenSCAD file for text only"""
        scad_content = f"""// Text for {name}
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

    def create_bambu_3mf(self, base_stl, text_stl, output_3mf, name):
        """
        Create a Bambu Labs compatible 3MF file with proper color assignments.
        Base is assigned to extruder 1, text to extruder 2.
        """
        try:
            # Load STL files
            base_mesh = stl_mesh.Mesh.from_file(base_stl)
            text_mesh = stl_mesh.Mesh.from_file(text_stl)

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

            # Create 3dmodel.model file
            self._create_model_file(base_mesh, text_mesh, model_dir, name)

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

    def _create_model_file(self, base_mesh, text_mesh, model_dir, name):
        """Create the 3D/3dmodel.model file with base and text as separate objects"""
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

        # Object 1: Base mesh
        base_obj = ET.SubElement(resources, 'object', {
            'id': '1',
            'type': 'model'
        })
        self._add_mesh_to_object(base_obj, base_mesh)

        # Object 2: Text mesh
        text_obj = ET.SubElement(resources, 'object', {
            'id': '2',
            'type': 'model'
        })
        self._add_mesh_to_object(text_obj, text_mesh)

        # Object 3: Component combining base and text
        component_obj = ET.SubElement(resources, 'object', {
            'id': '3',
            'type': 'model'
        })
        components = ET.SubElement(component_obj, 'components')

        # Add base component (no transform)
        ET.SubElement(components, 'component', {
            'objectid': '1',
            'transform': '1 0 0 0 1 0 0 0 1 0 0 0'
        })

        # Add text component (no transform - already positioned correctly in STL)
        ET.SubElement(components, 'component', {
            'objectid': '2',
            'transform': '1 0 0 0 1 0 0 0 1 0 0 0'
        })

        # Build plate (identity transform matrix - required for proper import)
        build = ET.SubElement(model_root, 'build')
        ET.SubElement(build, 'item', {
            'objectid': '3',
            'transform': '1 0 0 0 0 1 0 0 0 0 1 0',
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
        Create the model_settings.config file.
        This is THE KEY FILE for color assignment in Bambu Studio!
        """
        config_root = ET.Element('config')

        # Object definition (id 3 is the component object)
        obj = ET.SubElement(config_root, 'object', {'id': '3'})

        # Base object metadata
        ET.SubElement(obj, 'metadata', {
            'key': 'name',
            'value': f'{name}.3mf'
        })
        ET.SubElement(obj, 'metadata', {
            'key': 'extruder',
            'value': '1'
        })

        # Part 1: Base - assigned to extruder 1
        part1 = ET.SubElement(obj, 'part', {
            'id': '1',
            'subtype': 'normal_part'
        })
        ET.SubElement(part1, 'metadata', {
            'key': 'name',
            'value': f'{name} - Base'
        })
        ET.SubElement(part1, 'metadata', {
            'key': 'extruder',
            'value': '1'  # First color
        })
        ET.SubElement(part1, 'metadata', {
            'key': 'matrix',
            'value': '1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1'
        })
        ET.SubElement(part1, 'metadata', {
            'key': 'source_object_id',
            'value': '1'
        })

        # Part 2: Text - assigned to extruder 2
        part2 = ET.SubElement(obj, 'part', {
            'id': '2',
            'subtype': 'normal_part'
        })
        ET.SubElement(part2, 'metadata', {
            'key': 'name',
            'value': f'{name} - Text'
        })
        ET.SubElement(part2, 'metadata', {
            'key': 'extruder',
            'value': '2'  # Second color - THIS IS THE KEY!
        })
        ET.SubElement(part2, 'metadata', {
            'key': 'matrix',
            'value': '1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1'
        })
        ET.SubElement(part2, 'metadata', {
            'key': 'source_object_id',
            'value': '2'
        })

        # Add text_info for the text part
        text_info = ET.SubElement(part2, 'text_info', {
            'text': name,
            'font_name': 'Arial',
            'style_name': 'Bold',
            'boldness': '109',
            'font_size': str(self.font_size),
            'thickness': str(self.text_height),
            'bold': '1',
            'italic': '0'
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
            'value': '3'
        })
        ET.SubElement(model_inst, 'metadata', {
            'key': 'instance_id',
            'value': '0'
        })

        # Assemble section
        assemble = ET.SubElement(config_root, 'assemble')
        ET.SubElement(assemble, 'assemble_item', {
            'object_id': '3',
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
        scad_base = os.path.join(self.temp_dir, f"{safe_name}_base.scad")
        scad_text = os.path.join(self.temp_dir, f"{safe_name}_text.scad")
        stl_base = os.path.join(self.temp_dir, f"{safe_name}_base.stl")
        stl_text = os.path.join(self.temp_dir, f"{safe_name}_text.stl")
        output_3mf = os.path.join(self.output_dir, f"{name}.3mf")

        # Calculate dimensions
        plate_width = self.calculate_plate_width(name)
        print(f"  Plate dimensions: {plate_width}mm x {self.base_height}mm")

        # Generate SCAD files
        print(f"  Generating OpenSCAD files...")
        self.generate_scad_base(name, scad_base)
        self.generate_scad_text(name, scad_text)

        # Render STL files
        print(f"  Rendering base STL...")
        if not self.render_stl(scad_base, stl_base):
            print(f"  Failed to render base")
            return False

        print(f"  Rendering text STL...")
        if not self.render_stl(scad_text, stl_text):
            print(f"  Failed to render text")
            return False

        # Create 3MF
        print(f"  Creating Bambu Labs 3MF with color assignments...")
        if not self.create_bambu_3mf(stl_base, stl_text, output_3mf, name):
            print(f"  Failed to create 3MF")
            return False

        print(f"  Success! Created: {name}.3mf")
        print(f"  - Base assigned to Color 1 (extruder 1)")
        print(f"  - Text assigned to Color 2 (extruder 2)")

        return True

    def generate_batch(self, names):
        """Generate nameplates for multiple names"""
        print(f"\n{'#'*60}")
        print(f"# BAMBU LABS NAMEPLATE GENERATOR")
        print(f"# Generating {len(names)} nameplate(s)")
        print(f"# With automatic color assignments!")
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
                print(f"  - {r['name']}.3mf")

        if failed:
            print(f"\nFailed to generate {len(failed)} nameplate(s):")
            for r in failed:
                print(f"  - {r['name']}")

        print(f"\n{'='*60}")
        print(f"READY TO PRINT!")
        print(f"{'='*60}")
        print(f"\nYour 3MF files are in the output/ directory.")
        print(f"Just import them directly into Bambu Studio - colors are already assigned!")
        print(f"\nNo manual setup needed - just load and print!")

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
