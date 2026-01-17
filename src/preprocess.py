
import pandas as pd

def inspect_data(file_path):
    print("📂 Loading dataset...\n")
    df = pd.read_csv(file_path)

    print("🔹 First 5 rows of the dataset:")
    print(df.head())

    print("\n🔹 Dataset structure & data types:")
    print(df.info())

    print("\n🔹 Statistical summary (numerical columns):")
    print(df.describe())

    print("\n🔹 Missing values per column:")
    print(df.isnull().sum())

    print("\n🔹 Column names:")
    print(df.columns.tolist())

    return df


if __name__ == "__main__":
    inspect_data("../data/raw/financial_data.csv")
