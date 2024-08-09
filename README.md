# Machine Status Tool (MST)

Machine Status Tool is a command-line utility to fetch and display machine status information for NTU CSIE work stations.

## Showcase

Here are some GIFs demonstrating the Machine Status Tool in action:

### Basic Workstation Stats
![Basic Workstation Stats](showcase/1.gif)

### Meow1 Stats
![Meow1 Stats](showcase/2.gif)

### Full Space View
![Full Space View](showcase/3.gif)

## Prerequisites

- Python 3.6 or higher
- pip3

## Installation

To install Machine Status Tool locally:

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/machine_status_tool.git
   cd machine_status_tool
   ```

2. Run the installation script:
   ```
   ./install_mst.sh
   ```

3. Follow the prompts to complete the installation.

After installation, you can use the `mst` command from anywhere in your terminal.

## Usage

Once installed, you can use Machine Status Tool with the following options:

```
mst [OPTIONS]
```

Options:
- `-p`, `--percentage`: See percentage view (default)
- `-f`, `--full`: See full space view
- `-w`, `--workstation`: See basic workstation stats (default)
- `-m1`, `--meow1`: See meow1 stats
- `-m2`, `--meow2`: See meow2 stats

Examples:
```
mst                 # Display percentage view of workstation stats
mst -f              # Display full space view of workstation stats
mst -m1             # Display percentage view of meow1 stats
mst -f -m2          # Display full space view of meow2 stats
```

## Uninstallation

To uninstall Machine Status Tool:

1. Navigate to the directory where you cloned the Machine Status Tool repository:
   ```
   cd path/to/machine_status_tool
   ```

2. Run the uninstallation script:
   ```
   ./uninstall_mst.sh
   ```

3. Follow the prompts to confirm and complete the uninstallation.

This will remove the `mst` command from your system and delete the associated virtual environment.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.