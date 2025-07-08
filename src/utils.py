import os
import glob
from datetime import datetime, timedelta

def cleanup_old_logs(log_dir="logs", max_age_days=7, keep_min=10):
    """
    Clean up old log files.
    
    Args:
        log_dir (str): Directory containing log files
        max_age_days (int): Maximum age of log files in days
        keep_min (int): Minimum number of log files to keep regardless of age
    """
    if not os.path.exists(log_dir):
        return
        
    # Get all log files
    log_files = glob.glob(os.path.join(log_dir, "*.log"))
    if not log_files:
        return
        
    # Sort by modification time (newest first)
    log_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    
    # Always keep the N most recent logs
    protected_logs = set(log_files[:keep_min])
    
    # Calculate cutoff date
    cutoff_date = datetime.now() - timedelta(days=max_age_days)
    
    # Delete old logs
    for log_file in log_files[keep_min:]:
        if log_file in protected_logs:
            continue
            
        # Check file age
        mod_time = datetime.fromtimestamp(os.path.getmtime(log_file))
        if mod_time < cutoff_date:
            try:
                os.remove(log_file)
                print(f"Deleted old log file: {log_file}")
            except OSError as e:
                print(f"Error deleting {log_file}: {e}") 