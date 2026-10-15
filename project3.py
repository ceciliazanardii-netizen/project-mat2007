
# mat2007 final project
# cost of a healthy diet from 2017 to 2024

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import skew, kurtosis

# dataset and years used in the analysis
FILE_NAME = "cost-healthy-diet.csv"
START_YEAR = 2017
END_YEAR = 2024
COST_COLUMN = "Cost of a healthy diet"

# columns needed for the analysis
REQUIRED_COLUMNS = ["Entity", "Code", "Year", COST_COLUMN]


# LOAD THE DATA
def load_data(filename):

    # check if the file exists
    if not os.path.exists(filename):
        print("Error: Could not find", filename)
        return None

    # try to read the csv file
    try:
        data = pd.read_csv(filename)
    except pd.errors.EmptyDataError:
        print("Error: The dataset is empty.")
        return None
    except pd.errors.ParserError:
        print("Error: The CSV file could not be read correctly.")
        return None
    except Exception as error:
        print("Unexpected error while reading the file:", error)
        return None

    return data


# CHECK THE DATA
def validate_data(data):

    # check that the dataset is not empty
    if data is None or data.empty:
        print("Error: No data are available for analysis.")
        return False

    # check that all the required columns exist
    for column in REQUIRED_COLUMNS:
        if column not in data.columns:
            print("Error: Missing required column:", column)
            return False

    # check that all years from 2017 to 2024 are included
    for year in range(START_YEAR, END_YEAR + 1):
        if year not in data["Year"].values:
            print("Error: Missing data for year", year)
            return False

    # check for zero or negative costs
    invalid_costs = (data[COST_COLUMN] <= 0).sum()
    if invalid_costs > 0:
        print("Error:", invalid_costs, "non-positive cost values were found.")
        return False

    # check if any country appears more than once in the same year
    duplicate_rows = data[data["Code"].notna()].duplicated(subset=["Entity", "Year"]).sum()
    if duplicate_rows > 0:
        print("Error:", duplicate_rows, "duplicate country-year observations were found.")
        return False

    return True


# CLEAN THE DATA
def clean_data(data):

    # print some information about the original dataset
    print("\n--- DATA CHECK ---")
    print("Original rows:", len(data))
    print("Original entities:", data["Entity"].nunique())
    print("\nMissing values:")
    print(data.isnull().sum())

    # remove rows without a country code
    countries = data[data["Code"].notna()].copy()

    # count how many years are available for each country
    year_counts = countries.groupby("Entity")["Year"].nunique()

    # calculate how many years each country should have
    required_number_of_years = END_YEAR - START_YEAR + 1

    # select countries that have data for all 8 years
    complete_countries = year_counts[year_counts == required_number_of_years].index

    # create a dataset with only those countries
    panel = countries[countries["Entity"].isin(complete_countries)].copy()

    # stop if no countries are left after cleaning
    if panel.empty:
        print("Error: No countries have complete data for the study period.")
        return None

    # print the size of the final dataset
    print("\nCountries with complete 2017-2024 data:", panel["Entity"].nunique())
    print("Rows in final dataset:", len(panel))

    return panel


# CALCULATE YEARLY STATISTICS
def calculate_yearly_statistics(panel):

    # calculate the number of countries, mean, median and standard deviation for each year
    yearly = panel.groupby("Year")[COST_COLUMN].agg(
        ["count", "mean", "median", "std"]
    ).reset_index()

    # calculate the standard error of the mean
    # standard error = standard deviation / square root of sample size
    yearly["sem"] = yearly["std"] / np.sqrt(yearly["count"])

    return yearly


# CALCULATE COUNTRY CHANGES
def calculate_country_changes(panel):

    # put the years into separate columns for each country
    wide = panel.pivot(index="Entity", columns="Year", values=COST_COLUMN)

    # check that the first and last years are available
    if START_YEAR not in wide.columns or END_YEAR not in wide.columns:
        print("Error: Start or end year is missing after reshaping the data.")
        return None

    # create a new dataframe to compare the two years
    comparison = pd.DataFrame()

    # get the cost for 2017 and 2024
    comparison["Cost_start"] = wide[START_YEAR]
    comparison["Cost_end"] = wide[END_YEAR]

    # calculate the difference between 2024 and 2017
    comparison["Change"] = comparison["Cost_end"] - comparison["Cost_start"]

    # check that the starting cost is greater than zero
    if (comparison["Cost_start"] <= 0).any():
        print("Error: Percentage change cannot be calculated from zero or negative values.")
        return None

    # calculate the percentage change for each country
    comparison["Percentage_change"] = comparison["Change"] / comparison["Cost_start"] * 100

    return comparison


# ANALYSE THE DISTRIBUTION
def analyse_distribution(comparison):

    # select the absolute changes for all countries
    changes = comparison["Change"]

    # calculate the main statistics for the changes
    results = {
        "mean": changes.mean(),
        "median": changes.median(),
        "std": changes.std(),

        # uncertainty of the average change
        "sem": changes.std() / np.sqrt(len(changes)),

        # smallest and largest changes
        "minimum": changes.min(),
        "maximum": changes.max(),

        # describe the shape of the distribution
        "skewness": skew(changes, bias=False),
        "kurtosis": kurtosis(changes, bias=False),

        # average percentage change across countries
        "mean_percentage_change": comparison["Percentage_change"].mean(),

        # count how many countries increased, decreased or stayed the same
        "increased": (changes > 0).sum(),
        "decreased": (changes < 0).sum(),
        "unchanged": (changes == 0).sum()
    }

    return results


