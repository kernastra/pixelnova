#!/usr/bin/env python3
"""
Photo Upscaler CLI - A command line tool for upscaling photos
"""

import click
from PIL import Image
from pathlib import Path


class PhotoUpscaler:
    """Main class for handling photo upscaling operations"""
    
    def __init__(self, input_folder="input", output_folder="output"):
        self.input_folder = Path(input_folder)
        self.output_folder = Path(output_folder)
        self.supported_formats = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
        
        # Create folders if they don't exist
        self.input_folder.mkdir(exist_ok=True)
        self.output_folder.mkdir(exist_ok=True)
    
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
                # Get original dimensions
                width, height = img.size
                
                # Calculate new dimensions
                new_width = int(width * scale_factor)
                new_height = int(height * scale_factor)
                
                # Choose resampling method
                if method == 'lanczos':
                    resampling = Image.LANCZOS
                elif method == 'bicubic':
                    resampling = Image.BICUBIC
                elif method == 'bilinear':
                    resampling = Image.BILINEAR
                else:
                    resampling = Image.LANCZOS
                
                # Upscale the image
                upscaled_img = img.resize((new_width, new_height), resampling)
                
                return upscaled_img
                
        except Exception as e:
            click.echo(f"Error upscaling {image_path}: {str(e)}", err=True)
            return None
    
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
        click.echo(f"Found {len(image_files)} image(s) to process.")

        for i, image_path in enumerate(image_files):
            click.echo(f"Processing {image_path.name}...")

            # Upscale the image
            upscaled_img = self.upscale_image(image_path, scale_factor, method)

            if upscaled_img is None:
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
                jpeg_formats = {'.jpg', '.jpeg', '.webp'}
                if extension.lower() in jpeg_formats:
                    if upscaled_img.mode in ('RGBA', 'P'):
                        upscaled_img = upscaled_img.convert('RGB')
                    upscaled_img.save(output_path, quality=95)
                else:
                    upscaled_img.save(output_path)
                click.echo(f"✓ Saved: {output_path.name}")
            except Exception as e:
                click.echo(f"✗ Error saving {output_path.name}: {str(e)}", err=True)
        
        click.echo(f"\nProcessing complete! Check the '{self.output_folder}' folder.")


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
            settings['custom_name'] = name.strip() or None
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
def main(input_folder, output_folder, scale, method, custom_name, prompt_name, interactive):
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
        click.echo(f"No image files found in '{input_folder}' folder.")
        click.echo("Please add some images to the input folder and try again.")
        return

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
        if not custom_name.strip():
            custom_name = None

    if custom_name:
        click.echo(f"Using custom base name: {custom_name}")

    # Confirm before processing
    if not click.confirm("\nProceed with upscaling?"):
        click.echo("Operation cancelled.")
        return

    # Process images
    click.echo("\nStarting upscaling process...")
    upscaler.process_images(image_files, scale, method, custom_name)


if __name__ == '__main__':
    main()
