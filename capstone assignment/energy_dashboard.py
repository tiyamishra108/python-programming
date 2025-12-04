import os
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt


def load_and_validate_data():
    """
    Loads ONLY building CSV files.
    Ignores any output files such as:
    - cleaned_energy_data.csv
    - building_summary.csv
    """

    script_dir = Path(__file__).parent


    csv_files = [f for f in script_dir.glob("*.csv")
                 if f.stem.lower().startswith("building")]

    if not csv_files:
        print("No building*.csv files found next to this script.")
        return pd.DataFrame()

    combined_df = []

    for file in csv_files:
        try:
            df = pd.read_csv(file, on_bad_lines='skip')

            
            df['building'] = file.stem

            
            if 'timestamp' not in df.columns or 'kwh' not in df.columns:
                continue

            
            df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
            df.dropna(subset=['timestamp', 'kwh'], inplace=True)

            combined_df.append(df)

        except Exception as e:
            print(f"Could not load {file.name}: {e}")

    if not combined_df:
        return pd.DataFrame()

    df_combined = pd.concat(combined_df, ignore_index=True)
    df_combined.sort_values("timestamp", inplace=True)
    return df_combined


def calculate_daily_totals(df):
    df = df.set_index("timestamp")
    return df.resample("D")['kwh'].sum()

def calculate_weekly_aggregates(df):
    df = df.set_index("timestamp")
    return df.resample("W")['kwh'].sum()

def building_wise_summary(df):
    return df.groupby("building")['kwh'].agg(['mean', 'min', 'max', 'sum'])


class MeterReading:
    def __init__(self, timestamp, kwh):
        self.timestamp = timestamp
        self.kwh = kwh

class Building:
    def __init__(self, name):
        self.name = name
        self.meter_readings = []

    def add_reading(self, timestamp, kwh):
        self.meter_readings.append(MeterReading(timestamp, kwh))

    def calculate_total_consumption(self):
        return sum(r.kwh for r in self.meter_readings)

    def generate_report(self):
        return f"{self.name}: Total = {self.calculate_total_consumption():.2f} kWh"

class BuildingManager:
    def __init__(self):
        self.buildings = {}

    def ingest_dataframe(self, df):
        for _, row in df.iterrows():
            name = row['building']
            ts = row['timestamp']
            kwh = row['kwh']

            if name not in self.buildings:
                self.buildings[name] = Building(name)

            self.buildings[name].add_reading(ts, kwh)

    def generate_all_reports(self):
        return [b.generate_report() for b in self.buildings.values()]


def create_dashboard(df, daily, weekly, summary):
    fig, ax = plt.subplots(3, 1, figsize=(12, 16))

    
    ax[0].plot(daily.index, daily.values)
    ax[0].set_title("Daily Consumption Trend")
    ax[0].set_xlabel("Date")
    ax[0].set_ylabel("kWh")

    df['week'] = df['timestamp'].dt.isocalendar().week
    weekly_avg = df.groupby("building")['kwh'].mean()

    ax[1].bar(weekly_avg.index, weekly_avg.values)
    ax[1].set_title("Avg Weekly Usage per Building")
    ax[1].set_ylabel("kWh")

    df['hour'] = df['timestamp'].dt.hour
    ax[2].scatter(df['hour'], df['kwh'])
    ax[2].set_title("Hourly Peak Consumption")
    ax[2].set_xlabel("Hour")
    ax[2].set_ylabel("kWh")

    plt.tight_layout()
    plt.savefig("dashboard.png")
    print("✔ dashboard.png saved")


def generate_summary_report(df, summary):
    total = df['kwh'].sum()
    highest = summary['sum'].idxmax()
    peak_time = df.loc[df['kwh'].idxmax(), 'timestamp']

    text = (
        "=== ENERGY SUMMARY REPORT ===\n"
        f"Total Consumption: {total:.2f} kWh\n"
        f"Highest Consuming Building: {highest}\n"
        f"Peak Load Time: {peak_time}\n"
    )

    with open("summary.txt", "w") as f:
        f.write(text)

    print("summary.txt saved")
    print(text)


def main():
    print("Loading CSV files from this folder...")

    df = load_and_validate_data()

    if df.empty:
        print("No valid CSVs found. Exiting.")
        return

    daily = calculate_daily_totals(df)
    weekly = calculate_weekly_aggregates(df)
    summary = building_wise_summary(df)

    manager = BuildingManager()
    manager.ingest_dataframe(df)

    create_dashboard(df, daily, weekly, summary)

    df.to_csv("cleaned_energy_data.csv", index=False)
    summary.to_csv("building_summary.csv")

    print("cleaned_energy_data.csv saved")
    print("building_summary.csv saved")

    generate_summary_report(df, summary)

    print("\nAll tasks completed successfully.")


if __name__ == "__main__":
    main()
