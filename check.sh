#!/bin/bash
echo "🔍 Checking PhishLab Pro Installation..."
echo ""

checks_passed=0
checks_total=0

# Check Python
((checks_total++))
if command -v python3 &> /dev/null; then
    echo "✅ Python3 installed: $(python3 --version)"
    ((checks_passed++))
else
    echo "❌ Python3 not found"
fi

# Check files
((checks_total++))
if [ -f "requirements.txt" ]; then
    echo "✅ requirements.txt exists"
    ((checks_passed++))
else
    echo "❌ requirements.txt missing"
fi

((checks_total++))
if [ -f "config.py" ]; then
    echo "✅ config.py exists"
    ((checks_passed++))
else
    echo "❌ config.py missing"
fi

((checks_total++))
if [ -f "app/__init__.py" ]; then
    echo "✅ app/__init__.py exists"
    ((checks_passed++))
else
    echo "❌ app/__init__.py missing"
fi

((checks_total++))
if [ -f "app/models.py" ]; then
    echo "✅ app/models.py exists"
    ((checks_passed++))
else
    echo "❌ app/models.py missing"
fi

((checks_total++))
if [ -f "app/templates/auth/login.html" ]; then
    echo "✅ Login template exists"
    ((checks_passed++))
else
    echo "❌ Login template missing"
fi

((checks_total++))
if [ -f "app/static/css/dark-theme.css" ]; then
    echo "✅ Dark theme CSS exists"
    ((checks_passed++))
else
    echo "❌ Dark theme CSS missing"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Results: $checks_passed/$checks_total checks passed"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ $checks_passed -eq $checks_total ]; then
    echo "✅ All checks passed! Ready to run setup.sh"
else
    echo "⚠️  Some files missing. Re-run installation."
fi
