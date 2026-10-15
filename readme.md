
# Cost of a Healthy Diet Around the World (2017–2024)

## Topic

This project looks at how the cost of a healthy diet changed around the world between 2017 and 2024.

I used a dataset from Our World in Data and analysed it using Python to look at how the average cost changed 

over time and how the increases differed between countries.

## Research Questions

1. How did the average cost of a healthy diet change between 2017 and 2024?
2. How did the increase differ between countries?

## Dataset

The dataset comes from Our World in Data, using data from the FAO and World Bank.

Dataset: https://ourworldindata.org/grapher/cost-healthy-diet

The file used in the project is `cost-healthy-diet.csv`.

The dataset contains 1,490 observations from 190 entities covering 2017–2024.

## Data Cleaning

Before analysing the data, the code checks for missing columns, invalid values and duplicate observations.

It then removes rows without a country code and kept only the countries that had data for all eight years.

This was done to make sure the same countries across the whole period were bieng compared.

After cleaning, the dataset contains 179 countries and 1,432 observations.

The cleaning is done automatically by the code.

## Analysis

The code calculates the mean, median, standard deviation and standard error for each year as well as difference 

between the cost in 2017 and 2024 for each country and the percentage change.

the code produces three graphs showing the change over time, the distribution of increases and which countries 

had the largest increases.

## Requirements and How to Run

The project was written in Python 3.

The libraries used are pandas, numpy, matplotlib and scipy.

To run the project, download project3.py and cost-healthy-diet.csv and put them in the same folder.

Then run:

python project3.py

The code reads and cleans the data, calculates the results and creates three graphs.

No manual cleaning is needed.

## Report

The full analysis, discussion and conclusion are included in MAT2007_Final_Report.pdf.

