import argparse
import sys
from .crawler import crawl_api
from .pretty_print import process_machine_data

def main():
    parser = argparse.ArgumentParser(description="Fetch and display machine status.")
    
    # Display mode group
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument("-p", "--percentage", action="store_true", help="See percentage (default)", default=True)
    mode_group.add_argument("-f", "--full", action="store_true", help="See full space")

    # Display type group
    display_group = parser.add_mutually_exclusive_group()
    display_group.add_argument("-w", "--workstation", action="store_true", help="See basic workstation stats (default)", default=True)
    display_group.add_argument("-m1", "--meow1", action="store_true", help="See meow1 stats")
    display_group.add_argument("-m2", "--meow2", action="store_true", help="See meow2 stats")

    args = parser.parse_args()

    # Crawl the API to get the JSON data
    api_url = "https://monitor.csie.ntu.edu.tw/api/machines"
    try:
        machine_data = crawl_api(api_url)
    except Exception as e:
        print(f"Error fetching data: {e}", file=sys.stderr)
        sys.exit(1)

    # Determine display mode and type
    display_mode = 1 if args.percentage else 2
    if args.meow1:
        display_type = 'meow1'
    elif args.meow2:
        display_type = 'meow2'
    else:
        display_type = 'all_ws'

    # Process and display the data
    try:
        process_machine_data(machine_data, display_mode, display_type)
    except Exception as e:
        print(f"Error processing data: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()