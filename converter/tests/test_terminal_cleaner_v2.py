"""
Tests for TerminalCleanerV2 class

This module contains comprehensive tests for the TerminalCleanerV2 utility class.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, call
from blessed import Terminal
import sys
from io import StringIO

from emoji_win.terminal_cleaner_v2 import TerminalCleanerV2, LineCountingWrapper


class TestTerminalCleanerV2:
    """Test cases for TerminalCleanerV2 class"""
    
    def setup_method(self):
        """Set up test fixtures before each test method"""
        self.mock_term = Mock(spec=Terminal)
        self.cleaner = TerminalCleanerV2(self.mock_term)
    
    def test_init(self):
        """Test TerminalCleanerV2 initialization"""
        assert self.cleaner.term is self.mock_term
        assert self.cleaner.lines_printed == 0
        assert not self.cleaner.is_tracking
        assert self.cleaner.original_stdout is None
    
    def test_start_tracking(self):
        """Test starting line tracking"""
        original_stdout = sys.stdout
        
        self.cleaner.start_tracking()
        
        assert self.cleaner.is_tracking
        assert self.cleaner.lines_printed == 0
        assert self.cleaner.original_stdout == original_stdout
        assert isinstance(sys.stdout, LineCountingWrapper)
        
        # Cleanup
        self.cleaner.stop_tracking()
    
    def test_stop_tracking(self):
        """Test stopping line tracking"""
        original_stdout = sys.stdout
        
        self.cleaner.start_tracking()
        self.cleaner.stop_tracking()
        
        assert not self.cleaner.is_tracking
        assert sys.stdout == original_stdout
        assert self.cleaner.original_stdout is None
    
    def test_add_lines_when_tracking(self):
        """Test manually adding lines when tracking is active"""
        self.cleaner.start_tracking()
        
        self.cleaner.add_lines(3)
        assert self.cleaner.lines_printed == 3
        
        self.cleaner.add_lines(2)
        assert self.cleaner.lines_printed == 5
        
        self.cleaner.stop_tracking()
    
    def test_add_lines_when_not_tracking(self):
        """Test manually adding lines when tracking is not active"""
        self.cleaner.add_lines(3)
        assert self.cleaner.lines_printed == 0  # Should not add when not tracking
    
    def test_clear_tracked_no_lines(self):
        """Test clearing when no lines are tracked"""
        self.cleaner.start_tracking()
        
        with patch('builtins.print') as mock_print:
            self.cleaner.clear_tracked()
            mock_print.assert_not_called()
        
        self.cleaner.stop_tracking()
    
    def test_clear_tracked_single_line(self):
        """Test clearing a single tracked line"""
        self.mock_term.move_up = "move_up"
        self.mock_term.clear_eol = "clear_eol"
        
        self.cleaner.start_tracking()
        self.cleaner.add_lines(1)
        
        with patch('builtins.print') as mock_print:
            self.cleaner.clear_tracked()
            
            # Should clear one line without moving up first
            expected_calls = [
                call("clear_eol", end='', flush=True)
            ]
            mock_print.assert_has_calls(expected_calls)
        
        assert self.cleaner.lines_printed == 0
        self.cleaner.stop_tracking()
    
    def test_clear_tracked_multiple_lines(self):
        """Test clearing multiple tracked lines"""
        self.mock_term.move_up = "move_up"
        self.mock_term.clear_eol = "clear_eol"
        
        self.cleaner.start_tracking()
        self.cleaner.add_lines(3)
        
        with patch('builtins.print') as mock_print:
            self.cleaner.clear_tracked()
            
            # Should clear 3 lines: first line (no move up), then move up and clear 2 more
            # Then move up 2 times to get to first line position
            expected_calls = [
                call("clear_eol", end='', flush=True),      # Clear line 3 (current)
                call("move_up", end='', flush=True),        # Move to line 2
                call("clear_eol", end='', flush=True),      # Clear line 2
                call("move_up", end='', flush=True),        # Move to line 1
                call("clear_eol", end='', flush=True),      # Clear line 1
                call("move_up", end='', flush=True),        # Move up to first line (3-1=2 times)
                call("move_up", end='', flush=True),        # Move up to first line
            ]
            mock_print.assert_has_calls(expected_calls)
        
        assert self.cleaner.lines_printed == 0
        self.cleaner.stop_tracking()
    
    def test_clear_tracked_exception_fallback(self):
        """Test fallback when clearing fails"""
        self.mock_term.clear = "clear_screen"
        
        self.cleaner.start_tracking()
        self.cleaner.add_lines(2)
        
        # Make move_up raise an exception
        self.mock_term.move_up = Mock(side_effect=Exception("Terminal error"))
        
        with patch('builtins.print') as mock_print:
            self.cleaner.clear_tracked()
            
            # Should fallback to clearing screen
            mock_print.assert_called_with("clear_screen", end='', flush=True)
        
        assert self.cleaner.lines_printed == 0
        self.cleaner.stop_tracking()
    
    def test_clear_and_redraw(self):
        """Test clear and redraw functionality"""
        draw_function = Mock()
        
        self.cleaner.start_tracking()
        self.cleaner.add_lines(2)
        
        self.mock_term.move_up = "move_up"
        self.mock_term.clear_eol = "clear_eol"
        
        with patch('builtins.print'):
            self.cleaner.clear_and_redraw(draw_function)
        
        # Should call draw function once
        draw_function.assert_called_once()
        
        # Should still be tracking
        assert self.cleaner.is_tracking
        
        self.cleaner.stop_tracking()
    
    def test_get_line_count(self):
        """Test getting current line count"""
        assert self.cleaner.get_line_count() == 0
        
        self.cleaner.start_tracking()
        self.cleaner.add_lines(5)
        
        assert self.cleaner.get_line_count() == 5
        
        self.cleaner.stop_tracking()
    
    def test_reset(self):
        """Test reset functionality"""
        self.cleaner.start_tracking()
        self.cleaner.add_lines(3)
        
        assert self.cleaner.is_tracking
        assert self.cleaner.lines_printed == 3
        
        self.cleaner.reset()
        
        assert not self.cleaner.is_tracking
        assert self.cleaner.lines_printed == 0


class TestLineCountingWrapper:
    """Test cases for LineCountingWrapper class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.mock_stdout = Mock()
        self.mock_cleaner = Mock()
        self.mock_cleaner.is_tracking = True
        self.mock_cleaner.lines_printed = 0
        self.wrapper = LineCountingWrapper(self.mock_stdout, self.mock_cleaner)
    
    def test_write_with_newlines(self):
        """Test writing text with newlines"""
        text = "Line 1\nLine 2\nLine 3\n"
        
        self.wrapper.write(text)
        
        # Should count 3 newlines
        assert self.mock_cleaner.lines_printed == 3
        self.mock_stdout.write.assert_called_once_with(text)
    
    def test_write_without_newlines(self):
        """Test writing text without newlines"""
        text = "Some text without newlines"
        
        self.wrapper.write(text)
        
        # Should not count any lines
        assert self.mock_cleaner.lines_printed == 0
        self.mock_stdout.write.assert_called_once_with(text)
    
    def test_write_when_not_tracking(self):
        """Test writing when cleaner is not tracking"""
        self.mock_cleaner.is_tracking = False
        text = "Line 1\nLine 2\n"
        
        self.wrapper.write(text)
        
        # Should not count lines when not tracking
        assert self.mock_cleaner.lines_printed == 0
        self.mock_stdout.write.assert_called_once_with(text)
    
    def test_flush(self):
        """Test flush method"""
        self.wrapper.flush()
        self.mock_stdout.flush.assert_called_once()
    
    def test_getattr_delegation(self):
        """Test that other attributes are delegated to original stdout"""
        self.mock_stdout.some_attribute = "test_value"
        
        assert self.wrapper.some_attribute == "test_value"


