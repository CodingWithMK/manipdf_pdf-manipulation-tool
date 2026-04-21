from pathlib import Path

import typer
from rich.console import Console

from manipdf.core import advanced, conversions, modification, organization, security

app = typer.Typer(help="ManiPDF - Local, privacy-first PDF manipulation suite.")
console = Console()

# --- Organization Commands ---

@app.command()
def merge(
    inputs: list[Path] = typer.Argument(..., help="Input PDF files to merge."),
    output: Path = typer.Option(..., "--output", "-o", help="Output merged PDF file.")
) -> None:
    """Merge multiple PDFs into one."""
    for path in inputs:
        if not path.exists():
            console.print(f"[bold red]Error: File '{path}' does not exist.[/bold red]")
            raise typer.Exit(code=1)
            
    with console.status("[bold green]Merging PDFs..."):
        organization.merge_pdfs(inputs, output)
    console.print(f"[bold green]Successfully merged into {output}[/bold green]")

@app.command()
def split(
    input_path: Path = typer.Argument(..., help="Input PDF file to split."),
    output_dir: Path = typer.Option(
        ..., "--output-dir", "-d", help="Directory to save split pages."
    )
) -> None:
    """Split a PDF into individual pages."""
    if not input_path.exists():
        console.print(f"[bold red]Error: File '{input_path}' does not exist.[/bold red]")
        raise typer.Exit(code=1)

    with console.status("[bold green]Splitting PDF..."):
        files = organization.split_pdf(input_path, output_dir)
    msg = (
        f"[bold green]Successfully split into {len(files)} pages "
        f"in {output_dir}[/bold green]"
    )
    console.print(msg)

@app.command()
def delete(
    input_path: Path = typer.Argument(..., help="Input PDF file."),
    pages: str = typer.Option(
        ..., "--pages", "-p", help="Page indices to delete (e.g., '0,2,3')."
    ),
    output: Path = typer.Option(..., "--output", "-o", help="Output PDF file.")
) -> None:
    """Delete specific pages from a PDF."""
    if not input_path.exists():
        console.print(f"[bold red]Error: File '{input_path}' does not exist.[/bold red]")
        raise typer.Exit(code=1)

    indices = [int(p.strip()) for p in pages.split(",")]
    organization.delete_pages(input_path, indices, output)
    console.print(f"[bold green]Pages {pages} deleted. Saved to {output}[/bold green]")

@app.command()
def rotate(
    input_path: Path = typer.Argument(..., help="Input PDF file."),
    pages: str = typer.Option(
        ..., "--pages", "-p", help="Page index and angle (e.g., '0:90,1:180')."
    ),
    output: Path = typer.Option(..., "--output", "-o", help="Output PDF file.")
) -> None:
    """Rotate specific pages."""
    if not input_path.exists():
        console.print(f"[bold red]Error: File '{input_path}' does not exist.[/bold red]")
        raise typer.Exit(code=1)

    rotations = {}
    for part in pages.split(","):
        idx, angle = part.split(":")
        rotations[int(idx)] = int(angle)
    organization.rotate_pages(input_path, rotations, output)
    console.print(f"[bold green]Rotated pages. Saved to {output}[/bold green]")

@app.command()
def extract(
    input_path: Path = typer.Argument(..., help="Input PDF file."),
    pages: str = typer.Option(
        ..., "--pages", "-p", help="Page indices to extract (e.g., '0,2')."
    ),
    output: Path = typer.Option(..., "--output", "-o", help="Output PDF file.")
) -> None:
    """Extract specific pages into a new PDF."""
    if not input_path.exists():
        console.print(f"[bold red]Error: File '{input_path}' does not exist.[/bold red]")
        raise typer.Exit(code=1)

    indices = [int(p.strip()) for p in pages.split(",")]
    with console.status("[bold green]Extracting pages..."):
        organization.extract_pages(input_path, indices, output)
    console.print(f"[bold green]Extracted pages {pages} to {output}[/bold green]")

