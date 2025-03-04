import os
import logging
import openai
from openai import AzureOpenAI
from pathlib import Path
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test-output.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def read_code_files(directory='.'):
    code_files = []
    try:
        for path in Path(directory).rglob('*'):
            if path.is_file() and path.suffix in ['.py', '.js', '.html']:  # Add more extensions as needed
                try:
                    with open(path, 'r') as f:
                        content = f.read()
                        code_files.append(f"File: {path}\nContent:\n{content}")
                        logger.info(f"Read file: {path}")
                except UnicodeDecodeError:
                    logger.warning(f"Skipped binary/unreadable file: {path}")
        return "\n".join(code_files)
    except Exception as e:
        logger.error(f"Error reading files: {str(e)}")
        raise

def generate_test_cases():
    client = openai.AzureOpenAI(
                api_key=os.environ["AZURE_OPENAI_API_KEY"],
                azure_deployment="gpt4o",
                api_version="2024-08-01-preview",
                azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"]
            )

    logger.info("Starting test generation process...")
    code_content = read_code_files()
    
    prompt = f"""
    Generate comprehensive Selenium test cases in Python using pytest format.
    Follow this exact structure:

    from selenium import webdriver
    import pytest

    class TestGeneratedCases:
        @pytest.fixture(scope='class')
        def setup(self):
            logger.info("Initializing browser")
            driver = webdriver.Chrome()
            yield driver
            driver.quit()

        # Add test methods here with detailed logging

    Include:
    - Detailed logging using Python's logging module
    - Assertions for proper validation
    - Error handling with try/except blocks
    - Page interaction best practices
    - Comments explaining test logic

    Target codebase:
    {code_content}
    """

    try:
        logger.info("Sending request to Azure OpenAI...")
        response = client.chat.completions.create(
            model="gpt4o",
            messages=[
                    {"role": "system", "content": "You are a Python expert specializing in code quality and test case generation. Your reviews are constructive, specific, and educational."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=2500
            )

        test_code = response.choices[0].message.content
        logger.info("Successfully received response from Azure OpenAI")
        logger.debug(f"Generated Test Code:\n{test_code}")

        # Save generated tests
        output_dir = Path('generated_tests')
        output_dir.mkdir(exist_ok=True)
        
        test_file = output_dir / 'test_generated.py'
        with open(test_file, 'w') as f:
            f.write(test_code)
            logger.info(f"Tests written to {test_file}")

        return True

    except Exception as e:
        logger.error(f"Test generation failed: {str(e)}")
        raise

if __name__ == "__main__":
    generate_test_cases()
