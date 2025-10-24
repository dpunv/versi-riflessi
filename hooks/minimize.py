#!/usr/bin/env python3
"""
Script per minimizzare file HTML rimuovendo commenti e spazi superflui
da HTML, CSS e JavaScript
"""

import re
import sys
from pathlib import Path


def minify_css(css_code):
    """Minimizza il codice CSS"""
    # Rimuovi commenti CSS /* ... */
    css_code = re.sub(r'/\*.*?\*/', '', css_code, flags=re.DOTALL)
    
    # Rimuovi spazi multipli e newline
    css_code = re.sub(r'\s+', ' ', css_code)
    
    # Rimuovi spazi attorno a caratteri speciali
    css_code = re.sub(r'\s*([{}:;,>+~])\s*', r'\1', css_code)
    
    # Rimuovi spazi attorno a parentesi
    css_code = re.sub(r'\s*([()])\s*', r'\1', css_code)
    
    # Rimuovi l'ultimo punto e virgola prima della }
    css_code = re.sub(r';\}', '}', css_code)
    
    return css_code.strip()


def minify_js(js_code):
    """Minimizza il codice JavaScript (minimizzazione base)"""
    # Rimuovi commenti singola linea //
    js_code = re.sub(r'//.*?$', '', js_code, flags=re.MULTILINE)
    
    # Rimuovi commenti multi-linea /* ... */
    js_code = re.sub(r'/\*.*?\*/', '', js_code, flags=re.DOTALL)
    
    # Rimuovi spazi multipli e newline (preservando stringhe)
    js_code = re.sub(r'\s+', ' ', js_code)
    
    # Rimuovi spazi attorno a operatori e punteggiatura
    js_code = re.sub(r'\s*([{}()\[\];,:<>!=+\-*/%&|^])\s*', r'\1', js_code)
    
    # Ripristina spazi necessari per parole chiave (usando word boundary)
    js_code = re.sub(r'\b(return|var|let|const|if|else|for|while|function|class|new|typeof|delete|instanceof)\b([a-zA-Z0-9_$])', r'\1 \2', js_code)
    js_code = re.sub(r'([a-zA-Z0-9_$])\b(return|var|let|const|if|else|for|while|function|class|new|typeof|delete|instanceof|in|of)\b', r'\1 \2', js_code)
    
    # Gestisci "in" e "of" separatamente per evitare falsi positivi (window, lines, ecc.)
    js_code = re.sub(r'\)in\(', ') in(', js_code)
    js_code = re.sub(r'\)in\[', ') in[', js_code)
    js_code = re.sub(r'\)of\(', ') of(', js_code)
    js_code = re.sub(r'\)of\[', ') of[', js_code)
    
    return js_code.strip()


def minify_html(html_code):
    """Minimizza il codice HTML"""
    # Estrai e salva i blocchi <style> e <script>
    style_blocks = []
    script_blocks = []
    
    # Processa blocchi <style>
    def replace_style(match):
        minified = minify_css(match.group(1))
        idx = len(style_blocks)
        style_blocks.append(f'<style>{minified}</style>')
        return f'___STYLE_BLOCK_{idx}___'
    
    html_code = re.sub(r'<style[^>]*>(.*?)</style>', replace_style, html_code, flags=re.DOTALL | re.IGNORECASE)
    
    # Processa blocchi <script>
    def replace_script(match):
        # Preserva gli attributi del tag script
        opening_tag = match.group(1)
        js_content = match.group(2)
        
        # Se il contenuto è vuoto o contiene solo spazi, preservalo così
        if not js_content.strip():
            minified = js_content
        else:
            minified = minify_js(js_content)
        
        idx = len(script_blocks)
        script_blocks.append(f'<script{opening_tag}>{minified}</script>')
        return f'___SCRIPT_BLOCK_{idx}___'
    
    html_code = re.sub(r'<script([^>]*)>(.*?)</script>', replace_script, html_code, flags=re.DOTALL | re.IGNORECASE)
    
    # Rimuovi commenti HTML <!-- ... -->
    html_code = re.sub(r'<!--.*?-->', '', html_code, flags=re.DOTALL)
    
    # Rimuovi spazi multipli e newline
    html_code = re.sub(r'\s+', ' ', html_code)
    
    # Rimuovi spazi attorno ai tag
    html_code = re.sub(r'>\s+<', '><', html_code)
    
    # Rimuovi spazi all'inizio e alla fine
    html_code = html_code.strip()
    
    # Ripristina i blocchi <style>
    for idx, block in enumerate(style_blocks):
        html_code = html_code.replace(f'___STYLE_BLOCK_{idx}___', block)
    
    # Ripristina i blocchi <script>
    for idx, block in enumerate(script_blocks):
        html_code = html_code.replace(f'___SCRIPT_BLOCK_{idx}___', block)
    
    return html_code


def minify_file(input_file, output_file=None):
    """Minimizza un file HTML"""
    input_path = Path(input_file)
    
    if not input_path.exists():
        print(f"Errore: il file '{input_file}' non esiste")
        return False
    
    # Leggi il file
    with open(input_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Minimizza
    minified_html = minify_html(html_content)
    
    # Determina il file di output
    if output_file is None:
        output_path = input_path.parent / f"{input_path.stem}.min{input_path.suffix}"
    else:
        output_path = Path(output_file)
    
    # Scrivi il file minimizzato
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(minified_html)
    
    # Statistiche
    original_size = len(html_content)
    minified_size = len(minified_html)
    reduction = ((original_size - minified_size) / original_size) * 100
    
    print(f"✓ File minimizzato salvato in: {output_path}")
    print(f"  Dimensione originale: {original_size:,} byte")
    print(f"  Dimensione minimizzata: {minified_size:,} byte")
    print(f"  Riduzione: {reduction:.1f}%")
    
    return True


def main():
    """Funzione principale"""
    if len(sys.argv) < 2:
        print("Uso: python minify_html.py <file_input.html> [file_output.html]")
        print("\nSe non specifichi un file di output, verrà creato un file")
        print("con il suffisso .min (es: index.html → index.min.html)")
        sys.exit(1)
    
    
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    success = minify_file(input_file, output_file)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()