@app.command()
def sort(
    input_path: Path = typer.Argument(..., help="Input PDF file."),
    order: str = typer.Option(
        ..., "--order", "-r", help="New page order (e.g., '2,0,1')."
    ),
    output: Path = typer.Option(..., "--output", "-o", help="Output PDF file.")
) -> None:
    """Sort pages based on a specific order."""
    if not input_path.exists():
        console.print(f"[bold red]Error: File '{input_path}' does not exist.[/bold red]")
        raise typer.Exit(code=1)

    indices = [int(p.strip()) for p in order.split(",")]
    with console.status("[bold green]Sorting pages..."):
        organization.sort_pages(input_path, indices, output)
    console.print(f"[bold green]Sorted pages saved to {output}[/bold green]")

@app.command()
def nup(
    input_path: Path = typer.Argument(..., help="Input PDF file."),
    rows: int = typer.Option(2, "--rows", "-r", help="Number of rows in the grid."),
    cols: int = typer.Option(2, "--cols", "-c", help="Number of columns in the grid."),
    output: Path = typer.Option(..., "--output", "-o", help="Output PDF file.")
) -> None:
    """Create an N-up layout (multiple pages per sheet)."""
    if not input_path.exists():
        console.print(f"[bold red]Error: File '{input_path}' does not exist.[/bold red]")
        raise typer.Exit(code=1)

    with console.status("[bold green]Creating N-up layout..."):
        organization.nup_pdf(input_path, rows, cols, output)
    msg = f"[bold green]Created {rows}x{cols} N-up PDF at {output}[/bold green]"
    console.print(msg)

@app.command()
def overlay(
    input_path: Path = typer.Argument(..., help="Base PDF file."),
    overlay_path: Path = typer.Argument(
        ..., help="Overlay PDF file (watermark/stamp)."
    ),
    output: Path = typer.Option(..., "--output", "-o", help="Output PDF file.")
) -> None:
    """Overlay one PDF onto another."""
    if not input_path.exists():
        console.print(f"[bold red]Error: File '{input_path}' does not exist.[/bold red]")
        raise typer.Exit(code=1)
    if not overlay_path.exists():
        console.print(f"[bold red]Error: File '{overlay_path}' does not exist.[/bold red]")
        raise typer.Exit(code=1)

    with console.status("[bold green]Overlaying PDFs..."):
        organization.overlay_pdf(input_path, overlay_path, output)
    console.print(f"[bold green]Overlay complete. Saved to {output}[/bold green]")

# --- Security Commands ---

@app.command()
def encrypt(
    input_path: Path = typer.Argument(..., help="Input PDF file."),
    password: str = typer.Option(
        ..., "--password", "-p", prompt=True, hide_input=True
    ),
    output: Path = typer.Option(
        ..., "--output", "-o", help="Output encrypted PDF file."
    )
) -> None:
    """Encrypt a PDF with a password."""
    if not input_path.exists():
        console.print(f"[bold red]Error: File '{input_path}' does not exist.[/bold red]")
        raise typer.Exit(code=1)

    security.encrypt_pdf(input_path, password, output)
    console.print(f"[bold green]Successfully encrypted {output}[/bold green]")

@app.command()
def decrypt(
    input_path: Path = typer.Argument(..., help="Input PDF file."),
    password: str = typer.Option(
        ..., "--password", "-p", prompt=True, hide_input=True
    ),
    output: Path = typer.Option(
        ..., "--output", "-o", help="Output decrypted PDF file."
    )
) -> None:
    """Decrypt a PDF with a password."""
    if not input_path.exists():
        console.print(f"[bold red]Error: File '{input_path}' does not exist.[/bold red]")
        raise typer.Exit(code=1)

    success = security.decrypt_pdf(input_path, password, output)
    if success:
        console.print(f"[bold green]Successfully decrypted {output}[/bold green]")
    else:
        console.print("[bold red]Decryption failed. Incorrect password?[/bold red]")
        raise typer.Exit(code=1)

