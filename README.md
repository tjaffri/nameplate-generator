# Automated Nameplate Generator

Generate 3D printable chest badge nameplates for any list of names!

## Quick Start - Batch Workflow

### 🚀 One-Time Setup (2 minutes):

1. **Open Bambu Studio** and load two filament slots:
   - **Slot 1:** Light Blue
   - **Slot 2:** Black

2. **Import any nameplate:**
   - Drag `output/stl/hadi_jaffri.stl` (the combined file) onto the build plate
   - Assign it to **Filament Slot 1** (Light Blue)

3. **Slice the object:**
   - Click **Slice Plate** button

4. **Add filament change in preview:**
   - Look at the **layer slider** on the right side of the preview
   - Move the slider to **layer 13** (2.5mm height with 0.2mm layers)
   - **Click the "+" button** next to the layer slider at layer 13
   - Select **Change Filament** → Choose **Slot 2** (Black)
   - The preview should now show blue base + black text

5. **Save as project:**
   - File → **Save Project As** → Name it: `nameplate_template.3mf`
   - This saves the filament change setting

### ⚡ For Each Additional Nameplate:

**Option A - One at a time (most reliable):**
1. Delete the current object from the plate
2. Import new nameplate STL
3. File → Open Project → `nameplate_template.3mf` to copy settings
4. Replace the object and slice

**Option B - Manual setup (if batch):**
1. Import all nameplates at once
2. Slice the plate
3. For each object, manually add filament change at layer 13

**Option C - Using Paint Tool:**
1. Import all nameplates at once (assign all to Light Blue by default)
2. Click **Paint** tool in the left toolbar
3. Select **Black** filament in the paint tool
4. Click on the text surfaces to paint them black
5. Use **Smart Fill** or **Bucket Fill** if available to paint all connected text surfaces
6. Repeat for each nameplate
7. Slice and print!

**Note:** The Paint tool requires manually painting each nameplate but can be faster than the layer slider method.

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

3. Find your STL files in `output/stl/` (bulk import the `*.stl` combined files)

## Directory Structure

```
3dclass/
├── generate_all_nameplates.py    ← Main script
├── names.txt                     ← List of names (edit this!)
├── README.md                     ← This file
├── .gitignore                    ← Keeps output/ out of git
└── output/                       ← Generated files (not in git)
    ├── stl/                      ← 🎯 STL files - USE THESE
    │   ├── *.stl                 ← Combined files (bulk import these!)
    │   ├── *_base.stl            ← Separate base (optional)
    │   └── *_text.stl            ← Separate text (optional)
    ├── scad/                     ← OpenSCAD source (for customization)
    │   └── *.scad
    └── final/                    ← 3MF files (experimental)
        └── *.3mf
```

## Features

- **Automatic sizing** - Base plate width adjusts to fit any name
- **Multi-color support** - Separate base and text STL files for easy color assignment
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
- **Colors:** Assign in slicer (suggested: Light Blue base, Black text)
- **Pin holes:** 1.5mm diameter, 4mm from corners

## Print Settings (Bambu A1)

- **Layer height:** 0.2mm
- **Infill:** 15-20%
- **Supports:** None needed
- **Brim:** Optional (helps adhesion)
- **Filament changes:** Automatic at layer transition

## Using the Files

### Option 1: Combined STL Files (RECOMMENDED) 🎯

**Best for bulk importing multiple nameplates:**

```bash
# Files are in output/stl/
output/stl/hadi_jaffri.stl           # Complete nameplate
output/stl/hussein_naqi.stl          # Complete nameplate
```

1. Import STL file(s) into Bambu Studio
2. Add **Change Filament** at layer **13** (for 0.2mm layers)
3. Save as preset and apply to all nameplates
4. See "Quick Start" above for detailed workflow

### Option 2: Separate STL Files

**For advanced customization:**

```bash
# Files are in output/stl/
output/stl/hadi_jaffri_base.stl      # Base plate only
output/stl/hadi_jaffri_text.stl      # Text only
```

1. Import both files separately
2. Assign different colors to each
3. They will automatically align correctly

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

Want to change sizes or fonts? Edit `generate_all_nameplates.py`:

```python
class NameplateGenerator:
    def __init__(self):
        self.base_height = 22        # Plate height in mm
        self.base_thickness = 2.5    # Base depth
        self.text_height = 1.2       # Text raise height
        self.font_size = 10          # Font size
        self.margin = 8              # Space around text
```

Colors are assigned in Bambu Studio when importing the STL files.

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
