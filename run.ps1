# Single-command runner for Rajasthan Royals SupeRR Selector
Write-Host "======================================================================" -ForegroundColor Magenta
Write-Host "  Rajasthan Royals: SupeRR Selector Season 2 Pipeline & Dashboard" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Magenta

# Check virtual environment
if (-Not (Test-Path ".venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    uv venv .venv
    uv pip install --python .venv/Scripts/python.exe -r requirements.txt
}

# Run unit tests
Write-Host "`n[Step 1/5] Running Unit Tests..." -ForegroundColor Yellow
.venv\Scripts\python -m pytest src/tests

# Run Pipeline
Write-Host "`n[Step 2/5] Running End-to-End Analytics Pipeline..." -ForegroundColor Yellow
.venv\Scripts\python src/pipeline.py

# Generate Figures
Write-Host "`n[Step 3/5] Generating Publication Figures..." -ForegroundColor Yellow
.venv\Scripts\python src/generate_figures.py

# Export CSVs & Reports
Write-Host "`n[Step 4/5] Generating Top 10 CSVs, Methodology Reports (DOCX & PDF), and Presentation..." -ForegroundColor Yellow
.venv\Scripts\python src/generate_report.py
.venv\Scripts\python src/generate_presentation.py

# Launch Dashboard
Write-Host "`n[Step 5/5] Launching Streamlit Interactive Dashboard..." -ForegroundColor Green
Write-Host "Dashboard will open at http://localhost:8501" -ForegroundColor Cyan
.venv\Scripts\streamlit run app.py