@app.command()
def redact(
    input_path: Path = typer.Argument(..., help="Input PDF file."),
    text: str = typer.Option(..., "--text", "-t", help="Text string to redact."),
    output: Path = typer.Option(..., "--output", "-o", help="Output PDF file.")
) -> None:
    """Redact specific text (black box it)."""
    if not input_path.exists():
        console.print(f"[bold red]Error: File '{input_path}' does not exist.[/bold red]")
        raise typer.Exit(code=1)

    with console.status("[bold green]Redacting text..."):
        count = security.redact_text(input_path, text, output)
    msg = (
        f"[bold green]Redacted {count} instances of '{text}'. "
        f"Saved to {output}[/bold green]"
    )
    console.print(msg)

@app.command()
def watermark(
    input_path: Path = typer.Argument(..., help="Input PDF file."),
    text: str = typer.Option(..., "--text", "-t", help="Watermark text."),
    output: Path = typer.Option(..., "--output", "-o", help="Output PDF file.")
) -> None:
    """Add a text watermark to every page."""
    if not input_path.exists():
        console.print(f"[bold red]Error: File '{input_path}' does not exist.[/bold red]")
        raise typer.Exit(code=1)

    security.add_watermark_text(input_path, text, output)
    console.print(f"[bold green]Watermarked PDF saved to {output}[/bold green]")

# --- Modification Commands ---

@app.command()
def number(
    input_path: Path = typer.Argument(..., help="Input PDF file."),
    output: Path = typer.Option(..., "--output", "-o", help="Output PDF file.")
) -> None:
    """Add page numbers to the bottom center."""
    if not input_path.exists():
        console.print(f"[bold red]Error: File '{input_path}' does not exist.[/bold red]")
        raise typer.Exit(code=1)

    modification.add_page_numbers(input_path, output)
    console.print(f"[bold green]Numbered PDF saved to {output}[/bold green]")

@app.command()
def edit_text(
    input_path: Path = typer.Argument(..., help="Input PDF file."),
    search: str = typer.Option(..., "--search", "-s", help="Text to find."),
    replace: str = typer.Option(..., "--replace", "-r", help="Text to replace with."),
    output: Path = typer.Option(..., "--output", "-o", help="Output PDF file.")
) -> None:
    """Find and replace text in a PDF (local)."""
    if not input_path.exists():
        console.print(f"[bold red]Error: File '{input_path}' does not exist.[/bold red]")
        raise typer.Exit(code=1)

    with console.status("[bold green]Replacing text..."):
        count = modification.find_replace_text(input_path, search, replace, output)
    console.print(f"[bold green]Replaced {count} instances. Saved to {output}[/bold green]")

@app.command()
def compress(
    input_path: Path = typer.Argument(..., help="Input PDF file."),
    output: Path = typer.Option(
        ..., "--output", "-o", help="Output compressed PDF file."
    )
) -> None:
    """Compress a PDF file."""
    if not input_path.exists():
        console.print(f"[bold red]Error: File '{input_path}' does not exist.[/bold red]")
        raise typer.Exit(code=1)

    with console.status("[bold green]Compressing PDF..."):
        modification.compress_pdf(input_path, output)
    console.print(f"[bold green]Compressed PDF saved to {output}[/bold green]")

# --- Conversion Commands ---

@app.command()
def to_pdf(
    inputs: list[Path] = typer.Argument(
        ..., help="Input files or directories (images or office docs)."
    ),
    output: Path = typer.Option(..., "--output", "-o", help="Output PDF file.")
) -> None:
    """Convert images or Office documents to PDF. Supports directories for images."""
    resolved_inputs: list[Path] = []
    image_exts = {".png", ".jpg", ".jpeg", ".bmp", ".tiff"}
    
    for path in inputs:
        if not path.exists():
            console.print(f"[bold red]Error: File or directory '{path}' does not exist.[/bold red]")
            raise typer.Exit(code=1)
        
        if path.is_dir():
            # Find all images in the directory and sort them alphabetically
            found_images = [
                p for p in path.iterdir() 
                if p.is_file() and p.suffix.lower() in image_exts
            ]
            resolved_inputs.extend(sorted(found_images))
        else:
            resolved_inputs.append(path)

    if not resolved_inputs:
        console.print("[bold yellow]No valid input files found.[/bold yellow]")
        return

    exts = {p.suffix.lower() for p in resolved_inputs}
    
    if exts.issubset(image_exts):
        with console.status("[bold green]Converting images to PDF..."):
            conversions.images_to_pdf(resolved_inputs, output)
        console.print(f"[bold green]Created {output}[/bold green]")
    else:
        if len(resolved_inputs) == 1:
            with console.status("[bold green]Converting Office doc to PDF..."):
                conversions.office_to_pdf(resolved_inputs[0], output.parent)
            console.print("[bold green]Conversion complete.[/bold green]")
        else:
            msg = "[yellow]Batch office conversion not yet optimized in CLI.[/yellow]"
            console.print(msg)

