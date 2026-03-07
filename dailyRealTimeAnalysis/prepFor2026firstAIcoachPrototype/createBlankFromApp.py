import os

def filter_lines(input_file, output_file, search_text):
    """
    Reads a CSV file and writes lines containing the search_text to a new file.
    Preserves the header line.
    """
    try:
        with open(input_file, 'r', encoding='utf-8') as f_in, \
             open(output_file, 'w', encoding='utf-8') as f_out:
            
            # Read the first line (header)
            header = f_in.readline()
            
            # Write the header to the output file
            # (Comment this out if you strictly want ONLY lines with the search text)
            f_out.write(header)
            
            # Iterate through the rest of the file
            count = 0
            for line in f_in:
                if search_text in line:
                    f_out.write(line)
                    count += 1
                    
        print(f"Success! Found {count} lines containing '{search_text}'.")
        print(f"Filtered data saved to: {output_file}")

    except FileNotFoundError:
        print(f"Error: The file '{input_file}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

# --- Configuration ---
input_filename = 'manicTimeApp.csv'       # Replace with your actual file name
output_filename = 'manicTimeBlank.csv'  # The name of the new file to be created
search_term = "Blank Screen Saver"

# --- Execution ---
if __name__ == "__main__":
    filter_lines(input_filename, output_filename, search_term)