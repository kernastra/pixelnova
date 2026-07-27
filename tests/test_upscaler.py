from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from click.testing import CliRunner
from PIL import Image

from upscaler import PhotoUpscaler, main


class PhotoUpscalerTests(unittest.TestCase):
    def test_creates_nested_input_and_output_folders(self):
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            upscaler = PhotoUpscaler(
                root / "nested" / "input",
                root / "nested" / "output",
            )

            self.assertTrue(upscaler.input_folder.is_dir())
            self.assertTrue(upscaler.output_folder.is_dir())

    def test_tiny_image_never_scales_to_zero_pixels(self):
        with TemporaryDirectory() as temp_dir:
            image_path = Path(temp_dir) / "tiny.png"
            Image.new("RGB", (1, 1)).save(image_path)
            upscaler = PhotoUpscaler(
                Path(temp_dir) / "input",
                Path(temp_dir) / "output",
            )

            result = upscaler.upscale_image(image_path, scale_factor=0.1)

            self.assertIsNotNone(result)
            self.assertEqual((1, 1), result.size)
            result.close()

    def test_tif_files_are_discovered(self):
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            upscaler = PhotoUpscaler(root / "input", root / "output")
            Image.new("RGB", (2, 2)).save(upscaler.input_folder / "photo.tif")

            files = upscaler.get_image_files()

            self.assertEqual(["photo.tif"], [path.name for path in files])

    def test_custom_name_cannot_escape_output_folder(self):
        for unsafe_name in ("../escaped", "nested/name", r"nested\\name", ".", ".."):
            with self.subTest(unsafe_name=unsafe_name):
                with self.assertRaises(ValueError):
                    PhotoUpscaler.validate_custom_name(unsafe_name)

    def test_rgba_image_can_be_saved_as_jpeg(self):
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            upscaler = PhotoUpscaler(root / "input", root / "output")
            image_path = upscaler.input_folder / "transparent.jpg"
            png_path = upscaler.input_folder / "transparent.png"
            Image.new("RGBA", (2, 2), (255, 0, 0, 128)).save(png_path)

            with Image.open(png_path) as image:
                image.save(image_path, format="PNG")

            succeeded, failed = upscaler.process_images([image_path])

            self.assertEqual((1, 0), (succeeded, failed))
            with Image.open(upscaler.output_folder / "transparent_upscaled.jpg") as output:
                self.assertEqual("RGB", output.mode)


class CliTests(unittest.TestCase):
    def test_yes_skips_confirmation(self):
        runner = CliRunner()
        with runner.isolated_filesystem():
            input_folder = Path("input")
            input_folder.mkdir()
            Image.new("RGB", (2, 2)).save(input_folder / "photo.png")

            result = runner.invoke(main, ["--yes"])

            self.assertEqual(0, result.exit_code, result.output)
            self.assertTrue(Path("output/photo_upscaled.png").is_file())

    def test_empty_input_returns_nonzero_exit(self):
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(main, ["--yes"])

            self.assertNotEqual(0, result.exit_code)
            self.assertIn("No image files found", result.output)

    def test_processing_failure_returns_nonzero_exit(self):
        runner = CliRunner()
        with runner.isolated_filesystem():
            input_folder = Path("input")
            input_folder.mkdir()
            (input_folder / "broken.png").write_text("not an image")

            result = runner.invoke(main, ["--yes"])

            self.assertNotEqual(0, result.exit_code)
            self.assertIn("1 image(s) could not be processed", result.output)


if __name__ == "__main__":
    unittest.main()
