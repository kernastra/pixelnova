#!/usr/bin/env python3
"""
Photo Upscaler CLI - A command line tool for upscaling photos
"""

from pathlib import Path

import click
from PIL import Image, ImageOps


class PhotoUpscaler:
    """Main class for handling photo upscaling operations"""

    supported_formats = {'.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff', '.webp'}
    resampling_methods = {
        'lanczos': Image.Resampling.LANCZOS,
        'bicubic': Image.Resampling.BICUBIC,
        'bilinear': Image.Resampling.BILINEAR,
    }
    
    def __init__(self, input_folder="input", output_folder="output"):
        self.input_folder = Path(input_folder)
        self.output_folder = Path(output_folder)
        
        # Create folders if they don't exist
        self.input_folder.mkdir(parents=True, exist_ok=True)
        self.output_folder.mkdir(parents=True, exist_ok=True)
    
    def get_image_files(self):
        """Get all supported image files from input folder"""
        image_files = []
        for file_path in self.input_folder.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in self.supported_formats:
                image_files.append(file_path)
        return sorted(image_files)
    
    def upscale_image(self, image_path, scale_factor=2, method='lanczos'):
        """Upscale an image using specified method"""
        try:
            with Image.open(image_path) as img:
                # Apply camera orientation before calculating output dimensions.
                img = ImageOps.exif_transpose(img)
                width, height = img.size
                
                # A valid scale factor can still round a tiny image down to zero.
                new_width = max(1, round(width * scale_factor))
                new_height = max(1, round(height * scale_factor))
                
                # Upscale the image
                upscaled_img = img.resize(
                    (new_width, new_height),
                    self.resampling_methods.get(method, Image.Resampling.LANCZOS),
                )
                
                return upscaled_img
                
        except Exception as e:
            click.echo(f"Error upscaling {image_path}: {str(e)}", err=True)
            return None

    @staticmethod
    def validate_custom_name(custom_name):
        """Validate that a custom base name cannot escape the output folder."""
        if custom_name is None:
            return None

        custom_name = custom_name.strip()
        if (
            not custom_name
            or custom_name in {'.', '..'}
            or '/' in custom_name
            or '\\' in custom_name
        ):
            raise ValueError("custom name must be a filename, not a path")

        return custom_name
    
    def generate_output_filename(self, base_name, extension):
        """Generate output filename with incremental numbering if file exists"""
        counter = 1
        output_path = self.output_folder / f"{base_name}{extension}"
        
        while output_path.exists():
            output_path = self.output_folder / f"{base_name}_{counter}{extension}"
            counter += 1
        
        return output_path
    
    def process_images(self, image_files, scale_factor=2, method='lanczos', custom_name=None):
        """Process all images in the input folder"""
        custom_name = self.validate_custom_name(custom_name)
        succeeded = 0
        failed = 0
        click.echo(f"Found {len(image_files)} image(s) to process.")

        for i, image_path in enumerate(image_files):
            click.echo(f"Processing {image_path.name}...")

            # Upscale the image
            upscaled_img = self.upscale_image(image_path, scale_factor, method)

            if upscaled_img is None:
                failed += 1
                continue

            # Determine output filename
            if custom_name and i == 0:
                # Use custom name for first image
                base_name = custom_name
            elif custom_name:
                # Use custom name with 1-based number for subsequent images
                base_name = f"{custom_name}_{i + 1}"
            else:
                # Use original filename with _upscaled suffix
                base_name = f"{image_path.stem}_upscaled"
            
            extension = image_path.suffix
            output_path = self.generate_output_filename(base_name, extension)
            
            # Save the upscaled image
            try:
                if extension.lower() in {'.jpg', '.jpeg'}:
                    if upscaled_img.mode not in {'RGB', 'L', 'CMYK'}:
                        upscaled_img = upscaled_img.convert('RGB')
                    upscaled_img.save(output_path, quality=95)
                elif extension.lower() == '.webp':
                    upscaled_img.save(output_path, quality=95)
                else:
                    upscaled_img.save(output_path)
                click.echo(f"✓ Saved: {output_path.name}")
                succeeded += 1
            except Exception as e:
                click.echo(f"✗ Error saving {output_path.name}: {str(e)}", err=True)
                failed += 1
            finally:
                upscaled_img.close()
        
        click.echo(
            f"\nProcessing complete: {succeeded} succeeded, {failed} failed. "
            f"Check the '{self.output_folder}' folder."
        )
        return succeeded, failed


