#!/bin/bash

# Check if the output.txt file is passed as an argument
if [ $# -ne 1 ]; then
  echo "Usage: $0 <path to output.txt>"
  exit 1
fi

file_path=$1

# Extract the test name
test_name=$(grep -oP '(?<=\[ ).*(?= ],)' "$file_path")


# Extract individual test results (both "ok" and "not ok")
tests=$(grep -oP '((ok ok)\s+\d+\s+.*?\(\d+ms\))' "$file_path")

# Initialize counters and duration
success_count=0
fail_count=0
total_tests=0
total_duration=$(grep -oP '\d+(?=ms$)' "$file_path" | tail -1)

# Create the beginning of the JSON structure
json=$(cat <<EOF
{
  "testName": "$test_name",
  "tests": [
EOF
)

# Loop through each test result and format it for JSON
while IFS= read -r line; do
  total_tests=$((total_tests + 1))

  # Extract test details
  status=$(echo "$line" | grep -q "ok" && echo true || echo false)
  if [ "$status" == "true" ]; then
    success_count=$((success_count + 1))
  else
    fail_count=$((fail_count + 1))
  fi

  name=$(echo "$line" | grep -oP '(?<=\d\s\s).*?(?=\()')
  duration=$(echo "$line" | grep -oP '\d+ms')

  # Append each test result to the JSON string
  json+=$(cat <<EOF
    {
      "name": "$name",
      "status": $status,
      "duration": "$duration"
    },
EOF
)

done <<< "$tests"

# Remove the last comma from the tests array
json=${json%,}

# Calculate rating
rating=$(echo "scale=2; ($success_count / $total_tests) * 100" | bc)

# Append the summary part to the JSON
json+=$(cat <<EOF
  ],
  "summary": {
    "success": $success_count,
    "failed": $fail_count,
    "rating": $rating,
    "duration": "${total_duration}ms"
  }
}
EOF
)

# Save to output.json
echo "$json" | ./jq . > output.json

echo "Conversion completed! See output.json"
