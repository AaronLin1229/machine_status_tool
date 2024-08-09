import json
import argparse
import re
from tabulate import tabulate
from colorama import Fore, Style, init

# Constants
SIZE_UNITS = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
WS_MACHINES = ['ws1', 'ws2', 'ws3', 'ws4', 'ws5', 'ws6', 'ws7', 'meow1', 'meow2']
GPU_MACHINES = ['meow1', 'meow2']

# Utility functions
def parse_bytes(size_bytes):
    if size_bytes == 0:
        return 0, 'B'
    i = 0
    while size_bytes >= 1024 and i < len(SIZE_UNITS) - 1:
        size_bytes /= 1024
        i += 1
    return size_bytes, SIZE_UNITS[i]

def convert_bytes(size_bytes, target_unit):
    units = {unit: 1024**i for i, unit in enumerate(SIZE_UNITS)}
    if target_unit not in units:
        raise ValueError(f"Unsupported unit. Choose from {', '.join(SIZE_UNITS)}")
    return size_bytes / units[target_unit]

def get_color(percentage):
    if percentage > 30:
        return Fore.GREEN
    elif percentage > 10:
        return Fore.YELLOW
    else:
        return Fore.RED

def string_color(s, color):
    return f"{color}{s}{Style.RESET_ALL}"

def replace_kth_segment(s, k, replacement):
    pattern = r'\|(.*?)(?=\|)'
    matches = list(re.finditer(pattern, s))
    if k < 0 or k >= len(matches):
        raise ValueError(f"Invalid k. Must be between 0 and {len(matches) - 1}")
    start, end = matches[k].span()
    return s[:start] + f'|{replacement}|' + s[end+1:]

