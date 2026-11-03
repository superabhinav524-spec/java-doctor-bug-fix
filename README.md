# JavaDoctor 🩺⚡
> **Automated Bug Hunter, Analyzer & Precision Auto-Fixer for Java**

JavaDoctor is a static analysis and automated code repair tool designed to find, explain, and automatically repair critical and subtle bugs in Java codebases. It pairs static rule patterns with automated patch generation and live `javac` compiler verification to ensure that every applied fix is syntactically sound.

---

## 🚀 Key Features

- **Precision Bug Detection**: Finds dangerous anti-patterns, null dereferences, resource leaks, infinite loops, and concurrency hazards.
- **Automated Fix Generation**: Automatically writes safe, idiomatically correct Java fixes and generates unified diffs.
- **Live `javac` Compiler Verification**: Automatically verifies generated patches by compiling with your system's Java compiler (auto-detects JDK 17/21/etc.) before accepting changes.
- **Non-Destructive Repairs**: Generates `.bak` file backups before modifying any files, and provides `--dry-run` to preview changes safely.
- **Interactive Web Dashboard**: Beautiful, zero-dependency browser-based workbench for interactive debugging, side-by-side diff comparison, live code doctoring, and project directory scans.
- **Developer-Friendly CLI**: Colored terminal reports, detailed explanations of *why* each bug occurs, line snippets with arrows, and instant fix suggestions.
- **Zero External Dependencies**: Core engine and web server run purely on the standard library with optional JDK integration.

---

## 📋 Detected Bug Categories & Rules

| Rule ID | Severity | Category | Description | Auto-Fixable? |
| :--- | :--- | :--- | :--- | :---: |
| `STRING_EQUALS_OPERATOR` | **CRITICAL** | Correctness | `==` or `!=` used for String comparison instead of `.equals()` | ✅ Yes |
| `NULL_DEREF_EQUALS` | **HIGH** | Null Safety | `var.equals("literal")` risks NPE; flips to `"literal".equals(var)` | ✅ Yes |
| `ARRAY_EQUALS` | **CRITICAL** | Correctness | `arr.equals(other)` checks address identity; replaces with `Arrays.equals` | ✅ Yes |
| `OFF_BY_ONE_LOOP` | **CRITICAL** | Correctness | `i <= arr.length` or `i <= list.size()` triggers `IndexOutOfBoundsException` | ✅ Yes |
| `INFINITE_LOOP_STEP` | **CRITICAL** | Correctness | Inverted loop step (e.g. `i--` in `i < limit` loop) hangs CPU | ✅ Yes |
| `EMPTY_CATCH_BLOCK` | **HIGH** | Error Handling | Silently swallowed exceptions; inserts trace logging | ✅ Yes |
| `BIGDECIMAL_DOUBLE_CONSTRUCTOR` | **HIGH** | Correctness | `new BigDecimal(0.1)` causes binary float inaccuracies | ✅ Yes |
| `OPTIONAL_ASSIGN_NULL` | **HIGH** | Null Safety | Assigning `null` to `Optional<T>` re-introduces NPEs | ✅ Yes |
| `COLLECTION_RETURN_NULL` | **MEDIUM** | Null Safety | Returning `null` from `List`/`Set`/`Map` method instead of `Collections.emptyList()` | ✅ Yes |
| `RESOURCE_LEAK` | **HIGH** | Resource Leak | Unclosed I/O streams/scanners outside `try-with-resources` | Guided |
| `CONCURRENT_MODIFICATION` | **CRITICAL** | Concurrency | Modifying collections inside enhanced for-loops | Guided |
| `RAW_THROWABLE` | **HIGH** | Error Handling | Direct `throw new Throwable()` or `Error()` | ✅ Yes |
| `DIVISION_BY_ZERO` | **CRITICAL** | Correctness | Explicit division or modulo by literal `0` | Flagged |

---

## 🛠️ Quick Start

### 1. Run via Batch / Shell Script
From the project folder:
```bash
# Scan a file or directory
.\javadoctor.bat scan examples

# Dry-run fixes to preview patches without touching disk
.\javadoctor.bat fix examples --dry-run

# Fix all files in a folder with backups (.bak) and compiler verification
.\javadoctor.bat fix examples

# Verify compilation with javac
.\javadoctor.bat verify examples/StringEqualityBug.java

# Launch the interactive Web Dashboard
.\javadoctor.bat web --port 8080
```

