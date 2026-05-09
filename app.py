import os
import sys

# Ensure the root directory is in the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.app import demo

if __name__ == "__main__":
    demo.launch()
