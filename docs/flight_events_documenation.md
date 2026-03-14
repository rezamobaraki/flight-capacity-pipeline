# Flightradar24 Data Service Documentation
## Historic Flight Events Data

**Confidential**

**Last Update:** 17th December 2021

## Introduction

Flightradar24 is a global leader in the tracking of live, worldwide flight movements via terrestrial Automatic Dependent Surveillance - Broadcast (ADS-B) and Multilateration (MLAT) data. Alongside the globally popular website and mobile applications, Flightradar24 provides innovative and robust flight data services to professional organizations of all sizes and industries. Our flight data is suitable for a wide variety of end use cases, ranging from internal research projects to integration within commercial products and major real-time operational systems.

Recipients of our flight data solutions value our services for the accuracy, reliability and coverage of air traffic surveillance offered uniquely by Flightradar24. We are proud to count top tier airlines, airports, airframe manufacturers and a wide range of international aviation solution providers and ancillary organisations as our long time customers. Outside of aviation, our data is also widely sought after and used in the fields of Academia, Tech, Finance, Consultancy, Engineering, Defence, Travel, Media, public bodies and governmental organisations.

Flightradar24 has great experience in ADS-B technology with over a decade of detecting, decoding, processing, storing, enhancing, displaying and distributing flight data. Each day over 2 million people use the Flightradar24 B2C products as the leading source of global flight tracking. The data provided within Flightradar24’s commercial flight data services is sourced from the same proprietary ADS-B and MLAT network, which are served from both our own ADS-B receiver hardware and our global volunteer installations.

This document will provide you with full details on the content, format and delivery of Flightradar24 Historic Flight Events Data. If the data service appears suitable for your intended use or if you have any further questions, please direct all enquiries to business@fr24.com or the Flightradar24 Business Team representative with whom you are currently in contact.

## Flightradar24 Historic Flight Events Data Overview

**Overview:** A professional flight data service that presents the timings and locations of key aircraft movements including Gate Departure, Takeoff, Cruise, Descent, Landing and Gate Arrival, alongside all primary flight, aircraft and operator information.

**Configuration:** Flexible based on the requirements of the Customer. Typical configurations include particular aircraft fleets, airports or geographic regions over defined historic time periods.

**Format:** Data is presented in Comma Separated Variables (CSV).

**Delivery:** Historic data sets can be delivered on a once-off or recurring basis (e.g. daily, weekly, monthly, annually). Data is delivered via a secure URL unique to the Customer.

## 1. Data Service Content and Format

Historic Flight Events Data fields are presented in the following tables:

| # | Data Field | Type* | Description | Example |
|---:|---|:---:|---|---|
| 1 | Address | T | 24 bit mode-S identifier in hexadecimal | `4CAFCD` |
| 2 | Altitude | T | Height above sea level, in feet<sup>1</sup> | `100` |
| 3 | Callsign | T | Up to 8 characters as sent from aircraft transponder | `SAS1530` |
| 4 | Date | D | Date of Event in Universal Coordinated Time (UTC) | `2019-05-31` |
| 5 | Destination_iata | D | IATA code for destination airport<sup>2</sup> | `ARN` |
| 6 | Destination_icao | D | ICAO code for destination airport | `ESSA` |
| 7 | Equipment | D | ICAO Aircraft Type Designator, mapped from address | `A20N` |
| 8 | Event | D | Type of Event, see full list in below table for details | `takeoff` |
| 9 | Flight | D | Commercial flight number, interpreted from callsign | `SK1530` |
| 10 | Flight_id | D | Unique identifier assigned by FR24 to each flight leg | `548794460` |
| 11 | Latitude | X | Floating point format | `51.4649` |
| 12 | Longitude | X | Floating point format | `-0.464989` |
| 13 | Operator | D | ICAO code for carrier operating the flight, mapped from address | `SZS` |
| 14 | Origin_iata | D | IATA code for origin airport<sup>3</sup> | `LHR` |
| 15 | Origin_icao | D | ICAO code for origin airport | `EGLL` |
| 16 | Registration | D | Aircraft registration as matched from address<sup>4</sup> | `EI-SIH` |
| 17 | Runway_landed | D | Optional identifier of destination runway (if configured) | `27L` |
| 18 | Runway_takeoff | D | Optional identifier of origin runway (if configured) | `12R` |
| 19 | Time | D | Time of event (in UTC) | `05:47:11` |

| # | Event Name | Description |
|---:|---|---|
| 1 | Cruising | Reached steady flight level |
| 2 | Descent | Left steady flight level towards destination |
| 3 | Diverting | Left scheduled course |
| 4 | Diverted | Landed at airport other than scheduled<sup>5</sup> |
| 5 | Gate_departure | Ground coverage reports movement away from gate<sup>6</sup> |
| 6 | Gate_arrival | Ground coverage reports movement stopped at gate |
| 7 | Holding | Waiting to land near destination |
| 8 | Landed | Either confirmed or estimated to be on runway |
| 9 | Takeoff | Coverage reports climb from runway |

