# Automated Nameplate Generator

Generate 3D printable chest badge nameplates with automatic color assignments for Bambu Studio!

## Quick Start

### 1. Add Names

Edit `names.txt` and add names (one per line):
```
Hadi Jaffri
Hussein Naqi
```

### 2. Generate Nameplates

```bash
source venv/bin/activate && python generate_bambu_3mf.py
```

This creates one 3MF file per nameplate in `output/` with colors already assigned!

### 3. Import and Print

1. **Open Bambu Studio**
2. **Drag the `*.3mf` files** from `output/` onto the build plate
3. **Slice and print!**

**That's it!** Colors are automatically assigned:
- Base → Extruder 1 (your first color)
- Text → Extruder 2 (your second color)

---

## How It Works

- Each 3MF file contains separate objects for base and text
- Base is assigned to Extruder 1, text to Extruder 2
- Nameplate width automatically adjusts to fit each name
- No manual color setup needed in Bambu Studio

---

## Specifications

- **Height:** 22mm total (2.5mm base + raised text)
- **Width:** Auto-calculated per name
- **Base thickness:** 2.5mm
- **Text height:** 1.2mm raised above base
- **Pin holes:** 1.5mm diameter, 4mm from corners (for badge attachment)

---

## Customization

Edit `generate_bambu_3mf.py` to change dimensions:

```python
self.base_height = 22        # Plate height in mm
self.base_thickness = 2.5    # Base depth
self.text_height = 1.2       # Text raise height
self.font_size = 10          # Font size
self.margin = 8              # Space around text
```

Then regenerate:
```bash
source venv/bin/activate && python generate_bambu_3mf.py
```

---

## Print Settings (Bambu A1)

- **Layer height:** 0.2mm
- **Infill:** 15-20%
- **Supports:** None needed
- **Brim:** Optional (helps adhesion)
- **Filament changes:** Automatic between base and text layers

---

## Troubleshooting

**OpenSCAD not found?**
```bash
brew install --cask openscad
```

**Want to regenerate everything?**
```bash
rm -rf output/*.3mf
source venv/bin/activate && python generate_bambu_3mf.py
```
