import json
import csv

def json_to_csv(input_file, output_file):
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        if not data:
            print("No data found in input file.")
            return

        # Get headers from the first item keys
        headers = list(data[0].keys())
        
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            
            for item in data:
                # Process lists (like key_concepts) into strings
                row = {}
                for key, value in item.items():
                    if isinstance(value, list):
                        row[key] = "; ".join(value)
                    else:
                        row[key] = value
                writer.writerow(row)
                
        print(f"Successfully converted {input_file} to {output_file}")
        
    except FileNotFoundError:
        print(f"Error: {input_file} not found.")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    json_to_csv('ai_studio_code.txt', 'ai_studio_data.csv')
