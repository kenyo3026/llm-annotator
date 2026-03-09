# Tests Overview

## Test Structure

This project follows the test design from drowcoder and includes a full unit test framework.

```
src/annotator/tests/
├── __init__.py                      # Test module init
├── base.py                          # Test report generation utilities
├── conftest.py                      # pytest config and fixtures
├── test_main.py                     # Main class tests
├── test_multilabel.py               # MultiLabel annotator tests
├── test_zeroshot_multilabel.py      # ZeroShot MultiLabel annotator tests
├── test_utils.py                    # Utility function tests
└── reports/                         # Test reports directory (git ignored)
```

## Test Coverage

### ✅ Full Coverage

**Total: 24 tests**

#### 1. Main Class Tests (8 tests)
- Config loading
- List annotators and models
- Setup MultiLabel annotator
- Setup ZeroShot annotator
- Default annotator setup
- Error handling

#### 2. MultiLabel Annotator Tests (5 tests)
- ✅ Basic annotation
- ✅ Label filtering (only predefined labels returned)
- ✅ Markdown code block parsing
- ✅ Empty tags response
- ✅ Invalid JSON error handling

#### 3. ZeroShot Annotator Tests (8 tests)
- ✅ Annotation with predefined labels
- ✅ Annotation with new label generation
- ✅ max_new_labels limit
- ✅ Zero new labels allowed (max_new_labels=0)
- ✅ All-new-labels scenario
- ✅ Markdown code block parsing
- ✅ Empty tags response
- ✅ Invalid JSON error handling

#### 4. Utility Tests (3 tests)
- Path resolution

## Running Tests

### Option 1: Run with pytest
```bash
# Run all tests
uv run pytest src/annotator/tests/ -v

# Run a specific test file
uv run pytest src/annotator/tests/test_multilabel.py -v

# Run a specific test
uv run pytest src/annotator/tests/test_zeroshot_multilabel.py::TestZeroShotAnnotatorLimits::test_max_new_labels_limit -v
```

### Option 2: Run test file directly (with report generation)
```bash
# Run a single test file and generate report
uv run python src/annotator/tests/test_multilabel.py
uv run python src/annotator/tests/test_zeroshot_multilabel.py

# Reports are saved under src/annotator/tests/reports/
# Filename format: report_{test_name}_{git_sha}_[dirty].log
```

### Option 3: Batch run script
```bash
# Run all tests and show summary
python run_tests.py
```

## Test Reports

Reports include:
- Git commit SHA (for traceability)
- Working directory status (clean/dirty)
- Test execution time
- Detailed test results

Example report filenames:
- `report_multilabel_9b97e058_dirty.log`
- `report_zeroshot_multilabel_9b97e058.log`

## Key Features

### 1. Git-aware report naming
- Auto-detect git commit SHA
- Flag uncommitted changes in working directory
- Easy to correlate test results with code version

### 2. Mock LLM calls
- All tests use mocks to avoid real API calls
- Fast runs, no API key required
- Predictable outcomes

### 3. Broad coverage
- **MultiLabel**: scenarios where only predefined labels can be chosen
- **ZeroShot**: scenarios where new labels can be generated
- Edge cases and error handling

## Test Design Principles

Aligned with drowcoder’s test style:
1. ✅ Use pytest fixtures for test resources
2. ✅ Use mocks to isolate external dependencies
3. ✅ Git-aware report generation
4. ✅ Clear test organization (by feature)
5. ✅ Focused, non-redundant test cases
