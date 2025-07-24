import sys
from pathlib import Path

import numpy as np
import pandas as pd


def main(output_dir):
    output_dir = Path(sys.argv[1])
    df = load_data(output_dir)

    groups = df.groupby(["school", "class"])

    df["attndnceCubd"] = (df["attendance"] / 100) ** 3
    add_numeric_class_features(df, groups, "attndnceCubd")
    add_numeric_class_features(df, groups, "baseline")
    add_categorical_class_features(df, groups, "Gender", "M")
    add_boolean_class_features(df, groups, "EAL")
    add_boolean_class_features(df, groups, "SEN")
    add_boolean_class_features(df, groups, "PP")

    save_results(df, output_dir)


def load_data(output_dir):
    dataset_df = pd.read_csv(
        output_dir / "dataset.csv", true_values=["T"], false_values=["F"]
    )
    results_df = pd.read_csv(output_dir / "results.csv")

    dataset_df.rename(columns={"patient_id": "student"}, inplace=True)
    results_df.rename(columns={"patient_id": "student"}, inplace=True)

    df = results_df.merge(dataset_df, on="student", how="left")

    df.rename(
        columns={"school_id": "school", "teacher_id": "teacher", "class_id": "class"},
        inplace=True,
    )

    return df


def add_numeric_class_features(df, groups, col):
    """Add class-level mean and centred features for a numeric column."""
    mean_col = f"{col}.classMean"
    centered_col = f"{col}.classCntd"

    df[mean_col] = groups[col].transform("mean")
    df[centered_col] = df[col] - df[mean_col]


def add_categorical_class_features(df, groups, col, val):
    """Add class-level proportion and centred features for a categorical column."""
    prop_col = f"{col}.classProp{val}"
    centered_col = f"{col}{val}.classCntd"

    # Proportion of values matching val per class
    df[prop_col] = groups[col].transform(lambda v: (v == val).mean())

    # Centered:
    #   val → proportion of others
    #   others → - proportion of val
    df[centered_col] = np.where(df[col] == val, 1 - df[prop_col], -df[prop_col])


def add_boolean_class_features(df, groups, col):
    """Add class-level proportion and centred features for boolean column."""
    prop_col = f"{col}.classPropY"
    centered_col = f"{col}Y.classCntd"

    # Proportion of True values per class
    df[prop_col] = groups[col].transform("mean")

    # Centered value:
    #   True → 1 - proportion of True values,
    #   False → -proportion of False values
    df[centered_col] = np.where(df[col], 1 - df[prop_col], -df[prop_col])


def save_results(df, output_dir):
    final_columns = [
        "student",
        "school",
        "class",
        "teacher",
        "date",
        "score",
        "Gender",
        "Gender.classPropM",
        "GenderM.classCntd",
        "EAL",
        "EAL.classPropY",
        "EALY.classCntd",
        "SEN",
        "SEN.classPropY",
        "SENY.classCntd",
        "PP",
        "PP.classPropY",
        "PPY.classCntd",
        "attndnceCubd",
        "attndnceCubd.classMean",
        "attndnceCubd.classCntd",
        "baseline",
        "baseline.classMean",
        "baseline.classCntd",
    ]

    df = df[final_columns].sort_values(["school", "class", "student"])

    output_path = output_dir / "results-plus.csv"
    df.to_csv(output_path, index=False, float_format="%.4f")


if __name__ == "__main__":
    main(Path(sys.argv[1]))
