#!/usr/bin/env python3
"""
Interactive CLI module for emoji-win

This module provides beautiful, interactive command-line interface using Rich and Inquirer.

Author: jjjuk
License: MIT
"""

import os
import sys
from pathlib import Path
from typing import List, Optional, Tuple

try:
    import inquirer
    from blessed import Terminal
    from rich.console import Console
    from rich.panel import Panel
    from rich.progress import (
        Progress,
        SpinnerColumn,
        TextColumn,
        BarColumn,
        TaskProgressColumn,
    )
    from rich.table import Table
    from rich.text import Text
    from rich.prompt import Prompt, Confirm
    from rich import print as rprint
    from rich.tree import Tree
    from rich.live import Live

    from rich import box
except ImportError as e:
    print(f"❌ Error: Required packages not installed: {e}")
    print("Please run: uv sync")
    sys.exit(1)

from .font_converter import convert_apple_emoji_to_windows
from .font_diagnostics import (
    diagnose_cbdt_cblc_directwrite_issues,
    analyze_font_structure,
)
from fontTools.ttLib import TTFont


class InteractiveCLI:
    """Beautiful interactive CLI for emoji-win"""

    def __init__(self):
        self.console = Console()
        self.term = Terminal()
        self.supported_extensions = [".ttf", ".otf"]  # Configurable for future

    def _prompt_with_cleanup(self, prompt_text: str, default: str = "") -> str:
        """
        Prompt user for input and clean up the prompt after use.

        Args:
            prompt_text: The prompt text to display
            default: Default value if user presses enter

        Returns:
            User input string
        """
        # For now, just use regular Prompt.ask without cleanup
        # The cleanup was causing complexity, and prompts are short-lived
        result: str

        if default:
            result = Prompt.ask(prompt_text, default=default)
        else:
            result = Prompt.ask(prompt_text)
        print(self.term.move_up(1) + self.term.clear_eos, end="", flush=True)
        return result

    def _confirm_with_cleanup(self, prompt_text: str) -> bool:
        """
        Prompt user for confirmation and clean up the prompt after use.

        Args:
            prompt_text: The prompt text to display

        Returns:
            True if user confirms, False otherwise
        """
        # For now, just use regular Confirm.ask without cleanup
        # The cleanup was causing complexity, and prompts are short-lived
        result: bool = Confirm.ask(prompt_text)
        print(self.term.move_up(1) + self.term.clear_eos, end="", flush=True)
        return result

    def show_banner(self):
        """Display beautiful banner"""
        banner = Panel.fit(
            "[bold blue]🍎 emoji-win[/bold blue]\n"
            "[dim]Get beautiful Apple emojis on Windows 11[/dim]\n"
            "[dim]Convert Apple Color Emoji fonts for Windows compatibility[/dim]",
            border_style="blue",
            padding=(1, 2),
        )
        self.console.print(banner)
        self.console.print()

    def find_font_files(self, directory: Path) -> List[Path]:
        """Find supported font files in directory"""
        font_files = []
        if directory.exists():
            for ext in self.supported_extensions:
                font_files.extend(directory.glob(f"*{ext}"))
        return sorted(font_files)

    def select_input_font(self) -> Optional[Path]:
        """Interactive font selection with Textual table selector"""
        # Look for fonts in common locations
        search_paths = [
            Path("../fonts"),  # Root fonts directory
            Path("fonts"),  # Local fonts directory
            Path("."),  # Current directory
        ]

        all_fonts = []
        for search_path in search_paths:
            fonts = self.find_font_files(search_path)
            for font in fonts:
                if font not in all_fonts:
                    all_fonts.append(font)

        if not all_fonts:
            self.console.print("[red]❌ No font files found in common locations[/red]")
            self.console.print(
                "[dim]Searched in: ../fonts/, fonts/, current directory[/dim]"
            )

            # Ask for manual path
            manual_path = self._prompt_with_cleanup(
                "[yellow]Enter path to font file[/yellow]", default=""
            )
            if manual_path:
                path = Path(manual_path)
                if path.exists() and path.suffix.lower() in self.supported_extensions:
                    return path
                else:
                    self.console.print("[red]❌ Invalid font file[/red]")
            return None

        try:
            # Use interactive table selector with arrow keys
            return self._interactive_table_selector(all_fonts)

        except (KeyboardInterrupt, EOFError):
            self.console.print("\n[yellow]Operation cancelled[/yellow]")
            return None

    def get_output_path(self, input_path: Path) -> Optional[Path]:
        """Get output path with smart default"""
        # Generate smart default
        default_name = f"{input_path.stem}ForWindows{input_path.suffix}"
        default_path = input_path.parent / default_name

        output_path_str = self._prompt_with_cleanup(
            f"[green]Output file path[/green]", default=str(default_path)
        )

        if not output_path_str:
            return None

        # Clean the path string (remove any extra whitespace or command artifacts)
        output_path_str = output_path_str.strip()
        output_path = Path(output_path_str)

        # Check if file exists
        if output_path.exists():
            overwrite = self._confirm_with_cleanup(
                f"File {output_path} already exists. [yellow]Overwrite?[/yellow]"
            )

            if not overwrite:
                return None

        # Create parent directory if needed
        output_path.parent.mkdir(parents=True, exist_ok=True)

        return output_path

    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size in human readable format"""
        for unit in ["B", "KB", "MB", "GB"]:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"

    def _interactive_table_selector(self, fonts: list[Path]) -> Optional[Path]:
        """Interactive font selector with arrow key navigation using blessed and Rich table"""
        selected_index = 0

        # Add custom path option to fonts list
        all_options = fonts + [None]  # None represents custom path option

        def file_selector_table():
            """Create Rich table with current selection highlighted"""
            table = Table(
                title="📁 Available Font Files",
                caption="Use ↑↓ arrows to navigate, Enter to select, Esc to cancel",
                caption_style="dim",
                show_header=True,
            )
            table.add_column("Font File", style="bright_cyan", min_width=25)
            table.add_column("Location", style="dim white", min_width=12)
            table.add_column("Size", style="bright_green", justify="right", min_width=8)

            for i, font_path in enumerate(all_options):
                row_style = None

                if font_path is None:  # Custom path option
                    name = "[italic]Enter custom path...[/italic]"
                    row_style = "dim white"
                    location = ""
                    size = ""
                else:
                    try:
                        size_bytes = font_path.stat().st_size
                        size = self._format_file_size(size_bytes)
                        location = str(font_path.parent)
                        name = font_path.name
                    except OSError:
                        name = font_path.name
                        location = str(font_path.parent)
                        size = "[dim]Unknown[/dim]"

                # Highlight selected row with blue background
                if i == selected_index:
                    row_style = "bold white on blue"

                table.add_row(name, location, size, style=row_style)

            return table

        # Main interaction loop using position anchored to current program start
        with self.term.cbreak(), self.term.hidden_cursor():
            # init table height
            table_height: int

            # Capture and print initial table
            with self.console.capture() as capture:
                self.console.print(file_selector_table())
            table_output = capture.get()

            # save table height
            table_height = len(table_output.splitlines())
            print(table_output, end="", flush=True)

            while True:
                key = self.term.inkey(timeout=0.1)
                if not key:
                    continue

                old_index = selected_index

                if key.name == "KEY_UP":
                    selected_index = max(0, selected_index - 1)

                elif key.name == "KEY_DOWN":
                    selected_index = min(len(all_options) - 1, selected_index + 1)

                # Only redraw if selection changed - go to exact position relative to program start
                if selected_index != old_index:
                    # Move to table start position (program start + offset for empty line)
                    print(
                        self.term.move_up(table_height),
                        end="",
                        flush=True,
                    )

                    # Redraw table
                    with self.console.capture() as capture:
                        self.console.print(file_selector_table())
                    table_output = capture.get()
                    print(table_output, end="", flush=True)

                elif key.name == "KEY_ENTER" or key == "\r" or key == "\n":
                    # Clear table before exiting
                    print(
                        self.term.move_up(table_height + 1) + self.term.clear_eos,
                        end="",
                        flush=True,
                    )
                    break
                elif key.name == "KEY_ESCAPE" or key == "\x1b":
                    # Move cursor below table before exiting
                    print()
                    return None
                elif key == "q" or key == "Q":
                    # Move cursor below table before exiting
                    print()
                    return None

        # Handle selection
        selected_option = all_options[selected_index]

        if selected_option is None:  # Custom path option
            manual_path = self._prompt_with_cleanup(
                "[yellow]📂 Enter path to font file[/yellow]"
            )
            if manual_path:
                path = Path(manual_path.strip())
                if path.exists() and path.suffix.lower() in self.supported_extensions:
                    return path
                else:
                    self.console.print("[red]❌ Invalid font file[/red]")
            return None
        else:
            return selected_option

    def convert_with_progress(self, input_path: Path, output_path: Path) -> bool:
        """Convert font with beautiful progress display"""

        # Track completed steps for display inside the panel
        completed_steps = []
        current_step = ""

        # Create initial panel content
        def create_panel_content():
            content = f"[bold]Input file:[/bold]  {input_path}\n\n"
            if completed_steps:
                for step in completed_steps:
                    content += f"[green]✓[/green] {step}\n"
            if current_step and current_step not in completed_steps:
                content += f"[yellow]⚡[/yellow] {current_step}...\n"
            if not completed_steps and not current_step:
                content += "[dim]Starting conversion...[/dim]"
            return content

        # Create live updating panel
        panel = Panel(
            create_panel_content(), title="🔄 Font Conversion", border_style="blue"
        )

        with Live(panel, console=self.console, refresh_per_second=4) as live:

            # Create progress display
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                console=self.console,
                transient=True,  # Progress bar disappears after completion
            ) as progress:

                # Add main conversion task
                convert_task = progress.add_task("Starting conversion...", total=10)

                def progress_callback(step, total, description):
                    """Update progress bar with real conversion progress and show persistent steps"""
                    nonlocal current_step, completed_steps

                    # Check if we've moved to a new major step
                    major_steps = [
                        "Loading Apple emoji font",
                        "Ensuring Windows-compatible character mapping",
                        "Analyzing color table format",
                        "Checking essential font tables",
                        "Updating font names for compatibility",
                        "Updating OS/2 table for DirectWrite",
                        "Updating head table",
                        "Updating post table",
                        "Verifying essential font tables",
                        "Optimizing bitmap sizes for DirectWrite",
                        "Saving Windows-compatible font",
                    ]

                    # Find which major step we're in
                    for major_step in major_steps:
                        if major_step.lower() in description.lower():
                            if major_step != current_step:
                                # Mark previous step as complete
                                if current_step and current_step not in completed_steps:
                                    completed_steps.append(current_step)

                                current_step = major_step

                                # Update the live panel
                                live.update(
                                    Panel(
                                        create_panel_content(),
                                        title="🔄 Font Conversion",
                                        border_style="blue",
                                    )
                                )
                            break

                    # Update progress bar
                    progress.update(
                        convert_task,
                        completed=step,
                        total=total,
                        description=description,
                    )

                try:
                    # Call the actual conversion function with progress callback and quiet mode
                    success = convert_apple_emoji_to_windows(
                        str(input_path),
                        str(output_path),
                        progress_callback=progress_callback,
                        quiet=True,  # Suppress duplicate console output
                    )

                    if success:
                        # Mark final step as complete
                        if current_step and current_step not in completed_steps:
                            completed_steps.append(current_step)

                        # Update panel with final completion
                        final_content = f"[bold]Input:[/bold]  {input_path}\n\n"
                        for step in completed_steps:
                            final_content += f"[green]✓[/green] {step}\n"

                        live.update(
                            Panel(
                                final_content,
                                title="🔄 Font Conversion",
                                border_style="green",
                            )
                        )

                        progress.update(
                            convert_task,
                            completed=10,
                            description="[green]✓[/green] Conversion complete!",
                        )

                        # Wait a moment to show completion
                        import time

                        time.sleep(1)

                        # Exit live context to finalize the panel

                    else:
                        progress.update(
                            convert_task, description="❌ Conversion failed"
                        )
                        return False

                except Exception as e:
                    progress.update(convert_task, description="❌ Error occurred")
                    return False

        # Show success panel after live context ends
        if success:
            self.console.print()
            success_panel = Panel(
                f"[bold green]✨ Font successfully converted![/bold green]\n\n"
                f"[bold]Output file:[/bold] {output_path}\n"
                f"[bold]File size:[/bold] {self._format_file_size(output_path.stat().st_size)}\n\n"
                f"[dim]To install on Windows:[/dim]\n"
                f"[dim]1. Copy the font file to your Windows machine[/dim]\n"
                f"[dim]2. Run windows_font_manager.bat as Administrator[/dim]\n"
                f"[dim]3. Choose option 1 (INSTALL)[/dim]\n"
                f"[dim]4. Restart Windows for changes to take effect[/dim]",
                title="🎉 Success",
                border_style="green",
            )
            self.console.print(success_panel)
            return True
        else:
            self.console.print("[red]❌ Font conversion failed[/red]")
            return False

    def interactive_convert(self) -> bool:
        """Interactive conversion workflow"""
        self.show_banner()

        # Select input font
        input_path = self.select_input_font()
        if not input_path:
            return False

        self.console.print()

        # Get output path
        output_path = self.get_output_path(input_path)
        if not output_path:
            return False

        self.console.print()

        # Convert
        return self.convert_with_progress(input_path, output_path)

    def interactive_analyze(self) -> bool:
        """Interactive font analysis"""
        self.show_banner()

        self.console.print("[bold blue]Font Analysis Mode[/bold blue]")
        input_path = self.select_input_font()
        if not input_path:
            return False

        self.console.print()

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
            transient=True,  # Progress disappears after completion
        ) as progress:
            task = progress.add_task("Analyzing font...", total=None)

            try:
                font = TTFont(str(input_path))
                analyze_font_structure(font)
                font.close()

                progress.update(task, description="[green]✓[/green] Analysis complete!")
                return True

            except Exception as e:
                progress.update(task, description="❌ Analysis failed")
                self.console.print(f"[red]❌ Error during analysis: {e}[/red]")
                return False

    def interactive_diagnose(self) -> bool:
        """Interactive font diagnosis"""
        self.show_banner()

        self.console.print("[bold blue]DirectWrite Diagnostics Mode[/bold blue]")
        input_path = self.select_input_font()
        if not input_path:
            return False

        self.console.print()

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
            transient=True,  # Progress disappears after completion
        ) as progress:
            task = progress.add_task("Diagnosing font...", total=None)

            try:
                font = TTFont(str(input_path))
                diagnose_cbdt_cblc_directwrite_issues(font)
                font.close()

                progress.update(
                    task, description="[green]✓[/green] Diagnosis complete!"
                )
                return True

            except Exception as e:
                progress.update(task, description="❌ Diagnosis failed")
                self.console.print(f"[red]❌ Error during diagnosis: {e}[/red]")
                return False