\* The letter `T` indicates data that is delivered directly from either an aircraft’s ADS-B or a mode-S transponder. `X` indicates data that is in general delivered from ADS-B transponders but derived for mode-S transponders via MLAT, and `D` indicates data that is always derived from either our own Flightradar24 aircraft database references and algorithms, or matched from third party providers of flight scheduling data.

**Notes**

1. Barometric relative to ISO 1013hPa pressure in flight, always 0 on ground.
2. Destination airports are interpreted from aircraft positions or flight routes, which are matched from a flight callsign. If no code is available for a given airport, this code will be blank.
3. For multi-leg segments, routes are reported for only the active leg.
4. The longer registration format including hyphens is used, for example `F-GSPI` rather than `FGSPI`.
5. Diversions are triggered either by transponder position reports or third party data sources.
6. Gate movement events rely on ground coverage which is continually improved but availability varies by airport.

## 2. Data examples

The following data presented in CSV format is an example of Flight `SK1530` from `ARN` to `LHR` on `2019-05-31`.

```csv
address,altitude,callsign,date,destination_iata,destination_icao,equipment,event,flight,flight_id,latitude,longitude,operator,origin_iata,origin_icao,registration,time
4CAFCD,0,SAS1530,2019-05-31,ARN,ESSA,A20N,gate_departure,SK1530,548794460,51.4684,-0.449829,SZS,LHR,EGLL,EI-SIH,05:36:59
4CAFCD,100,SAS1530,2019-05-31,ARN,ESSA,A20N,takeoff,SK1530,548794460,51.4649,-0.464989,SZS,LHR,EGLL,EI-SIH,05:47:11
4CAFCD,39000,SAS1530,2019-05-31,ARN,ESSA,A20N,cruising,SK1530,548794460,52.9233,2.0156,SZS,LHR,EGLL,EI-SIH,06:10:01
4CAFCD,36900,SAS1530,2019-05-31,ARN,ESSA,A20N,descent,SK1530,548794460,59.1152,15.2306,SZS,LHR,EGLL,EI-SIH,07:23:51
4CAFCD,0,SAS1530,2019-05-31,ARN,ESSA,A20N,landed,SK1530,548794460,59.6569,17.9416,SZS,LHR,EGLL,EI-SIH,07:46:10
4CAFCD,0,SAS1530,2019-05-31,ARN,ESSA,A20N,gate_arrival,SK1530,548794460,59.6547,17.9392,SZS,LHR,EGLL,EI-SIH,07:47:20
```

Please note that this example includes data for the full number of data attributes available, including those which are optional. For CSV formats only 7-bit ASCII characters are included so there is no need to support special character sets for any supplied data fields.

Full 24hr data samples can be accessed via the following links:

### Flightradar24 Historic Flight Events Data Sample (CSV) - SAS Airlines 2021.07.23
- Username: `sas_airline_sample_events`
- Password: `aipheFahbae4za`
- Link: https://secure.flightradar24.com/sas_airline_sample_events/

### Flightradar24 Historic Flight Events Data Sample (CSV) - Arlanda Airport 2021.07.23
- Username: `arlanda_airport_sample_events`
- Password: `AiX1paijei2aiz`
- Link: https://secure.flightradar24.com/arlanda_airport_sample_events/

## 3. Data Delivery

Once an order for Historic Flight Events Data has been confirmed, Flightradar24 will begin creating the data set according to the agreed configuration. Once complete, the Customer will be sent a HTTPS link with a unique username and password via email. This URL link will take the Customer to a secure cloud directory where Flightradar24 will have uploaded the data for download.

For recurring data deliveries of the same configuration, Customers can continue to use the same link and access credentials. Downloads of data files can be made manually, or for recurring data deliveries it may be preferable for Customers to build an automatic retrieval system. Customers can then connect their software to this server periodically depending on their desired download schedule.

## 4. Frequently Asked Questions

### 4.1 Where do the different data fields come from?

The data provided within Flightradar24’s commercial flight data services is sourced from the same proprietary ADS-B and MLAT network as used for the Flightradar24 website and apps, which are served from both our own ADS-B receiver hardware and our global volunteer installations. To this raw ADS-B transponder data Flightradar24 applies advanced algorithms to seamlessly match each detected flight call sign to a unique aircraft and flight number, sourced from both our own comprehensive aircraft databases and third party flight schedules respectively.

The data fields **address** and **callsign** are supplied directly from the aircraft’s transponder. **Latitude** and **longitude** are sourced from on-board GPS data, which for aircraft equipped with ADS-B is also sent directly from the aircraft transponder. **Registration** and **Equipment** are mapped directly from **address** using our carefully maintained aircraft database. **Origin** is primarily inferred from low altitude aircraft movements, whilst **Destination** and **Flight** are fields mapped from both our own data algorithms as well as external sources of scheduled flight routes. **Date** and **Time** are recorded using live flight positions. **Events** are plotted based on an algorithm that compares changes of an aircraft’s position, speed and altitude over a certain period of time. The first evidence of change corresponds to the Event log.

