import os
import re

def extract_last_values(log_file_path):
    with open(log_file_path, 'r') as file:
        content = file.read()

    # Find all matches for "Injected flit rate average"
    injected_flit_rate_matches = list(re.finditer(r'Injected flit rate average\s*=\s*([\d.]+)', content))
    
    # Find all matches for "Accepted flit rate average"
    accepted_flit_rate_matches = list(re.finditer(r'Accepted flit rate average\s*=\s*([\d.]+)', content))

    # Extract the last match for "Injected flit rate average" if there are any matches
    injected_flit_rate = float(injected_flit_rate_matches[-1].group(1)) if len(injected_flit_rate_matches) else None

    # Extract the last match for "Accepted flit rate average" if there are any matches
    accepted_flit_rate = float(accepted_flit_rate_matches[-1].group(1)) if len(accepted_flit_rate_matches) else None

    return injected_flit_rate, accepted_flit_rate

def create_pass_fail_file(log_file_path, pass_fail):
    pass_fail_file_path = log_file_path.replace(".log", "." + pass_fail)
    with open(pass_fail_file_path, 'w') as pass_fail_file:
        pass_fail_file.write(pass_fail)

def main():
    log_dir = "./logs"  # Change this to the directory where your log files are stored

    # Collect log files
    log_files = [f for f in os.listdir(log_dir) if f.endswith(".log")]

    # Process each log file
    for log_file in log_files:
        log_file_path = os.path.join(log_dir, log_file)

        # Extract values from the log file
        injected_flit_rate, accepted_flit_rate = extract_last_values(log_file_path)

        # Determine pass/fail and create pass/fail file
        if injected_flit_rate is not None and accepted_flit_rate is not None:
            pass_fail = "PASS"
        else:
            pass_fail = "FAIL"
        create_pass_fail_file(log_file_path, pass_fail)

        # Print results or failure information
        print(f"Results for {log_file}:")
        if injected_flit_rate is not None and accepted_flit_rate is not None:
            print(f"Injected flit rate average: {injected_flit_rate}")
            print(f"Accepted flit rate average: {accepted_flit_rate}")
        else:
            print("Failed to extract values or no matches found.")
        print(f"Pass/Fail: {pass_fail}")
        print("----------------------------")

if __name__ == "__main__":
    main()
