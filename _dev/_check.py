# -*- coding: utf-8 -*-
"""Лёгкий валидатор JS-блока в index.html: баланс скобок + целостность строк/комментариев."""
import re, sys

path = r"C:\Users\bonda\.cline\data\workspaces\chat\knights-coop\index.html"
src = open(path, encoding="utf-8").read()

m = re.search(r"<script>(.*)</script>", src, re.S)
if not m:
    print("FAIL: script block not found")
    sys.exit(1)
js = m.group(1)

def validate(code):
    i, n = 0, len(code)
    stack = []
    pairs = {')': '(', ']': '[', '}': '{'}
    line = 1
    errors = []
    mode_stack = []
    while i < n:
        ch = code[i]
        if ch == '\n':
            line += 1
            i += 1
            continue
        # line comment
        if ch == '/' and i + 1 < n and code[i+1] == '/':
            while i < n and code[i] != '\n':
                i += 1
            continue
        # block comment
        if ch == '/' and i + 1 < n and code[i+1] == '*':
            i += 2
            while i + 1 < n and not (code[i] == '*' and code[i+1] == '/'):
                if code[i] == '\n':
                    line += 1
                i += 1
            i += 2
            continue
        # strings (single/double/template)
        if ch in ("'", '"', '`'):
            quote = ch
            i += 1
            while i < n:
                c = code[i]
                if c == '\\':
                    i += 2
                    continue
                if c == quote:
                    i += 1
                    break
                if c == '\n' and quote != '`':
                    errors.append("Unterminated string starting line %d" % line)
                    break
                if c == '\n':
                    line += 1
                i += 1
            continue
        if ch in '([{':
            stack.append((ch, line))
        elif ch in ')]}':
            if not stack:
                errors.append("Extra closing %s at line %d" % (ch, line))
            elif stack[-1][0] != pairs[ch]:
                errors.append("Mismatch %s at line %d (expected for %s)" % (ch, line, stack[-1][0]))
            else:
                stack.pop()
        i += 1
    if stack:
        errors.append("Unclosed %s from line %d" % (stack[-1][0], stack[-1][1]))
    return errors

errs = validate(js)
if errs:
    print("FAIL")
    for e in errs[:30]:
        print("  ", e)
    sys.exit(1)

# Проверка наличия ключевых функций
for func in ["drawKnight", "drawSkeleton", "drawBoss", "drawKing", "updatePlayers",
             "updateMonsters", "updateBoss", "updateWorld", "drawShop", "startToll",
             "updateEnding", "drawEndingScene", "function loop", "newGame", "startLevel"]:
    if func not in js:
        print("FAIL: missing %s" % func)
        sys.exit(1)

print("OK: JS balanced, all key functions present, %d chars of script" % len(js))
