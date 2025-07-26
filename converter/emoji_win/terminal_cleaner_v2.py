"""
Terminal Cleaner V2 Module

A utility class for managing terminal content clearing without relying on cursor position.
This version tracks lines manually instead of using get_location().

Author: jjjuk
License: MIT
"""

from blessed import Terminal
from typing import Optional, Callable
import sys
from io import StringIO


class TerminalCleanerV2:
    """
    Helper class for managing terminal content clearing by tracking lines manually.
    
    This version doesn't rely on get_location() which may not work in all terminals.
    Instead, it tracks the number of lines printed and clears exactly that many.
    
    Example usage:
        term = Terminal()
        cleaner = TerminalCleanerV2(term)
        
        # Start tracking
        cleaner.start_tracking()
        print("Some content")
        print("More content")
        
        # Clear all tracked content
        cleaner.clear_tracked()
        
        # Or clear and redraw in one operation
        def draw_content():
            print("New content")
        
        cleaner.clear_and_redraw(draw_content)
    """
    
    def __init__(self, terminal: Terminal):
        """
        Initialize TerminalCleanerV2 with a blessed Terminal instance.
        
        Args:
            terminal: A blessed Terminal instance
        """
        self.term = terminal
        self.lines_printed = 0
        self.is_tracking = False
        self.original_stdout = None
        self.captured_output = None
    
    def start_tracking(self) -> None:
        """
        Start tracking printed lines.
        
        This method begins counting how many lines are printed to stdout.
        """
        self.lines_printed = 0
        self.is_tracking = True
        
        # Capture stdout to count lines
        self.original_stdout = sys.stdout
        self.captured_output = StringIO()
        sys.stdout = LineCountingWrapper(self.original_stdout, self)
    
    def stop_tracking(self) -> None:
        """
        Stop tracking printed lines.
        
        This restores normal stdout behavior.
        """
        if self.original_stdout:
            sys.stdout = self.original_stdout
            self.original_stdout = None
        self.captured_output = None
        self.is_tracking = False
    
    def add_lines(self, count: int) -> None:
        """
        Manually add to the line count.
        
        Args:
            count: Number of lines to add to the count
        """
        if self.is_tracking:
            self.lines_printed += count
    
    def clear_tracked(self) -> None:
        """
        Clear all tracked lines.
        
        This method moves the cursor up by the number of tracked lines
        and clears each line.
        """
        if not self.is_tracking or self.lines_printed == 0:
            return
        
        try:
            # Stop tracking during clear to avoid counting clear operations
            was_tracking = self.is_tracking
            self.stop_tracking()
            
            # Move up and clear each line
            for i in range(self.lines_printed):
                if i > 0:  # Don't move up on first iteration (we're already on the last line)
                    print(self.term.move_up, end='', flush=True)
                print(self.term.clear_eol, end='', flush=True)
            
            # Move up to the first line position
            if self.lines_printed > 0:
                for _ in range(self.lines_printed - 1):
                    print(self.term.move_up, end='', flush=True)
            
            # Reset line count
            self.lines_printed = 0
            
            # Resume tracking if it was active
            if was_tracking:
                self.start_tracking()
                
        except Exception:
            # Fallback: clear screen if positioning fails
            print(self.term.clear, end='', flush=True)
            self.lines_printed = 0
    
    def clear_and_redraw(self, draw_function: Callable[[], None]) -> None:
        """
        Clear tracked content and redraw using provided function.
        
        This method:
        1. Clears all tracked lines
        2. Calls the draw function to redraw content
        3. Continues tracking the new content
        
        Args:
            draw_function: A callable that draws the new content
        """
        self.clear_tracked()
        draw_function()
    
    def get_line_count(self) -> int:
        """
        Get the current number of tracked lines.
        
        Returns:
            Number of lines currently being tracked
        """
        return self.lines_printed
    
    def reset(self) -> None:
        """
        Reset the cleaner to initial state.
        
        This stops tracking and resets the line count.
        """
        self.stop_tracking()
        self.lines_printed = 0


class LineCountingWrapper:
    """Wrapper for stdout that counts lines printed"""
    
    def __init__(self, original_stdout, cleaner):
        self.original_stdout = original_stdout
        self.cleaner = cleaner
    
    def write(self, text):
        # Count newlines in the text
        if text and self.cleaner.is_tracking:
            newline_count = text.count('\n')
            if newline_count > 0:
                self.cleaner.lines_printed += newline_count
        
        # Write to original stdout
        return self.original_stdout.write(text)
    
    def flush(self):
        return self.original_stdout.flush()
    
    def __getattr__(self, name):
        return getattr(self.original_stdout, name)
