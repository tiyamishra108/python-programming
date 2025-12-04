import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

if not os.path.exists("plots"):
    os.mkdir("plots")

file_name = "weather_data.csv" 

df = pd.read_csv(file_name)

print("\n------ RAW DATA LOADED ------\n")
print(df.head(), "\n")
print(df.info(), "\n")

df["date"] = pd.to_datetime(df["date"], errors="coerce")         
df.fillna(method="bfill", inplace=True)                          

df.to_csv("cleaned_weather.csv", index=False)


temp = np.array(df["temperature_C"])

stats = {
    "Mean Temperature": temp.mean(),
    "Max Temperature": temp.max(),
    "Min Temperature": temp.min(),
    "Std Deviation": temp.std(),
    "Total Rainfall": df["rainfall_mm"].sum(),
    "Mean Humidity": df["humidity_percent"].mean()
}

print("\n------ NUMPY STATISTICS ------\n")
for k, v in stats.items():
    print(f"{k} : {v}")

df["month"] = df["date"].dt.month

monthly = df.groupby("month").agg({
    "temperature_C": ["mean", "min", "max"],
    "rainfall_mm": "sum",
    "humidity_percent": "mean"
})


monthly.to_csv("monthly_summary.csv")


plt.figure(figsize=(10,4))
plt.plot(df["date"], df["temperature_C"], color="red")
plt.title("Daily Temperature Trend")
plt.xlabel("Date")
plt.ylabel("Temperature (°C)")
plt.savefig("plots/temp_trend.png")
plt.close()


plt.figure(figsize=(8,4))
df.groupby("month")["rainfall_mm"].sum().plot(kind="bar", color="blue")
plt.title("Monthly Rainfall")
plt.xlabel("Month")
plt.ylabel("Rainfall (mm)")
plt.savefig("plots/rainfall_bar.png")
plt.close()


plt.figure(figsize=(6,4))
plt.scatter(df["humidity_percent"], df["temperature_C"], color="purple")
plt.title("Humidity vs Temperature")
plt.xlabel("Humidity (%)")
plt.ylabel("Temperature (°C)")
plt.savefig("plots/humidity_scatter.png")
plt.close()


plt.figure(figsize=(10,5))
plt.plot(df["date"], df["temperature_C"], label="Temperature", color="green")
plt.bar(df["date"], df["rainfall_mm"], alpha=0.4, label="Rainfall", color="orange")
plt.title("Temperature & Rainfall Combined Plot")
plt.legend()
plt.savefig("plots/combined_plot.png")
plt.close()


with open("report_summary.txt", "w") as f:
    f.write("======== WEATHER DATA ANALYSIS REPORT ========\n\n")
    for k, v in stats.items():
        f.write(f"{k} : {v}\n")
    f.write("\n------ Monthly Summary ------\n")
    f.write(str(monthly))

print("\n✔ All tasks completed successfully!")
print("👉 Outputs generated:\n"
      "- cleaned_weather.csv\n"
      "- monthly_summary.csv\n"
      "- report_summary.txt\n"
      "- plots folder containing 4 graphs\n")
