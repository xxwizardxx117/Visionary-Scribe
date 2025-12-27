import unittest
import json
import datetime
from unittest.mock import mock_open, patch
from Story import store_feedback  # Assuming the function is in Story.py

class TestFeedbackStorage(unittest.TestCase):

    @patch("builtins.open", new_callable=mock_open, read_data="[]")
    def test_store_feedback_append_to_empty_file(self, mock_file):
        feedback_data = {
            "prompt": "Sample prompt",
            "image_path": "sample_image.png",
            "conditional_caption": "Sample conditional caption",
            "unconditional_caption": "Sample unconditional caption",
            "Text generation Parameters": ["None", "None", "Paragraph", "None"],
            "feedback": "Great!",
            "rating": "4: Good",
            "timestamp": datetime.datetime.now().isoformat()
        }

        # Call the function to test
        store_feedback(feedback_data, filename="test_feedback.json")

        # Combine all write calls to get the full JSON string
        written_data = ''.join(call[0][0] for call in mock_file().write.call_args_list)
        written_data_json = json.loads(written_data)  # Parse it as JSON

        # Assertions
        self.assertEqual(len(written_data_json), 1)
        self.assertEqual(written_data_json[0]["feedback"], "Great!")

    @patch("builtins.open", new_callable=mock_open, read_data=json.dumps([
        {
            "prompt": "Existing prompt",
            "feedback": "Good job",
            "rating": "4: Good",
            "timestamp": datetime.datetime.now().isoformat()
        }
    ]))
    def test_store_feedback_append_to_existing_data(self, mock_file):
        feedback_data = {
            "prompt": "New prompt",
            "image_path": "new_image.png",
            "conditional_caption": "New conditional caption",
            "unconditional_caption": "New unconditional caption",
            "Text generation Parameters": ["Describe Image", "None", "Paragraph", "40 - 50"],
            "feedback": "Excellent!",
            "rating": "5: Excellent",
            "timestamp": datetime.datetime.now().isoformat()
        }

        # Call the function to test
        store_feedback(feedback_data, filename="feedback.json")

        # Combine all write calls to get the full JSON string
        written_data = ''.join(call[0][0] for call in mock_file().write.call_args_list)
        written_data_json = json.loads(written_data)  # Parse it as JSON

        # Check that both entries are in the data
        self.assertEqual(len(written_data_json), 2)
        self.assertEqual(written_data_json[1]["feedback"], "Excellent!")

    @patch("builtins.open", new_callable=mock_open, read_data="invalid_json")
    def test_store_feedback_handles_invalid_json(self, mock_file):
        feedback_data = {
            "prompt": "Sample prompt",
            "feedback": "Nice job!",
            "rating": "5: Excellent",
            "timestamp": datetime.datetime.now().isoformat()
        }

        # Attempt to call the function; it should not raise an error
        try:
            store_feedback(feedback_data, filename="feedback.json")
            error_raised = False
        except json.JSONDecodeError:
            error_raised = True

        # Assert that no JSON error was raised
        self.assertFalse(error_raised, "Function should handle invalid JSON gracefully")

    def test_store_feedback_actual_file(self):
        feedback_data = {
            "prompt": "colliding worlds , mars and earth",
            "image_path": "sample_image.png",
            "conditional_caption": "earth and mars colliding",
            "unconditional_caption": "mars and earth colliding in space",
            "Text generation Parameters": ["None", "None", "Paragraph", "None"],
            "feedback": "Great!",
            "rating": "4: Good",
            "timestamp": datetime.datetime.now().isoformat()
        }

        # Ensure the test file is empty before the test
        with open("test_feedback.json", "w") as file:
            file.write("[]")

        # Call the function to test
        store_feedback(feedback_data, filename="test_feedback.json")

        # Read the file content
        with open("test_feedback.json", "r") as file:
            written_data_json = json.load(file)

        # Assertions
        self.assertEqual(len(written_data_json), 1)
        self.assertEqual(written_data_json[0]["feedback"], "Great!")
    
if __name__ == "__main__":
    unittest.main()





# Overview of the Test File
# This test file, test_feedback.py, verifies the functionality of a function called store_feedback, which is assumed to be in Story.py. The purpose of store_feedback is to save user feedback data to a JSON file, either appending it to existing data or creating a new entry.

# Structure of test_feedback.py
# The file is structured using Python's unittest framework, which allows defining tests in a class and using various assertions to check that the code behaves as expected. Here’s a breakdown of each test:

# 1. test_store_feedback_append_to_empty_file
# Purpose: Verifies that the store_feedback function correctly writes new feedback data to an empty file.
# What It Does:
# Setup: Mocks an empty JSON file ([]).
# Execution: Calls store_feedback with a sample feedback dictionary.
# Verification:
# Combines all calls to write into a single JSON string, which is then parsed.
# Checks that there is only one item in the JSON array, confirming that the feedback was added correctly.
# Asserts that the feedback content matches what was passed in.
# 2. test_store_feedback_append_to_existing_data
# Purpose: Ensures that store_feedback correctly appends feedback to an already populated file.
# What It Does:
# Setup: Mocks a file with existing JSON feedback data.
# Execution: Calls store_feedback with new feedback data to add to this existing file.
# Verification:
# Combines all write calls to form a single JSON string.
# Confirms that there are now two entries in the JSON array (the original and the new).
# Verifies that the second entry’s content matches the new feedback data.
# 3. test_store_feedback_handles_invalid_json
# Purpose: Tests that store_feedback can handle cases where the existing file contains invalid JSON (e.g., corrupted or malformed).
# What It Does:
# Setup: Mocks a file with invalid JSON content ("invalid_json").
# Execution: Calls store_feedback with new feedback data.
# Verification:
# Confirms that no JSON decoding error is raised, indicating that store_feedback handles invalid JSON gracefully.
# Key Concepts and Techniques Used
# Mocking with patch: Each test uses patch from unittest.mock to replace the file handling in store_feedback with a mock object, allowing control over file content without writing to disk.
# Combining Write Calls: Since json.dump may split the data into multiple write calls, the test combines these calls into one string to treat them as a single JSON output.
# Assertions: Each test includes assertions to verify both the structure and the content of the resulting JSON data.
# Purpose of store_feedback
# The store_feedback function is designed to:

# Load existing feedback data from a JSON file.
# Append new feedback data to this list.
# Save the updated list back to the file, handling cases where the file is empty or contains invalid data.