# Data processing functions
def load_machine_data(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    if data['result'] != 'ok':
        raise ValueError("Error: Unable to retrieve machine status")
    return data['message']

def get_machine_stats(data, machine_type='ws', specific_machine=None):
    if specific_machine:
        machine_lst = [specific_machine]
    elif machine_type == 'ws':
        machine_lst = WS_MACHINES
    else:
        machine_lst = GPU_MACHINES
    
    stats_lst = []
    for machine_name in machine_lst:
        machine_info = data[machine_name]
        stats = {
            'Machine': machine_name,
            'CPU Avail.': machine_info['cpu']['arr'][9] * 100,
            'Memory Avail.': [sum(machine_info['mem']['arr'][-2:]), sum(machine_info['mem']['arr'])],
            'Swap Free': [machine_info['swp']['arr'][1], sum(machine_info['swp']['arr'])],
            '/tmp2 Avail.': [machine_info['tmp2']['arr'][2], sum(machine_info['tmp2']['arr'])],
            'Uptime': machine_info['uptime']
        }
        
        if machine_type == 'gpu' or specific_machine:
            stats.update({
                'GPU Name': [f'GPU {i}' for i in range(len(machine_info['gpu']))],
                'GPU Util.': machine_info['gpu'],
                'GPU Memory Avail.': [(tot - in_use, in_use) for in_use, tot in zip(machine_info['gpumem'], machine_info['gpumem_tot'])]
            })
        
        stats_lst.append(stats)
    
    return stats_lst

# Formatting functions
def format_resource(available, total, display_mode):
    available = min(available, total)
    percentage = (available / total) * 100
    avail_val, avail_unit = parse_bytes(available)
    total_val, total_unit = parse_bytes(total)
    
    if SIZE_UNITS.index(total_unit) > SIZE_UNITS.index(avail_unit):
        avail_val = convert_bytes(available, total_unit)
        avail_unit = total_unit
    elif SIZE_UNITS.index(avail_unit) > SIZE_UNITS.index(total_unit):
        total_val = convert_bytes(total, avail_unit)
        total_unit = avail_unit

    if display_mode == 1:
        return f"{avail_val:.2f}{avail_unit}  {percentage:.2f}%"
    else:
        return f"{avail_val:.2f}{avail_unit}  /{total_val:.2f}{avail_unit}"

# Table creation functions
def create_ws_table_1(stats_lst):
    table_header = ['Machine', 'CPU Avail.', 'Memory Avail.', 'Swap Free', '/tmp2 Avail.', 'Uptime']
    table_data = [
        [
            st['Machine'],
            f"{st['CPU Avail.']:.2f}%",
            format_resource(*st['Memory Avail.'], 1),
            format_resource(*st['Swap Free'], 1),
            format_resource(*st['/tmp2 Avail.'], 1),
            st['Uptime']
        ] for st in stats_lst
    ]
    return tabulate(table_data, headers=table_header, tablefmt='grid')

def create_gpu_table_1(data):
    headers = ["GPU Name", "GPU Util.", "GPU Memory Avail."]
    table_data = [
        [
            gpu_name,
            f"{gpu_util * 100:.2f}%",
            format_resource(*gpu_memory, 1)
        ] for gpu_name, gpu_util, gpu_memory in zip(data['GPU Name'], data['GPU Util.'], data['GPU Memory Avail.'])
    ]
    return tabulate(table_data, headers=headers, tablefmt="grid")

def create_ws_table_2(stats_lst):
    table_header = ['Machine', 'CPU Avail.', 'Memory Avail.', 'Swap Free', '/tmp2 Avail.', 'Uptime']
    table_data = [
        [
            st['Machine'],
            f"{st['CPU Avail.']:.2f}%",
            format_resource(*st['Memory Avail.'], 2),
            format_resource(*st['Swap Free'], 2),
            format_resource(*st['/tmp2 Avail.'], 2),
            st['Uptime']
        ] for st in stats_lst
    ]
    return tabulate(table_data, headers=table_header, tablefmt='grid')

def create_gpu_table_2(data):
    headers = ["GPU Name", "GPU Util.", "GPU Memory Avail."]
    table_data = [
        [
            gpu_name,
            f"{gpu_util * 100:.2f}%",
            format_resource(*gpu_memory, 2)
        ] for gpu_name, gpu_util, gpu_memory in zip(data['GPU Name'], data['GPU Util.'], data['GPU Memory Avail.'])
    ]
    return tabulate(table_data, headers=headers, tablefmt="grid")

# Table modification functions
def parse_cpu_avail(info):
    return [
        "".join([
            ' ' * (len(lst[0]) + len(lst[2]) - 1),
            string_color(lst[1], get_color(float(lst[1][:-1]))),
            ' ' * 1
        ]) for lst in [re.findall(r'\s+|\S+', line) for line in info]
    ]

def parse_gpu_avail(info):
    return [
        "".join([
            ' ' * (len(lst[0]) + len(lst[2]) - 1),
            string_color(lst[1], get_color(100 - float(lst[1][:-1]))),
            ' ' * 1
        ]) for lst in [re.findall(r'\s+|\S+', line) for line in info]
    ]

def parse_lst(info):
    parsed = [re.findall(r'\s+|\S+', s) for s in info]
    sep_0, s_1, sep_1, s_2, sep_2 = zip(*[(p[0], p[1], p[2], p[3], p[4]) for p in parsed])
    
    max_s_1 = max(map(len, s_1))
    sep_0 = [' ' * (len(s) + max_s_1 - len(s_1[i])) for i, s in enumerate(sep_0)]
    sep_1 = [' ' * (len(s) - (max_s_1 - len(s_1[i])) + len(sep_2[i]) - 1) for i, s in enumerate(sep_1)]
    sep_2 = [' ' for _ in sep_2]
    
    s_2 = [string_color(s, get_color(float(s[:-1]))) for s in s_2]
    
    return [''.join(parts) for parts in zip(sep_0, s_1, sep_1, s_2, sep_2)]

def parse_resource_usage(info):
    parsed = [re.findall(r'\s+|\S+', s) for s in info]
    sep_0, s_1, sep_1, s_2, sep_2 = zip(*[(p[0], p[1], p[2], p[3], p[4]) for p in parsed if len(p) >= 5])
    
    max_s_1 = max(map(len, s_1))
    sep_0 = [' ' * (len(s) + max_s_1 - len(s_1[i])) for i, s in enumerate(sep_0)]
    sep_1 = [' ' * (len(s) - (max_s_1 - len(s_1[i])) + len(sep_2[i]) - 1) for i, s in enumerate(sep_1)]
    sep_2 = [' ' for _ in sep_2]
    
    available = []
    total = []
    for s in s_2:
        parts = s.split('/')
        if len(parts) == 2:
            try:
                avail = float(parts[0].strip())
                tot = float(parts[1].strip()[:-2])  # Remove unit (e.g., 'GB')
                available.append(avail)
                total.append(tot)
            except ValueError:
                available.append(0)
                total.append(1)  # Avoid division by zero
        else:
            available.append(0)
            total.append(1)  # Avoid division by zero
    
    percentages = [(1 - a / t) * 100 if t != 0 else 0 for a, t in zip(available, total)]
    
    s_1 = [string_color(s, get_color(p)) for s, p in zip(s_1, percentages)]
    
    return [''.join(parts) for parts in zip(sep_0, s_1, sep_1, s_2, sep_2)]

def modify_ws_table_1(table):
    table_lst = table.split('\n')
    info_lst = [list(filter(None, col)) for col in zip(*[line.split('|')[1:-1] for line in table_lst[3::2]])]
    
    info_lst[1] = parse_cpu_avail(info_lst[1])
    for i in range(2, 5):
        info_lst[i] = parse_lst(info_lst[i])
    
    for idx in range(3, len(table_lst), 2):
        for j in range(len(info_lst)):
            table_lst[idx] = replace_kth_segment(table_lst[idx], j, info_lst[j][(idx-3)//2])
    
    return "\n".join(table_lst)

def modify_gpu_table_1(table):
    table_lst = table.split('\n')
    info_lst = [list(filter(None, col)) for col in zip(*[line.split('|')[1:-1] for line in table_lst[3::2]])]
    
    info_lst[1] = parse_gpu_avail(info_lst[1])
    info_lst[2] = parse_lst(info_lst[2])
    
    for idx in range(3, len(table_lst), 2):
        for j in range(len(info_lst)):
            table_lst[idx] = replace_kth_segment(table_lst[idx], j, info_lst[j][(idx-3)//2])
    
    return "\n".join(table_lst)

def modify_ws_table_2(table):
    table_lst = table.split('\n')
    info_lst = [list(filter(None, col)) for col in zip(*[line.split('|')[1:-1] for line in table_lst[3::2]])]
    
    info_lst[1] = parse_cpu_avail(info_lst[1])
    for i in range(2, 5):
        info_lst[i] = parse_resource_usage(info_lst[i])
    
    for idx in range(3, len(table_lst), 2):
        for j in range(len(info_lst)):
            table_lst[idx] = replace_kth_segment(table_lst[idx], j, info_lst[j][(idx-3)//2])
    
    return "\n".join(table_lst)

def modify_gpu_table_2(table):
    table_lst = table.split('\n')
    info_lst = [list(filter(None, col)) for col in zip(*[line.split('|')[1:-1] for line in table_lst[3::2]])]
    
    info_lst[1] = parse_gpu_avail(info_lst[1])
    info_lst[2] = parse_resource_usage(info_lst[2])
    
    for idx in range(3, len(table_lst), 2):
        for j in range(len(info_lst)):
            table_lst[idx] = replace_kth_segment(table_lst[idx], j, info_lst[j][(idx-3)//2])
    
    return "\n".join(table_lst)

def process_machine_data(data, display_mode, display_type):
    """
    Process the machine data and display the results.
    
    :param data: JSON object containing machine status data
    :param display_mode: 1 for 'Available and Percentage', 2 for 'Available / Total'
    :param display_type: 'all_ws' for all workstations, 'meow1' for meow1 stats, 'meow2' for meow2 stats
    """
    if data['result'] != 'ok':
        raise ValueError("Error: Unable to retrieve machine status")
    
    machine_data = data['message']
    
    if display_type == 'all_ws':
        ws_stats = get_machine_stats(machine_data, 'ws')
        if display_mode == 1:
            ws_table = create_ws_table_1(ws_stats)
            ws_table = modify_ws_table_1(ws_table)
        else:
            ws_table = create_ws_table_2(ws_stats)
            ws_table = modify_ws_table_2(ws_table)
        print(ws_table)
    
    elif display_type in ['meow1', 'meow2']:
        machine_stats = get_machine_stats(machine_data, 'gpu', display_type)
        if display_mode == 1:
            ws_table = create_ws_table_1(machine_stats)
            ws_table = modify_ws_table_1(ws_table)
            print(ws_table)

            gpu_table = create_gpu_table_1(machine_stats[0])
            gpu_table = modify_gpu_table_1(gpu_table)
        else:
            ws_table = create_ws_table_2(machine_stats)
            ws_table = modify_ws_table_2(ws_table)
            print(ws_table)

            gpu_table = create_gpu_table_2(machine_stats[0])
            gpu_table = modify_gpu_table_2(gpu_table)
        print(gpu_table)

def main():
    parser = argparse.ArgumentParser(description="Display machine status with customizable output.")
    parser.add_argument("--mode", type=int, choices=[1, 2], default=1,
                        help="Display mode: 1 for 'Available and Percentage', 2 for 'Available / Total'")
    parser.add_argument("--display", type=str, choices=['all_ws', 'meow1', 'meow2'], required=True,
                        help="'all_ws': Basic stats of ws1-ws7, meow1, meow2; 'meow1': Stats of meow1; 'meow2': Stats of meow2")
    parser.add_argument("--file", type=str, required=True,
                        help="Path to the JSON file containing machine status data")
    args = parser.parse_args()

    with open(args.file, 'r') as f:
        machine_data = json.load(f)
    
    process_machine_data(machine_data, args.mode, args.display)

if __name__ == "__main__":
    main()