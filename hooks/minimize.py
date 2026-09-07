#!/usr/bin/env python3
"""
Script di build e minimizzazione per Versi Riflessi.
- Legge i file sorgente da code/ (code/full.html, code/styles/style.css, code/scripts/*.js)
- Unisce ed include inline CSS e JS
- Adatta i percorsi degli asset (../images/ -> images/, ../manifest.json -> manifest.json)
- Minimizza al massimo HTML, CSS e JS
- Genera index.html pronto per il deploy
- Minimizza code/scripts/service-worker.js -> ./service-worker.js
"""

import re
import sys
from pathlib import Path


def minify_css(css: str) -> str:
    """Minimizza il codice CSS"""
    # Rimuovi commenti CSS /* ... */
    css = re.sub(r'/\*[\s\S]*?\*/', '', css)
    # Rimuovi spazi multipli e newline
    css = re.sub(r'\s+', ' ', css)
    # Rimuovi spazi attorno a caratteri speciali
    css = re.sub(r'\s*([{}:;,>+~])\s*', r'\1', css)
    # Rimuovi spazi attorno a parentesi
    css = re.sub(r'\s*([()])\s*', r'\1', css)
    # Rimuovi l'ultimo punto e virgola prima della }
    css = re.sub(r';\}', '}', css)
    return css.strip()


def minify_js(js: str) -> str:
    """
    Minimizza JavaScript preservando in modo sicuro stringhe singole,
    doppie e template literals (backtick) e commenti.
    """
    pattern = re.compile(
        r'(?P<STRING_DQ>"(?:[^"\\]|\\.)*")|'
        r"(?P<STRING_SQ>'(?:[^'\\]|\\.)*')|"
        r'(?P<STRING_BT>`(?:[^`\\]|\\.)*`)|'
        r'(?P<COMMENT_LINE>//[^\r\n]*)|'
        r'(?P<COMMENT_BLOCK>/\*[\s\S]*?\*/)|'
        r'(?P<WHITESPACE>\s+)|'
        r'(?P<WORD>[a-zA-Z_$][a-zA-Z0-9_$]*)|'
        r'(?P<NUMBER>0[xX][0-9a-fA-F]+|\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)|'
        r'(?P<PUNCT>[{}()\[\];,:])|'
        r'(?P<OP>===|!==|==|!=|<=|>=|=>|\+\+|--|&&|\|\||<<|>>|\+=|-=|\*=|/=|%=|&=|\|=|\^=|[+\-*/%&|^~!<>=?])|'
        r'(?P<OTHER>.)'
    )

    KEYWORD_SPACES = {
        'return', 'var', 'let', 'const', 'if', 'else', 'for', 'while', 'do',
        'function', 'class', 'new', 'typeof', 'delete', 'instanceof', 'in',
        'of', 'throw', 'case', 'catch', 'finally', 'try', 'await', 'async',
        'yield', 'import', 'export', 'default', 'extends'
    }

    tokens = []
    for m in pattern.finditer(js):
        kind = m.lastgroup
        val = m.group()
        if kind in ('COMMENT_LINE', 'COMMENT_BLOCK'):
            continue
        tokens.append((kind, val))

    output = []
    prev_kind = None
    prev_val = None

    for kind, val in tokens:
        if kind == 'WHITESPACE':
            continue

        if prev_kind is not None:
            # Word or number followed by word or number
            if (prev_kind in ('WORD', 'NUMBER') and kind in ('WORD', 'NUMBER')):
                output.append(' ')
            # Keyword followed by string
            elif prev_kind == 'WORD' and prev_val in KEYWORD_SPACES and kind in ('STRING_DQ', 'STRING_SQ', 'STRING_BT'):
                output.append(' ')
            # + followed by + or - followed by -
            elif prev_val == '+' and val in ('+', '++'):
                output.append(' ')
            elif prev_val == '-' and val in ('-', '--'):
                output.append(' ')

        output.append(val)
        prev_kind = kind
        prev_val = val

    return ''.join(output).strip()


def minify_html(html: str) -> str:
    """Minimizza il codice HTML preservando blocchi <style> e <script> già minimizzati"""
    style_blocks = []
    script_blocks = []

    def save_style(match):
        idx = len(style_blocks)
        style_blocks.append(match.group(0))
        return f'___STYLE_BLOCK_{idx}___'

    def save_script(match):
        idx = len(script_blocks)
        script_blocks.append(match.group(0))
        return f'___SCRIPT_BLOCK_{idx}___'

    html = re.sub(r'<style[^>]*>[\s\S]*?</style>', save_style, html, flags=re.IGNORECASE)
    html = re.sub(r'<script[^>]*>[\s\S]*?</script>', save_script, html, flags=re.IGNORECASE)

    # Rimuovi commenti HTML
    html = re.sub(r'<!--[\s\S]*?-->', '', html)

    # Rimuovi spazi multipli e newline
    html = re.sub(r'\s+', ' ', html)

    # Rimuovi spazi tra tag
    html = re.sub(r'>\s+<', '><', html)

    html = html.strip()

    # Ripristina style
    for idx, block in enumerate(style_blocks):
        html = html.replace(f'___STYLE_BLOCK_{idx}___', block)

    # Ripristina script
    for idx, block in enumerate(script_blocks):
        html = html.replace(f'___SCRIPT_BLOCK_{idx}___', block)

    return html


