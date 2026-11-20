"""
math_formatter.py - Converts scientific and LaTeX math notation to clean, beautifully readable Unicode & Markdown.
Handles inline equations ($...$, \(...\)), display equations ($$...$$, \[...\]), fractions, Greek symbols,
superscripts, subscripts, roots, and physical units so that Markdown renderers display formulas crisply.
"""

import re

GREEK_MAP = {
    r"\alpha": "α", r"\beta": "β", r"\gamma": "γ", r"\Gamma": "Γ",
    r"\delta": "δ", r"\Delta": "Δ", r"\epsilon": "ε", r"\varepsilon": "ε",
    r"\zeta": "ζ", r"\eta": "η", r"\theta": "θ", r"\vartheta": "θ", r"\Theta": "Θ",
    r"\iota": "ι", r"\kappa": "κ", r"\lambda": "λ", r"\Lambda": "Λ",
    r"\mu": "μ", r"\nu": "ν", r"\xi": "ξ", r"\Xi": "Ξ",
    r"\pi": "π", r"\Pi": "Π", r"\rho": "ρ", r"\varrho": "ρ",
    r"\sigma": "σ", r"\Sigma": "Σ", r"\tau": "τ", r"\upsilon": "υ",
    r"\phi": "φ", r"\varphi": "ϕ", r"\Phi": "Φ", r"\chi": "χ",
    r"\psi": "ψ", r"\Psi": "Ψ", r"\omega": "ω", r"\Omega": "Ω",
}

MATH_SYMBOLS = {
    r"\times": "×", r"\cdot": "·", r"\div": "÷", r"\pm": "±", r"\mp": "∓",
    r"\leq": "≤", r"\le": "≤", r"\geq": "≥", r"\ge": "≥",
    r"\neq": "≠", r"\ne": "≠", r"\approx": "≈", r"\equiv": "≡",
    r"\infty": "∞", r"\partial": "∂", r"\nabla": "∇",
    r"\int": "∫", r"\iint": "∬", r"\iiint": "∭", r"\oint": "∮",
    r"\sum": "∑", r"\prod": "∏",
    r"\rightarrow": "→", r"\to": "→", r"\leftarrow": "←",
    r"\Rightarrow": "⇒", r"\Leftarrow": "⇐", r"\leftrightarrow": "↔",
    r"\in": "∈", r"\notin": "∉", r"\subset": "⊂", r"\subseteq": "⊆",
    r"\forall": "∀", r"\exists": "∃", r"\angle": "∠", r"\perp": "⊥",
    r"\degree": "°", r"^\circ": "°",
}

CAL_MAP = {
    "A": "𝒜", "B": "ℬ", "C": "𝒞", "D": "𝒟", "E": "ℰ", "F": "ℱ",
    "G": "𝒢", "H": "ℋ", "I": "ℐ", "J": "𝒥", "K": "𝒦", "L": "ℒ",
    "M": "ℳ", "N": "𝒩", "O": "𝒪", "P": "𝒫", "Q": "𝒬", "R": "ℛ",
    "S": "𝒮", "T": "𝒯", "U": "𝒰", "V": "𝒱", "W": "𝒲", "X": "𝒳",
    "Y": "𝒴", "Z": "𝒵"
}

SUP_MAP = {
    "0": "⁰", "1": "¹", "2": "²", "3": "³", "4": "⁴",
    "5": "⁵", "6": "⁶", "7": "⁷", "8": "⁸", "9": "⁹",
    "+": "⁺", "-": "⁻", "=": "⁼", "(": "⁽", ")": "⁾",
    "n": "ⁿ", "i": "ⁱ", "x": "ˣ", "y": "ʸ",
}

SUB_MAP = {
    "0": "₀", "1": "₁", "2": "₂", "3": "₃", "4": "₄",
    "5": "₅", "6": "₆", "7": "₇", "8": "₈", "9": "₉",
    "+": "₊", "-": "₋", "=": "₌", "(": "₍", ")": "₎",
    "a": "ₐ", "e": "ₑ", "h": "ₕ", "i": "ᵢ", "j": "ⱼ", "k": "ₖ",
    "l": "ₗ", "m": "ₘ", "n": "ₙ", "o": "ₒ", "p": "ₚ", "r": "ᵣ",
    "s": "ₛ", "t": "ₜ", "u": "ᵤ", "v": "ᵥ", "x": "ₓ",
    "B": "ᵦ", "E": "ₑ",
}


def _extract_braces(s: str, start_idx: int):
    if start_idx >= len(s) or s[start_idx] != '{':
        return None, start_idx
    depth = 0
    for i in range(start_idx, len(s)):
        if s[i] == '{':
            depth += 1
        elif s[i] == '}':
            depth -= 1
            if depth == 0:
                return s[start_idx + 1:i], i + 1
    return None, start_idx


def _to_subscript(s: str) -> str:
    res = []
    all_mapped = True
    for ch in s:
        if ch in SUB_MAP:
            res.append(SUB_MAP[ch])
        else:
            all_mapped = False
            res.append(ch)
    if all_mapped:
        return "".join(res)
    return f"_{s}"


def _to_superscript(s: str) -> str:
    res = []
    all_mapped = True
    for ch in s:
        if ch in SUP_MAP:
            res.append(SUP_MAP[ch])
        else:
            all_mapped = False
            res.append(ch)
    if all_mapped:
        return "".join(res)
    return f"^{s}"


