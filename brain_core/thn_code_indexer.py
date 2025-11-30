"""
THN code indexing module for parsing and embedding repository code.

Provides functions to:
- Clone and manage THN repositories
- Parse code files (Python, shell, config)
- Generate embeddings for code chunks
- Store chunks and embeddings in code_index table
"""
import ast
import json
import logging
import os
import re
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Any

try:
    import git
except ImportError:
    git = None
    logging.warning("GitPython not installed. Repository cloning will not work.")

from psycopg2.extras import Json

from .db import get_conn
from .embedding_service import generate_embedding

logger = logging.getLogger(__name__)

# Repository metadata storage path
METADATA_DIR = Path("repos/.metadata")


def clone_repository(repository_url: str, repository_name: str, target_dir: str = "repos") -> str:
    """
    Clone a Git repository into the repos directory.
    
    Args:
        repository_url: Git repository URL (SSH or HTTPS)
        repository_name: Name identifier for the repository
        target_dir: Base directory for repositories (default: "repos")
    
    Returns:
        Local path to cloned repository
    
    Raises:
        ValueError: If repository_url is invalid or git is not available
        Exception: If clone fails (network, authentication, etc.)
    """
    if git is None:
        raise ValueError("GitPython not installed. Install with: pip install gitpython")
    
    target_path = Path(target_dir) / repository_name
    
    if target_path.exists():
        logger.warning(f"Repository {repository_name} already exists at {target_path}")
        return str(target_path)
    
    try:
        logger.info(f"Cloning repository {repository_name} from {repository_url}")
        repo = git.Repo.clone_from(repository_url, str(target_path))
        logger.info(f"Successfully cloned {repository_name} to {target_path}")
        return str(target_path)
    except git.exc.GitCommandError as e:
        logger.error(f"Failed to clone repository: {e}")
        raise Exception(f"Failed to clone repository: {e}")
    except Exception as e:
        logger.error(f"Unexpected error cloning repository: {e}")
        raise


def update_repository(repository_path: str) -> bool:
    """
    Update an existing repository (pull latest changes).
    
    Args:
        repository_path: Local path to repository
    
    Returns:
        True if update succeeded, False otherwise
    """
    if git is None:
        logger.error("GitPython not installed")
        return False
    
    try:
        repo = git.Repo(repository_path)
        
        # Check for uncommitted changes
        if repo.is_dirty():
            logger.warning(f"Repository {repository_path} has uncommitted changes")
        
        # Pull latest changes
        repo.remotes.origin.pull()
        logger.info(f"Successfully updated repository {repository_path}")
        return True
    except git.exc.GitCommandError as e:
        logger.error(f"Failed to update repository: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error updating repository: {e}")
        return False


