![Photo Upscaler CLI](img.png)

A command-line tool for upscaling photos with an interactive menu, customizable naming, and batch output options.

## Features

- **Interactive Menu**: Guided menu to configure and run the upscaler without memorising flags
- **Batch Processing**: Upscale multiple images in one run
- **Multiple Upscaling Methods**: Lanczos, Bicubic, and Bilinear
- **Custom Naming**: Set a custom base name or use original filenames
- **Auto-numbering**: Automatically appends numbers to avoid overwriting existing files
- **Flexible Scale Factors**: Any scale factor ≥ 0.1 (e.g. 1.5x, 2x, 4x)
- **Multiple Format Support**: JPEG, PNG, BMP, TIFF, WebP

## Requirements

- Python 3.6+
- Pillow
- Click

## Installation

1. Clone or download this project
2. Run the setup script:
   ```bash
   python setup.py
   ```

This will install required dependencies (Pillow, Click) and create `input` and `output` folders.

Alternatively, use the provided shell script which handles virtual environment creation automatically:
```bash
bash run.sh
```

## Usage

### Interactive Menu

The easiest way to use the tool — launches a guided menu where you can configure all settings before running:

```bash
python upscaler.py --interactive
# or
python upscaler.py -I
```

Menu options:

```
==================================================
  Photo Upscaler CLI — Main Menu
==================================================
  1. Run upscaler
  2. Set scale factor      (current: 2.0x)
  3. Set upscale method    (current: lanczos)
  4. Set custom output name (current: none)
  5. Set input folder      (current: input)
  6. Set output folder     (current: output)
  7. View input folder contents
  8. Exit
==================================================
```

### Command-line Usage

1. Place your images in the `input` folder
2. Run:
   ```bash
   python upscaler.py
   ```

### All Options

| Flag | Short | Default | Description |
|---|---|---|---|
| `--interactive` | `-I` | off | Launch interactive menu |
| `--input-folder` | `-i` | `input` | Folder containing source images |
| `--output-folder` | `-o` | `output` | Folder for upscaled output |
| `--scale` | `-s` | `2.0` | Scale factor (minimum 0.1) |
| `--method` | `-m` | `lanczos` | Upscaling method: `lanczos`, `bicubic`, `bilinear` |
| `--custom-name` | `-n` | — | Custom base name for output files |
| `--prompt-name` | `-p` | off | Prompt for custom filename at runtime |

### Examples

```bash
# Interactive menu
python upscaler.py -I

# 4x upscale using Lanczos
python upscaler.py --scale 4.0 --method lanczos

# Custom output name
python upscaler.py --custom-name "enhanced_photo"

# Custom folders and scale
python upscaler.py -i /home/user/photos -o /home/user/upscaled -s 3.0

# Prompt for a name at runtime
python upscaler.py --prompt-name
```

## Supported Image Formats

| Format | Extensions |
|---|---|
| JPEG | `.jpg`, `.jpeg` |
| PNG | `.png` |
| BMP | `.bmp` |
| TIFF | `.tiff` |
| WebP | `.webp` |

## File Naming

| Scenario | Result |
|---|---|
| No custom name | `photo.jpg` → `photo_upscaled.jpg` |
| Custom name, single file | `photo.jpg` → `custom_name.jpg` |
| Custom name, first of many | `custom_name.jpg` |
| Custom name, subsequent files | `custom_name_2.jpg`, `custom_name_3.jpg`, … |
| Filename conflict | Incremental suffix appended automatically |

## Helper Scripts

| Script | Purpose |
|---|---|
| `setup.py` | Installs dependencies and creates `input`/`output` folders |
| `run.sh` | Creates a virtual environment (if needed), then runs the upscaler |
| `example.py` | Generates sample test images in the `input` folder |
| `demo.py` | Runs a full demo with custom naming via subprocess |

## License

MIT License - see [LICENSE](LICENSE) for details.