def build(project_root: Path = None):
    """Esegue la build e minimizzazione da code/ a root"""
    if project_root is None:
        project_root = Path(__file__).resolve().parent.parent

    code_dir = project_root / 'code'
    full_html_path = code_dir / 'full.html'
    style_css_path = code_dir / 'styles' / 'style.css'
    poesie_js_path = code_dir / 'scripts' / 'poesie.js'
    app_js_path = code_dir / 'scripts' / 'applicazione.js'
    sw_src_path = code_dir / 'scripts' / 'service-worker.js'

    output_index_path = project_root / 'index.html'
    output_sw_path = project_root / 'service-worker.js'

    if not full_html_path.exists():
        print(f"Errore: File sorgente non trovato in {full_html_path}")
        return False

    print("🚀 Avvio compilazione e minimizzazione di Versi Riflessi...")

    # 1. Leggi HTML sorgente
    with open(full_html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # 2. Leggi e minimizza CSS
    if style_css_path.exists():
        with open(style_css_path, 'r', encoding='utf-8') as f:
            css_raw = f.read()
        css_min = minify_css(css_raw)
        # Sostituisci il tag <link rel="stylesheet" ...> con <style>...</style>
        html_content = re.sub(
            r'<link\s+[^>]*rel=["\']stylesheet["\'][^>]*>',
            f'<style>{css_min}</style>',
            html_content,
            flags=re.IGNORECASE
        )
        print(f"  ✓ CSS compilato: {len(css_raw):,} B → {len(css_min):,} B")

    # 3. Leggi e minimizza JS (poesie.js + applicazione.js)
    js_parts = []
    if poesie_js_path.exists():
        with open(poesie_js_path, 'r', encoding='utf-8') as f:
            js_parts.append(f.read())
    if app_js_path.exists():
        with open(app_js_path, 'r', encoding='utf-8') as f:
            js_parts.append(f.read())

    if js_parts:
        js_combined = '\n;\n'.join(js_parts)
        js_min = minify_js(js_combined)

        # Rimuovi i tag <script src="scripts/..."></script>
        html_content = re.sub(
            r'<script\s+[^>]*src=["\']scripts/[^"\']+["\'][^>]*>\s*</script>',
            '',
            html_content,
            flags=re.IGNORECASE
        )

        # Inserisci il blocco <script> prima di </body>
        script_tag = f'<script>{js_min}</script>'
        if '</body>' in html_content:
            html_content = html_content.replace('</body>', f'{script_tag}</body>')
        else:
            html_content += script_tag

        print(f"  ✓ JavaScript compilato: {len(js_combined):,} B → {len(js_min):,} B")

    # 4. Adatta i percorsi degli asset relativi (da ../images/ a images/, da ../manifest.json a manifest.json)
    html_content = html_content.replace('../images/', 'images/')
    html_content = html_content.replace('../manifest.json', 'manifest.json')

    # 5. Minimizza l'intero HTML
    html_min = minify_html(html_content)

    # Scrivi index.html finale
    with open(output_index_path, 'w', encoding='utf-8') as f:
        f.write(html_min)

    # Calcola statistiche sorgenti totali
    total_src_size = len(html_content)
    if style_css_path.exists():
        total_src_size += style_css_path.stat().st_size
    if poesie_js_path.exists():
        total_src_size += poesie_js_path.stat().st_size
    if app_js_path.exists():
        total_src_size += app_js_path.stat().st_size

    final_index_size = len(html_min.encode('utf-8'))
    reduction = ((total_src_size - final_index_size) / total_src_size) * 100

    print(f"✓ index.html generato con successo: {output_index_path}")
    print(f"  Dimensione totale sorgenti dev: {total_src_size:,} byte")
    print(f"  Dimensione bundle finale: {final_index_size:,} byte ({reduction:.1f}% riduzione)")

    # 6. Compila e minimizza Service Worker alla root
    if sw_src_path.exists():
        with open(sw_src_path, 'r', encoding='utf-8') as f:
            sw_raw = f.read()
        sw_min = minify_js(sw_raw)
        with open(output_sw_path, 'w', encoding='utf-8') as f:
            f.write(sw_min)
        print(f"✓ service-worker.js generato alla root: {len(sw_raw):,} B → {len(sw_min):,} B")

    print("✨ Build completata con successo!")
    return True


def main():
    project_root = Path(__file__).resolve().parent.parent
    success = build(project_root)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()