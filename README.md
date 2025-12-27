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

Your STL files will be in the `output/` directory.

### 2. Import into Bambu Studio (One-Time Setup)

1. **Open Bambu Studio**

2. **Import one nameplate** to set up the modifier:
   - Drag `output/hadi_jaffri.stl` onto the build plate

3. **Add Height Range Modifier**:
   - Right-click the object → **Add Modifier** → **Height Range**
   - Set **Range 1 (Base):** Start: `0mm` → End: `2.5mm` → Filament: **Light Blue**
   - Set **Range 2 (Text):** Start: `2.5mm` → End: `10mm` → Filament: **Black**
   - Check preview - should show blue base + black text

4. **Save as Preset**:
   - Right-click the object → **Save settings as preset**
   - Name it: `Nameplate-MultiColor`

### 3. Bulk Import All Nameplates

1. **Remove the test nameplate** from the build plate

2. **Select and drag ALL STL files** from `output/` folder onto the build plate at once

3. **Select all objects** (Ctrl+A or Cmd+A)

4. **Apply the preset**:
   - Right-click any selected object → **Load settings preset** → `Nameplate-MultiColor`
   - All nameplates will instantly get the color settings applied!

5. **Slice and print!**

---

## How It Works

- **Base plate:** 0mm to 2.5mm height (Light Blue)
- **Raised text:** 2.5mm to top (Black)
- **Automatic sizing:** Plate width adjusts to fit each name
- **Height Range Modifier:** Applies different colors at different Z heights

---

## Specifications

- **Height:** 22mm (fixed)
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

**"Height Range" not in the Add Modifier menu?**
- Update Bambu Studio to the latest version
- Or use: Right-click → **Add Modifier** → Look for **Height Range** or **Layer Range**

**Text not showing as different color?**
- Make sure Range 1 ends at exactly `2.5mm` and Range 2 starts at `2.5mm`
- Check that you've selected different filament slots for each range

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
