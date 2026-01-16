#!/usr/bin/env python3
"""
TOPSIS Command Line Program
Usage: python topsis.py <InputDataFile> <Weights> <Impacts> <OutputResultFileName>
"""

import sys
import pandas as pd
import numpy as np
from pathlib import Path

def main():
    # Check correct number of parameters (5 total = program + 4 args)
    if len(sys.argv) != 5:
        print("Error: Expected 4 arguments: <InputDataFile> <Weights> <Impacts> <OutputResultFileName>.")
        sys.exit(1)
    
    input_file, weights_str, impacts_str, output_file = sys.argv[1:]
    
    # File not found
    if not Path(input_file).exists():
        print("Error: Input file not found.")
        sys.exit(1)
    
    # Read CSV or XLSX
    try:
        if input_file.endswith('.csv'):
            df = pd.read_csv(input_file)
        elif input_file.endswith('.xlsx'):
            df = pd.read_excel(input_file)
        else:
            print("Error: Input file must be .csv or .xlsx")
            sys.exit(1)
    except Exception as e:
        print(f"Error: Cannot read input file: {e}")
        sys.exit(1)
    
    # Minimum 3 columns
    if df.shape[1] < 3:
        print("Error: Input file must contain at least 3 columns.")
        sys.exit(1)
    
    # Numeric columns 2+
    try:
        numeric_cols = df.iloc[:, 1:].apply(pd.to_numeric, errors='raise')
        df.iloc[:, 1:] = numeric_cols
    except ValueError:
        print("Error: Non-numeric value found in criteria columns.")
        sys.exit(1)
    
    n_criteria = df.shape[1] - 1
    
    # Parse weights
    try:
        weights = [float(x.strip()) for x in weights_str.split(',')]
    except ValueError:
        print("Error: Weights must be numeric and comma-separated.")
        sys.exit(1)
    
    if len(weights) != n_criteria:
        print(f"Error: Number of weights ({len(weights)}) must match criteria ({n_criteria}).")
        sys.exit(1)
    
    # Normalize weights
    weights = np.array(weights) / weights.sum()
    
    # Parse impacts
    impacts = [imp.strip().upper() for imp in impacts_str.split(',')]
    if len(impacts) != n_criteria or not all(imp in ['+', '-'] for imp in impacts):
        print("Error: Impacts must be '+' or '-' only, comma-separated.")
        sys.exit(1)
    
    # TOPSIS Algorithm
    data = df.iloc[:, 1:].values
    norm = np.sqrt(np.sum(data**2, axis=0))
    r = data / norm
    v = r * weights
    
    # Ideal solutions
    ideal_best = np.array([np.max(v[:, j]) if impacts[j] == '+' else np.min(v[:, j]) for j in range(n_criteria)])
    ideal_worst = np.array([np.min(v[:, j]) if impacts[j] == '+' else np.max(v[:, j]) for j in range(n_criteria)])
    
    # Separation measures
    s_pos = np.sqrt(np.sum((v - ideal_best)**2, axis=1))
    s_neg = np.sqrt(np.sum((v - ideal_worst)**2, axis=1))
    
    # TOPSIS Score & Rank
    score = s_neg / (s_pos + s_neg)
    rank = np.argsort(-score) + 1
    
    # Output (exact format)
    output_df = df.copy()
    output_df['Topsis Score'] = np.round(score, 4)
    output_df['Rank'] = rank.astype(int)
    
    output_df.to_csv(output_file, index=False)
    print(f"Output saved to: {output_file}")

if __name__ == "__main__":
    main()