def _parse_fractions(eq: str) -> str:
    while True:
        idx = eq.find(r"\frac")
        if idx == -1:
            break
        after_frac = idx + len(r"\frac")
        while after_frac < len(eq) and eq[after_frac].isspace():
            after_frac += 1
        num, next_idx = _extract_braces(eq, after_frac)
        if num is None:
            break
        while next_idx < len(eq) and eq[next_idx].isspace():
            next_idx += 1
        den, end_idx = _extract_braces(eq, next_idx)
        if den is None:
            break
        clean_num = format_equation(num)
        clean_den = format_equation(den)
        eq = eq[:idx] + f"({clean_num} / {clean_den})" + eq[end_idx:]
    return eq


def format_equation(expr: str) -> str:
    eq = expr.strip()
    if not eq:
        return ""

    # Parse fractions before braces cleanup
    eq = _parse_fractions(eq)

    # Mathcal: \mathcal{E} -> ℰ
    def _rep_cal(m):
        ch = m.group(1)
        return CAL_MAP.get(ch, ch)
    eq = re.sub(r"\\mathcal\{([A-Za-z])\}", _rep_cal, eq)

    # Text / mathrm / mathbf / mathit
    eq = re.sub(r"\\(text|mathrm|mathbf|mathit|boldsymbol)\{([^{}]+)\}", r"\2", eq)

    # Square roots: \sqrt{...}
    while r"\sqrt" in eq:
        idx = eq.find(r"\sqrt")
        after = idx + len(r"\sqrt")
        while after < len(eq) and eq[after].isspace():
            after += 1
        inner, end_idx = _extract_braces(eq, after)
        if inner is not None:
            clean_inner = format_equation(inner)
            eq = eq[:idx] + f"√({clean_inner})" + eq[end_idx:]
        else:
            m = re.match(r"\\sqrt\s*([0-9a-zA-Z])", eq[idx:])
            if m:
                eq = eq[:idx] + f"√({m.group(1)})" + eq[idx + m.end():]
            else:
                break

    # Greek symbols
    for k, v in GREEK_MAP.items():
        eq = re.sub(re.escape(k) + r"(?![A-Za-z])", v, eq)

    # Math symbols
    for k, v in MATH_SYMBOLS.items():
        eq = re.sub(re.escape(k) + r"(?![A-Za-z])", v, eq)

    # Superscripts: ^{...} or ^x
    def _rep_sup(m):
        inner = m.group(1) or m.group(2)
        return _to_superscript(inner)
    eq = re.sub(r"\^\{([^{}]+)\}|\^([0-9a-zA-Z+-])", _rep_sup, eq)

    # Subscripts: _{...} or _x
    def _rep_sub(m):
        inner = m.group(1) or m.group(2)
        return _to_subscript(inner)
    eq = re.sub(r"_\{([^{}]+)\}|_([0-9a-zA-Z+-])", _rep_sub, eq)

    # Clean redundant braces & slashes
    eq = eq.replace("{", "").replace("}", "")
    eq = re.sub(r"\\,", " ", eq)
    eq = re.sub(r"\\;", " ", eq)
    eq = re.sub(r"\\quad", "  ", eq)
    eq = re.sub(r"\\qquad", "   ", eq)
    eq = re.sub(r"\\left|\\right", "", eq)
    eq = re.sub(r"\\", "", eq)

    # Collapse space after diff/delta e.g. Δ t -> Δt, Δ Φ -> ΔΦ (only Greek delta/partial or standalone d)
    eq = re.sub(r"([Δδ∂])\s+([A-Za-zα-ωΑ-Ω])", r"\1\2", eq)
    eq = re.sub(r"\bd\s+([A-Za-z])", r"d\1", eq)

    # Clean multiplication spacing: e.g. -N ( -> -N · (
    eq = re.sub(r"([0-9A-Za-zα-ωΑ-Ωℰ])\s*\(([^\)]+)\)", r"\1 · (\2)", eq)

    eq = re.sub(r"\s+", " ", eq).strip()
    return eq


def format_scientific_text(content: str) -> str:
    """Transforms raw LaTeX and mathematical notation inside text into clean, beautiful Unicode and Markdown."""
    if not content:
        return ""

    # Replace display equations: $$...$$ or \[...\]
    def _rep_display(m):
        raw = m.group(1)
        formatted = format_equation(raw)
        return f"\n\n> 📐 **Formula:** `{formatted}`\n\n"

    res = re.sub(r"\$\$(.+?)\$\$", _rep_display, content, flags=re.DOTALL)
    res = re.sub(r"\\\[(.+?)\\\]", _rep_display, res, flags=re.DOTALL)

    # Replace inline equations: $...$ or \(...\)
    def _rep_inline(m):
        raw = m.group(1).strip()
        # If it's a simple currency amount like $100 or $5, don't convert
        if re.match(r"^\d+(\.\d+)?$", raw):
            return f"${raw}"
        formatted = format_equation(raw)
        if len(formatted) == 1 and formatted.isalpha():
            return f"**{formatted}**"
        return f"**{formatted}**" if any(c in formatted for c in "=+-/·*<>≤≥≠≈√ΔΦλπθΩℰ⁰¹²³⁴⁵⁶⁷⁸⁹₀₁₂₃₄₅₆₇₈₉ᵦ") else formatted

    res = re.sub(r"\$([^\$\n]+?)\$", _rep_inline, res)
    res = re.sub(r"\\\((.+?)\\\)", _rep_inline, res)

    # Clean redundant empty lines
    res = re.sub(r"\n{3,}", "\n\n", res)
    return res