@app.command()
def from_pdf(
    input_path: Path = typer.Argument(..., help="Input PDF file."),
    output_dir: Path = typer.Option(
        ..., "--output-dir", "-d", help="Directory to save images."
    ),
    extract: bool = typer.Option(
        False, "--extract", "-e", help="Extract embedded images."
    )
) -> None:
    """Convert PDF pages to images or extract embedded images."""
    if not input_path.exists():
        console.print(f"[bold red]Error: File '{input_path}' does not exist.[/bold red]")
        raise typer.Exit(code=1)

    if extract:
        with console.status("[bold green]Extracting images..."):
            files = conversions.extract_images_from_pdf(input_path, output_dir)
        msg = f"[bold green]Extracted {len(files)} images to {output_dir}[/bold green]"
        console.print(msg)
    else:
        with console.status("[bold green]Rendering PDF pages to images..."):
            files = conversions.pdf_to_images(input_path, output_dir)
        msg = f"[bold green]Rendered {len(files)} pages in {output_dir}[/bold green]"
        console.print(msg)

# --- Advanced Commands ---

@app.command()
def blank(
    output: Path = typer.Option(..., "--output", "-o", help="Output PDF file."),
    pages: int = typer.Option(1, "--pages", "-p", help="Number of pages.")
) -> None:
    """Create a blank PDF."""
    advanced.create_blank_pdf(output, pages)
    msg = f"[bold green]Created {pages}-page blank PDF at {output}[/bold green]"
    console.print(msg)

@app.command()
def ocr(
    input_path: Path = typer.Argument(..., help="Input PDF file."),
    output: Path = typer.Option(..., "--output", "-o", help="Output OCRed PDF file."),
    lang: str = typer.Option("eng", "--lang", "-l", help="OCR language (e.g., 'eng', 'deu').")
) -> None:
    """Apply OCR to a PDF to make it searchable."""
    if not input_path.exists():
        console.print(f"[bold red]Error: File '{input_path}' does not exist.[/bold red]")
        raise typer.Exit(code=1)

    with console.status("[bold green]Applying OCR (this may take a while)..."):
        try:
            advanced.ocr_pdf(input_path, output, lang)
            console.print(f"[bold green]OCRed PDF saved to {output}[/bold green]")
        except Exception as e:
            console.print(f"[bold red]OCR failed: {e}[/bold red]")
            raise typer.Exit(code=1)

@app.command()
def compare(
    pdf1: Path = typer.Argument(..., help="First PDF."),
    pdf2: Path = typer.Argument(..., help="Second PDF."),
    output: Path = typer.Option(..., "--output", "-o", help="Output comparison PDF.")
) -> None:
    """Compare two PDFs by overlaying them."""
    if not pdf1.exists():
        console.print(f"[bold red]Error: File '{pdf1}' does not exist.[/bold red]")
        raise typer.Exit(code=1)
    if not pdf2.exists():
        console.print(f"[bold red]Error: File '{pdf2}' does not exist.[/bold red]")
        raise typer.Exit(code=1)

    with console.status("[bold green]Comparing PDFs..."):
        advanced.compare_pdfs(pdf1, pdf2, output)
    console.print(f"[bold green]Comparison PDF created at {output}[/bold green]")

@app.command()
def gui() -> None:
    """Launch the ManiPDF Graphical User Interface (GUI)."""
    from manipdf.gui.main import main
    main()

if __name__ == "__main__":
    app()
