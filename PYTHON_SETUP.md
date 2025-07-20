# Python Setup Guide for StockLift (Python < 3.11)

## Current Issue
You're running Python 3.13.3, but StockLift requires Python < 3.11 for compatibility with the ML libraries.

## Solution Options

### Option 1: Install Python 3.10 (Recommended)

#### Windows:
1. **Download Python 3.10** from [python.org](https://www.python.org/downloads/release/python-3109/)
2. **Install Python 3.10.9** (latest stable 3.10.x version)
3. **Create a virtual environment:**
   ```bash
   # Navigate to your project directory
   cd StockLift-ScriptedByHer-main
   
   # Create virtual environment with Python 3.10
   python3.10 -m venv venv
   
   # Activate virtual environment
   venv\Scripts\activate
   
   # Install requirements
   pip install -r requirements.txt
   ```

#### macOS/Linux:
```bash
# Install Python 3.10 using pyenv (recommended)
pyenv install 3.10.9
pyenv local 3.10.9

# Or using conda
conda create -n stocklift python=3.10
conda activate stocklift

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### Option 2: Use Python 3.9

If Python 3.10 is not available, Python 3.9 is also compatible:

```bash
# Install Python 3.9.18 (latest 3.9.x)
python3.9 -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
```

### Option 3: Use Python 3.8

Python 3.8 is also supported but may require some version adjustments:

```bash
# Install Python 3.8.18 (latest 3.8.x)
python3.8 -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
```

## Verification Steps

1. **Check Python version:**
   ```bash
   python --version
   # Should show Python 3.x.x where x < 11
   ```

2. **Test imports:**
   ```bash
   python -c "import flask, pandas, numpy, sklearn, xgboost, mlxtend; print('All imports successful!')"
   ```

3. **Test Flask app:**
   ```bash
   python -c "from app import app; print('Flask app imported successfully!')"
   ```

## Environment Variables

Set up your environment variables:

```bash
# Windows
set GOOGLE_API_KEY=your-google-api-key

# macOS/Linux
export GOOGLE_API_KEY=your-google-api-key
```

## Running the Application

```bash
# Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# Run the Flask app
python app.py
```

## Troubleshooting

### If you get compilation errors:
- Make sure you're using Python < 3.11
- Try installing pre-compiled wheels: `pip install --only-binary=all -r requirements.txt`
- On Windows, you might need Microsoft Visual C++ Build Tools

### If you get import errors:
- Verify you're in the correct virtual environment
- Check that all packages installed correctly: `pip list`
- Try reinstalling: `pip install --force-reinstall -r requirements.txt`

## Deployment Considerations

For deployment platforms (Render, Vercel, etc.):
- Specify Python version in your deployment configuration
- Use `runtime.txt` file with content: `python-3.10.9`
- Ensure all model files are included in the repository 