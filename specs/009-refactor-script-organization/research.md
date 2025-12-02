# Research: Refactor Script Organization

## Path Reference Updates

### Decision: Use `../repos/` for Repos Directory

**Rationale**: The `repos/` directory has been moved from `project_chat/repos/` to `../repos/` (one level up from project root). All code references need to be updated to use the new relative path.

**Alternatives considered**:
- Absolute paths: Rejected - not portable across environments
- Environment variable: Rejected - unnecessary complexity for simple path change
- Configuration file: Rejected - overkill for a single path reference

### Files Requiring Path Updates

1. **`scripts/index_thn_code.py`**:
   - Line 44: Help text mentions `repos/` directory
   - Update to reference `../repos/` in documentation

2. **`brain_core/thn_code_indexer.py`**:
   - Line 33: `METADATA_DIR = Path("repos/.metadata")` → `Path("../repos/.metadata")`
   - Line 36: `target_dir: str = "repos"` → `target_dir: str = "../repos"`

### File Move Strategy

**Decision**: Direct file moves with no code changes required (except path updates above)

**Rationale**: 
- All scripts are standalone Python files
- They use relative imports that will continue to work
- No import path changes needed for moved scripts
- Only path references to external `repos/` directory need updating

**Alternatives considered**:
- Creating symlinks: Rejected - adds complexity, direct moves are cleaner
- Updating import paths: Rejected - not needed, scripts use relative imports correctly

## Directory Structure

### Decision: Create `tools/` Directory for Audit Tools

**Rationale**: Separates audit/maintenance tools from utility scripts. `audit_conversations.py` is a diagnostic tool, not a utility script.

**Alternatives considered**:
- Keep in root: Rejected - clutters root directory
- Put in `scripts/`: Rejected - audit tools are conceptually different from utility scripts

## Verification Strategy

**Decision**: Manual verification after moves

**Rationale**: 
- Simple file moves require verification that:
  1. Files are in correct locations
  2. Path references updated correctly
  3. Scripts still execute properly
  4. No broken imports

**Alternatives considered**:
- Automated tests: Rejected - overkill for organizational refactoring
- Git mv: Preferred - preserves history and makes changes clear

