# test_blip_text_generation.py

import unittest
from PIL import Image
from unittest.mock import patch
from app import blip_text_generation  # Ensure that this is accessible in app.py
import os

class TestBLIPTextGeneration(unittest.TestCase):

    @patch('app.blip_text_generation')
    def test_blip_mock_output_structure_1(self, mock_blip_text_generation):
        # First mock test for output structure
        mock_blip_text_generation.return_value = "A beautiful scenic landscape."
        mock_image = Image.new('RGB', (100, 100))  # Mock image
        result = blip_text_generation(mock_image)
        
        # Assertions
        self.assertIsInstance(result, str, "Output should be a string.")
        self.assertGreater(len(result), 10, "Output text should be more than 10 characters.")

    @patch('app.blip_text_generation')
    def test_blip_mock_output_structure_2(self, mock_blip_text_generation):
        # Second mock test with different mock output
        mock_blip_text_generation.return_value = "A bustling city at night."
        mock_image = Image.new('RGB', (150, 150))
        result = blip_text_generation(mock_image)
        
        self.assertIsInstance(result, str, "Output should be a string.")
        self.assertGreater(len(result), 10, "Output text should be more than 10 characters.")
    
    @patch('app.blip_text_generation')
    def test_blip_mock_output_structure_3(self, mock_blip_text_generation):
        # Third mock test for additional variation
        mock_blip_text_generation.return_value = "A calm forest with sunlight filtering through trees."
        mock_image = Image.new('RGB', (200, 200))
        result = blip_text_generation(mock_image)
        
        self.assertIsInstance(result, str, "Output should be a string.")
        self.assertGreater(len(result), 10, "Output text should be more than 10 characters.")
    
    def test_blip_real_image(self):
        # Real test with actual image file named test_blip_generation
        file_path = "test_blip_generation.png"
        if not os.path.exists(file_path):
            self.skipTest(f"File {file_path} does not exist.")
        
        real_image = Image.open(file_path)  # Ensure this file exists in the test directory
        result = blip_text_generation(real_image)
        
        # Assertions for the real output
        self.assertIsInstance(result, str, "Output should be a string.")
        self.assertGreater(len(result), 10, "Output text should be more than 10 characters.")
        print("-> Passed 3 Tests.\n\nTesting real image:\n")
        self.assertIn("blue", result.lower(), "Output should describe the main subject.")
        self.assertIn("car", result.lower(), "Output should describe the main subject.")
        print("Test Passed")
if __name__ == "__main__":
    unittest.main()
