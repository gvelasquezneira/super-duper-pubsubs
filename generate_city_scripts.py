import csv
import os

def read_original_code():
    """Read the original publix.py code to use as a template"""
    try:
        with open('publix.py', 'r') as file:
            return file.read()
    except FileNotFoundError:
        print("Error: publix.py not found. Make sure it exists in the current directory.")
        exit(1)

def get_unique_cities():
    """Get all unique cities from the CSV file"""
    try:
        cities = set()
        with open('publix_locations.csv', 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if 'city' in row:
                    cities.add(row['city'])
                else:
                    print("Error: 'city' column not found in CSV.")
                    exit(1)
        return cities
    except FileNotFoundError:
        print("Error: publix_locations.csv not found. Make sure it exists in the current directory.")
        exit(1)

def create_city_csv(city):
    """Create a CSV file for each city"""
    clean_city_name = city.replace(' ', '').replace(',', '')
    try:
        with open('publix_locations.csv', 'r') as input_file:
            reader = csv.DictReader(input_file)
            fieldnames = reader.fieldnames
            
            with open(f'publix_{clean_city_name}.csv', 'w', newline='') as output_file:
                writer = csv.DictWriter(output_file, fieldnames=fieldnames)
                writer.writeheader()
                
                # Reset the reader to the beginning of the file
                input_file.seek(0)
                next(input_file)  # Skip the header row
                
                for row in reader:
                    if row['city'] == city:
                        writer.writerow(row)
        
        print(f"Created CSV file: publix_{clean_city_name}.csv")
    except Exception as e:
        print(f"Error creating CSV for {city}: {str(e)}")

def create_city_script(city, original_code):
    """Create a Python script specific to this city"""
    clean_city_name = city.replace(' ', '').replace(',', '')
    
    # Modify the code to use the city-specific CSV
    modified_code = original_code.replace(
        "with open('publix_locations.csv', 'r') as file:",
        f"with open('publix_{clean_city_name}.csv', 'r') as file:"
    )
    
    # Look for output file patterns and make them city-specific
    if "results_" in modified_code and ".csv" in modified_code:
        modified_code = modified_code.replace(
            "results_",
            f"results_{clean_city_name}_"
        )
    
    # Add a comment at the top to indicate this is a city-specific script
    header_comment = f"""# This is an auto-generated script for {city} Publix locations
# Generated on: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

"""
    modified_code = header_comment + modified_code
    
    # Write the modified code to a new file
    with open(f'publix_{clean_city_name}.py', 'w') as file:
        file.write(modified_code)
    
    print(f"Created script: publix_{clean_city_name}.py")

def main():
    """Main function to generate all city scripts"""
    # Get the original publix.py code
    original_code = read_original_code()
    
    # Get all unique cities from the CSV
    cities = get_unique_cities()
    
    if not cities:
        print("No cities found in the CSV file.")
        return
    
    print(f"Found {len(cities)} unique cities.")
    
    # Create scripts for each city
    for city in cities:
        create_city_csv(city)
        create_city_script(city, original_code)
    
    print(f"\nSuccessfully generated scripts for {len(cities)} cities!")

if __name__ == "__main__":
    main()