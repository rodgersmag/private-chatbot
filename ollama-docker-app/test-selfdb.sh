#!/bin/bash
# Test SelfDB - Run the complete SelfDB test suite

echo "🧪 Running SelfDB Test Suite..."
echo ""

# Check if services are running
echo "🔍 Checking if SelfDB services are running..."
if ! curl -f http://localhost:8000/docs >/dev/null 2>&1; then
    echo "❌ SelfDB backend is not running. Please start services first:"
    echo "   ./start-all.sh"
    exit 1
fi

if ! curl -f http://localhost:8001/health >/dev/null 2>&1; then
    echo "❌ SelfDB storage service is not running. Please start services first:"
    echo "   ./start-all.sh"
    exit 1
fi

echo "✅ SelfDB services are running"
echo ""

# Change to the tests directory
cd SelfDB/tests

# Run the test suite
echo "🚀 Starting test execution..."
echo ""

uv run run_all_tests.py

echo ""
echo "📊 Test execution complete!"
echo ""
echo "📄 Check the test results file in SelfDB/tests/ for detailed output"