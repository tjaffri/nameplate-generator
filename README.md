# Automated Nameplate Generator

Generate 3D printable chest badge nameplates as single-color STL files for Bambu Studio!

## Quick Start

### 1. Add Names

Edit `names.txt` and add names (one per line):
```
Hadi Jaffri
Hussein Naqi
```

### 2. Generate Nameplates

```bash
source venv/bin/activate && python generate_nameplates.py
```

This creates one STL file per nameplate in `output/`!

### 3. Import and Print

1. **Open Bambu Studio**
2. **Drag the `*.stl` files** from `output/` onto the build plate
3. **Slice and print!**

**That's it!** Single-color solid nameplates with no floating regions.

---

## How It Works

- Each STL file is a single solid piece (base + text merged)
- Nameplate width automatically adjusts to fit each name
- No geometry errors or missing letters
- Simple single-color printing

---

## Specifications

- **Height:** 13.5mm total
- **Width:** Auto-calculated per name (65-90mm typical)
- **Base thickness:** 2.0mm
- **Text height:** 1.2mm raised above base
- **Font:** Liberation Sans Bold, 9pt
- **Pin holes:** 1.0mm diameter, 2mm from corners (for badge attachment)
- **Build plate capacity:** ~30 nameplates per print on Bambu A1 (256×256mm)

---

## Customization

Edit `generate_nameplates.py` to change dimensions:

```python
self.base_height = 13.5      # Plate height in mm
self.base_thickness = 2.0    # Base depth
self.text_height = 1.2       # Text raise height
self.font_size = 9           # Font size in points
self.margin = 7              # Space around text
```

Then regenerate:
```bash
source venv/bin/activate && python generate_nameplates.py
```

---

## Print Settings (Bambu A1)

- **Layer height:** 0.2mm
- **Infill:** 15-20%
- **Supports:** None needed
- **Brim:** Optional (helps adhesion)
- **Single color:** No filament changes needed

---

## Troubleshooting

**OpenSCAD not found?**
```bash
brew install --cask openscad
```

**Want to regenerate everything?**
```bash
rm -rf output/*.stl
source venv/bin/activate && python generate_nameplates.py
```
