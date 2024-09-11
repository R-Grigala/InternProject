#!/bin/bash

# Check if the correct number of arguments is provided
if [ "$#" -ne 1 ]; then
  echo "Usage: $0 path_to_accounts_csv"
  exit 1
fi

# Input CSV file path
input_file="$1"

# Check if the input file exists
if [ ! -f "$input_file" ]; then
  echo "Error: File '$input_file' not found!"
  exit 1
fi

# Output file path
output_file="accounts_new.csv"

# Temporary file for processing
temp_file=$(mktemp)

# Function to convert name to email format
convert_to_email() {
  local first_letter="$1"
  local surname="$2"
  local location_id="$3"

  # If location_id is 1, don't include it in the email
  if [ "$location_id" -eq 1 ]; then
    echo "${first_letter}${surname}@abc.com"
  else
    echo "${first_letter}${surname}${location_id}@abc.com"
  fi
}

echo "Starting processing..."

# Initialize email tracking to avoid duplicate emails
declare -A email_count

# Read the input file and process each line
{
  read -r header  # Read and store the header line
  while IFS=, read -r id loc name title email department; do
    # Skip lines where id or name is missing
    if [ -z "$id" ] || [ -z "$name" ]; then
      continue
    fi

    # Remove quotes from title if any
    title=$(echo "$title" | sed 's/"//g')

    # Extract first name and surname
    first_name=$(echo "$name" | awk '{print $1}')
    surname=$(echo "$name" | awk '{print $2}')

    # Format the name: capitalize first letter, rest lowercase
    formatted_name=$(echo "$first_name $surname" | awk '{print toupper(substr($1,1,1)) tolower(substr($1,2)) " " toupper(substr($2,1,1)) tolower(substr($2,2))}')

    # Create the base email format: first letter of first name and full surname, all lowercase
    first_letter=$(echo "$first_name" | cut -c1 | tr '[:upper:]' '[:lower:]')
    surname_lower=$(echo "$surname" | tr '[:upper:]' '[:lower:]')
    base_email=$(convert_to_email "$first_letter" "$surname_lower" "$loc")

    # If the email has been used, increment the count for that email base
    if [ -n "${email_count[$base_email]}" ]; then
      email_count[$base_email]=$((email_count[$base_email] + 1))
      email_with_location=$(convert_to_email "$first_letter" "$surname_lower" "$loc")
    else
      email_with_location=$base_email
      email_count[$base_email]=1
    fi

    # Write the updated line to the temporary file
    echo "$id,$loc,$formatted_name,$title,$email_with_location,$department" >> "$temp_file"
  done
} < "$input_file"

# Add the header to the output file
echo "id,location_id,name,title,email,department" > "$output_file"

# Append the processed lines to the output file
cat "$temp_file" >> "$output_file"

# Clean up
rm "$temp_file"

echo "Processing complete. Updated file: $output_file"
