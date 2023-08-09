import pandas as pd


dataframe = pd.read_csv("output/dataset.csv.gz")
num_rows = len(dataframe)

with open("output/summary.txt", "w") as f:
    f.write(f"There are {num_rows} patients in the population\n")
