import unittest
import os
import time
from datetime import datetime
from unittest.mock import patch
from app import generate

class TestSD3ImageGeneration(unittest.TestCase):

    # Set up paths and folder
    test_folder = os.path.join("tests", "test_images")

    @classmethod
    def setUpClass(cls):
        # Create test_images folder if it does not exist
        os.makedirs(cls.test_folder, exist_ok=True)
        print(f"Created directory: {cls.test_folder}")

    @patch('app.prompt')
    def test_prompt_1(self, mock_prompt):
        # Set prompt to return a mock string for the first scenario
        mock_prompt.get.return_value = "A scenic mountain landscape"
        
        # Generate two images with unique names for prompt 1
        for suffix in ["a", "b"]:
            image_filename = os.path.join(self.test_folder, f"case_1{suffix}.png")
            
            # Remove the image if it exists (unlikely due to naming convention)
            if os.path.exists(image_filename):
                os.remove(image_filename)
                print(f"Deleted existing '{image_filename}' before test.")

            generate()  # Call generate to produce "generated_image.png"

            # Rename generated image to unique filename in the test folder
            if os.path.exists("generated_image.png"):
                os.rename("generated_image.png", image_filename)
                print(f"Saved generated image as '{image_filename}'.")

            # Check if the file was created with the correct name
            self.assertTrue(os.path.exists(image_filename), f"Output file '{image_filename}' should be saved in test_images folder.")

    @patch('app.prompt')
    def test_prompt_2(self, mock_prompt):
        # Set prompt to return a mock string for the second scenario
        mock_prompt.get.return_value = "A beautiful sunset over mountains"
        
        # Generate two images with unique names for prompt 2
        for suffix in ["a", "b"]:
            image_filename = os.path.join(self.test_folder, f"case_2{suffix}.png")
            
            # Remove the image if it exists (unlikely due to naming convention)
            if os.path.exists(image_filename):
                os.remove(image_filename)
                print(f"Deleted existing '{image_filename}' before test.")

            generate()  # Call generate to produce "generated_image.png"

            # Rename generated image to unique filename in the test folder
            if os.path.exists("generated_image.png"):
                os.rename("generated_image.png", image_filename)
                print(f"Saved generated image as '{image_filename}'.")

            # Check if the file was created with the correct name
            self.assertTrue(os.path.exists(image_filename), f"Output file '{image_filename}' should be saved in test_images folder.")

    @classmethod
    def tearDownClass(cls):
        # Delay the cleanup by 30 seconds
        print("Waiting 30 seconds before deleting the test_images folder...")
        time.sleep(30)

        # Remove the entire test_images directory after the delay
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
