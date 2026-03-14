# Rotate Data Challenge

Rotate helps airlines turn data into action and improve day-to-day commercial decision-making. We combine state-of-the-art market data, cloud-based tools and analytics with expert support and training.

One of the core metrics used to decide on future investments by airlines is the current available cargo capacity calculation. This is basically the total amount of cargo that can be shipped between different airports given the current flight paths and aircraft.

We want to determine the actual cargo capacity from history data defined from 2 numbers:

1. The number of flights that have traveled between different airports
2. The total amount of volume and/or weight that can be shipped if an aircraft would be fully packed

To get to these numbers we provide two data sets:

1. **flights_events.zip**: this is a collection of events received from Flightradar24. More details about this data are available in `flight_events_documenation.pdf`.
2. **airplane_details.json**: details about the individual aircraft. The schema of this file is provided here:

| field | Example | Description |
|---|---|---|
| `code_iata` | `388` | IATA Aircraft Type Designator |
| `code_icao` | `A388` | ICAO Aircraft Type Designator |
| `full_name` | `Airbus A380-800` | Full name of the aircraft |
| `category` | `A380` | The aircraft category group |
| `average_speed_mph` | `550` | Average cruise speed |
| `volume` | `86.74944` | The volume capacity of the aircraft in m3 |
| `payload` | `83417.6077` | The weight capacity of the aircraft in kg |

We need your help to calculate the total cargo capacity.

## Question 1

Choose a method of accessing the data in the data zip file. This could be flat-file based or loading the data into a database. Make sure to model the data so it becomes easy for you to access multiple times for your analyses. *(Hint: play with the different data types.)*

## Question 2

Create a capacity table that calculates the total available cargo capacity in weight and volume per flight.

**Hint:** The provided data is a subset of the real-world data, so you are going to miss details. Write down what you noticed and how you decided to handle it.

## Question 3

We want you to show us what you find interesting to work on, so come with a way of presenting the data that shows this. *(Please pick one; don’t try to do everything, and be wary of your time.)*

For example:

1. Create an API endpoint that accepts two airports as input and returns the total capacity per day
2. Create a report/graph describing the capacity between the different airports for a given day (doesn’t need to be pretty)
3. Build a model to predict the capacity per route
4. Surprise us...

## Presenting

Whatever you build, be prepared to present it to our team in about 10 minutes the next time we meet. Secondly, we are very interested in how you came up with the result, so we will discuss this in the next 30 minutes.

## Contact

If you have any questions, you can contact me and I’ll try to answer within an hour during working hours (Monday/Friday 9:00 till 17:00). Outside of working hours, I can’t give you any guarantees ;).

- Hans@letsrotate.com — Lead Data Engineer

Good luck,

Hans
