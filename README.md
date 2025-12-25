# Automated Nameplate Generator

Generate 3D printable chest badge nameplates for any list of names!

## Quick Start - Batch Workflow

### 🚀 For Each Nameplate (20 seconds):

1. **Open Bambu Studio**

2. **Import the base plate:**
   - Drag `output/stl/hadi_jaffri_base.stl` onto the build plate
   - In the right panel, assign **Light Blue** filament (or your preferred base color)

3. **Import the text:**
   - Drag `output/stl/hadi_jaffri_text.stl` onto the build plate
   - In the right panel, assign **Black** filament (or your preferred text color)
   - The text should automatically align on top of the base

4. **Verify alignment:**
   - Both objects should be perfectly aligned at the same X/Y position
   - The text sits on top of the base (Z = 2.5mm)
   - Use the preview to verify colors look correct

5. **Slice and print!**
   - Click "Slice Plate"
   - The printer will automatically change filament at the correct layer

**Time for 20 nameplates: ~7 minutes total** (20 sec × 20 nameplates)

### ➕ Generate nameplates for new names:

1. Edit `names.txt` and add names (one per line):
   ```
   Hadi Jaffri
   Hussein Naqi
   Ali Ahmed
   Sara Khan
   ```

2. Run the generator:
   ```bash
   source venv/bin/activate && python generate_all_nameplates.py
   ```

3. Find your 3MF files in `output/final/`

## Directory Structure

```
3dclass/
├── generate_all_nameplates.py    ← Main script
├── names.txt                     ← List of names (edit this!)
├── README.md                     ← This file
├── .gitignore                    ← Keeps output/ out of git
└── output/                       ← Generated files (not in git)
    ├── final/                    ← 🎯 3MF files - READY TO PRINT
    │   ├── hadi_jaffri.3mf
    │   └── hussein_naqi.3mf
    ├── stl/                      ← Individual STL parts
    │   ├── *_base.stl
    │   ├── *_text.stl
    │   └── *.stl (combined)
    └── scad/                     ← OpenSCAD source (for customization)
        └── *.scad
```

## Features

- **Automatic sizing** - Base plate width adjusts to fit any name
- **Color support** - 3MF files include light blue base & black text
- **Proper 3D text** - Real letter shapes, not blocks
- **Pin holes** - For badge attachment
- **Batch generation** - Process multiple names at once
- **Organized output** - Interim and final files separated
- **Git-friendly** - Generated files excluded via .gitignore

## Specifications

- **Height:** 22mm (fixed)
- **Width:** Auto-calculated per name (e.g., 80mm for "Hadi Jaffri", 90mm for "Hussein Naqi")
- **Base thickness:** 2.5mm
- **Text height:** 1.2mm raised above base
- **Colors:** Light Blue (#87CEEB) base, Black (#000000) text
- **Pin holes:** 1.5mm diameter, 4mm from corners

## Print Settings (Bambu A1)

- **Layer height:** 0.2mm
- **Infill:** 15-20%
- **Supports:** None needed
- **Brim:** Optional (helps adhesion)
- **Filament changes:** Automatic at layer transition

## Using the Files

### Option 1: Separate STL Files (RECOMMENDED) 🎯

**Best method for Bambu Studio:**

```bash
# Files are in output/stl/
output/stl/hadi_jaffri_base.stl      # → Set to LIGHT BLUE
output/stl/hadi_jaffri_text.stl      # → Set to BLACK
```

1. Import **both files** into Bambu Studio
2. Assign **Light Blue** to the base part
3. Assign **Black** to the text part
4. They will automatically align correctly
5. Slice and print!

### Option 2: Combined STL File

**For single-color prints or manual setup:**

```bash
# Files are in output/stl/
output/stl/hadi_jaffri.stl      # Combined base + text
```

1. Import the combined STL file
2. Use Bambu Studio's paint tool to color different regions
3. Or print in a single color

### Option 3: 3MF Files (Experimental)

**May not work in all versions of Bambu Studio:**

```bash
# Files are in output/final/
output/final/hadi_jaffri.3mf
output/final/hussein_naqi.3mf
```

Note: 3MF color support varies by Bambu Studio version. Use Option 1 if colors don't import correctly.

### Option 4: OpenSCAD Source

**For customization:**

```bash
# Files are in output/scad/
output/scad/hadi_jaffri.scad
```

1. Open in OpenSCAD
2. Edit parameters as needed
3. Render (F6) and export to STL

## Customization

Want to change colors, sizes, or fonts? Edit `generate_all_nameplates.py`:

```python
class NameplateGenerator:
    def __init__(self):
        self.base_height = 22        # Plate height in mm
        self.base_thickness = 2.5    # Base depth
        self.text_height = 1.2       # Text raise height
        self.font_size = 10          # Font size
        self.margin = 8              # Space around text
        self.base_color = "#87CEEB"  # Light blue (change hex code)
        self.text_color = "#000000"  # Black (change hex code)
```

Then regenerate:
```bash
source venv/bin/activate && python generate_all_nameplates.py
```

## Command Line Usage

```bash
# Use names.txt (one name per line)
source venv/bin/activate && python generate_all_nameplates.py

# Or pass names directly as arguments
source venv/bin/activate && python generate_all_nameplates.py "John Doe" "Jane Smith" "Alice Brown"
```

## Troubleshooting

**Text wider than base?**
- The script automatically calculates width
- If still issues, decrease `font_size` in `generate_all_nameplates.py`

**Colors not showing in Bambu Studio?**
- Use separate STL files: import both `*_base.stl` and `*_text.stl` from `output/stl/`
- Assign colors to each part individually in the right panel
- The `.3mf` files may not work in all Bambu Studio versions

**OpenSCAD not found?**
- Install with: `brew install --cask openscad`
- Or download from: https://openscad.org/

**Want to regenerate everything?**
```bash
rm -rf output/
source venv/bin/activate && python generate_all_nameplates.py
```

## Git Integration

The `.gitignore` file excludes `output/` directory, so generated files won't be committed to git. This keeps your repository clean while allowing you to regenerate files anytime.

Only these files are tracked in git:
- `generate_all_nameplates.py` (the generator script)
- `names.txt` (your list of names)
- `README.md` (this documentation)
- `.gitignore` (git configuration)

## Tips

- **Pin attachment:** Use small safety pins through the corner holes
- **First layer:** Clean your print bed well for best adhesion
- **Filament:** PLA works great, PETG/ABS also work
- **Batch printing:** You can print multiple nameplates at once
- **Name length:** Very long names automatically get wider plates
- **Font:** Using Arial Bold by default, editable in .scad files