# PRINT THE RESULTS
def print_results(yearly, comparison, results):

    # count the countries included in the analysis
    number_countries = len(comparison)
    print("\n--- MAIN RESULTS ---")
    print("Countries analysed:", number_countries)

    # find the average cost in 2017 and 2024
    start_mean = yearly.loc[yearly["Year"] == START_YEAR, "mean"].iloc[0]
    end_mean = yearly.loc[yearly["Year"] == END_YEAR, "mean"].iloc[0]

    # print the average costs for both years
    print("\nMean cost in", START_YEAR, ":", round(start_mean, 2), "international-$ per person per day")
    print("Mean cost in", END_YEAR, ":", round(end_mean, 2), "international-$ per person per day")

    # print the statistics for the country changes
    print("\nMean absolute change:", round(results["mean"], 2))
    print("Median absolute change:", round(results["median"], 2))
    print("Standard deviation of changes:", round(results["std"], 2))
    print("Standard error of mean change:", round(results["sem"], 3))
    print("Mean percentage change:", round(results["mean_percentage_change"], 1), "%")
    print("Skewness:", round(results["skewness"], 2))
    print("Excess kurtosis:", round(results["kurtosis"], 2))

    # print how many countries increased or decreased
    print("\nCountries with an increase:", results["increased"])
    print("Countries with a decrease:", results["decreased"])
    print("Countries unchanged:", results["unchanged"])

    # calculate the percentage of countries with an increase
    percentage_increased = results["increased"] / number_countries * 100
    print("Percentage of countries with an increase:", round(percentage_increased, 1), "%")


# PLOT THE YEARLY TREND
def plot_yearly_trend(yearly):

    # create a new figure
    plt.figure(figsize=(9, 5))

    # plot the yearly mean with standard error bars
    plt.errorbar(
        yearly["Year"], yearly["mean"], yerr=yearly["sem"],
        marker="o", capsize=4, label="Mean ± standard error"
    )

    # plot the median on the same graph
    plt.plot(yearly["Year"], yearly["median"], marker="s", label="Median")

    # add labels and title
    plt.xlabel("Year")
    plt.ylabel("International-$ (2021 prices) per person per day")
    plt.title("Cost of a Healthy Diet Across Countries, " + str(START_YEAR) + "-" + str(END_YEAR))

    # show all years on the x-axis
    plt.xticks(range(START_YEAR, END_YEAR + 1))

    # add legend and adjust the layout
    plt.legend()
    plt.tight_layout()

    # save and display the graph
    plt.savefig("yearly_trend_with_uncertainty.png", dpi=300)
    plt.show()


# PLOT THE DISTRIBUTION OF CHANGES
def plot_change_distribution(comparison, results):

    # create a new figure
    plt.figure(figsize=(9, 5))

    # plot the changes across all countries in a histogram
    plt.hist(comparison["Change"], bins=18, edgecolor="black")

    # add a line showing the mean
    plt.axvline(
        results["mean"], linestyle="--",
        label="Mean = " + str(round(results["mean"], 2))
    )

    # add a line showing the median
    plt.axvline(
        results["median"], linestyle=":",
        label="Median = " + str(round(results["median"], 2))
    )

    # add labels and title
    plt.xlabel("Change from " + str(START_YEAR) + " to " + str(END_YEAR) + " (international-$ per person per day)")
    plt.ylabel("Number of countries")
    plt.title("Distribution of Country-Level Changes")

    # add legend and adjust the layout
    plt.legend()
    plt.tight_layout()

    # save and display the graph
    plt.savefig("change_distribution_statistics.png", dpi=300)
    plt.show()


# PLOT THE LARGEST INCREASES
def plot_largest_increases(comparison):

    # select the 10 countries with the largest increases
    top_10 = comparison.nlargest(10, "Change")

    # create a horizontal bar chart
    plt.figure(figsize=(10, 6))
    bars = plt.barh(top_10.index, top_10["Change"])

    # put the largest increase at the top
    plt.gca().invert_yaxis()

    # add the value next to each bar
    for bar in bars:
        value = bar.get_width()
        plt.text(
            value + 0.04,
            bar.get_y() + bar.get_height() / 2,
            str(round(value, 2)),
            va="center"
        )

    # add labels and title
    plt.xlabel("Absolute increase (international-$ per person per day)")
    plt.ylabel("Country")
    plt.title("Countries with the Largest Increase " + str(START_YEAR) + "-" + str(END_YEAR))

    # save and display the graph
    plt.tight_layout()
    plt.savefig("largest_increases.png", dpi=300)
    plt.show()


# MAIN PROGRAM
def main():

    
    data = load_data(FILE_NAME)
    if data is None:
        return

    
    if not validate_data(data):
        return


    panel = clean_data(data)
    if panel is None:
        return

    yearly = calculate_yearly_statistics(panel)

   
    comparison = calculate_country_changes(panel)
    if comparison is None or comparison.empty:
        print("Error: Country comparison could not be created.")
        return

  
    results = analyse_distribution(comparison)

  
    print_results(yearly, comparison, results)

    plot_yearly_trend(yearly)
    plot_change_distribution(comparison, results)
    plot_largest_increases(comparison)


# run the program
if __name__ == "__main__":
    main()
