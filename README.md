# Automated Nameplate Generator

Generate 3D printable chest badge nameplates for any list of names!

## Quick Start - Batch Workflow

### 🚀 One-Time Setup (30 seconds):

1. **Open Bambu Studio**

2. **Import any nameplate:**
   - Drag `output/stl/hadi_jaffri.stl` onto the build plate

3. **Add Height Range Modifier:**
   - Right-click the object → **Add Modifier** → **Height Range**

4. **Configure colors:**
   - Click the modifier in the list
   - Set **Range 1:** 0mm to 2.5mm → Select **Light Blue** filament slot
   - Set **Range 2:** 2.5mm to 10mm → Select **Black** filament slot
   - The preview should now show blue base + black text ✨

5. **Save as preset:**
   - Right-click the object → **Save settings as preset**
   - Name it: `Nameplate Multi-Color`

### ⚡ For Each Additional Nameplate (10 seconds):

1. **Import STL:** Drag `nameplate.stl` onto build plate
2. **Apply preset:** Right-click object → **Load settings preset** → `Nameplate Multi-Color`
3. **Done!** Colors applied instantly

**Time for 20 nameplates: ~3.5 minutes total** (30 sec setup + 10 sec × 20)

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

### Option 1: 3MF Files (RECOMMENDED) 🎯

**Easiest method - Colors already set!**

```bash
# Files are in output/final/
output/final/hadi_jaffri.3mf
output/final/hussein_naqi.3mf
```

1. Import the .3mf file into Bambu Studio
2. Colors are pre-assigned (no manual setup needed)
3. Slice and print!

### Option 2: Separate STL Files

**For manual color assignment or other slicers:**

```bash
# Files are in output/stl/
output/stl/hadi_jaffri_base.stl      # → Set to LIGHT BLUE
output/stl/hadi_jaffri_text.stl      # → Set to BLACK
```

1. Import both files into your slicer
2. Manually assign colors
3. They should align automatically

### Option 3: OpenSCAD Source

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
- Make sure you're importing `.3mf` files from `output/final/`
- STL files don't include color info (use Option 2 above)

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