def run_interactive_menu():
    """Launch a guided interactive menu for the upscaler."""
    # Default settings
    settings = {
        'input_folder': 'input',
        'output_folder': 'output',
        'scale': 2.0,
        'method': 'lanczos',
        'custom_name': None,
    }

    while True:
        click.echo("\n" + "=" * 50)
        click.echo("  Photo Upscaler CLI — Main Menu")
        click.echo("=" * 50)
        click.echo(f"  1. Run upscaler")
        click.echo(f"  2. Set scale factor      (current: {settings['scale']}x)")
        click.echo(f"  3. Set upscale method    (current: {settings['method']})")
        click.echo(f"  4. Set custom output name (current: {settings['custom_name'] or 'none'})")
        click.echo(f"  5. Set input folder      (current: {settings['input_folder']})")
        click.echo(f"  6. Set output folder     (current: {settings['output_folder']})")
        click.echo(f"  7. View input folder contents")
        click.echo(f"  8. Exit")
        click.echo("=" * 50)

        choice = click.prompt("Select an option", type=click.IntRange(1, 8))

        if choice == 1:
            upscaler = PhotoUpscaler(settings['input_folder'], settings['output_folder'])
            image_files = upscaler.get_image_files()
            if not image_files:
                click.echo(f"\nNo images found in '{settings['input_folder']}'. Add images and try again.")
                continue
            click.echo(f"\nFound {len(image_files)} image(s). Settings summary:")
            click.echo(f"  Scale:       {settings['scale']}x")
            click.echo(f"  Method:      {settings['method']}")
            click.echo(f"  Output name: {settings['custom_name'] or '(original name + _upscaled)'}")
            click.echo(f"  Output dir:  {settings['output_folder']}")
            if click.confirm("\nProceed with upscaling?"):
                click.echo("")
                upscaler.process_images(image_files, settings['scale'], settings['method'], settings['custom_name'])

        elif choice == 2:
            settings['scale'] = click.prompt("Enter scale factor", type=click.FloatRange(min=0.1), default=settings['scale'])

        elif choice == 3:
            settings['method'] = click.prompt(
                "Select method",
                type=click.Choice(['lanczos', 'bicubic', 'bilinear']),
                default=settings['method'],
            )

        elif choice == 4:
            name = click.prompt("Enter custom base name (or leave blank to clear)", default="", show_default=False)
            try:
                settings['custom_name'] = PhotoUpscaler.validate_custom_name(name.strip() or None)
            except ValueError as exc:
                click.echo(f"Invalid custom name: {exc}", err=True)
                continue
            click.echo(f"Custom name set to: {settings['custom_name'] or 'none'}")

        elif choice == 5:
            settings['input_folder'] = click.prompt("Enter input folder path", default=settings['input_folder'])

        elif choice == 6:
            settings['output_folder'] = click.prompt("Enter output folder path", default=settings['output_folder'])

        elif choice == 7:
            upscaler = PhotoUpscaler(settings['input_folder'], settings['output_folder'])
            image_files = upscaler.get_image_files()
            click.echo(f"\nContents of '{settings['input_folder']}':")
            if image_files:
                for f in image_files:
                    size_kb = f.stat().st_size // 1024
                    click.echo(f"  {f.name}  ({size_kb} KB)")
            else:
                click.echo("  (no supported images found)")

        elif choice == 8:
            click.echo("Goodbye!")
            break


@click.command()
@click.option('--input-folder', '-i', default='input',
              help='Input folder containing images to upscale (default: input)')
@click.option('--output-folder', '-o', default='output',
              help='Output folder for upscaled images (default: output)')
@click.option('--scale', '-s', default=2.0, type=click.FloatRange(min=0.1),
              help='Scale factor for upscaling (default: 2.0)')
@click.option('--method', '-m', default='lanczos',
              type=click.Choice(['lanczos', 'bicubic', 'bilinear']),
              help='Upscaling method (default: lanczos)')
@click.option('--custom-name', '-n', default=None,
              help='Custom base name for output files')
@click.option('--prompt-name', '-p', is_flag=True,
              help='Prompt for custom filename during execution')
@click.option('--interactive', '-I', is_flag=True,
              help='Launch interactive menu')
@click.option('--yes', '-y', is_flag=True,
              help='Skip the confirmation prompt')
def main(input_folder, output_folder, scale, method, custom_name, prompt_name, interactive, yes):
    """
    Photo Upscaler CLI - Upscale photos from input folder to output folder

    This tool will:
    1. Read all supported image files from the input folder
    2. Upscale them using the specified method and scale factor
    3. Save them to the output folder with optional custom naming
    """

    click.echo("Photo Upscaler CLI")
    click.echo("=" * 50)

    if interactive:
        run_interactive_menu()
        return

    # Initialize upscaler
    upscaler = PhotoUpscaler(input_folder, output_folder)

    # Check if input folder has images
    image_files = upscaler.get_image_files()
    if not image_files:
        raise click.ClickException(
            f"No image files found in '{input_folder}'. "
            "Add supported images and try again."
        )

    # Display current settings
    click.echo(f"Input folder: {input_folder}")
    click.echo(f"Output folder: {output_folder}")
    click.echo(f"Scale factor: {scale}x")
    click.echo(f"Method: {method}")
    click.echo(f"Images found: {len(image_files)}")

    # Handle custom naming
    if prompt_name:
        custom_name = click.prompt("\nEnter custom base name for output files (or press Enter to use original names)",
                                   default="", show_default=False)
        custom_name = custom_name.strip() or None

    try:
        custom_name = PhotoUpscaler.validate_custom_name(custom_name)
    except ValueError as exc:
        raise click.BadParameter(str(exc), param_hint="'--custom-name'") from exc

    if custom_name:
        click.echo(f"Using custom base name: {custom_name}")

    # Confirm before processing
    if not yes and not click.confirm("\nProceed with upscaling?"):
        click.echo("Operation cancelled.")
        return

    # Process images
    click.echo("\nStarting upscaling process...")
    _, failed = upscaler.process_images(image_files, scale, method, custom_name)
    if failed:
        raise click.ClickException(f"{failed} image(s) could not be processed")


if __name__ == '__main__':
    main()