Note that aircraft without an ADS-B transponder do not transmit GPS data. To calculate the position of aircraft transmitting via mode-S we use a technique called Multilateration (MLAT). MLAT is only possible when the aircraft is flying within direct range of at least four ADS-B ground receivers and as such is not available at low altitudes or on ground. More details on calculating the position of an aircraft via MLAT can be found at https://www.flightradar24.com/how-it-works.

### 4.2 What is Flightradar24’s coverage level?

Flightradar24 operates and invests significantly in building the world’s largest, independent, terrestrial ADS-B network, maintaining over 30,000 receivers worldwide that feed data into the company network 24/7. Each receiver has a range from 250-450 km (150-250 miles) and operates on the 1090 MHz frequency. Coverage across all major commercial flight routes worldwide is very high.

Gaps in positional data may be observed over some areas of deep ocean or areas of very low population, where the aircraft is out of direct range of an ADS-B receiver. It is very important to recognise that availability of aircraft positional data via ADS-B and MLAT is strictly dependent on the type of transponder data broadcast from a particular aircraft, combined with the range of receiver coverage in the region where the aircraft is flying.

As complimentary data sources, Flightradar24 also acquires and integrates data from multiple worldwide Air Navigation Service Providers (ANSPs), North American Radar data, space-based ADS-B data (sADS-B) and ADS-C data. Flightradar24’s network is constantly evolving, with growth focused on high quality receiver installations that bring the most benefit to our existing locations.

For an up-to-date picture of coverage in a particular geographic region, please refer to the live map at www.flightradar24.com, where the positions and movements of aircraft are displayed in real time. Ensure you appropriately adjust website **Settings > Estimations** to `Off` when making this kind of evaluation. Note that in areas with no direct ADS-B coverage available, estimated flight positions are not included in Flightradar24’s Historic Flight Positions data. In addition, aircraft that have their information restricted or blocked from view on Flightradar24’s website and apps will similarly not have this information included in any historic data set.

### 4.3 Is it possible to track OOOI movements with FR24 Historic Flight Events Data?

Yes. **Gate departure** (equivalent to out of the gate) represents when a flight crew have turned on the aircraft’s transponder and movement is detected by changing GPS coordinates. **Takeoff** and **Landed** represent “off the ground” and “on the ground” events and finally, **Gate arrival** applies when the aircraft stops (into the gate). As indicated previously, the detection of on-ground Events is dependent on the level of ADS-B coverage available across different airport locations.

### 4.4 Why does a flight not have a full set of data fields?

ADS-B signals from an aircraft must be detected by a receiver in line of sight. As such, missing data fields may occur where an aircraft is operating outside of Flightradar24’s direct coverage. The detection of on-ground Events is particularly dependent on the level of ADS-B coverage available across different airport locations.

Lesser data may also be seen for aircraft not equipped with an ADS-B transponder, as such aircraft do not transmit GPS position reports. Where possible, we will calculate the position of aircraft broadcasting via Mode-S using Multilateration, however this is not possible on ground or at very low altitudes.

For non-commercial operations such as business and private aircraft, some fields associated with a commercial (passenger) operation may not be present. Some business aircraft will also have their identifying information restricted, such as aircraft **address** and **registration**, and therefore these fields will not be present in the data set. In a small number of cases, missing data may also originate from an incorrect or unavailable call sign entered by the aircraft crew at the time of takeoff. Without a correct call sign Flightradar24 cannot match the flight to the scheduled route.

### 4.5 What determines which flight events are included within a requested date range?

Flightradar24’s Historic Flight Events exports begin with all flight events where **Date** matches the first day of the data set configuration in UTC. Therefore, if a Customer requires a complete events record for all aircraft in flight on the first day of a specified date range in a time zone ahead of UTC, the data export should begin with the day prior. This would also ensure complete events record for flights around midnight which may takeoff before the requested data set configuration date but land at the specified date.

### 4.6 Can we request a data sample before purchase?

Flightradar24 has a range of stock data samples in CSV available for you to evaluate the service content, format and delivery method. Bespoke data samples may also be discussed and provided prior to large data purchases.

### 4.7 How long will it take for the data to be delivered, and how big are the data files?

The time taken for completion of a data export depends on the size and configuration of the data request. Smaller data sets take a matter of minutes or hours, whereas the largest or most complex, such as multiple years of global data or areas of multiple latitudes and longitude, can take multiple days to process. For very large amounts of data, delivery may be staged into separate time periods as new files become available.

The size of a data file will depend on the number of flight movements that are included in the configuration. As Flightradar24 typically tracks between 150,000 - 200,000 flights per day globally, orders for larger data exports will consist of substantial data volumes. Your Business Team representative can assist with estimations of delivery time and file size.

### 4.8 Is it possible to set up automated download of recurring data?

In the case of a recurring data service, Customers often choose to create a simple app or tool which will periodically ping and check the remote directory / HTTPS link provided by FR24 for dataset delivery. On each occasion such a tool could check the specified directory for new unacquired CSV file names and download into the Customer’s internal repository avoiding any duplication.

For further questions or to begin your service, please contact us with all enquiries at business@fr24.com.
