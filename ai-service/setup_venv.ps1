if (Test-Path .venv) {
    Remove-Item -Recurse -Force .venv
}
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install torch --index-url https://download.pytorch.org/whl/cpu
.\.venv\Scripts\python.exe -m pip install transformers sentence-transformers soundfile
.\.venv\Scripts\python.exe -c "import torch; import transformers; import sentence_transformers; import soundfile; print('All imports successful!')"
.\.venv\Scripts\python.exe -m pytest -q
