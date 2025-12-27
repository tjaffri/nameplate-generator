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

This creates one `.3mf` file per nameplate in `output/`.
Each file contains TWO separate objects: base (Light Blue) and text (Black).

### 2. Bulk Import into Bambu Studio

1. **Open Bambu Studio**

2. **Bulk import all nameplates:**
   - Select ALL `*.3mf` files from `output/` folder
   - Drag them onto the build plate at once
   - Each nameplate appears as TWO objects: "Name - Base" and "Name - Text"

3. **Assign colors to all bases:**
   - In the object list, select all "*- Base" objects
   - (Hold Ctrl/Cmd and click each base, or use Shift-click)
   - In the right panel, assign **Light Blue** filament

4. **Assign colors to all text:**
   - In the object list, select all "*- Text" objects
   - In the right panel, assign **Black** filament

5. **Slice and print!**
   - Text is automatically positioned on top of bases
   - Printer will change filament at layer transition

---

## How It Works

- **Each 3MF file:** Contains base + text as separate objects
- **Base object:** Flat plate 2.5mm thick → Light Blue
- **Text object:** Raised letters 1.2mm tall → Black
- **Automatic positioning:** Text sits on top of base at Z=2.5mm
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

**Can't see separate objects in Bambu Studio?**
- Look for two items per nameplate in the object list (right panel)
- One named "Name - Base" and one named "Name - Text"

**Objects not aligned?**
- They should be automatically aligned
- If not, select both → right-click → **Align** → **Center XY**

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