### 2. Run via Python Module
```bash
# Scan target
python -m javadoctor.cli.main scan path/to/MyClass.java

# Apply fixes with javac verification
python -m javadoctor.cli.main fix path/to/MyClass.java

# List all available rules
python -m javadoctor.cli.main rules

# Start Web Server
python -m javadoctor.cli.main web
```

---

## 🌐 Web Dashboard

JavaDoctor includes a built-in web dashboard. To launch:
```bash
.\javadoctor.bat web --port 8080
```
Open **`http://localhost:8080`** in any browser.

The dashboard features:
1. **Code Doctor / Playground**: Paste any Java code, select from sample presets, scan for bugs, view side-by-side unified diffs, and click **Auto-Fix** to instantly clean the code.
2. **Project Scanner**: Scan entire folders, view breakdown cards (Files with bugs, Total issues, Critical vulnerabilities), and fix files with 1 click.
3. **Rules Catalog**: Complete searchable documentation of all static rules with impact analyses.

---

## 🧪 Running Automated Tests

Run the comprehensive unit test suite and `javac` verification tests:
```bash
python -m unittest discover -s tests -p "test_*.py"
```

All 16 test suites verify:
- Rule detection accuracy across edge cases.
- Patch generation and auto-imports (e.g. `java.util.Arrays`, `java.util.Collections`).
- End-to-end compilation with JDK 17 to ensure patched Java code compiles with zero errors.

---

## 📁 Project Structure

```
java-bug-doctor/
├── javadoctor/
│   ├── core/
│   │   ├── models.py         # Bug, Severity, Category, FileReport, ScanSummary
│   │   ├── engine.py         # Scanner, Fixer, PatchGenerator
│   │   └── verifier.py       # Javac integration (auto-detects JDK 17/21/etc.)
│   ├── rules/
│   │   ├── base.py           # BaseRule and RuleRegistry
│   │   ├── string_rules.py   # String equality (==), null dereference (.equals)
│   │   ├── array_rules.py    # Array .equals(), off-by-one loops (<= length)
│   │   ├── loop_rules.py     # Inverted loop step / infinite loops
│   │   ├── exception_rules.py# Swallowed exceptions in empty catch blocks
│   │   ├── numeric_rules.py  # BigDecimal(double), division by zero
│   │   ├── null_safety_rules.py # Optional null assignment, collection null return
│   │   ├── resource_rules.py # Stream and scanner leaks
│   │   └── concurrency_rules.py # ConcurrentModification in for-each
│   ├── cli/
│   │   └── main.py           # Interactive CLI with colors and diffs
│   └── web/
│       ├── server.py         # Zero-dependency HTTP REST API
│       └── static/           # Modern Dark-Mode Web Dashboard (HTML/CSS/JS)
├── examples/                 # Sample buggy Java files for testing
│   ├── StringEqualityBug.java
│   ├── ArrayEqualsBug.java
│   ├── OffByOneLoopBug.java
│   ├── SwallowedExceptionBug.java
│   ├── BigDecimalPrecisionBug.java
│   ├── CollectionNullReturnBug.java
│   └── ResourceLeakBug.java
├── tests/                    # Unit and integration test suite
│   ├── test_rules.py
│   ├── test_engine.py
│   └── test_javac_integration.py
├── javadoctor.bat            # Windows quick-run command
├── javadoctor.ps1            # PowerShell quick-run script
├── pyproject.toml            # Python package setup
└── README.md
```

---

## 💡 Adding Custom Rules

To add a new bug detection and fixing rule:
1. Create a class subclassing `BaseRule` in `javadoctor/rules/`:
```python
from .base import BaseRule, registry
from ..core.models import Bug, Severity, Category

@registry.register
class MyCustomRule(BaseRule):
    rule_id = "MY_CUSTOM_RULE"
    name = "Custom Rule Title"
    severity = Severity.HIGH
    category = Category.CORRECTNESS
    description = "Detects custom pattern..."
    why = "Explanation of danger..."

    def detect(self, code: str, file_path: str = "") -> List[Bug]:
        # Return list of detected Bug objects
        ...

    def fix(self, code: str) -> Tuple[str, int]:
        # Return (fixed_code, num_fixes_applied)
        ...
```
2. The engine, CLI, and Web Dashboard will automatically detect and integrate your rule!
