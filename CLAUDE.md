# Project Rules and Guidelines

## Project Structure

```
insect-detection-cpu-test/
├── detect_insect.py          # Main detection script
├── requirements.txt          # Python dependencies
├── .gitignore               # Git ignore rules
├── README.md                # Project documentation
├── RULES.md                 # This file
├── input_images/            # Input directory (not tracked)
├── output_images/           # Output directory (not tracked)
├── logs/                    # Log files (not tracked)
└── weights/                 # Model weights (not tracked)
```

## Coding Standards

### Python Code Style
- Follow PEP 8 style guidelines
- Use meaningful variable and function names
- Include docstrings for all functions and classes
- Maximum line length: 88 characters (Black formatter)

### File Naming
- Use snake_case for Python files
- Use descriptive names that indicate purpose
- Avoid abbreviations unless commonly understood

## Performance Requirements

- Processing time per image: ≤ 1,000ms (CPU environment)
- Memory usage: Efficient handling of large image batches
- Error handling: Continue processing on individual file failures

## Logging Standards

### Log Format
- CSV format: `filename, detected, count, time_ms`
- Include timestamp in log filename
- Log both to console and file

### Log Levels
- INFO: Normal processing information
- WARNING: Non-critical issues
- ERROR: Processing failures that don't stop execution
- CRITICAL: Fatal errors that stop execution

## Testing Requirements

### Accuracy Metrics
- True positive rate: ≥ 80%
- False positive rate: ≤ 10%
- Test with ≥ 20 sample images

### Stability Testing
- Must process 50 consecutive images without crashes
- Handle various image formats (JPEG, PNG)
- Handle various image resolutions

## Dependencies

### Required Libraries
- Python 3.9+
- PyTorch (CPU version)
- Ultralytics YOLOv8
- OpenCV
- NumPy

### Installation
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### Virtual Environment Information
- **Environment Name**: venv
- **Python Version**: 3.10.12
- **Pip Version**: 22.0.2
- **Location**: `/home/win/work/projetct/insect-detection-cpu-test/venv/`
- **Created**: 2025-06-30

## Usage Guidelines

### Command Line Interface
```bash
python detect_insect.py --input input_images/ --output output_images/
```

### Required Arguments
- `--input`: Input directory containing images
- `--output`: Output directory for processed images

### Optional Arguments
- `--help`: Display usage information
- `--model`: Specify custom model weights path

## File Handling Rules

### Input Files
- Support JPEG and PNG formats
- Process all valid images in input directory
- Skip invalid or corrupted files with warning

### Output Files
- Save as PNG format regardless of input format
- Maintain original resolution
- Use same filename as input with .png extension

## Error Handling

### Exception Management
- Catch and log exceptions for individual files
- Continue processing remaining files
- Provide meaningful error messages
- Exit gracefully on critical errors

### Resource Management
- Close file handles properly
- Clean up temporary resources
- Handle memory efficiently for large batches

## Version Control

### Git Workflow
- Use meaningful commit messages
- Don't commit large files (images, models)
- Keep repository clean and organized

### Ignored Files
- Model weights (*.pt, *.pth)
- Input/output directories
- Log files
- Temporary files
- Python cache files

## Documentation

### Code Documentation
- Include module-level docstrings
- Document all public functions
- Explain complex algorithms
- Provide usage examples

### Project Documentation
- Keep README.md updated
- Document installation steps
- Provide usage examples
- Include troubleshooting guide

## Information Search Guidelines

### Web Search Usage
- Use `mcp__gemini-google-search__google_search` when latest information is needed
- Search for current library versions, API changes, or recent documentation
- Use web search when local information is insufficient or outdated
- Verify information from multiple sources when possible

## Security Guidelines

### Sensitive Information Protection
- **NEVER commit API keys, passwords, or secrets** to version control
- Use environment variables for all sensitive configuration
- Store API keys in `.env` files (which must be in `.gitignore`)
- Use configuration files in `.gitignore` for local settings
- Regularly audit code for accidentally committed secrets

### Files to Never Commit
- API keys (Google, OpenAI, AWS, etc.)
- Database credentials
- Private keys and certificates
- Local configuration files with sensitive data
- `.mcp.json` and similar MCP configuration files
- Any file containing `password`, `secret`, `key`, `token`

### Security Best Practices
- Review all files before committing with `git status` and `git diff`
- Use `.gitignore` to prevent accidental commits of sensitive files
- Revoke and regenerate any accidentally committed secrets immediately
- Implement pre-commit hooks for sensitive data detection
- Store production secrets in secure secret management systems