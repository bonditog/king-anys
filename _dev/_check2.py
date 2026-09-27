# -*- coding: utf-8 -*-
"""Вторая фаза валидации: битые ссылки на функции и ключевые константы."""
import re, sys

path = r"C:\Users\bonda\.cline\data\workspaces\chat\knights-coop\index.html"
src = open(path, encoding="utf-8").read()
js = re.search(r"<script>(.*)</script>", src, re.S).group(1)

# уберём строки и комментарии
def strip(code):
    out = []
    i, n = 0, len(code)
    while i < n:
        ch = code[i]
        if ch == '/' and i + 1 < n and code[i+1] == '/':
            while i < n and code[i] != '\n':
                i += 1
            continue
        if ch == '/' and i + 1 < n and code[i+1] == '*':
            i += 2
            while i + 1 < n and not (code[i] == '*' and code[i+1] == '/'):
                i += 1
            i += 2
            continue
        if ch in ("'", '"', '`'):
            q = ch
            i += 1
            while i < n:
                c = code[i]
                if c == '\\':
                    i += 2
                    continue
                if c == q:
                    i += 1
                    break
                i += 1
            out.append(' ')
            continue
        out.append(ch)
        i += 1
    return ''.join(out)

jsx = strip(js)

# определённые функции (named function declarations / var x=function...)
defined = set(re.findall(r'function\s+([A-Za-z_$][\w$]*)\s*\(', jsx))
defined |= set(re.findall(r'var\s+([A-Za-z_$][\w$]*)\s*=\s*function\b', jsx))
defined |= set(re.findall(r'var\s+([A-Za-z_$][\w$]*)', jsx))
defined |= {'SND'}  # объект с методами
methods = set(re.findall(r'SND\.([A-Za-z_$][\w$]*)\s*\(', jsx))

# все вызовы funName( 
calls = set(re.findall(r'(?<![\.\w$])([A-Za-z_$][\w$]*)\s*\(', jsx))

whitelist = {
    'Math', 'window', 'document', 'canvas', 'ctx', 'performance', 'requestAnimationFrame',
    'console', 'String', 'Object', 'Array', 'isNaN', 'parseInt', 'parseFloat', 'JSON',
}
kw = {'if','for','while','switch','function','return','var','typeof','in','new','instanceof','do','else','catch','case','default','try','throw','delete','void','this'}
unknown = set()
for c in sorted(calls):
    if c in defined or c in whitelist or c in kw:
        continue
    unknown.add(c)

if unknown:
    print("FAIL: undefined calls:", ", ".join(sorted(unknown)))
    # фильтруем, что реально похоже на ошибку — методы G-объектов не входят
    sys.exit(1)

# K.x ссылки
kprops = set(re.findall(r'K\.([A-Za-z_$][\w$]*)', jsx))
ki = jsx.index('var K=')
kei = jsx.index('};', ki)
kdefs = jsx[ki + 6:kei + 1]
kdefnames = set(re.findall(r'\b(\w+)\s*:', kdefs))
missing_k = kprops - kdefnames
if missing_k:
    print("FAIL: missing K props:", sorted(missing_k))
    sys.exit(1)

print("OK second phase: %d calls checked, no unknown refs; SND methods: %s" % (len(calls), sorted(methods)))