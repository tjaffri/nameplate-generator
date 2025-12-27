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

This creates one combined STL file per nameplate in `output/`.

### 2. Bulk Import into Bambu Studio

1. **Open Bambu Studio**

2. **Bulk import all nameplates:**
   - Select ALL `*.stl` files from `output/` folder
   - Drag them onto the build plate at once

3. **Apply multi-color (choose one method):**

   **Method A: Group and apply modifier (if supported):**
   - Select all imported objects (Ctrl+A / Cmd+A)
   - Right-click → **Group** (if available)
   - Right-click group → **Add Modifier** → **Height Range**
   - Range 1: 0mm to 2.5mm → Light Blue
   - Range 2: 2.5mm to 10mm → Black

   **Method B: Copy settings from one object:**
   - Set up height range modifier on first nameplate
   - Right-click → **Copy**
   - Select all other nameplates → Right-click → **Paste**

   **Method C: Apply individually:**
   - For each nameplate, add height range modifier manually
   - Range 1: 0mm to 2.5mm → Light Blue
   - Range 2: 2.5mm to 10mm → Black

4. **Slice and print!**

---

## How It Works

- **Each STL file:** Complete nameplate (base + text combined)
- **Base:** 0mm to 2.5mm height → Light Blue
- **Text:** 2.5mm to 3.7mm height → Black
- **Height Range Modifier:** Assigns different colors at different Z heights
- **Automatic sizing:** Each nameplate width adjusts to fit the name

---

## Specifications

- **Height:** 22mm total (2.5mm base + raised text)
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

**No "Height Range" modifier option?**
- Try updating Bambu Studio to the latest version
- Alternative: Print in single color, or manually paint regions

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
- **Filament changes:** Automatic at 2.5mm layer height (with height range modifier)
