"""
Ollama Client Module
Handles communication with local Ollama LLM for natural language to JSON strategy conversion.
"""

import json
import re
import os
from typing import Dict, List, Optional, Tuple, Generator
import requests
from strategy_validator import StrategyValidator, validate_json_string


# Load the system prompt
PROMPT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "prompts", "strategy_conversion_prompt.txt")


class OllamaClient:
    """Client for interacting with Ollama local LLM."""
    
    def __init__(self, model: str = "mistral:7b-instruct", base_url: str = "http://localhost:11434"):
        """
        Initialize Ollama client.
        
        Args:
            model: The Ollama model to use (e.g., 'mistral:7b-instruct', 'llama2', 'codellama')
            base_url: Base URL for Ollama API (default: http://localhost:11434)
        """
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.system_prompt = self._load_system_prompt()
        self.validator = StrategyValidator()
    
    def _load_system_prompt(self) -> str:
        """Load the system prompt from file."""
        try:
            with open(PROMPT_FILE, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            # Fallback minimal prompt if file not found
            return """You are a stock strategy converter. Convert natural language to JSON format.
Output only valid JSON with 'name', 'description', and 'conditions' fields."""
    
    def is_available(self) -> Tuple[bool, str]:
        """
        Check if Ollama is available and running.
        
        Returns:
            Tuple of (is_available, message)
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [m.get("name", "") for m in models]
                
                # Check if our model is available
                model_base = self.model.split(":")[0]
                available = any(model_base in name for name in model_names)
                
                if available:
                    return True, f"Connected to Ollama. Model '{self.model}' is available."
                else:
                    return False, f"Ollama is running but model '{self.model}' not found. Available: {model_names}"
            else:
                return False, f"Ollama returned status {response.status_code}"
        except requests.exceptions.ConnectionError:
            return False, "Cannot connect to Ollama. Please ensure Ollama is running (ollama serve)."
        except requests.exceptions.Timeout:
            return False, "Connection to Ollama timed out."
        except Exception as e:
            return False, f"Error checking Ollama: {str(e)}"
    
    def warmup_model(self) -> Tuple[bool, str]:
        """
        Warm up the model by sending a simple request.
        This loads the model into memory for faster subsequent requests.
        
        Returns:
            Tuple of (success, message)
        """
        try:
            payload = {
                "model": self.model,
                "prompt": "Hello",
                "stream": False,
                "options": {
                    "num_predict": 1,  # Generate only 1 token
                }
            }
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=300  # 5 minute timeout for model loading
            )
            
            if response.status_code == 200:
                return True, "Model loaded and ready!"
            else:
                return False, f"Failed to warm up model: {response.status_code}"
                
        except requests.exceptions.Timeout:
            return False, "Model loading timed out. Try again or use a smaller model."
        except Exception as e:
            return False, f"Error warming up model: {str(e)}"
    
    def get_available_models(self) -> List[str]:
        """Get list of available models from Ollama."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                return [m.get("name", "") for m in models]
        except:
            pass
        return []
    
    def generate(self, user_prompt: str, temperature: float = 0.1) -> Tuple[bool, str, str]:
        """
        Generate a response from the LLM.
        
        Args:
            user_prompt: The user's natural language input
            temperature: LLM temperature (lower = more deterministic)
        
        Returns:
            Tuple of (success, response_text, error_message)
        """
        try:
            payload = {
                "model": self.model,
                "prompt": user_prompt,
                "system": self.system_prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": 2048,  # Max tokens to generate
                }
            }
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=300  # 5 minute timeout for generation (model may need to load)
            )
            
            if response.status_code == 200:
                result = response.json()
                generated_text = result.get("response", "")
                return True, generated_text, ""
            else:
                return False, "", f"Ollama error: {response.status_code} - {response.text}"
                
        except requests.exceptions.Timeout:
            return False, "", "Request timed out. The model might be loading or the query is too complex."
        except requests.exceptions.ConnectionError:
            return False, "", "Cannot connect to Ollama. Please ensure it's running."
        except Exception as e:
            return False, "", f"Error generating response: {str(e)}"
    
    def generate_stream(self, user_prompt: str, temperature: float = 0.1) -> Generator[str, None, None]:
        """
        Generate a streaming response from the LLM.
        
        Yields:
            Chunks of generated text
        """
        try:
            payload = {
                "model": self.model,
                "prompt": user_prompt,
                "system": self.system_prompt,
                "stream": True,
                "options": {
                    "temperature": temperature,
                    "num_predict": 2048,
                }
            }
            
            with requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                stream=True,
                timeout=300  # 5 minute timeout
            ) as response:
                if response.status_code == 200:
                    for line in response.iter_lines():
                        if line:
                            try:
                                data = json.loads(line)
                                chunk = data.get("response", "")
                                if chunk:
                                    yield chunk
                            except json.JSONDecodeError:
                                continue
                                
        except Exception as e:
            yield f"[Error: {str(e)}]"
    
    def _extract_json(self, text: str) -> Optional[str]:
        """
        Extract JSON from LLM response, handling markdown code blocks.
        
        Args:
            text: Raw LLM response text
        
        Returns:
            Extracted JSON string or None
        """
        # Remove any leading/trailing whitespace
        text = text.strip()
        
        # Try to find JSON in markdown code blocks
        # Pattern 1: ```json ... ```
        json_block = re.search(r'```(?:json)?\s*(.*?)```', text, re.DOTALL)
        if json_block:
            return json_block.group(1).strip()
        
        # Pattern 2: Just find the JSON object directly
        # Find the first { and last matching }
        start = text.find('{')
        if start != -1:
            # Count braces to find matching end
            depth = 0
            end = start
            for i, char in enumerate(text[start:], start):
                if char == '{':
                    depth += 1
                elif char == '}':
                    depth -= 1
                    if depth == 0:
                        end = i + 1
                        break
            
            if end > start:
                return text[start:end]
        
        # If nothing found, return the whole text
        return text
    
    def parse_strategy_from_nl(self, natural_language: str, auto_fix: bool = True) -> Tuple[bool, Optional[Dict], str, str]:
        """
        Convert natural language description to a strategy JSON.
        
        Args:
            natural_language: The user's natural language strategy description
            auto_fix: Whether to automatically fix/sanitize the strategy
        
        Returns:
            Tuple of (success, strategy_dict, ai_explanation, error_message)
        """
        # Generate the strategy
        success, response, error = self.generate(natural_language)
        
        if not success:
            return False, None, "", error
        
        # Extract JSON from response
        json_str = self._extract_json(response)
        
        if not json_str:
            return False, None, "", "Could not extract JSON from LLM response"
        
        # Parse and validate
        try:
            strategy = json.loads(json_str)
        except json.JSONDecodeError as e:
            return False, None, "", f"Invalid JSON from LLM: {str(e)}"
        
        # Validate
        is_valid, errors, warnings = self.validator.validate_strategy(strategy)
        
        if not is_valid:
            if auto_fix:
                # Try to sanitize/fix
                strategy = self.validator.sanitize_strategy(strategy)
                is_valid, errors, warnings = self.validator.validate_strategy(strategy)
                
                if not is_valid:
                    return False, None, "", f"Could not fix strategy: {'; '.join(errors)}"
            else:
                return False, None, "", f"Invalid strategy: {'; '.join(errors)}"
        
        # Generate explanation
        explanation = self._generate_explanation(strategy)
        
        return True, strategy, explanation, ""
    
    def parse_strategy_from_document(self, document_text: str) -> Tuple[bool, List[Dict], List[str], str]:
        """
        Parse one or more strategies from a document.
        
        Args:
            document_text: Full text content of the document
        
        Returns:
            Tuple of (success, list_of_strategies, list_of_explanations, error_message)
        """
        # For now, treat the whole document as one strategy description
        # Future enhancement: split into sections and parse each
        
        success, strategy, explanation, error = self.parse_strategy_from_nl(document_text)
        
        if success:
            return True, [strategy], [explanation], ""
        else:
            return False, [], [], error
    
    def _generate_explanation(self, strategy: Dict) -> str:
        """
        Generate a plain English explanation of the strategy.
        
        Args:
            strategy: The validated strategy dictionary
        
        Returns:
            Plain English explanation
        """
        explanation_prompt = f"""Explain this trading strategy in plain English for a beginner investor. 
Be concise but thorough. Explain what each condition looks for and why it might be useful.

Strategy JSON:
{json.dumps(strategy, indent=2)}

Provide a clear, numbered explanation of each condition and an overall summary of what this strategy is trying to find."""

        success, response, error = self.generate(explanation_prompt, temperature=0.3)
        
        if success:
            return response.strip()
        else:
            # Fallback to basic explanation
            return self._basic_explanation(strategy)
    
    def _basic_explanation(self, strategy: Dict) -> str:
        """Generate a basic explanation without LLM."""
        lines = [f"**{strategy.get('name', 'Strategy')}**\n"]
        lines.append(strategy.get('description', 'No description provided.'))
        lines.append("\n**Conditions:**")
        
        for i, cond in enumerate(strategy.get('conditions', []), 1):
            lhs = cond.get('lhs', {})
            rhs = cond.get('rhs', {})
            op = cond.get('operator', '?')
            
            lhs_name = lhs.get('name', 'unknown')
            lhs_tf = lhs.get('timeframe', 'daily')
            
            if rhs.get('type') == 'value':
                rhs_str = str(rhs.get('value', '?'))
            else:
                rhs_name = rhs.get('name', 'unknown')
                rhs_tf = rhs.get('timeframe', 'daily')
                rhs_str = f"{rhs_tf} {rhs_name}"
            
            lines.append(f"{i}. {lhs_tf.capitalize()} {lhs_name} {op} {rhs_str}")
        
        return "\n".join(lines)
    
    def generate_strategy_explanation(self, strategy: Dict) -> str:
        """
        Public method to generate explanation for any strategy.
        
        Args:
            strategy: Strategy dictionary
        
        Returns:
            Plain English explanation
        """
        return self._generate_explanation(strategy)


