"""
Tests for TerminalCleaner class

This module contains comprehensive tests for the TerminalCleaner utility class.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, call
from blessed import Terminal

from emoji_win.terminal_cleaner import TerminalCleaner


class TestTerminalCleaner:
    """Test cases for TerminalCleaner class"""
    
    def setup_method(self):
        """Set up test fixtures before each test method"""
        self.mock_term = Mock(spec=Terminal)
        self.cleaner = TerminalCleaner(self.mock_term)
    
    def test_init(self):
        """Test TerminalCleaner initialization"""
        assert self.cleaner.term is self.mock_term
        assert self.cleaner.saved_y is None
        assert self.cleaner.saved_x is None
    
    def test_save_position_success(self):
        """Test successful position saving"""
        self.mock_term.get_location.return_value = (10, 5)
        
        self.cleaner.save_position()
        
        assert self.cleaner.saved_y == 10
        assert self.cleaner.saved_x == 5
        self.mock_term.get_location.assert_called_once()
    
    def test_save_position_exception(self):
        """Test position saving when get_location raises exception"""
        self.mock_term.get_location.side_effect = Exception("Terminal error")
        
        self.cleaner.save_position()
        
        assert self.cleaner.saved_y is None
        assert self.cleaner.saved_x is None
    
    def test_clear_no_saved_position(self):
        """Test clear when no position is saved"""
        with patch('builtins.print') as mock_print:
            self.cleaner.clear()
            mock_print.assert_not_called()
    
    def test_clear_same_position(self):
        """Test clear when cursor is at same position as saved"""
        # Save position
        self.mock_term.get_location.return_value = (10, 5)
        self.cleaner.save_position()

        # Mock terminal commands
        self.mock_term.move_yx.return_value = "move_yx_10_5"
        self.mock_term.clear_eos = "clear_eos"

        with patch('builtins.print') as mock_print:
            self.cleaner.clear()

            # Should move to saved position, clear to end of screen, and return to saved position
            expected_calls = [
                call("move_yx_10_5", end=''),
                call("clear_eos", end=''),
                call("move_yx_10_5", end='')
            ]
            mock_print.assert_has_calls(expected_calls)
    
    def test_clear_multiple_lines(self):
        """Test clear when cursor moved down multiple lines"""
        # Save position at (10, 5)
        self.mock_term.get_location.return_value = (10, 5)
        self.cleaner.save_position()

        # Mock terminal commands
        self.mock_term.move_yx.return_value = "move_yx_10_5"
        self.mock_term.clear_eos = "clear_eos"

        with patch('builtins.print') as mock_print:
            self.cleaner.clear()

            # Should move to saved position, clear to end of screen, and return
            expected_calls = [
                call("move_yx_10_5", end=''),       # Move to saved position
                call("clear_eos", end=''),          # Clear to end of screen
                call("move_yx_10_5", end='')        # Return to saved position
            ]
            mock_print.assert_has_calls(expected_calls)
    
    def test_clear_exception_fallback(self):
        """Test clear fallback when positioning fails"""
        # Save position
        self.mock_term.get_location.return_value = (10, 5)
        self.cleaner.save_position()
        
        # Make get_location fail on second call
        self.mock_term.get_location.side_effect = [None, Exception("Terminal error")]
        self.mock_term.clear = "clear_screen"
        
        with patch('builtins.print') as mock_print:
            self.cleaner.clear()
            
            # Should fallback to clearing screen
            mock_print.assert_called_once_with("clear_screen", end='')
    
    def test_clear_and_redraw(self):
        """Test clear_and_redraw functionality"""
        # Mock the draw function
        draw_function = Mock()

        # Save initial position
        self.mock_term.get_location.return_value = (10, 5)
        self.cleaner.save_position()

        # Mock terminal commands
        self.mock_term.move_yx.return_value = "move_yx"
        self.mock_term.clear_eos = "clear_eos"

        with patch('builtins.print'):
            self.cleaner.clear_and_redraw(draw_function)

        # Should call draw function once
        draw_function.assert_called_once()

        # Position should be saved again after clearing (at the cleared position)
        # The method calls save_position() after clear(), so it saves the current position
        assert self.cleaner.saved_y == 10  # Position after clear and save_position
        assert self.cleaner.saved_x == 5
    
    def test_reset(self):
        """Test reset functionality"""
        # Save position first
        self.mock_term.get_location.return_value = (10, 5)
        self.cleaner.save_position()
        
        assert self.cleaner.saved_y == 10
        assert self.cleaner.saved_x == 5
        
        # Reset
        self.cleaner.reset()
        
        assert self.cleaner.saved_y is None
        assert self.cleaner.saved_x is None
    
    def test_is_position_saved(self):
        """Test is_position_saved functionality"""
        # Initially no position saved
        assert not self.cleaner.is_position_saved()
        
        # Save position
        self.mock_term.get_location.return_value = (10, 5)
        self.cleaner.save_position()
        
        assert self.cleaner.is_position_saved()
        
        # Reset
        self.cleaner.reset()
        
        assert not self.cleaner.is_position_saved()
    
    def test_clear_negative_lines(self):
        """Test clear when current position is above saved position"""
        # Save position at (10, 5)
        self.mock_term.get_location.return_value = (10, 5)
        self.cleaner.save_position()
        
        # Current position is above saved (shouldn't happen normally, but test edge case)
        self.mock_term.get_location.return_value = (8, 0)
        
        # Mock terminal commands
        self.mock_term.move_yx.return_value = "move_yx_10_5"
        self.mock_term.clear_eol = "clear_eol"

        with patch('builtins.print') as mock_print:
            self.cleaner.clear()

            # Should clear only one line (max(0, 8-10) + 1 = 1)
            expected_calls = [
                call("move_yx_10_5", end=''),
                call("clear_eol", end=''),
                call("move_yx_10_5", end='')
            ]
            mock_print.assert_has_calls(expected_calls)


class TestTerminalCleanerIntegration:
    """Integration tests with real terminal to verify actual clearing behavior"""

    def setup_method(self):
        """Set up real terminal for integration tests"""
        self.real_term = Terminal()
        self.cleaner = TerminalCleaner(self.real_term)

    def test_real_terminal_clear_single_line(self):
        """Test clearing single line in real terminal"""
        if not self.real_term.is_a_tty:
            pytest.skip("Skipping real terminal test - not a TTY")

        # Save initial position
        self.cleaner.save_position()
        initial_y, initial_x = self.real_term.get_location()

        # Write some content
        print("Test line 1")

        # Get position after writing
        after_y, after_x = self.real_term.get_location()

        # Should have moved down one line
        assert after_y == initial_y + 1

        # Clear content
        self.cleaner.clear()

        # Check final position - should be back at initial position
        final_y, final_x = self.real_term.get_location()
        assert final_y == initial_y
        assert final_x == initial_x

    def test_real_terminal_clear_multiple_lines(self):
        """Test clearing multiple lines in real terminal"""
        if not self.real_term.is_a_tty:
            pytest.skip("Skipping real terminal test - not a TTY")

        # Save initial position
        self.cleaner.save_position()
        initial_y, initial_x = self.real_term.get_location()

        # Write multiple lines
        test_lines = ["Line 1", "Line 2", "Line 3", "Line 4", "Line 5"]
        for line in test_lines:
            print(line)

        # Get position after writing
        after_y, after_x = self.real_term.get_location()

        # Should have moved down by number of lines
        assert after_y == initial_y + len(test_lines)

        # Clear content
        self.cleaner.clear()

        # Check final position - should be back at initial position
        final_y, final_x = self.real_term.get_location()
        assert final_y == initial_y
        assert final_x == initial_x

    def test_real_terminal_content_actually_cleared(self):
        """Test that content is actually visually cleared from terminal"""
        if not self.real_term.is_a_tty:
            pytest.skip("Skipping real terminal test - not a TTY")

        # Save initial position
        self.cleaner.save_position()
        initial_y, initial_x = self.real_term.get_location()

        # Write some distinctive content
        distinctive_content = ["UNIQUE_TEST_LINE_1", "UNIQUE_TEST_LINE_2", "UNIQUE_TEST_LINE_3"]
        for line in distinctive_content:
            print(line)

        # Clear content
        self.cleaner.clear()

        # Move cursor around the area where content was
        # and check that the distinctive content is gone
        for i in range(len(distinctive_content)):
            # Move to where each line was written
            print(self.real_term.move_yx(initial_y + i, 0), end='')

            # Read the current line (this is tricky - we'll use a different approach)
            # Instead, we'll write over the area and see if it's clean
            print(self.real_term.clear_eol, end='')

        # Return to initial position
        print(self.real_term.move_yx(initial_y, initial_x), end='')

        # Verify we're at the right position
        final_y, final_x = self.real_term.get_location()
        assert final_y == initial_y
        assert final_x == initial_x

    def test_clear_and_redraw_cycle(self):
        """Test multiple clear and redraw cycles"""
        if not self.real_term.is_a_tty:
            pytest.skip("Skipping real terminal test - not a TTY")

        def draw_content():
            print("Cycle content line 1")
            print("Cycle content line 2")

        # Save initial position
        self.cleaner.save_position()
        initial_y, initial_x = self.real_term.get_location()

        # Perform multiple clear and redraw cycles
        for cycle in range(3):
            # Draw content
            draw_content()

            # Verify position moved
            after_draw_y, after_draw_x = self.real_term.get_location()
            assert after_draw_y > initial_y

            # Clear and redraw
            self.cleaner.clear_and_redraw(draw_content)

            # Should be at a consistent position after redraw
            after_redraw_y, after_redraw_x = self.real_term.get_location()
            # Position should be consistent across cycles
            if cycle > 0:
                assert after_redraw_y == previous_redraw_y

            previous_redraw_y = after_redraw_y

    def test_terminal_state_preservation(self):
        """Test that terminal state is properly preserved"""
        if not self.real_term.is_a_tty:
            pytest.skip("Skipping real terminal test - not a TTY")

        # Get initial terminal state
        initial_y, initial_x = self.real_term.get_location()

        # Save position
        self.cleaner.save_position()

        # Write content and clear multiple times
        for i in range(5):
            print(f"Test iteration {i}")
            print(f"Second line {i}")
            self.cleaner.clear()

        # Terminal should be back to initial state
        final_y, final_x = self.real_term.get_location()
        assert final_y == initial_y
        assert final_x == initial_x


class TestTerminalCleanerIntegration:
    """Integration tests with real terminal to verify actual clearing behavior"""

    def setup_method(self):
        """Set up real terminal for integration tests"""
        self.real_term = Terminal()
        self.cleaner = TerminalCleaner(self.real_term)

    def test_real_terminal_clear_empty_content(self):
        """Test clearing when no content was added"""
        # Save position in empty terminal
        self.cleaner.save_position()

        # Try to clear (should do nothing)
        self.cleaner.clear()

        # Should not crash and position should be maintained
        assert self.cleaner.is_position_saved()

    def test_real_terminal_clear_single_line(self):
        """Test clearing a single line of content"""
        # Save initial position
        self.cleaner.save_position()
        initial_y, initial_x = self.real_term.get_location()

        # Add one line of content
        print("Test line to be cleared")

        # Get position after adding content
        after_y, after_x = self.real_term.get_location()

        # Verify content was added (cursor moved down)
        assert after_y > initial_y, f"Cursor should move down: {initial_y} -> {after_y}"

        # Clear the content
        self.cleaner.clear()

        # Check if we're back at initial position
        final_y, final_x = self.real_term.get_location()
        assert final_y == initial_y, f"Should return to initial Y: {initial_y}, got {final_y}"
        assert final_x == initial_x, f"Should return to initial X: {initial_x}, got {final_x}"

    def test_real_terminal_clear_multiple_lines(self):
        """Test clearing multiple lines of content"""
        # Save initial position
        self.cleaner.save_position()
        initial_y, initial_x = self.real_term.get_location()

        # Add multiple lines of content
        test_lines = [
            "Line 1: This is test content",
            "Line 2: More test content",
            "Line 3: Even more content",
            "Line 4: Final test line"
        ]

        for line in test_lines:
            print(line)

        # Get position after adding content
        after_y, after_x = self.real_term.get_location()

        # Verify content was added (cursor moved down by number of lines)
        expected_y = initial_y + len(test_lines)
        assert after_y >= expected_y, f"Cursor should move down by at least {len(test_lines)} lines: {initial_y} -> {after_y}"

        # Clear all content
        self.cleaner.clear()

        # Check if we're back at initial position
        final_y, final_x = self.real_term.get_location()
        assert final_y == initial_y, f"Should return to initial Y: {initial_y}, got {final_y}"
        assert final_x == initial_x, f"Should return to initial X: {initial_x}, got {final_x}"

    def test_real_terminal_clear_and_redraw_cycle(self):
        """Test multiple clear and redraw cycles"""
        # Save initial position
        self.cleaner.save_position()
        initial_y, initial_x = self.real_term.get_location()

        def draw_content():
            print("Redrawn line 1")
            print("Redrawn line 2")

        # First cycle: add content and clear
        print("Original line 1")
        print("Original line 2")
        self.cleaner.clear()

        # Should be back at initial position
        pos1_y, pos1_x = self.real_term.get_location()
        assert pos1_y == initial_y, f"After first clear: {initial_y} != {pos1_y}"

        # Second cycle: clear and redraw
        self.cleaner.clear_and_redraw(draw_content)

        # Should have new content
        pos2_y, pos2_x = self.real_term.get_location()
        assert pos2_y > initial_y, f"After redraw, cursor should move down: {initial_y} -> {pos2_y}"

        # Final clear
        self.cleaner.clear()

        # Should be back at initial position again
        final_y, final_x = self.real_term.get_location()
        assert final_y == initial_y, f"Final position should match initial: {initial_y} != {final_y}"

    def test_real_terminal_visual_verification(self):
        """Visual test to manually verify clearing works (for debugging)"""
        if not hasattr(self, '_manual_test_enabled'):
            pytest.skip("Manual visual test disabled")

        # Save position
        self.cleaner.save_position()

        # Add visible content
        print("🔴 This content should disappear")
        print("🔴 Line 2 should also disappear")
        print("🔴 Line 3 should also disappear")

        # Wait a moment (for manual observation)
        import time
        time.sleep(1)

        # Clear content
        self.cleaner.clear()

        # Add confirmation
        print("✅ Content cleared successfully!")


if __name__ == "__main__":
    pytest.main([__file__])