class TestTerminalCleanerV2Integration:
    """Integration tests with real terminal to verify actual clearing behavior"""

    def setup_method(self):
        """Set up real terminal for integration tests"""
        self.real_term = Terminal()
        self.cleaner = TerminalCleanerV2(self.real_term)

    def test_real_terminal_clear_single_line(self):
        """Test clearing a single line of content in real terminal"""
        # Start tracking
        self.cleaner.start_tracking()

        # Add one line of content
        print("🔴 This line should be cleared")

        # Verify line was tracked
        assert self.cleaner.get_line_count() == 1

        # Clear the content
        self.cleaner.clear_tracked()

        # Verify line count is reset
        assert self.cleaner.get_line_count() == 0

        # Add confirmation that clearing worked
        print("✅ Single line cleared successfully!")

        self.cleaner.stop_tracking()

    def test_real_terminal_clear_multiple_lines(self):
        """Test clearing multiple lines of content in real terminal"""
        # Start tracking
        self.cleaner.start_tracking()

        # Add multiple lines of content
        test_lines = [
            "🔴 Line 1: This should be cleared",
            "🔴 Line 2: This should also be cleared",
            "🔴 Line 3: This should also be cleared",
            "🔴 Line 4: Final line to be cleared"
        ]

        for line in test_lines:
            print(line)

        # Verify lines were tracked
        assert self.cleaner.get_line_count() == len(test_lines)

        # Clear all content
        self.cleaner.clear_tracked()

        # Verify line count is reset
        assert self.cleaner.get_line_count() == 0

        # Add confirmation that clearing worked
        print("✅ Multiple lines cleared successfully!")

        self.cleaner.stop_tracking()

    def test_real_terminal_clear_and_redraw_cycle(self):
        """Test multiple clear and redraw cycles in real terminal"""
        # Start tracking
        self.cleaner.start_tracking()

        def draw_content():
            print("🟢 Redrawn line 1")
            print("🟢 Redrawn line 2")

        # First cycle: add content and clear
        print("🔴 Original line 1")
        print("🔴 Original line 2")

        assert self.cleaner.get_line_count() == 2

        self.cleaner.clear_tracked()
        assert self.cleaner.get_line_count() == 0

        # Second cycle: clear and redraw
        self.cleaner.clear_and_redraw(draw_content)

        # Should have new content tracked
        assert self.cleaner.get_line_count() == 2

        # Final clear
        self.cleaner.clear_tracked()
        assert self.cleaner.get_line_count() == 0

        # Add confirmation
        print("✅ Clear and redraw cycle completed successfully!")

        self.cleaner.stop_tracking()

    def test_real_terminal_automatic_line_counting(self):
        """Test that lines are automatically counted when printed"""
        # Start tracking
        self.cleaner.start_tracking()

        # Print content normally - should be automatically tracked
        print("Auto-tracked line 1")
        print("Auto-tracked line 2")
        print("Auto-tracked line 3")

        # Verify automatic tracking worked
        assert self.cleaner.get_line_count() == 3

        # Clear automatically tracked content
        self.cleaner.clear_tracked()

        # Verify clearing worked
        assert self.cleaner.get_line_count() == 0

        # Add confirmation
        print("✅ Automatic line counting works!")

        self.cleaner.stop_tracking()

    def test_rich_table_integration(self):
        """Test that our cleaner works correctly with Rich tables"""
        from rich.console import Console
        from rich.table import Table

        # Create a console that outputs to our terminal
        console = Console()

        # Start tracking
        self.cleaner.start_tracking()

        # Add content above table (should NOT be cleared)
        print("🟢 CONTENT ABOVE TABLE - SHOULD REMAIN")
        print("🟢 Another line above - SHOULD REMAIN")

        # Create and print Rich table (should be cleared)
        table = Table(
            title="📁 Test Table",
            show_header=True,
            header_style="bold blue",
            title_style="bold cyan",
            border_style="bright_blue"
        )
        table.add_column("File", style="bright_cyan", min_width=20)
        table.add_column("Size", style="bright_green", justify="right", min_width=8)

        table.add_row("test1.txt", "1.2 MB")
        table.add_row("test2.txt", "2.5 MB")
        table.add_row("test3.txt", "3.8 MB")

        # Print empty line before table
        print()
        console.print(table)
        print()
        print("Use arrows to navigate")

        # Verify we tracked the right number of lines
        # Rich table with 3 rows typically outputs ~11 lines:
        # 1 empty + title + header border + header + separator + 3 data rows + bottom border + 1 empty + 1 instruction
        actual_lines = self.cleaner.get_line_count()

        print(f"🔍 Tracked lines: {actual_lines}")

        # Should be reasonable number (not 0, not too many)
        assert 8 <= actual_lines <= 15, f"Unexpected line count: {actual_lines}"

        # Clear only the tracked content (table and related lines)
        self.cleaner.clear_tracked()

        # Add confirmation
        print("✅ Rich table cleared - content above should remain!")

        self.cleaner.stop_tracking()

    def test_multiple_table_redraws(self):
        """Test multiple table redraws to ensure proper clearing"""
        from rich.console import Console
        from rich.table import Table

        console = Console()

        # Add permanent content that should never be cleared
        print("🟢 PERMANENT LINE 1 - NEVER CLEAR")
        print("🟢 PERMANENT LINE 2 - NEVER CLEAR")
        print("🟢 PERMANENT LINE 3 - NEVER CLEAR")

        def create_test_table(title_suffix: str):
            """Create a test table with given suffix"""
            table = Table(
                title=f"📁 Test Table {title_suffix}",
                show_header=True,
                header_style="bold blue",
                title_style="bold cyan",
                border_style="bright_blue"
            )
            table.add_column("Item", style="bright_cyan", min_width=15)
            table.add_column("Value", style="bright_green", justify="right", min_width=8)

            table.add_row(f"Item A{title_suffix}", f"{title_suffix}.1")
            table.add_row(f"Item B{title_suffix}", f"{title_suffix}.2")

            return table

        def draw_table_interface(table_num: int):
            """Draw table interface"""
            table = create_test_table(str(table_num))
            print()  # Empty line before
            console.print(table)
            print()  # Empty line after
            print(f"🔴 Table {table_num} interface - SHOULD BE CLEARED")

        # Test multiple redraws
        self.cleaner.start_tracking()

        # First table
        draw_table_interface(1)
        first_count = self.cleaner.get_line_count()
        print(f"🔍 First table lines: {first_count}")
        assert 8 <= first_count <= 12, f"Unexpected first table line count: {first_count}"

        # Clear and redraw second table
        self.cleaner.clear_and_redraw(lambda: draw_table_interface(2))
        second_count = self.cleaner.get_line_count()
        print(f"🔍 Second table lines: {second_count}")
        assert second_count == first_count, f"Line count changed: {first_count} -> {second_count}"

        # Clear and redraw third table
        self.cleaner.clear_and_redraw(lambda: draw_table_interface(3))
        third_count = self.cleaner.get_line_count()
        print(f"🔍 Third table lines: {third_count}")
        assert third_count == first_count, f"Line count changed: {first_count} -> {third_count}"

        # Final clear
        self.cleaner.clear_tracked()
        assert self.cleaner.get_line_count() == 0

        # Add confirmation
        print("✅ Multiple table redraws completed - permanent content should remain!")

        self.cleaner.stop_tracking()

    def test_precise_line_counting_with_rich(self):
        """Test that line counting is precise with Rich output"""
        from rich.console import Console
        from rich.table import Table
        from io import StringIO

        # Create a console that captures output to count actual lines
        string_buffer = StringIO()
        capture_console = Console(file=string_buffer, width=80)

        # Create the same table we'll use in real test
        table = Table(
            title="📁 Line Count Test",
            show_header=True,
            header_style="bold blue",
            title_style="bold cyan",
            border_style="bright_blue"
        )
        table.add_column("File", style="bright_cyan", min_width=20)
        table.add_column("Size", style="bright_green", justify="right", min_width=8)

        table.add_row("test1.txt", "1.2 MB")
        table.add_row("test2.txt", "2.5 MB")

        # Capture what Rich actually outputs
        print("", file=string_buffer)  # Empty line before
        capture_console.print(table)
        print("", file=string_buffer)  # Empty line after
        print("Instructions line", file=string_buffer)

        # Count actual lines in Rich output
        captured_output = string_buffer.getvalue()
        actual_rich_lines = captured_output.count('\n')

        print(f"🔍 Rich actually outputs {actual_rich_lines} lines")

        # Now test our cleaner with the same content
        self.cleaner.start_tracking()

        print()  # Empty line before
        Console().print(table)  # Use real console
        print()  # Empty line after
        print("Instructions line")

        tracked_lines = self.cleaner.get_line_count()
        print(f"🔍 Our cleaner tracked {tracked_lines} lines")

        # They should match
        assert tracked_lines == actual_rich_lines, f"Line count mismatch: tracked={tracked_lines}, actual={actual_rich_lines}"

        # Clear and verify
        self.cleaner.clear_tracked()
        assert self.cleaner.get_line_count() == 0

        print("✅ Precise line counting verified!")

        self.cleaner.stop_tracking()

    def test_no_over_clearing(self):
        """Test that we don't clear more lines than we should"""
        # Add content that should NEVER be cleared
        print("🟢 PROTECTED LINE 1 - MUST REMAIN")
        print("🟢 PROTECTED LINE 2 - MUST REMAIN")
        print("🟢 PROTECTED LINE 3 - MUST REMAIN")
        print("🟢 PROTECTED LINE 4 - MUST REMAIN")
        print("🟢 PROTECTED LINE 5 - MUST REMAIN")

        # Start tracking AFTER the protected content
        self.cleaner.start_tracking()

        # Add content that SHOULD be cleared
        print("🔴 CLEARABLE LINE 1")
        print("🔴 CLEARABLE LINE 2")
        print("🔴 CLEARABLE LINE 3")

        # Verify we only tracked the clearable lines
        assert self.cleaner.get_line_count() == 3

        # Clear only the tracked content
        self.cleaner.clear_tracked()

        # Verify clearing worked
        assert self.cleaner.get_line_count() == 0

        # Add confirmation - protected content should still be visible above
        print("✅ Clearing completed - protected content above should remain!")

        self.cleaner.stop_tracking()


if __name__ == "__main__":
    pytest.main([__file__])
