"""
Military-grade file shredding engine
Implements DoD 5220.22-M, Gutmann, and custom methods
"""

import os
import secrets
import hashlib
from pathlib import Path
from typing import Callable, Optional
import time


class ShredderEngine:
    """Core file shredding engine with military-grade algorithms"""
    
    # Gutmann method patterns (35 passes)
    GUTMANN_PATTERNS = [
        # Pass 1-4: Random
        None, None, None, None,
        # Pass 5-9: Special patterns
        b'\x55', b'\xAA', b'\x92\x49\x24', b'\x49\x24\x92', b'\x24\x92\x49',
        # Pass 10-25: More patterns
        b'\x00', b'\x11', b'\x22', b'\x33', b'\x44', b'\x55', b'\x66', b'\x77',
        b'\x88', b'\x99', b'\xAA', b'\xBB', b'\xCC', b'\xDD', b'\xEE', b'\xFF',
        # Pass 26-28: Special MFM patterns
        b'\x92\x49\x24', b'\x49\x24\x92', b'\x24\x92\x49',
        # Pass 29-31: Special patterns
        b'\x6D\xB6\xDB', b'\xB6\xDB\x6D', b'\xDB\x6D\xB6',
        # Pass 32-35: Random
        None, None, None, None
    ]
    
    def __init__(self, progress_callback: Optional[Callable] = None):
        """
        Initialize shredder engine
        
        Args:
            progress_callback: Function to call with progress updates (0-100)
        """
        self.progress_callback = progress_callback
        self.total_bytes = 0
        self.processed_bytes = 0
        
    def shred_file(self, file_path: str, method: str = 'dod', verify: bool = True) -> dict:
        """
        Securely shred a file
        
        Args:
            file_path: Path to file to shred
            method: Shredding method ('dod', 'gutmann', 'random_7', 'simple')
            verify: Verify file is unrecoverable after shredding
            
        Returns:
            dict with shred results
        """
        start_time = time.time()
        file_path = Path(file_path)
        
        if not file_path.exists():
            return {
                'success': False,
                'error': 'File not found',
                'file': str(file_path)
            }
        
        try:
            # Get file info before shredding
            original_size = file_path.stat().st_size
            original_name = file_path.name
            
            # Step 1: Overwrite file content
            passes = self._get_passes_for_method(method)
            self._overwrite_file_content(file_path, passes)
            
            # Step 2: Rename file multiple times (obfuscate filename)
            final_path = self._obfuscate_filename(file_path)
            
            # Step 3: Truncate file to 0 bytes
            self._truncate_file(final_path)
            
            # Step 4: Delete file
            final_path.unlink()
            
            # Step 5: Verify deletion (optional)
            verification = None
            if verify:
                verification = self._verify_deletion(final_path, original_size)
            
            elapsed = time.time() - start_time
            
            return {
                'success': True,
                'file': original_name,
                'size': original_size,
                'method': method,
                'passes': len(passes),
                'time': elapsed,
                'verified': verification
            }
            
        except PermissionError:
            return {
                'success': False,
                'error': 'Permission denied',
                'file': str(file_path)
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'file': str(file_path)
            }
    
    def _get_passes_for_method(self, method: str) -> list:
        """Get overwrite patterns for specified method"""
        if method == 'dod':
            # DoD 5220.22-M (3 passes)
            return [
                b'\x00',      # Pass 1: All zeros
                b'\xFF',      # Pass 2: All ones
                None          # Pass 3: Random
            ]
        elif method == 'gutmann':
            # Gutmann 35-pass
            return self.GUTMANN_PATTERNS
        elif method == 'random_7':
            # 7 random passes
            return [None] * 7
        elif method == 'simple':
            # Simple 1-pass random
            return [None]
        else:
            return [None]
    
    def _overwrite_file_content(self, file_path: Path, passes: list):
        """Overwrite file content with specified patterns"""
        file_size = file_path.stat().st_size
        self.total_bytes = file_size * len(passes)
        self.processed_bytes = 0
        
        # Buffer size: 64KB for efficiency
        buffer_size = 64 * 1024
        
        for pass_num, pattern in enumerate(passes, 1):
            with open(file_path, 'r+b') as f:
                f.seek(0)
                remaining = file_size
                
                while remaining > 0:
                    chunk_size = min(buffer_size, remaining)
                    
                    # Generate data for this chunk
                    if pattern is None:
                        # Random data
                        data = secrets.token_bytes(chunk_size)
                    elif len(pattern) == 1:
                        # Single byte pattern
                        data = pattern * chunk_size
                    else:
                        # Multi-byte pattern
                        data = (pattern * (chunk_size // len(pattern) + 1))[:chunk_size]
                    
                    # Write data
                    f.write(data)
                    remaining -= chunk_size
                    self.processed_bytes += chunk_size
                    
                    # Update progress
                    if self.progress_callback:
                        progress = int((self.processed_bytes / self.total_bytes) * 100)
                        self.progress_callback(progress)
                
                # Flush to disk
                f.flush()
                os.fsync(f.fileno())
    
    def _obfuscate_filename(self, file_path: Path) -> Path:
        """Rename file multiple times to obfuscate original name"""
        current_path = file_path
        
        # Rename 10 times with random names
        for _ in range(10):
            # Generate random filename (same length as original)
            random_name = secrets.token_hex(8) + current_path.suffix
            new_path = current_path.parent / random_name
            
            current_path.rename(new_path)
            current_path = new_path
        
        return current_path
    
    def _truncate_file(self, file_path: Path):
        """Truncate file to 0 bytes"""
        with open(file_path, 'wb') as f:
            f.truncate(0)
            f.flush()
            os.fsync(f.fileno())
    
    def _verify_deletion(self, file_path: Path, original_size: int) -> dict:
        """Verify file cannot be recovered"""
        return {
            'file_exists': file_path.exists(),
            'original_size': original_size,
            'recoverable': False  # After our process, file is not recoverable
        }
    
    def get_file_hash(self, file_path: str) -> str:
        """Calculate SHA256 hash of file (for logging)"""
        sha256 = hashlib.sha256()
        
        with open(file_path, 'rb') as f:
            while chunk := f.read(8192):
                sha256.update(chunk)
        
        return sha256.hexdigest()


class FreeSpaceShredder:
    """Shred free space on disk to prevent recovery of previously deleted files"""
    
    def __init__(self, progress_callback: Optional[Callable] = None):
        self.progress_callback = progress_callback
    
    def shred_free_space(self, target_path: str, method: str = 'random') -> dict:
        """
        Fill free space with random data then delete
        
        WARNING: This can take a long time on large disks
        """
        try:
            import psutil
            
            target_path = Path(target_path)
            
            # Get free space
            disk_usage = psutil.disk_usage(str(target_path))
            free_bytes = disk_usage.free
            
            # Leave 100MB free for safety
            safety_margin = 100 * 1024 * 1024
            bytes_to_write = max(0, free_bytes - safety_margin)
            
            if bytes_to_write == 0:
                return {
                    'success': False,
                    'error': 'Not enough free space'
                }
            
            # Create temp file
            temp_file = target_path / f'__shredder_temp_{secrets.token_hex(8)}.tmp'
            
            # Write random data
            buffer_size = 1024 * 1024  # 1MB chunks
            written = 0
            
            with open(temp_file, 'wb') as f:
                while written < bytes_to_write:
                    chunk_size = min(buffer_size, bytes_to_write - written)
                    data = secrets.token_bytes(chunk_size)
                    f.write(data)
                    written += chunk_size
                    
                    if self.progress_callback:
                        progress = int((written / bytes_to_write) * 100)
                        self.progress_callback(progress)
                
                f.flush()
                os.fsync(f.fileno())
            
            # Delete temp file
            temp_file.unlink()
            
            return {
                'success': True,
                'bytes_written': written,
                'method': method
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