def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from a PDF file."""
    try:
        import PyPDF2
        text = []
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text.append(page.extract_text())
        return "\n".join(text)
    except ImportError:
        raise ImportError("PyPDF2 is required for PDF support. Install with: pip install PyPDF2")
    except Exception as e:
        raise Exception(f"Error reading PDF: {str(e)}")


def extract_text_from_docx(file_path: str) -> str:
    """Extract text from a DOCX file."""
    try:
        from docx import Document
        doc = Document(file_path)
        text = []
        for paragraph in doc.paragraphs:
            text.append(paragraph.text)
        return "\n".join(text)
    except ImportError:
        raise ImportError("python-docx is required for DOCX support. Install with: pip install python-docx")
    except Exception as e:
        raise Exception(f"Error reading DOCX: {str(e)}")


def extract_text_from_file(file_path: str) -> str:
    """
    Extract text from various file formats.
    
    Supported formats: .txt, .pdf, .docx
    """
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext == '.txt':
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    elif ext == '.pdf':
        return extract_text_from_pdf(file_path)
    elif ext == '.docx':
        return extract_text_from_docx(file_path)
    else:
        raise ValueError(f"Unsupported file format: {ext}. Supported: .txt, .pdf, .docx")


# For testing
if __name__ == "__main__":
    client = OllamaClient()
    
    # Check availability
    available, message = client.is_available()
    print(f"Ollama available: {available}")
    print(f"Message: {message}")
    
    if available:
        # Test conversion
        test_input = "Find stocks with RSI less than 30 and price above 100"
        print(f"\nTest input: {test_input}")
        
        success, strategy, explanation, error = client.parse_strategy_from_nl(test_input)
        
        if success:
            print("\n✅ Generated Strategy:")
            print(json.dumps(strategy, indent=2))
            print("\n💡 Explanation:")
            print(explanation)
        else:
            print(f"\n❌ Error: {error}")
