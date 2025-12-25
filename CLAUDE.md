# Project Rules and Guidelines

## Project Requirements

### Base Project Information
- **Base Repository**: https://github.com/Murasan201/insect-detection-training
- **Current Repository**: https://github.com/Murasan201/12-002-insect-observer-logger
- **Project Evolution**: This project extends the base insect detection system to add activity monitoring capabilities

### Current Project Scope
- **Primary Goal**: Develop an insect activity measurement application based on the existing detection system
- **Extension Features**: Add logging, monitoring, and analysis capabilities for insect behavior observation
- **Target Application**: Real-time or batch processing of insect activity data with quantitative metrics

### Requirements Specification
- **Base requirements defined in**: `docs/requirements/insect_detection_application_test_project_requirements_spec.md`
- **Current project requirements defined in**: `docs/requirements/12-002_昆虫自動観察＆ログ記録アプリ_要件定義書.md`
- **MUST review both documents before starting any work**
- Base document contains detailed functional and non-functional requirements for the detection system
- Current document contains specific requirements for insect activity monitoring and logging application
- Provides context for all development decisions

### Design Documents Structure
- **All design documents are organized under `docs/design/` following the standard document management structure**
- **Document Management Standard**: Follow `docs/document_management_standards.md` for all documentation work
- **Basic Design Documents** (under `docs/design/basic_design/`):
  - System Architecture Design - Overall system structure and component relationships
  - Hardware Design - Hardware specifications, electrical design, and physical configuration
  - Data Design - Data models, file formats, quality management, and lifecycle policies
  - Interface Design - User interfaces, module APIs, external integrations, and hardware interfaces
- **Detailed Design Documents** (under `docs/design/detailed_design/`):
  - Software Design - Software modules, APIs, classes, and implementation details
  - Class Diagram Design - PlantUML class diagrams and relationships
- **MUST review both basic and detailed design documents before implementation**
- All design documents are written in Japanese with English filenames
- These documents provide comprehensive technical specifications for the development phase

## Project Structure

```
12-002-insect-observer-logger/
├── CLAUDE.md                # Project rules and guidelines (this file)
├── LICENSE                  # Project license
├── requirements.txt         # Python dependencies
├── detect_insect.py         # Legacy detection script (batch processing)
├── detector.py              # New detection module
├── train_yolo.py           # Training script
├── book_integration.py     # Book integration utilities
├── yolov8_training_colab.ipynb # Training notebook
├── test_camera_detection.py  # Camera-based detection test module
├── test_simple_realtime.py   # Real-time detection with desktop display
├── test_libcamera_yolo.py    # File-based detection with libcamera
├── test_*.py                # Other camera test modules
├── run_test_camera.sh       # Camera test wrapper script
├── docs/                   # ★ All documentation (following standard structure)
│   ├── index.md            # Document index
│   ├── README.md           # Documentation guide
│   ├── document_management_standards.md # ★ Standard documentation rules
│   ├── troubleshooting.md  # ★ Troubleshooting guide for camera issues
│   ├── requirements/       # Requirements documents
│   ├── specifications/     # System specifications
│   ├── design/            # Design documents
│   │   ├── basic_design/  # Basic design documents
│   │   └── detailed_design/ # Detailed design documents
│   ├── deployment/        # Deployment guides
│   ├── operations/        # Operations guides
│   ├── testing/           # Test documents
│   ├── research/          # Research materials
│   └── references/        # Reference materials
├── models/                # ★ Data model classes
│   ├── detection_models.py
│   ├── activity_models.py
│   └── system_models.py
├── config/                # ★ Configuration management
│   ├── config_manager.py
│   └── system_config.json
├── utils/                 # ★ Utility modules
│   ├── data_validator.py
│   └── file_naming.py
├── production/                 # ★ Production environment scripts and data
│   ├── insect_detection_logs/  # Real-world long-duration logging data
│   └── *.py                    # Production-ready observation scripts
├── input_images/          # Input directory (not tracked)
├── output_images/         # Output directory (not tracked)
├── logs/                  # Log files (not tracked)
└── weights/               # Model weights (not tracked)
```

## Test Modules

### Camera Detection Test Module
- **File**: `test_camera_detection.py`
- **Purpose**: Single-function test script for real-time object detection using camera input
- **Usage**: For testing and validating YOLOv8 model performance with live camera feed
- **Detailed Usage**: See `software_design.md` for comprehensive usage instructions and parameters

### Production Environment Directory
The `production/` directory contains all scripts and data used in the actual production environment (Raspberry Pi with Camera Module 3).

- **Purpose**: Production-ready scripts and real observation data
- **Scripts**:
  - `test_logging_left_half.py` - Long-duration logging script (main production script)
  - `test_camera_left_half_realtime.py` - Real-time detection with left-half area
  - `visualize_detection_data.py` - Data visualization tool
- **Data Location**: `production/insect_detection_logs/`
- **Data Files**:
  - `left_half_detection_log_*.csv` - Long-duration detection logs (8-9 hours each)
  - `insect_detection_log_*.csv` - Detection test logs
  - `*_metadata_*.json` - Session metadata files
  - `*.png` - Visualization graphs
- **Note**: This directory is the source of truth for production environment operations

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

