import unittest
import os
import time
from PIL import Image
from unittest.mock import patch
from app import generate, blip_text_generation
from Story import create_new_window, generate_text

class TestVisionaryScribePipeline(unittest.TestCase):

    # Folder for storing test images
    test_folder = os.path.join("tests", "test_images")

    @classmethod
    def setUpClass(cls):
        os.makedirs(cls.test_folder, exist_ok=True)
        print(f"Created directory: {cls.test_folder}")

    @patch('Story.generate_text')
    @patch('app.blip_text_generation')
    @patch('app.generate')
    @patch('app.prompt')  # Patching prompt directly
    def test_pipeline_mock_1(self, mock_prompt, mock_generate, mock_blip_text_generation, mock_generate_text):
        # Initial prompt setup
        mock_prompt.get.return_value = "A scenic mountain landscape"
        mock_generate.return_value = "generated_image.png"

        # BLIP caption output
        mock_blip_text_generation.return_value = "A scenic mountain landscape with a lake."

        # Set expectations for final output from `generate_text`
        button_values = ["Describe", "metaphor", "poetic", "50"]
        expected_text_output = "A serene mountain scene by the lake, described in metaphor."
        mock_generate_text.return_value = expected_text_output

        # Step 1: Generate image
        generate()
        self.assertTrue(os.path.exists("generated_image.png"), "Generated image file not found after generate().")

        # Step 2: Caption generation with BLIP
        mock_image = Image.open("generated_image.png")
        conditional_caption = blip_text_generation(mock_image)
        unconditional_caption = blip_text_generation(mock_image)
        print(f"Conditional caption: '{conditional_caption}'")
        print(f"Unconditional caption: '{unconditional_caption}'")

        # Step 3: Refine text output using create_new_window (mimics user interaction)
        final_text_result = generate_text(conditional_caption, unconditional_caption, button_values)
        self.assertEqual(final_text_result, expected_text_output)
        print(f"Final refined text: '{final_text_result}'")

        # Move generated image to test_images folder at the end
        image_filename = os.path.join(self.test_folder, "pipeline_case_1a.png")
        os.rename("generated_image.png", image_filename)
        print(f"Saved generated image as '{image_filename}'.")

    @patch('Story.generate_text')
    @patch('app.blip_text_generation')
    @patch('app.generate')
    @patch('app.prompt')  # Patching prompt directly
    def test_pipeline_mock_2(self, mock_prompt, mock_generate, mock_blip_text_generation, mock_generate_text):
        # Initial prompt setup
        mock_prompt.get.return_value = "A bustling city at night"
        mock_generate.return_value = "generated_image.png"

        # BLIP caption output
        mock_blip_text_generation.return_value = "A bustling city skyline at night."

        # Set expectations for final output from `generate_text`
        button_values = ["Summarize", "simile", "formal", "30"]
        expected_text_output = "City lights twinkle like stars over the skyline."
        mock_generate_text.return_value = expected_text_output

        # Step 1: Generate image
        generate()
        self.assertTrue(os.path.exists("generated_image.png"), "Generated image file not found after generate().")

        # Step 2: Caption generation with BLIP
        mock_image = Image.open("generated_image.png")
        conditional_caption = blip_text_generation(mock_image)
        unconditional_caption = blip_text_generation(mock_image)
        print(f"Conditional caption: '{conditional_caption}'")
        print(f"Unconditional caption: '{unconditional_caption}'")

        # Step 3: Refine text output using create_new_window (mimics user interaction)
        final_text_result = generate_text(conditional_caption, unconditional_caption, button_values)
        self.assertEqual(final_text_result, expected_text_output)
        print(f"Final refined text: '{final_text_result}'")

        # Move generated image to test_images folder at the end
        image_filename = os.path.join(self.test_folder, "pipeline_case_1b.png")
        os.rename("generated_image.png", image_filename)
        print(f"Saved generated image as '{image_filename}'.")

    @classmethod
    def tearDownClass(cls):
        print("Waiting 30 seconds before deleting the test_images folder...")
        time.sleep(30)
        if os.path.exists(cls.test_folder):
            for root, dirs, files in os.walk(cls.test_folder, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
            os.rmdir(cls.test_folder)
            print(f"Deleted directory: {cls.test_folder}")

if __name__ == "__main__":
    unittest.main()
