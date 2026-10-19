# Work1 - Flask Jinja2 SSTI Vulnerability Reproduction and Security Detection Experiment

## Experiment Introduction

This experiment completes the reproduction of Server-Side Template Injection (SSTI) vulnerability in Flask+Jinja2, Static Application Security Testing (SAST) for source code, Software Composition Analysis (SCA), vulnerability fixing and verification. Bandit is used for Python static security scanning, and pip-audit is adopted to scan vulnerabilities in third-party components.

Vulnerability ID: CVE-2019-8341
Vulnerability Name: Jinja2 Server-Side Template Injection (SSTI)

> 
> Note: CVE-2019-8341 is disputed. The Jinja2 official team regards this issue as improper API usage by developers. Passing untrusted user input into `render_template_string()` directly is **not a native vulnerability of the Jinja2 framework**. The vulhub `flask/ssti` target is a teaching environment for this vulnerability scenario.
> CWE ID: CWE-1336, Improper Neutralization of Special Elements Used in a Template Engine

## Environment Information

- Python 3.x
- Flask
- Jinja2 2.10 (version affected by this CVE)
- Bandit: Static security detection tool for Python source code (SAST)
- pip-audit: Vulnerability scanner for Python dependency packages (SCA)

## 1. Vulnerability Principle

The Jinja2 template engine supports the syntax `{{expression}}` to execute server-side expressions.
When the code directly concatenates **user-controllable input into template strings** and passes them to `render_template_string()` for rendering, attackers can construct template expressions to execute template code on the server side. Remote code execution may be achieved under appropriate conditions.

### Vulnerable Code app.py (Vulnerable Version)

```
from flask import Flask, render_template_string, request
app = Flask(__name__)

@app.route('/')
def index():
    user_input = request.args.get('name','guest')
    tpl = f"Hello {user_input}"
    return render_template_string(tpl)

if __name__ == "__main__":
    app.run(host="0.0.0.0",port=5000,debug=True)
```

> 
> Risk point: The f-string directly splices user input into template source code and hands it over to Jinja2 for rendering.

## 2. Vulnerability Reproduction Steps

1. Install dependencies: `pip install flask jinja2==2.10`
2. Run vulnerable code: `python app.py`
3. Visit the payload URL:
`http://127.0.0.1:5000/?name={{1%2B2}}`
4. Result: The page outputs `Hello 3`, indicating that `1+2` is executed by the template engine on the server side, and the SSTI vulnerability exists.

## 3. Static Security Detection (SAST Bandit)

### Execution Command

```
bandit -r app.py
```

### Detection Description

Bandit scans Python source code and identifies dangerous coding patterns. In this case, Bandit can detect the high-risk coding risk that user-controllable input is directly passed into template rendering.

## 4. Software Composition Analysis (SCA pip-audit)

### Execution Command

```
pip-audit
```

### Detection Description

pip-audit scans all Python third-party dependency packages of the project to identify known CVE vulnerabilities in components. Jinja2 2.10 in this environment will detect CVE-2019-8341.

## 5. Vulnerability Fix

Fix idea: **Do not splice user input into template source code; pass user input as template variables.**

### Fixed Code app_fixed.py

```
from flask import Flask, render_template_string, request
app = Flask(__name__)

@app.route('/')
def index():
    user_input = request.args.get('name','guest')
    return render_template_string("Hello {{name}}", name=user_input)

if __name__ == "__main__":
    app.run(host="0.0.0.0",port=5000,debug=True)
```

## 6. Fix Verification

Restart the service and visit the same payload:
`http://127.0.0.1:5000/?name={{1%2B2}}`
The page outputs `Hello {{1+2}}` as raw text. The template engine no longer parses the template syntax passed by users, and the vulnerability is fixed successfully.

## 7. GitHub Actions CI Pipeline

Configure GitHub Actions workflow. Every code commit will automatically execute:

1. Bandit SAST source code scan
2. pip-audit SCA dependency scan
Screenshots of successful pipeline can be put into the report. The pipeline automatically detects code security risks.

## Submission Checklist

1. Link to public GitHub repository
2. README.md document
3. Link to GitHub Actions pipeline page
4. Source files: app.py (vulnerable version), app_fixed.py (fixed version)