def load_repository_metadata(repository_name: str) -> Optional[Dict[str, Any]]:
    """
    Load repository metadata from file.
    
    Args:
        repository_name: Name of the repository
    
    Returns:
        Metadata dict or None if not found
    """
    metadata_file = METADATA_DIR / f"{repository_name}.json"
    if not metadata_file.exists():
        return None
    
    try:
        with open(metadata_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load metadata for {repository_name}: {e}")
        return None


def save_repository_metadata(repository_name: str, metadata: Dict[str, Any]) -> None:
    """
    Save repository metadata to file.
    
    Args:
        repository_name: Name of the repository
        metadata: Metadata dict to save
    """
    METADATA_DIR.mkdir(parents=True, exist_ok=True)
    metadata_file = METADATA_DIR / f"{repository_name}.json"
    
    try:
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        logger.debug(f"Saved metadata for {repository_name}")
    except Exception as e:
        logger.error(f"Failed to save metadata for {repository_name}: {e}")


def get_repository_commit_hash(repository_path: str) -> Optional[str]:
    """
    Get the current commit hash of a repository.
    
    Args:
        repository_path: Local path to repository
    
    Returns:
        Commit hash string or None if error
    """
    if git is None:
        return None
    
    try:
        repo = git.Repo(repository_path)
        return repo.head.commit.hexsha
    except Exception as e:
        logger.error(f"Failed to get commit hash: {e}")
        return None


def scan_code_files(repository_path: str) -> List[Dict[str, str]]:
    """
    Scan repository for code files to index.
    
    Args:
        repository_path: Local path to repository
    
    Returns:
        List of dicts with 'path' and 'language' keys
    """
    code_files = []
    repo_path = Path(repository_path)
    
    # File extensions to include
    python_extensions = {'.py'}
    shell_extensions = {'.sh', '.bash', '.zsh'}
    config_extensions = {'.yaml', '.yml', '.json', '.toml', '.conf', '.cfg'}
    
    all_extensions = python_extensions | shell_extensions | config_extensions
    
    # Directories to exclude
    exclude_dirs = {'.git', '__pycache__', '.venv', 'venv', 'node_modules', '.idea', '.vscode'}
    
    for root, dirs, files in os.walk(repo_path):
        # Filter out excluded directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for file in files:
            file_path = Path(root) / file
            relative_path = file_path.relative_to(repo_path)
            
            # Check if file has code extension
            if file_path.suffix.lower() in all_extensions:
                language = detect_language(str(file_path))
                if language:
                    code_files.append({
                        'path': str(relative_path),
                        'language': language,
                        'full_path': str(file_path)
                    })
    
    logger.info(f"Found {len(code_files)} code files in {repository_path}")
    return code_files


def detect_language(file_path: str) -> Optional[str]:
    """
    Detect programming language from file path and extension.
    
    Args:
        file_path: Path to file
    
    Returns:
        Language identifier (python, bash, yaml, etc.) or None
    """
    path = Path(file_path)
    ext = path.suffix.lower()
    
    # Python files
    if ext == '.py':
        return 'python'
    
    # Shell scripts
    if ext in {'.sh', '.bash', '.zsh'}:
        return 'bash'
    
    # Config files
    if ext in {'.yaml', '.yml'}:
        return 'yaml'
    if ext == '.json':
        return 'json'
    if ext == '.toml':
        return 'toml'
    if ext in {'.conf', '.cfg'}:
        return 'config'
    
    # Check shebang for shell scripts
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            first_line = f.readline().strip()
            if first_line.startswith('#!'):
                if 'bash' in first_line or 'sh' in first_line:
                    return 'bash'
                if 'python' in first_line:
                    return 'python'
    except Exception:
        pass
    
    return None


def parse_python_file(file_path: str) -> List[Dict[str, Any]]:
    """
    Parse Python file using AST to extract functions and classes.
    
    Args:
        file_path: Path to Python file
    
    Returns:
        List of code chunks with metadata
    """
    chunks = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            tree = ast.parse(content, filename=file_path)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                # Extract function
                start_line = node.lineno
                end_line = node.end_lineno if hasattr(node, 'end_lineno') else start_line
                
                # Get function source
                lines = content.split('\n')
                function_lines = lines[start_line - 1:end_line]
                function_text = '\n'.join(function_lines)
                
                # Extract docstring
                docstring = ast.get_docstring(node)
                
                chunks.append({
                    'chunk_text': function_text,
                    'metadata': {
                        'function_name': node.name,
                        'line_start': start_line,
                        'line_end': end_line,
                        'docstring': docstring,
                        'is_async': isinstance(node, ast.AsyncFunctionDef)
                    }
                })
            
            elif isinstance(node, ast.ClassDef):
                # Extract class
                start_line = node.lineno
                end_line = node.end_lineno if hasattr(node, 'end_lineno') else start_line
                
                lines = content.split('\n')
                class_lines = lines[start_line - 1:end_line]
                class_text = '\n'.join(class_lines)
                
                # Extract docstring
                docstring = ast.get_docstring(node)
                
                chunks.append({
                    'chunk_text': class_text,
                    'metadata': {
                        'class_name': node.name,
                        'line_start': start_line,
                        'line_end': end_line,
                        'docstring': docstring
                    }
                })
        
        logger.debug(f"Parsed {len(chunks)} chunks from {file_path}")
        return chunks
        
    except SyntaxError as e:
        logger.warning(f"Syntax error in {file_path}: {e}. Using fallback parsing.")
        # Fallback to line-based chunking
        return parse_file_lines(file_path, 'python')
    except Exception as e:
        logger.error(f"Error parsing Python file {file_path}: {e}")
        return []


def parse_shell_file(file_path: str) -> List[Dict[str, Any]]:
    """
    Parse shell script to extract functions.
    
    Args:
        file_path: Path to shell script
    
    Returns:
        List of code chunks with metadata
    """
    chunks = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        current_function = None
        function_start = None
        function_lines = []
        
        for i, line in enumerate(lines, 1):
            # Match function definition: function_name() { or function function_name {
            func_match = re.match(r'^\s*(function\s+)?(\w+)\s*\(\)\s*\{?', line)
            if func_match:
                # Save previous function if exists
                if current_function and function_lines:
                    chunks.append({
                        'chunk_text': ''.join(function_lines),
                        'metadata': {
                            'function_name': current_function,
                            'line_start': function_start,
                            'line_end': i - 1
                        }
                    })
                
                # Start new function
                current_function = func_match.group(2)
                function_start = i
                function_lines = [line]
            elif current_function:
                function_lines.append(line)
                # Check for function end (closing brace on its own line)
                if line.strip() == '}' and current_function:
                    chunks.append({
                        'chunk_text': ''.join(function_lines),
                        'metadata': {
                            'function_name': current_function,
                            'line_start': function_start,
                            'line_end': i
                        }
                    })
                    current_function = None
                    function_lines = []
        
        # Handle function that doesn't close before end of file
        if current_function and function_lines:
            chunks.append({
                'chunk_text': ''.join(function_lines),
                'metadata': {
                    'function_name': current_function,
                    'line_start': function_start,
                    'line_end': len(lines)
                }
            })
        
        # If no functions found, create a single chunk for the whole file
        if not chunks:
            chunks.append({
                'chunk_text': ''.join(lines),
                'metadata': {
                    'line_start': 1,
                    'line_end': len(lines)
                }
            })
        
        logger.debug(f"Parsed {len(chunks)} chunks from {file_path}")
        return chunks
        
    except Exception as e:
        logger.error(f"Error parsing shell file {file_path}: {e}")
        return []


def parse_config_file(file_path: str, language: str) -> List[Dict[str, Any]]:
    """
    Parse config file (YAML, JSON, TOML) to extract sections.
    
    Args:
        file_path: Path to config file
        language: Config language (yaml, json, toml)
    
    Returns:
        List of code chunks with metadata
    """
    chunks = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if language == 'json':
            # For JSON, try to extract top-level keys as sections
            try:
                data = json.loads(content)
                for key, value in data.items():
                    chunk_text = json.dumps({key: value}, indent=2)
                    chunks.append({
                        'chunk_text': chunk_text,
                        'metadata': {
                            'section': key,
                            'line_start': 1,
                            'line_end': len(content.split('\n'))
                        }
                    })
            except json.JSONDecodeError:
                # Invalid JSON, use whole file
                chunks.append({
                    'chunk_text': content,
                    'metadata': {
                        'line_start': 1,
                        'line_end': len(content.split('\n'))
                    }
                })
        else:
            # For YAML/TOML, use whole file as single chunk
            # Could be enhanced to parse sections, but keeping it simple for now
            chunks.append({
                'chunk_text': content,
                'metadata': {
                    'line_start': 1,
                    'line_end': len(content.split('\n'))
                }
            })
        
        logger.debug(f"Parsed {len(chunks)} chunks from {file_path}")
        return chunks
        
    except Exception as e:
        logger.error(f"Error parsing config file {file_path}: {e}")
        return []


def parse_file_lines(file_path: str, language: str) -> List[Dict[str, Any]]:
    """
    Fallback parser: chunk file by lines (for unsupported languages or parse errors).
    
    Args:
        file_path: Path to file
        language: Language identifier
    
    Returns:
        List of code chunks (single chunk for whole file)
    """
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        lines = content.split('\n')
        
        # Create chunks of ~100 lines each
        chunk_size = 100
        chunks = []
        
        for i in range(0, len(lines), chunk_size):
            chunk_lines = lines[i:i + chunk_size]
            chunk_text = '\n'.join(chunk_lines)
            
            chunks.append({
                'chunk_text': chunk_text,
                'metadata': {
                    'line_start': i + 1,
                    'line_end': min(i + chunk_size, len(lines)),
                    'chunk_index': i // chunk_size
                }
            })
        
        logger.debug(f"Created {len(chunks)} line-based chunks from {file_path}")
        return chunks
        
    except Exception as e:
        logger.error(f"Error parsing file lines {file_path}: {e}")
        return []


def parse_code_file(file_path: str, language: str) -> List[Dict[str, Any]]:
    """
    Parse a code file and extract chunks with metadata.
    
    Routes to language-specific parsers.
    
    Args:
        file_path: Path to code file
        language: Programming language (python, bash, yaml, etc.)
    
    Returns:
        List of code chunks with metadata
    """
    if language == 'python':
        return parse_python_file(file_path)
    elif language == 'bash':
        return parse_shell_file(file_path)
    elif language in {'yaml', 'json', 'toml', 'config'}:
        return parse_config_file(file_path, language)
    else:
        # Fallback to line-based chunking
        logger.debug(f"Using line-based parsing for {language} file {file_path}")
        return parse_file_lines(file_path, language)


def generate_code_embedding(chunk_text: str, metadata: Dict[str, Any]) -> List[float]:
    """
    Generate embedding for a code chunk with context.
    
    Combines chunk text with metadata (file path, function name) for better context.
    
    Args:
        chunk_text: The code chunk text
        metadata: Chunk metadata (file path, function name, etc.)
    
    Returns:
        1536-dimensional embedding vector
    """
    # Build context string with metadata
    context_parts = []
    
    if 'file_path' in metadata:
        context_parts.append(f"File: {metadata['file_path']}")
    if 'function_name' in metadata:
        context_parts.append(f"Function: {metadata['function_name']}")
    if 'class_name' in metadata:
        context_parts.append(f"Class: {metadata['class_name']}")
    if 'docstring' in metadata and metadata['docstring']:
        context_parts.append(f"Description: {metadata['docstring']}")
    
    context = "\n".join(context_parts)
    
    # Combine context with code
    if context:
        combined_text = f"{context}\n\n{chunk_text}"
    else:
        combined_text = chunk_text
    
    # Generate embedding
    return generate_embedding(combined_text)


def store_code_chunk(
    repository_name: str,
    file_path: str,
    language: str,
    chunk_text: str,
    chunk_metadata: Dict[str, Any],
    embedding: Optional[List[float]] = None,
    production_targets: Optional[List[str]] = None
) -> uuid.UUID:
    """
    Store a code chunk in the code_index table.
    
    Args:
        repository_name: Name of the repository
        file_path: Relative path from repository root
        language: Programming language
        chunk_text: The code chunk text
        chunk_metadata: Additional metadata (JSONB)
        embedding: Optional embedding vector (if None, will be generated)
        production_targets: Optional list of production machine names
    
    Returns:
        UUID of the stored chunk
    """
    chunk_id = uuid.uuid4()
    
    # Generate embedding if not provided
    if embedding is None:
        try:
            # Include file_path in metadata for embedding context
            embedding_metadata = chunk_metadata.copy()
            embedding_metadata['file_path'] = file_path
            embedding = generate_code_embedding(chunk_text, embedding_metadata)
        except Exception as e:
            logger.error(f"Failed to generate embedding for chunk: {e}")
            embedding = None
    
    # Convert embedding to string format for PostgreSQL
    embedding_str = None
    if embedding:
        embedding_str = '[' + ','.join(str(x) for x in embedding) + ']'
    
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO code_index (
                    id, repository_name, file_path, language, chunk_text,
                    chunk_metadata, embedding, production_targets, indexed_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s::vector, %s, now())
                """,
                (
                    str(chunk_id),
                    repository_name,
                    file_path,
                    language,
                    chunk_text,
                    Json(chunk_metadata) if chunk_metadata else None,
                    embedding_str,
                    production_targets
                )
            )
            conn.commit()
    
    logger.debug(f"Stored code chunk {chunk_id} from {file_path}")
    return chunk_id


def index_repository(
    repository_path: str,
    repository_name: str,
    production_targets: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Index all code files in a repository, generating embeddings and storing in database.
    
    Args:
        repository_path: Local filesystem path to repository root
        repository_name: Name identifier for the repository
        production_targets: Optional list of production machine names where this code runs
    
    Returns:
        Dict with statistics about indexing
    """
    stats = {
        'files_processed': 0,
        'chunks_created': 0,
        'embeddings_generated': 0,
        'errors': []
    }
    
    try:
        # Load existing metadata to check for incremental updates
        metadata = load_repository_metadata(repository_name)
        last_commit = get_repository_commit_hash(repository_path)
        
        # Check if repository needs re-indexing
        if metadata and metadata.get('last_indexed_commit') == last_commit:
            logger.info(f"Repository {repository_name} already indexed at commit {last_commit}")
            return stats
        
        # Scan for code files
        code_files = scan_code_files(repository_path)
        stats['files_processed'] = len(code_files)
        
        # Process files and generate chunks
        all_chunks = []
        for file_info in code_files:
            try:
                chunks = parse_code_file(file_info['full_path'], file_info['language'])
                for chunk in chunks:
                    chunk['file_path'] = file_info['path']
                    chunk['language'] = file_info['language']
                    chunk['full_path'] = file_info['full_path']
                all_chunks.extend(chunks)
            except Exception as e:
                error_msg = f"Error processing {file_info['path']}: {e}"
                logger.error(error_msg)
                stats['errors'].append(error_msg)
        
        stats['chunks_created'] = len(all_chunks)
        
        # Batch process embeddings (50 chunks per batch with 1s delay)
        batch_size = 50
        delay_seconds = 1
        
        for i in range(0, len(all_chunks), batch_size):
            batch = all_chunks[i:i + batch_size]
            logger.info(f"Processing batch {i // batch_size + 1} ({len(batch)} chunks)")
            
            for chunk in batch:
                try:
                    # Generate embedding with metadata context
                    embedding_metadata = chunk['metadata'].copy()
                    embedding_metadata['file_path'] = chunk['file_path']
                    embedding = generate_code_embedding(chunk['chunk_text'], embedding_metadata)
                    
                    # Store chunk
                    store_code_chunk(
                        repository_name=repository_name,
                        file_path=chunk['file_path'],
                        language=chunk['language'],
                        chunk_text=chunk['chunk_text'],
                        chunk_metadata=chunk['metadata'],
                        embedding=embedding,
                        production_targets=production_targets
                    )
                    
                    stats['embeddings_generated'] += 1
                except Exception as e:
                    error_msg = f"Error storing chunk from {chunk['file_path']}: {e}"
                    logger.error(error_msg)
                    stats['errors'].append(error_msg)
            
            # Delay between batches (except for last batch)
            if i + batch_size < len(all_chunks):
                import time
                time.sleep(delay_seconds)
        
        # Update repository metadata
        from datetime import datetime
        save_repository_metadata(repository_name, {
            'name': repository_name,
            'local_path': repository_path,
            'last_indexed_commit': last_commit,
            'last_indexed_at': datetime.utcnow().isoformat() + 'Z',
            'production_targets': production_targets
        })
        
        logger.info(f"Indexing complete for {repository_name}: {stats}")
        return stats
        
    except Exception as e:
        error_msg = f"Failed to index repository {repository_name}: {e}"
        logger.error(error_msg)
        stats['errors'].append(error_msg)
        return stats

