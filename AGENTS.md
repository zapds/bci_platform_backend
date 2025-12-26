# AGENTS.md - BCI Platform Backend

This document provides comprehensive information for AI agents working on the BCI (Brain-Computer Interface) Platform backend codebase.

## Project Overview

This is a FastAPI-based backend service for a Brain-Computer Interface platform. It handles EEG dataset management, including upload, storage, retrieval, metadata extraction, preprocessing, and visualization of EDF (European Data Format) files.

## Technology Stack

- **Framework**: FastAPI (v0.125.0)
- **EEG Processing**: MNE-Python (v1.11.0) - for reading and analyzing EDF files
- **Data Processing**: Pandas (v2.3.3)
- **Visualization**: Matplotlib (via MNE-Python)
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
│   ├── datasets.py         # Dataset CRUD operations and metadata extraction
│   ├── preprocessing.py    # EEG preprocessing operations (channel selection, montage)
│   └── visualizations.py   # EEG visualization generation (plots, PSD, topomaps)
├── models/
│   ├── dataset.py          # Pydantic models for dataset request/response validation
│   └── preprocessing.py    # Pydantic models for preprocessing request/response validation
├── datasets/               # Storage directory for uploaded datasets
│   ├── {id}.fif            # FIF data files (MNE-Python native format)
│   └── {id}.meta           # JSON metadata files
└── visuals/                # Storage directory for cached visualizations
    └── {id}_{type}.png     # Cached visualization images
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
  - `preprocessing_router` - tagged as "preprocessing"
  - `visualizations_router` - tagged as "visualizations"

### API Endpoints

#### Datasets (`api/datasets.py`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/datasets/new` | Upload a new EDF dataset |
| GET | `/api/datasets` | List all datasets with file metadata |
| GET | `/api/datasets/{id}` | Download a dataset file |
| GET | `/api/datasets/{id}/metadata` | Get EEG metadata extracted from the file |
| DELETE | `/api/datasets/{id}` | Delete a dataset and its metadata |

#### Preprocessing (`api/preprocessing.py`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/preprocessing/{id}/channels` | List all channels in a dataset |
| POST | `/api/preprocessing/{id}/pick_channels` | Select specific channels (manual or all EEG) |
| POST | `/api/preprocessing/{id}/set_montage` | Set electrode montage (default: standard_1020) |

#### Visualizations (`api/visualizations.py`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/datasets/{id}/visualizations/plot` | Get raw EEG plot visualization |
| GET | `/api/datasets/{id}/visualizations/psd` | Get PSD (Power Spectral Density) plot |
| GET | `/api/datasets/{id}/visualizations/psd_topomap` | Get PSD topomap (requires montage) |

## Timeline Navigation & Workflow

### Flexible Stage Navigation

The preprocessing pipeline is designed to allow **non-linear navigation**. Users can navigate to any part of the timeline, skipping any stages in between. This is achieved through:

1. **Immutable Dataset Operations**: Each preprocessing operation creates a new dataset with a new ID, preserving the original data
2. **Independent Stages**: Preprocessing stages are independent and can be applied in any order
3. **Direct Access**: Users can jump directly to any stage without completing prior stages (where technically feasible)

### How It Works

- Each preprocessing operation (e.g., `pick_channels`, `set_montage`) returns a **new dataset ID**
- The original dataset remains unchanged
- Users can branch off from any point in their processing history
- Visualizations can be generated for any dataset at any stage

### Example Workflow

```
Original Dataset (id: abc123)
    ├── pick_channels → New Dataset (id: def456)
    │       └── set_montage → New Dataset (id: ghi789)
    │               └── visualizations...
    └── set_montage → New Dataset (id: jkl012)  # Skip channel selection
            └── visualizations...
```

### Stage Dependencies

While stages can be skipped, some operations have prerequisites:
- **PSD Topomap**: Requires a montage to be set (electrode positions needed)

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

1. **Data File**: `{id}.fif` - The EEG data stored in MNE-Python's native FIF format
2. **Metadata File**: `{id}.meta` - JSON file containing user-provided metadata

**Note**: Users upload EDF files, which are converted to FIF format for internal storage. When downloading, FIF files are exported back to EDF format.

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

- Use `mne.io.read_raw_edf()` for reading uploaded EDF files
- Use `raw.save()` to store data in FIF format (MNE-Python's native format)
- Use `raw.export()` to convert FIF back to EDF for downloads
- Use `preload=False` when only reading metadata to save memory
- Access channel types via `raw.get_channel_types()`
- Access recording info via `raw.info`

### File Format Flow

1. **Upload**: User uploads `.edf` file → converted and stored as `.fif`
2. **Storage**: Data stored internally as `.fif` (MNE-Python native format)
3. **Download**: `.fif` file exported back to `.edf` for user download

### Why FIF Format?

- FIF is MNE-Python's native format, providing better integration with MNE processing pipelines
- Faster read/write operations for MNE-based analysis
- Preserves all MNE-specific metadata and annotations
- Enables future preprocessing and analysis features

### Supported Upload Formats

Currently only `.edf` (European Data Format) files are accepted for upload. Validation occurs on upload.

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
