
import csv
import os

def convert_csv_to_md(input_file, output_dir):
    try:
        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        with open(input_file, mode='r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            for index, row in enumerate(reader, start=1):
                output_file = os.path.join(output_dir, f'demand_forecast_{index}.md')
                with open(output_file, mode='w', encoding='utf-8') as mdfile:
                    for header, value in row.items():
                        mdfile.write(f"{header}: {value}\n")
        
        print(f"Successfully converted {input_file} to multiple files in {output_dir}")
    except FileNotFoundError:
        print(f"Error: The file {input_file} was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    input_csv = 'unique_item_demand_forecast.csv'
    output_directory = 'unique_item'
    convert_csv_to_md(input_csv, output_directory)
