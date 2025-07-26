"""
Terminal Cleaner Module

A utility class for managing terminal cursor position and clearing content
when working with blessed terminal library.

Author: jjjuk
License: MIT
"""

from blessed import Terminal
from typing import Optional, Callable


class TerminalCleaner:
    """
    Helper class for managing terminal cursor position and clearing content.
    
    This class provides a clean way to:
    1. Save cursor position before drawing content
    2. Clear content from saved position to current position
    3. Clear and redraw content in one operation
    
    Example usage:
        term = Terminal()
        cleaner = TerminalCleaner(term)
        
        # Save position before drawing
        cleaner.save_position()
        print("Some content")
        print("More content")
        
        # Clear all content from saved position
        cleaner.clear()
        
        # Or clear and redraw in one operation
        def draw_content():
            print("New content")
        
        cleaner.clear_and_redraw(draw_content)
    """
    
    def __init__(self, terminal: Terminal):
        """
        Initialize TerminalCleaner with a blessed Terminal instance.
        
        Args:
            terminal: A blessed Terminal instance
        """
        self.term = terminal
        self.saved_y: Optional[int] = None
        self.saved_x: Optional[int] = None
    
    def save_position(self) -> None:
        """
        Save current cursor position.
        
        This position will be used as the starting point for clearing operations.
        """
        try:
            self.saved_y, self.saved_x = self.term.get_location()
        except Exception:
            # Fallback if get_location fails
            self.saved_y = None
            self.saved_x = None
    
    def clear(self) -> None:
        """
        Clear content from saved position to current position.

        This method:
        1. Calculates how many lines were added since save_position()
        2. Moves cursor back to saved position
        3. Clears from saved position to end of screen
        4. Leaves cursor at saved position

        If no position was saved, this method does nothing.
        """
        if self.saved_y is None or self.saved_x is None:
            return

        try:
            # Move to saved position
            print(self.term.move_yx(self.saved_y, self.saved_x), end='')

            # Clear from saved position to end of screen
            # This is more reliable than trying to calculate exact lines
            print(self.term.clear_eos, end='')

            # Return to saved position
            print(self.term.move_yx(self.saved_y, self.saved_x), end='')

        except Exception:
            # Fallback: try to clear screen if positioning fails
            print(self.term.clear, end='')
    
    def clear_and_redraw(self, draw_function: Callable[[], None]) -> None:
        """
        Clear content and redraw using provided function.
        
        This method:
        1. Clears content from saved position to current position
        2. Saves new position (at the cleared location)
        3. Calls the draw function to redraw content
        
        Args:
            draw_function: A callable that draws the new content
        """
        self.clear()
        self.save_position()
        draw_function()
    
    def reset(self) -> None:
        """
        Reset saved position.
        
        After calling this method, clear() will do nothing until
        save_position() is called again.
        """
        self.saved_y = None
        self.saved_x = None
    
    def is_position_saved(self) -> bool:
        """
        Check if a position has been saved.
        
        Returns:
            True if save_position() has been called and position is saved
        """
        return self.saved_y is not None and self.saved_x is not None
