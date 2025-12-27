# Automated Nameplate Generator

Generate 3D printable chest badge nameplates for any list of names!

## Quick Start

### 1. Generate Nameplates

Edit `names.txt` and add names (one per line):
```
Hadi Jaffri
Hussein Naqi
Ali Ahmed
Sara Khan
```

Run the generator:
```bash
source venv/bin/activate && python generate_all_nameplates.py
```

This creates TWO files per nameplate in `output/`:
- `name_base.stl` (base plate - Light Blue)
- `name_text.stl` (raised text - Black)

### 2. Bulk Import into Bambu Studio

1. **Open Bambu Studio**

2. **Bulk import all BASE files:**
   - Select ALL `*_base.stl` files from `output/` folder
   - Drag them onto the build plate at once
   - Select all imported objects (Ctrl+A or Cmd+A)
   - In the right panel, assign **Light Blue** filament to all

3. **Bulk import all TEXT files:**
   - Select ALL `*_text.stl` files from `output/` folder
   - Drag them onto the build plate at once
   - Select all imported text objects (Ctrl+A or Cmd+A)
   - In the right panel, assign **Black** filament to all
   - Text automatically aligns on top of bases

4. **Slice and print!**
   - All nameplates now have proper colors
   - Printer will automatically change filament at layer transition

---

## How It Works

- **Base files:** Flat plates 2.5mm thick (Light Blue)
- **Text files:** Raised letters 1.2mm tall (Black)
- **Automatic alignment:** Text positions perfectly on base at Z=2.5mm
- **Automatic sizing:** Each nameplate width adjusts to fit the name

---

## Specifications

- **Height:** 22mm total (2.5mm base + space for text)
- **Width:** Auto-calculated per name
- **Base thickness:** 2.5mm
- **Text height:** 1.2mm raised above base
- **Pin holes:** 1.5mm diameter, 4mm from corners (for badge attachment)

---

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

Then regenerate:
```bash
source venv/bin/activate && python generate_all_nameplates.py
```

---

## Troubleshooting

**Text and base not aligning?**
- They should align automatically - both are positioned at (0,0)
- If not aligned, select base + text, right-click → **Align** → **Center**

**OpenSCAD not found?**
- Install with: `brew install --cask openscad`
- Or download from: https://openscad.org/

**Want to regenerate everything?**
```bash
rm -rf output/
source venv/bin/activate && python generate_all_nameplates.py
```

---

## Print Settings (Bambu A1)

- **Layer height:** 0.2mm
- **Infill:** 15-20%
- **Supports:** None needed
- **Brim:** Optional (helps adhesion)
- **Filament changes:** Automatic at 2.5mm layer height
