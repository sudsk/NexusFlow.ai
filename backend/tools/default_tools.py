# backend/tools/default_tools.py
"""
Default tools that can be used by agents in any framework
"""

import json
import logging
import requests
import time
from typing import Dict, Any, Optional, List
from datetime import datetime
import os

logger = logging.getLogger(__name__)

def web_search(params: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Search the web for information
    
    Args:
        params: 
            query (str): The search query
            num_results (int, optional): Number of results to return
        context: Execution context
        
    Returns:
        Dictionary with search results
    """
    query = params.get('query')
    if not query:
        raise ValueError("Query parameter is required")
        
    num_results = params.get('num_results', 5)
    
    # Get API key from environment (or use mock mode for development)
    use_mock = os.environ.get('USE_MOCK_TOOLS', 'false').lower() == 'true'
    search_api_key = os.environ.get('SEARCH_API_KEY')
    
    if use_mock:
        # Mock implementation for development/testing
        logger.info(f"[MOCK] Web search for: {query}")
        time.sleep(1)  # Simulate API delay
        
        mock_results = [
            {
                "title": f"Result 1 for {query}",
                "link": "https://example.com/1",
                "snippet": f"This is a mock search result for {query}. It contains some relevant information about the topic."
            }

def document_retrieval(params: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Retrieve documents from a knowledge base
    
    Args:
        params:
            query (str): Search query for documents
            collection (str, optional): Collection to search
            limit (int, optional): Maximum number of documents to return
        context: Execution context
        
    Returns:
        Dictionary with retrieved documents
    """
    query = params.get('query')
    if not query:
        raise ValueError("Query parameter is required")
        
    collection = params.get('collection', 'default')
    limit = params.get('limit', 5)
    
    # Mock implementation for development/testing
    use_mock = os.environ.get('USE_MOCK_TOOLS', 'false').lower() == 'true'
    
    if use_mock:
        logger.info(f"[MOCK] Document retrieval - Query: {query}, Collection: {collection}")
        time.sleep(1)  # Simulate API delay
        
        mock_docs = [
            {
                "id": "doc-1",
                "title": f"Document about {query}",
                "content": f"This document contains information about {query}. It discusses key concepts and provides examples.",
                "metadata": {
                    "source": "knowledge_base",
                    "created_at": "2024-01-15T10:30:00Z",
                    "collection": collection
                }
            },
            {
                "id": "doc-2",
                "title": f"Understanding {query}",
                "content": f"A comprehensive guide to understanding {query} and related concepts. This document provides in-depth explanations and case studies.",
                "metadata": {
                    "source": "knowledge_base",
                    "created_at": "2024-02-20T14:45:00Z",
                    "collection": collection
                }
            },
            {
                "id": "doc-3",
                "title": f"Best practices for {query}",
                "content": f"Learn about best practices and recommended approaches for working with {query}. This guide includes tips, tricks, and common pitfalls to avoid.",
                "metadata": {
                    "source": "knowledge_base",
                    "created_at": "2024-03-10T09:15:00Z",
                    "collection": collection
                }
            }
        ]
        
        return {
            "query": query,
            "collection": collection,
            "documents": mock_docs[:limit],
            "total": len(mock_docs)
        }
    
    else:
        # In a real implementation, connect to a vector database or knowledge base
        # This is a placeholder for the actual implementation
        logger.warning("Real document retrieval not implemented, using mock data")
        return document_retrieval(params, context)

def image_generation(params: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Generate an image based on a text prompt
    
    Args:
        params:
            prompt (str): Text description of the desired image
            style (str, optional): Style of the image
            size (str, optional): Size of the image (e.g., "512x512")
        context: Execution context
        
    Returns:
        Dictionary with image URL or data
    """
    prompt = params.get('prompt')
    if not prompt:
        raise ValueError("Prompt parameter is required")
        
    style = params.get('style', 'natural')
    size = params.get('size', '512x512')
    
    # Mock implementation for development/testing
    use_mock = os.environ.get('USE_MOCK_TOOLS', 'false').lower() == 'true'
    image_api_key = os.environ.get('IMAGE_API_KEY')
    
    if use_mock or not image_api_key:
        logger.info(f"[MOCK] Image generation - Prompt: {prompt}, Style: {style}")
        time.sleep(2)  # Simulate API delay
        
        # Return a placeholder image URL
        return {
            "prompt": prompt,
            "style": style,
            "size": size,
            "image_url": f"https://placehold.co/{size}?text={prompt[:20]}",
            "mock": True
        }
    
    else:
        # Real implementation using image generation API
        try:
            # Example using a generic image API (replace with your preferred provider)
            api_url = "https://api.image-provider.com/generate"
            headers = {
                "Authorization": f"Bearer {image_api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "prompt": prompt,
                "style": style,
                "size": size
            }
            
            response = requests.post(api_url, headers=headers, json=payload)
            response.raise_for_status()
            
            # Parse response (adjust based on actual API response format)
            api_response = response.json()
            
            return {
                "prompt": prompt,
                "style": style,
                "size": size,
                "image_url": api_response.get("url"),
                "image_id": api_response.get("id")
            }
            
        except Exception as e:
            logger.exception(f"Error in image generation: {str(e)}")
            raise ValueError(f"Image generation failed: {str(e)}")
            
def translation(params: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Translate text from one language to another
    
    Args:
        params:
            text (str): Text to translate
            source_language (str, optional): Source language code
            target_language (str): Target language code
        context: Execution context
        
    Returns:
        Dictionary with translated text
    """
    text = params.get('text')
    if not text:
        raise ValueError("Text parameter is required")
        
    target_language = params.get('target_language')
    if not target_language:
        raise ValueError("Target language parameter is required")
        
    source_language = params.get('source_language', 'auto')
    
    # Mock implementation for development/testing
    use_mock = os.environ.get('USE_MOCK_TOOLS', 'false').lower() == 'true'
    
    if use_mock:
        logger.info(f"[MOCK] Translation - Text: {text[:50]}..., Source: {source_language}, Target: {target_language}")
        time.sleep(1)  # Simulate API delay
        
        # Simple mock translation (just adds language code as prefix)
        translated_text = f"[{target_language}] {text}"
        
        return {
            "original_text": text,
            "translated_text": translated_text,
            "source_language": source_language,
            "target_language": target_language,
            "mock": True
        }
    
    else:
        # Real implementation using translation API
        try:
            # Example using a generic translation API (replace with your preferred provider)
            translation_api_key = os.environ.get('TRANSLATION_API_KEY')
            if not translation_api_key:
                logger.warning("No translation API key configured, using mock response")
                return translation(params, context)
                
            api_url = "https://api.translation-provider.com/translate"
            headers = {
                "Authorization": f"Bearer {translation_api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "text": text,
                "source": source_language,
                "target": target_language
            }
            
            response = requests.post(api_url, headers=headers, json=payload)
            response.raise_for_status()
            
            # Parse response (adjust based on actual API response format)
            api_response = response.json()
            
            return {
                "original_text": text,
                "translated_text": api_response.get("translated_text"),
                "source_language": api_response.get("detected_source") or source_language,
                "target_language": target_language
            }
            
        except Exception as e:
            logger.exception(f"Error in translation: {str(e)}")
            raise ValueError(f"Translation failed: {str(e)}"),
            {
                "title": f"Result 2 for {query}",
                "link": "https://example.com/2",
                "snippet": f"Another mock result with different information about {query}."
            },
            {
                "title": f"Result 3 for {query}",
                "link": "https://example.com/3",
                "snippet": f"A third perspective on {query} with additional details and references."
            }
        ]
        
        # Generate additional mock results if needed
        while len(mock_results) < num_results:
            idx = len(mock_results) + 1
            mock_results.append({
                "title": f"Result {idx} for {query}",
                "link": f"https://example.com/{idx}",
                "snippet": f"Additional information about {query}, point #{idx}."
            })
        
        return {
            "results": mock_results[:num_results],
            "total": num_results,
            "query": query
        }
    
    elif not search_api_key:
        logger.warning("No search API key configured, using mock response")
        # Fall back to mock implementation
        return web_search(params, context)
    
    else:
        # Real implementation using a search API
        try:
            # Example using a generic search API (replace with your preferred provider)
            api_url = "https://api.search-provider.com/search"
            headers = {
                "Authorization": f"Bearer {search_api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "q": query,
                "limit": num_results
            }
            
            response = requests.post(api_url, headers=headers, json=payload)
            response.raise_for_status()
            
            # Parse response (adjust based on actual API response format)
            api_response = response.json()
            
            return {
                "results": api_response.get("items", []),
                "total": api_response.get("total_results", len(api_response.get("items", []))),
                "query": query
            }
            
        except Exception as e:
            logger.exception(f"Error in web search: {str(e)}")
            raise ValueError(f"Search failed: {str(e)}")

def calculate(params: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Perform calculations
    
    Args:
        params:
            expression (str): The mathematical expression to evaluate
        context: Execution context
        
    Returns:
        Dictionary with calculation result
    """
    expression = params.get('expression')
    if not expression:
        raise ValueError("Expression parameter is required")
    
    # Safely evaluate the expression
    try:
        # Very basic implementation for simple calculations only
        # For a production version, use a proper safe math evaluation library
        import math
        
        # Define allowed names/functions
        allowed_names = {
            'abs': abs,
            'round': round,
            'min': min,
            'max': max,
            'sum': sum,
            'pow': pow,
            # Math module functions
            'sin': math.sin,
            'cos': math.cos,
            'tan': math.tan,
            'sqrt': math.sqrt,
            'log': math.log,
            'log10': math.log10,
            'exp': math.exp,
            'floor': math.floor,
            'ceil': math.ceil,
            # Constants
            'pi': math.pi,
            'e': math.e
        }
        
        # Use restricted environment for eval
        result = eval(expression, {"__builtins__": {}}, allowed_names)
        
        return {
            "expression": expression,
            "result": result
        }
    except Exception as e:
        logger.exception(f"Error in calculation: {str(e)}")
        raise ValueError(f"Calculation failed: {str(e)}")

def data_analysis(params: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Analyze data and generate insights
    
    Args:
        params:
            data (List[Dict]): Data to analyze
            analysis_type (str): Type of analysis to perform
        context: Execution context
        
    Returns:
        Dictionary with analysis results
    """
    data = params.get('data')
    if not data:
        raise ValueError("Data parameter is required")
        
    if not isinstance(data, list):
        raise ValueError("Data must be a list")
        
    analysis_type = params.get('analysis_type', 'descriptive')
    
    # Handle different analysis types
    if analysis_type == 'descriptive':
        return _descriptive_analysis(data)
    elif analysis_type == 'exploratory':
        return _exploratory_analysis(data)
    else:
        raise ValueError(f"Unsupported analysis type: {analysis_type}")

def _descriptive_analysis(data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Basic descriptive statistics for tabular data"""
    if not data or len(data) == 0:
        return {"error": "Empty dataset"}
    
    # Get all numeric fields
    first_item = data[0]
    numeric_fields = [
        field for field, value in first_item.items()
        if isinstance(value, (int, float))
    ]
    
    # Calculate statistics for each numeric field
    stats = {}
    for field in numeric_fields:
        values = [item.get(field) for item in data if item.get(field) is not None]
        if values:
            stats[field] = {
                "count": len(values),
                "min": min(values),
                "max": max(values),
                "mean": sum(values) / len(values),
                "sum": sum(values)
            }
            
            # Calculate median
            sorted_values = sorted(values)
            mid = len(sorted_values) // 2
            if len(sorted_values) % 2 == 0:
                stats[field]["median"] = (sorted_values[mid-1] + sorted_values[mid]) / 2
            else:
                stats[field]["median"] = sorted_values[mid]
    
    return {
        "type": "descriptive",
        "record_count": len(data),
        "numeric_fields": numeric_fields,
        "statistics": stats
    }

def _exploratory_analysis(data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """More detailed exploratory analysis"""
    # First get basic descriptive statistics
    base_stats = _descriptive_analysis(data)
    
    if "error" in base_stats:
        return base_stats
    
    # Identify field types
    first_item = data[0]
    field_types = {}
    for field, value in first_item.items():
        if isinstance(value, (int, float)):
            field_types[field] = "numeric"
        elif isinstance(value, str):
            field_types[field] = "string"
        elif isinstance(value, bool):
            field_types[field] = "boolean"
        elif isinstance(value, (list, dict)):
            field_types[field] = "complex"
        else:
            field_types[field] = "unknown"
    
    # Category analysis for string fields
    category_stats = {}
    for field, field_type in field_types.items():
        if field_type == "string":
            value_counts = {}
            for item in data:
                value = item.get(field)
                if value is not None:
                    value_counts[value] = value_counts.get(value, 0) + 1
            
            top_categories = sorted(
                [(value, count) for value, count in value_counts.items()],
                key=lambda x: x[1],
                reverse=True
            )[:5]  # Get top 5
            
            category_stats[field] = {
                "unique_values": len(value_counts),
                "top_categories": dict(top_categories)
            }
    
    # Find correlations between numeric fields
    correlations = {}
    numeric_fields = base_stats.get("numeric_fields", [])
    
    if len(numeric_fields) > 1:
        # Basic correlation calculation
        for i, field1 in enumerate(numeric_fields):
            for field2 in numeric_fields[i+1:]:
                # Extract paired values (both non-None)
                pairs = [
                    (item.get(field1), item.get(field2))
                    for item in data
                    if item.get(field1) is not None and item.get(field2) is not None
                ]
                
                if len(pairs) > 1:
                    # Calculate covariance and correlation
                    x_values = [x for x, y in pairs]
                    y_values = [y for x, y in pairs]
                    
                    x_mean = sum(x_values) / len(x_values)
                    y_mean = sum(y_values) / len(y_values)
                    
                    # Covariance
                    covariance = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, y_values)) / len(pairs)
                    
                    # Standard deviations
                    x_std = (sum((x - x_mean) ** 2 for x in x_values) / len(x_values)) ** 0.5
                    y_std = (sum((y - y_mean) ** 2 for y in y_values) / len(y_values)) ** 0.5
                    
                    # Correlation coefficient
                    correlation = covariance / (x_std * y_std) if x_std > 0 and y_std > 0 else 0
                    
                    correlations[f"{field1}:{field2}"] = round(correlation, 3)
    
    return {
        **base_stats,
        "field_types": field_types,
        "category_stats": category_stats,
        "correlations": correlations
    }

def code_execution(params: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Execute code in a secure sandbox environment
    
    Args:
        params:
            language (str): Programming language ('python' or 'javascript')
            code (str): Code to execute
        context: Execution context
        
    Returns:
        Dictionary with execution result
    """
    language = params.get('language')
    code = params.get('code')
    
    if not language:
        raise ValueError("Language parameter is required")
        
    if not code:
        raise ValueError("Code parameter is required")
        
    if language not in ['python', 'javascript']:
        raise ValueError("Unsupported language. Supported languages: python, javascript")
    
    # In a production environment, this should use a secure sandbox
    # For MVP, we'll use restricted execution with timeouts
    
    # Use mock mode for safety during development
    use_mock = os.environ.get('USE_MOCK_TOOLS', 'false').lower() == 'true'
    allow_execution = os.environ.get('ALLOW_CODE_EXECUTION', 'false').lower() == 'true'
    
    if use_mock:
        # Mock implementation
        logger.info(f"[MOCK] Code execution - Language: {language}")
        logger.info(f"[MOCK] Code: {code}")
        time.sleep(1)  # Simulate execution time
        
        return {
            "language": language,
            "output": f"[MOCK] Execution successful for {language} code. Output would appear here.",
            "success": True
        }
        
    elif not allow_execution:
        logger.warning("Code execution is disabled. Enable with ALLOW_CODE_EXECUTION=true")
        return {
            "language": language,
            "output": "Code execution is disabled for security reasons.",
            "success": False,
            "error": "Execution disabled"
        }
        
    else:
        # Real implementation with security restrictions
        try:
            if language == 'python':
                # Execute Python code with severe restrictions
                import subprocess
                import tempfile
                
                # Create temporary file for code
                with tempfile.NamedTemporaryFile(suffix='.py', mode='w', delete=False) as temp:
                    temp_filename = temp.name
                    temp.write(code)
                
                try:
                    # Execute with timeout and restricted permissions
                    result = subprocess.run(
                        ['python', temp_filename],
                        capture_output=True,
                        text=True,
                        timeout=10,  # 10 second timeout
                        check=False
                    )
                    
                    output = result.stdout
                    error = result.stderr
                    success = result.returncode == 0
                    
                    return {
                        "language": language,
                        "output": output,
                        "error": error if error else None,
                        "success": success
                    }
                    
                finally:
                    # Clean up temp file
                    try:
                        os.unlink(temp_filename)
                    except Exception:
                        pass
                        
            elif language == 'javascript':
                # Execute JavaScript using Node.js
                import subprocess
                import tempfile
                
                # Create temporary file for code
                with tempfile.NamedTemporaryFile(suffix='.js', mode='w', delete=False) as temp:
                    temp_filename = temp.name
                    temp.write(code)
                
                try:
                    # Execute with timeout and restricted permissions
                    result = subprocess.run(
                        ['node', temp_filename],
                        capture_output=True,
                        text=True,
                        timeout=10,  # 10 second timeout
                        check=False
                    )
                    
                    output = result.stdout
                    error = result.stderr
                    success = result.returncode == 0
                    
                    return {
                        "language": language,
                        "output": output,
                        "error": error if error else None,
                        "success": success
                    }
                    
                finally:
                    # Clean up temp file
                    try:
                        os.unlink(temp_filename)
                    except Exception:
                        pass
                        
        except subprocess.TimeoutExpired:
            return {
                "language": language,
                "output": "Execution timed out after 10 seconds",
                "error": "Timeout",
                "success": False
            }
        except Exception as e:
            logger.exception(f"Error in code execution: {str(e)}")
            return {
                "language": language,
                "output": "",
                "error": str(e),
                "success": False
            }