### System Environment Information
- **Python Version**: 3.10.12 (System Level)
- **Pip Version**: 22.0.2
- **Installation Type**: User-level packages (pip install --user)
- **Package Location**: `/home/win/.local/lib/python3.10/site-packages/`
- **System**: Linux WSL2 (Ubuntu)
- **Architecture**: x86_64
- **Last Updated**: 2025-07-04

### Installed Key Packages
- **torch**: 2.7.1 (Deep Learning Framework)
- **torchvision**: 0.22.1 (Computer Vision)
- **ultralytics**: 8.3.162 (YOLOv8 Implementation)
- **opencv-python**: 4.11.0.86 (Computer Vision)
- **numpy**: 2.2.6 (Numerical Computing)
- **pandas**: 2.3.0 (Data Analysis)

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
- Don't commit large files (images, models, datasets)
- Keep repository clean and organized

### Dataset Management
- **NEVER commit dataset files to GitHub**
- Datasets are excluded via .gitignore due to:
  - Large file sizes (500+ images)
  - License considerations (CC BY 4.0 attribution requirements)
  - Repository efficiency (focus on code, not data)
- Use external storage or download scripts for dataset distribution

### Ignored Files
- **Model weights (*.pt, *.pth, *.onnx)** - Store in Hugging Face instead
- Input/output directories
- Log files
- Temporary files
- Python cache files
- **Dataset files (datasets/, *.jpg, *.png, *.txt, data.yaml)**
- **dev-memo.md** - Personal development memo (not tracked)

### Model File Distribution Policy

**IMPORTANT: Model files must NOT be uploaded to GitHub**

#### Rationale
- **License Compliance**: Trained models inherit AGPL-3.0 from YOLOv8
- **File Size**: Model files (6.3MB+) approach GitHub's recommended limits
- **Distribution Strategy**: Hugging Face Model Hub is optimized for ML models
- **Commercial Safety**: Separation maintains MIT license for codebase

#### Approved Distribution Method
- **GitHub Repository**: Source code, training scripts, documentation (MIT License)
- **Hugging Face Model Hub**: Trained model weights with proper AGPL-3.0 attribution
- **Book Integration**: Programmatic download via `huggingface_hub` library

#### Fine-tuned Model Repository
- **Model Location**: https://huggingface.co/Murasan/beetle-detection-yolov8
- **License**: AGPL-3.0 (inherited from YOLOv8)
- **Available Formats**: PyTorch (.pt), ONNX (.onnx)
- **Performance**: mAP@0.5: 97.63%, mAP@0.5:0.95: 89.56%

#### Prohibited Actions
- ❌ Committing model files (*.pt, *.pth, *.onnx) to GitHub
- ❌ Using Git LFS for model storage
- ❌ Distributing models without proper AGPL-3.0 compliance
- ❌ Mixing model files with MIT-licensed codebase

#### Implementation
```python
# Correct approach - Reference external models
from huggingface_hub import hf_hub_download

model_path = hf_hub_download(
    repo_id="Murasan/beetle-detection-yolov8",
    filename="best.pt",
    local_dir="./weights"
)
```

## Documentation

### Document Management Standards
- **MUST follow the standards defined in `docs/document_management_standards.md`**
- **All documentation MUST be consolidated under the `docs/` directory** - Do NOT place .md files in the project root (except README.md and CLAUDE.md)
- All documentation MUST be organized under the `docs/` directory structure
- Use standardized naming conventions for all documents
- Separate basic design documents from detailed design documents
- Maintain document index and cross-references
- **docs/README.md serves as the master index** for all documentation

### Code Documentation
- Include module-level docstrings
- Document all public functions
- Explain complex algorithms
- Provide usage examples

### Project Documentation Structure
- **Document Index**: `docs/index.md` - Central reference for all documents
- **Requirements**: Store in `docs/requirements/` directory
- **Basic Design**: Store in `docs/design/basic_design/` directory
- **Detailed Design**: Store in `docs/design/detailed_design/` directory
- **Deployment Guides**: Store in `docs/deployment/` directory
- **Operations Guides**: Store in `docs/operations/` directory

### Project Documentation
- Keep README.md updated
- **README.md must be written in English**
- Document installation steps
- Provide usage examples
- Include troubleshooting guide
- **All technical documents must follow the document management standards**
- **Implementation progress is tracked in `docs/README.md`** - Contains completed phases and next steps

## Information Search Guidelines

### Web Search Usage
- **ALWAYS use `mcp__gemini-google-search__google_search` for web searches** (MCP Google search agent)
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
- GitHub personal access tokens and authentication credentials
- Email addresses used for GitHub authentication
- Git configuration files containing personal information

### Security Best Practices
- Review all files before committing with `git status` and `git diff`
- Use `.gitignore` to prevent accidental commits of sensitive files
- Revoke and regenerate any accidentally committed secrets immediately
- Implement pre-commit hooks for sensitive data detection
- Store production secrets in secure secret management systems

## Subagent Guidelines

### Model Selection
- **ALWAYS use `sonnet` model for subagents** when using the Task tool
- Sonnet provides optimal balance of speed and capability for code tasks
- Only use `opus` for complex architectural decisions requiring deep reasoning
- Use `haiku` for simple, quick tasks like file searches