# AGENTS.md - BCI Platform Backend

This document provides comprehensive information for AI agents working on the BCI (Brain-Computer Interface) Platform backend codebase.

## Project Overview

This is a FastAPI-based backend service for a Brain-Computer Interface platform. It handles EEG dataset management, including upload, storage, retrieval, and metadata extraction from EDF (European Data Format) files.

## Technology Stack

- **Framework**: FastAPI (v0.125.0)
- **EEG Processing**: MNE-Python (v1.11.0) - for reading and analyzing EDF files
- **Data Processing**: Pandas (v2.3.3)
- **Data Validation**: Pydantic (via FastAPI)
- **Language**: Python 3.13+

## File Structure

```
backend/
├── main.py                 # FastAPI application entry point
├── requirements.txt        # Python dependencies
├── test.py                 # Development/testing script (not production)
├── AGENTS.md               # This file
├── api/
│   ├── router.py           # Main API router, aggregates all sub-routers
│   └── datasets.py         # Dataset CRUD operations and metadata extraction
├── models/
│   └── dataset.py          # Pydantic models for request/response validation
└── datasets/               # Storage directory for uploaded datasets
    ├── {id}.edf            # EDF data files
    └── {id}.meta           # JSON metadata files
```

## Architecture

### Entry Point (`main.py`)

- Creates the FastAPI application instance
- Includes the main API router with all routes

### Router Structure (`api/router.py`)

- All API routes are prefixed with `/api`
- Sub-routers are included with tags for OpenAPI documentation
- Current sub-routers:
  - `datasets_router` - tagged as "datasets"

### API Endpoints (`api/datasets.py`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/datasets/new` | Upload a new EDF dataset |
| GET | `/api/datasets` | List all datasets with file metadata |
| GET | `/api/datasets/{id}` | Download a dataset file |
| GET | `/api/datasets/{id}/metadata` | Get EEG metadata extracted from the file |
| DELETE | `/api/datasets/{id}` | Delete a dataset and its metadata |

## Artifact Design

### Artifact ID Generation

Artifacts use an 8-character lowercase base32-encoded UUID:

```python
def generate_artifact_id(length: int = 8) -> str:
    raw = uuid.uuid4().bytes
    b32 = base64.b32encode(raw).decode("ascii").lower()
    return b32[:length]
```

Example IDs: `74pzy7nv`, `a3bc8def`

### File Storage Pattern

Each dataset consists of two files stored in the `datasets/` directory:

1. **Data File**: `{id}.edf` - The raw EDF file containing EEG data
2. **Metadata File**: `{id}.meta` - JSON file containing user-provided metadata

### Metadata File Format (`{id}.meta`)

```json
{
  "original_filename": "recording_session_001.edf"
}
```

The `.meta` file stores metadata that cannot be extracted from the EDF file itself. Currently includes:
- `original_filename`: The original filename provided during upload

### Pydantic Models (`models/dataset.py`)

| Model | Purpose |
|-------|---------|
| `DatasetMetadata` | EEG metadata extracted from file + original filename |
| `DatasetResponse` | Response wrapper with dataset_id and metadata |
| `DatasetUploadResponse` | Response after successful upload |
| `DatasetFileMetadata` | File-level metadata for listing datasets |
| `DatasetDeleteResponse` | Confirmation of deletion |

#### DatasetMetadata Fields

- `original_filename`: Original uploaded filename
- `duration_seconds`: Recording duration
- `sampling_frequency_hz`: Sample rate in Hz
- `time_points`: Number of time samples
- `eeg_channel_count`: Number of EEG channels
- `highpass_hz`: High-pass filter cutoff
- `lowpass_hz`: Low-pass filter cutoff

#### DatasetFileMetadata Fields

- `id`: Artifact ID
- `original_filename`: Original uploaded filename
- `size_bytes`: File size in bytes
- `created_at`: Unix timestamp of creation
- `modified_at`: Unix timestamp of last modification

## Coding Conventions

### File Organization

- **API routes**: Place in `api/` directory, one file per resource
- **Pydantic models**: Place in `models/` directory, grouped by domain
- **Utilities**: Can be added to a `utils/` directory if needed

### Naming Conventions

- **Files**: lowercase with underscores (snake_case)
- **Classes**: PascalCase
- **Functions/Variables**: snake_case
- **Constants**: UPPER_SNAKE_CASE
- **Artifact IDs**: 8-character lowercase alphanumeric

### API Design

- Use RESTful conventions
- All routes prefixed with `/api`
- Use Pydantic models for request/response validation
- Return appropriate HTTP status codes:
  - `200`: Success
  - `400`: Bad request (e.g., invalid file type)
  - `404`: Resource not found

### Error Handling

Use FastAPI's `HTTPException` for API errors:

```python
raise HTTPException(status_code=404, detail="Dataset not found")
```

## EEG/EDF Processing

### MNE-Python Usage

- Use `mne.io.read_raw_edf()` for reading EDF files
- Use `preload=False` when only reading metadata to save memory
- Access channel types via `raw.get_channel_types()`
- Access recording info via `raw.info`

### Supported File Formats

Currently only `.edf` (European Data Format) files are accepted. Validation occurs on upload.

## Adding New Features

### Adding a New API Endpoint

1. Add the route function to the appropriate file in `api/`
2. Create necessary Pydantic models in `models/`
3. If creating a new resource, create a new router and include it in `api/router.py`

### Adding New Metadata Fields

1. Add the field to the relevant Pydantic model in `models/dataset.py`
2. Update `save_metadata()` calls to include new data
3. Update `load_metadata()` consumers to handle the new field
4. Consider backward compatibility for existing `.meta` files

### Adding New Artifact Types

Follow the existing pattern:
1. Create a storage directory (e.g., `models/`, `results/`)
2. Use `generate_artifact_id()` for ID generation
3. Store data file as `{id}.{extension}`
4. Store metadata as `{id}.meta` in JSON format

## Running the Application

```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn main:app --reload

# Or with specific host/port
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Testing

The `test.py` file is a development script for testing MNE functionality. It is not a test suite. When adding proper tests:

- Use pytest as the test framework
- Place tests in a `tests/` directory
- Name test files as `test_*.py`

## Future Considerations

- **Pipeline Processing**: The platform name suggests future EEG processing pipelines
- **Annotations**: The test.py shows annotation handling with MNE, suggesting future support for event markers
- **Additional Formats**: May need to support other EEG formats (BDF, GDF, etc.)
