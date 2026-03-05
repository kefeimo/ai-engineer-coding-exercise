# Archived Investigation Files

This directory contains historical investigation files from the RAGAS + GPT4All compatibility research and early development.

## Investigation Documents

### RAGAS-GPT4ALL-FINDINGS.md
- **Status:** Superseded by INVESTIGATION.md
- **Content:** Initial findings that concluded RAGAS doesn't support GPT4All
- **Outcome:** This conclusion was proven incorrect in later investigation

### RAGAS-GPT4ALL-INVESTIGATION.md
- **Status:** Complete and accurate
- **Content:** Full investigation showing GPT4All DOES work with RAGAS using custom wrapper
- **Breakthrough:** Discovered parameter name mismatch (temperature vs temp) as root cause
- **Result:** Successfully achieved faithfulness score 1.0 with RAGAS 0.2.15 + GPT4All

## Test Scripts (Historical)

### test_ragas_gpt4all.py
- Test script for RAGAS 0.4.3 with GPT4All (failed - requires OpenAI)

### test_ragas_v0.1.py
- Test script for RAGAS 0.1.22 (failed - temperature parameter error)

### test_ragas_v0.2_fixed.py
- **BREAKTHROUGH:** Custom GPT4AllFixed wrapper that converts temperature→temp
- Successfully evaluated with RAGAS 0.2.15

### test_ragas_v0.3.py
- Test script for RAGAS 0.3.9 (hung after 120s)

### run_ragas_baseline_old.py
- Original monolithic script that combined query execution and evaluation
- Replaced by 3-stage pipeline for better separation of concerns

## Setup Scripts

### setup_eval_env.sh
- Shell script to set up evaluation virtual environment
- Created venv-eval and installed dependencies
- Now superseded by manual setup documented in README.md

## Documentation

### README-original.md
- Original README before 3-stage pipeline refactoring
- Historical reference for OpenAI vs GPT4All approach

## Why Archived?

These documents were valuable during research but are now superseded by:
- **Current evaluation approach:** 3-stage pipeline with OpenAI (faster, more reliable)
- **README.md:** Complete documentation of current evaluation system
- **EVALUATION-3-STAGE-WORKFLOW.md:** Step-by-step guide for running evaluations

The GPT4All breakthrough is preserved for historical reference and as a backup evaluation method.

Created: 2026-03-05
