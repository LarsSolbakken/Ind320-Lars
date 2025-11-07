
# try:
#     test_df = (spark.read
#     .format("mongodb")
#     .option("spark.mongodb.connection.uri", "mongodb://127.0.0.1:27017")
#     .option("spark.mongodb.database", "test")
#     .option("spark.mongodb.collection", "testcoll")
#     .load()
# )
#     print("✅ Mongo connector is working!")
# except Exception as e:
#     print("❌ Mongo connector not loaded:", e)



#!!!#notater 
# # -------------------------
# # 2) Fetch Elhub API data for 2021
# # -------------------------
# base_url = "https://api.elhub.no/energy-data/v0/price-areas"

# # Make a list of months in 2021
# months = pd.date_range("2021-01-01", "2021-12-31", freq="MS")

# all_data = []

# for start in months:
#     end = start + pd.offsets.MonthEnd(1)

#     params = {
#         "dataset": "PRODUCTION_PER_GROUP_MBA_HOUR",
#         "startDate": start.strftime("%Y-%m-%d"),
#         "endDate": end.strftime("%Y-%m-%d")
#     }

#     print(f"Fetching {params['startDate']} to {params['endDate']}...")
#     r = requests.get(base_url, params=params)
#     r.raise_for_status()
#     data = r.json()

#     # Flatten "productionPerGroupMbaHour"
#     for item in data["data"]:
#         prod = item["attributes"].get("productionPerGroupMbaHour", [])
#         all_data.extend(prod)

# print(f"Total records fetched: {len(all_data)}")

# # -------------------------
# # 3) Convert to DataFrame
# # -------------------------
# df = pd.DataFrame(all_data)

# # Clean up time column
# df["startTime"] = pd.to_datetime(df["startTime"], errors="coerce")

# # Keep relevant columns only
# df_clean = df[["priceArea", "productionGroup", "startTime", "quantityKwh"]].copy()

# print(df_clean.head())
# print("Shape:", df_clean.shape)

# # -------------------------
# # 4) Insert into MongoDB
# # -------------------------
# # Convert DataFrame to list of dicts
# records = df_clean.to_dict(orient="records")

# # Insert into NEW collection
# collection.delete_many({})   # optional: clear old data
# collection.insert_many(records)

# print(f"✅ Inserted {len(records)} records into {db.name}.{collection.name}")





# print(spark.version)# --- Write test ---
# mini = spark.createDataFrame([Row(a=1, b="x"), Row(a=2, b="y")])
# mini.write.format("mongodb") \
#     .mode("append") \
#     .option("uri", "mongodb://127.0.0.1:27017/test.testcoll") \
#     .save()

# print("✅ Write done")

# # --- Read test ---
# df_mongo = spark.read.format("mongodb") \
#     .option("uri", "mongodb://127.0.0.1:27017/test.testcoll") \
#     .load()
# df_mongo.show(5)



#!!!notater


# from pymongo.mongo_client import MongoClient
# from pymongo.server_api import ServerApi

# uri = "mongodb+srv://tveit001_db_user:Am5spYHS69kraxQF@cluster0.3m91rus.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# # Create a new client and connect to the server
# client = MongoClient(uri, server_api=ServerApi('1'))

# # Send a ping to confirm a successful connection
# try:
#     client.admin.command('ping')
#     print("Pinged your deployment. You successfully connected to MongoDB!")
# except Exception as e:
#     print(e)

# import requests
# import pandas as pd

# base_url = "https://api.elhub.no/energy-data/v0/price-areas"

# # Make a list of months in 2021
# months = pd.date_range("2021-01-01", "2021-12-31", freq="MS")

# all_data = []

# for start in months:
#     end = start + pd.offsets.MonthEnd(1)   # <-- keep as datetime
    
#     # Build URL params
#     params = {
#         "dataset": "PRODUCTION_PER_GROUP_MBA_HOUR",
#         "startDate": start.strftime("%Y-%m-%d"),
#         "endDate": end.strftime("%Y-%m-%d")
#     }

#     print(f"Fetching {params['startDate']} to {params['endDate']}...")

#     r = requests.get(base_url, params=params)
#     r.raise_for_status()
#     data = r.json()
#     # import json
#     # print(json.dumps(data, indent=2)[:1000]) 
#     # Flatten "productionPerGroupMbaHour"
#     records = []
#     for item in data["data"]:
#         prod = item["attributes"].get("productionPerGroupMbaHour", [])
#         records.extend(prod)

#     all_data.extend(records)

# # Convert to DataFrame
# df = pd.DataFrame(all_data)
# print(df.head())


# use('mongodbVSCodePlaygroundDB');

# // Insert a few documents into the sales collection.
# db.getCollection('sales').insertMany([
#   { 'item': 'abc', 'price': 10, 'quantity': 2, 'date': new Date('2014-03-01T08:00:00Z') },
#   { 'item': 'jkl', 'price': 20, 'quantity': 1, 'date': new Date('2014-03-01T09:00:00Z') },
#   { 'item': 'xyz', 'price': 5, 'quantity': 10, 'date': new Date('2014-03-15T09:00:00Z') },
#   { 'item': 'xyz', 'price': 5, 'quantity': 20, 'date': new Date('2014-04-04T11:21:39.736Z') },
#   { 'item': 'abc', 'price': 10, 'quantity': 10, 'date': new Date('2014-04-04T21:23:13.331Z') },
#   { 'item': 'def', 'price': 7.5, 'quantity': 5, 'date': new Date('2015-06-04T05:08:13Z') },
#   { 'item': 'def', 'price': 7.5, 'quantity': 10, 'date': new Date('2015-09-10T08:43:00Z') },
#   { 'item': 'abc', 'price': 10, 'quantity': 5, 'date': new Date('2016-02-06T20:20:13Z') },
# ]);

# // Run a find command to view items sold on April 4th, 2014.
# const salesOnApril4th = db.getCollection('sales').find({
#   date: { $gte: new Date('2014-04-04'), $lt: new Date('2014-04-05') }
# }).count();

# // Print a message to the output window.
# console.log(`${salesOnApril4th} sales occurred in 2014.`);

# // Here we run an aggregation and open a cursor to the results.
# // Use '.toArray()' to exhaust the cursor to return the whole result set.
# // You can use '.hasNext()/.next()' to iterate through the cursor page by page.
# db.getCollection('sales').aggregate([
#   // Find all of the sales that occurred in 2014.
#   { $match: { date: { $gte: new Date('2014-01-01'), $lt: new Date('2015-01-01') } } },
#   // Group the total sales for each product.
#   { $group: { _id: '$item', totalSaleAmount: { $sum: { $multiply: [ '$price', '$quantity' ] } } } }




# --- Write test ---
# mini = spark.createDataFrame([{"a": 1, "b": "x"}, {"a": 2, "b": "y"}])
# mini.write.format("mongodb") \
#     .mode("append") \
#     .option("uri", "mongodb://127.0.0.1:27017/test.testcoll") \
#     .save()

# print("✅ Write done")

# # --- Read test ---
# df_mongo = spark.read.format("mongodb") \
#     .option("uri", "mongodb://127.0.0.1:27017/test.testcoll") \
#     .load()
# df_mongo.show(5)








 # import json
    # print(json.dumps(data, indent=2)[:1000]) 
    # Flatten "productionPerGroupMbaHour"











# Optional: increase partitions a bit before write (tune if needed)
# df_spark = df_spark.repartition(8, "priceArea", "productionGroup")
# df_spark = df_spark.withColumnRenamed("priceArea", "pricearea") \
#                    .withColumnRenamed("productionGroup", "productiongroup") \
#                    .withColumnRenamed("startTime", "starttime") \
#                    .withColumnRenamed("quantityKwh", "quantitykwh")
# df_spark.printSchema()
# df_spark.show(5)






######streamlitapp
 # if df_month.empty:
    #     st.warning("No data available for this selection.")
    # else:
    #     fig2, ax2 = plt.subplots(figsize=(8, 6))
    #     sns.lineplot(data=df_month, x="starttime", y="quantitykwh", hue="productiongroup", ax=ax2)
    #     month_names = [pd.to_datetime(str(m), format="%m").strftime("%B") for m in selected_month]
    #     ax2.set_title(f"Production in {selected_area}, {', '.join(month_names)} 2021")
    #     # ax2.set_title(f"Production in {selected_area}, {pd.to_datetime(str(selected_month), format='%m').strftime('%B')} 2021")
    #     ax2.set_xlabel("Date")
    #     ax2.set_ylabel("kWh")
    #     st.pyplot(fig2)

    #     summary = df_month.groupby("productiongroup")["quantitykwh"].sum().reset_index()
    #     summary["quantitykwh"] = (summary["quantitykwh"]/1e6).round(2)  # convert to GWh
    #     st.write("### Monthly Summary (GWh)")
    #     st.dataframe(summary)

# months = list(range(1, 13))
    # selected_month = st.multiselect("Select Month", months, format_func=lambda x: pd.to_datetime(str(x), format="%m").strftime("%B"))
    
    
    # df_month = df[
    #     (df["pricearea"] == selected_area) &
    #     (df["productiongroup"].isin(selected_groups)) &
    #     (df["starttime"].dt.month.isin(selected_month))
    # ]



# /* global use, db */
# // MongoDB Playground
# // To disable this template go to Settings | MongoDB | Use Default Template For Playground.
# // Make sure you are connected to enable completions and to be able to run a playground.
# // Use Ctrl+Space inside a snippet or a string literal to trigger completions.
# // The result of the last command run in a playground is shown on the results panel.
# // By default the first 20 documents will be returned with a cursor.
# // Use 'console.log()' to print to the debug output.
# // For more documentation on playgrounds please refer to
# // https://www.mongodb.com/docs/mongodb-vscode/playgrounds/

# // Select the database to use.
# use('mongodbVSCodePlaygroundDB');

# // Insert a few documents into the sales collection.
# db.getCollection('sales').insertMany([
#   { 'item': 'abc', 'price': 10, 'quantity': 2, 'date': new Date('2014-03-01T08:00:00Z') },
#   { 'item': 'jkl', 'price': 20, 'quantity': 1, 'date': new Date('2014-03-01T09:00:00Z') },
#   { 'item': 'xyz', 'price': 5, 'quantity': 10, 'date': new Date('2014-03-15T09:00:00Z') },
#   { 'item': 'xyz', 'price': 5, 'quantity': 20, 'date': new Date('2014-04-04T11:21:39.736Z') },
#   { 'item': 'abc', 'price': 10, 'quantity': 10, 'date': new Date('2014-04-04T21:23:13.331Z') },
#   { 'item': 'def', 'price': 7.5, 'quantity': 5, 'date': new Date('2015-06-04T05:08:13Z') },
#   { 'item': 'def', 'price': 7.5, 'quantity': 10, 'date': new Date('2015-09-10T08:43:00Z') },
#   { 'item': 'abc', 'price': 10, 'quantity': 5, 'date': new Date('2016-02-06T20:20:13Z') },
# ]);

# // Run a find command to view items sold on April 4th, 2014.
# const salesOnApril4th = db.getCollection('sales').find({
#   date: { $gte: new Date('2014-04-04'), $lt: new Date('2014-04-05') }
# }).count();

# // Print a message to the output window.
# console.log(`${salesOnApril4th} sales occurred in 2014.`);

# // Here we run an aggregation and open a cursor to the results.
# // Use '.toArray()' to exhaust the cursor to return the whole result set.
# // You can use '.hasNext()/.next()' to iterate through the cursor page by page.
# db.getCollection('sales').aggregate([
#   // Find all of the sales that occurred in 2014.
#   { $match: { date: { $gte: new Date('2014-01-01'), $lt: new Date('2015-01-01') } } },
#   // Group the total sales for each product.
#   { $group: { _id: '$item', totalSaleAmount: { $sum: { $multiply: [ '$price', '$quantity' ] } } } }
# ]);


# import streamlit as st 
# st.title("⚡ Electricity Production in Norway (Elhub 2021)")

# import streamlit as st
# import pandas as pd
# import matplotlib.pyplot as plt
# import seaborn as sns
# from pymongo import MongoClient

# # -------------------------
# # Connect to MongoDB Atlas
# # -------------------------
# # Connection string is stored securely in .streamlit/secrets.toml
# # Example format in secrets.toml:
# # [mongo]
# # uri = "mongodb+srv://<user>:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority"

# uri = st.secrets["mongo"]["uri"]   # get MongoDB URI from secrets
# client = MongoClient(uri)          # connect to MongoDB Atlas
# db = client["elhub2021"]           # use database "elhub2021"
# collection = db["production_per_group_hour"]  # collection with production data

# # Load all MongoDB documents into a pandas DataFrame
# # Exclude "_id" field since it is only MongoDB's internal ID
# docs = list(collection.find({}, {"_id": 0}))
# df = pd.DataFrame(docs)

# # Ensure timestamps are parsed as datetime objects
# df["starttime"] = pd.to_datetime(df["starttime"], errors="coerce")

# # -------------------------
# # Streamlit UI setup
# # -------------------------

# st.write("Visualizing electricity production data from Elhub API, stored in MongoDB.")

# # Define consistent colors for each production group
# colors = {
#     "hydro": "#1f77b4",
#     "wind": "#2ca02c",
#     "solar": "#ffbb00",
#     "thermal": "#d62728",
#     "other": "#7f7f7f"
# }

# # Map price area codes (NO1–NO5) to region names for easier interpretation
# price_area_names = {
#     "NO1": "NO1 (Østlandet)",
#     "NO2": "NO2 (Sørlandet)",
#     "NO3": "NO3 (Midt-Norge)",
#     "NO4": "NO4 (Nord-Norge)",
#     "NO5": "NO5 (Vestlandet)"
# }

# # -------------------------
# # Global filters (shared by both plots)
# # -------------------------
# st.subheader("Filters")

# # Radio button selector for price area
# # User sees human-friendly labels, but filtering still uses NO1–NO5 codes
# price_areas = sorted(df["pricearea"].unique())
# selected_label = st.radio("Select Price Area", [price_area_names[p] for p in price_areas], horizontal=True)
# selected_area = [k for k, v in price_area_names.items() if v == selected_label][0]

# # Month range slider (choose start and end month)
# months = pd.date_range("2021-01-01", "2021-12-01", freq="MS")
# start, end = st.select_slider(
#     "Select month range",
#     options=months,
#     value=(months[0], months[-1]),   # default = full year
#     format_func=lambda p: p.strftime("%B")  # display month names
# )

# # Split page into two columns (pie chart left, line plot right)
# col1, col2 = st.columns(2)

# # ---- Left Column: Pie Chart ----
# with col1:
#     st.subheader("Total Production by Group")
   
#     # Filter dataset by selected area + month range
#     df_area = df[
#         (df["pricearea"] == selected_area) &
#         (df["starttime"].dt.month >= start.month) &
#         (df["starttime"].dt.month <= end.month)
#     ]

#     # Aggregate total production per group
#     totals = df_area.groupby("productiongroup")["quantitykwh"].sum()

#     # Display total production in GWh as a metric above the chart
#     st.metric("Total Production (GWh)", f"{totals.sum()/1e6:.1f}")

#     # Pie chart showing share of each production group
#     fig1, ax1 = plt.subplots(figsize=(8, 6))
#     totals.plot(kind="pie", autopct='%1.1f%%', ax=ax1, colors=[colors[g] for g in totals.index])
#     ax1.set_ylabel("")
#     ax1.set_title(f"Total Production in {selected_area}, 2021")
#     st.pyplot(fig1)

# # ---- Right Column: Line Plot ----
# with col2:
#     st.subheader("Monthly Production Trends")

#     # Ensure "other" group is always shown last in the pill selector
#     prod_groups = sorted(df["productiongroup"].unique())
#     if "other" in prod_groups:
#         prod_groups = [g for g in prod_groups if g != "other"] + ["other"]

#     # Pills allow multiple group selection
#     selected_groups = st.pills(
#         "Select Production Groups",
#         prod_groups,
#         default=prod_groups,
#         selection_mode="multi"
#     )
    
#     # Filter dataset by selected area, production groups, and time range
#     df_range = df[
#         (df["pricearea"] == selected_area) &
#         (df["productiongroup"].isin(selected_groups)) &
#         (df["starttime"] >= start) &
#         (df["starttime"] <= end)
#     ]
   
#     # If no data available for the selection, show warning
#     if df_range.empty:
#         st.warning("No data available for this selection.")
#     else:
#         # Line plot of hourly production, grouped by production group
#         fig2, ax2 = plt.subplots(figsize=(8, 6))
#         sns.lineplot(
#             data=df_range,
#             x="starttime", y="quantitykwh",
#             hue="productiongroup", palette=colors,
#             ax=ax2
#         )

#         # Title includes selected area and month range
#         ax2.set_title(
#             f"Production in {selected_area}, "
#             f"{start.strftime('%B')} – {end.strftime('%B')} 2021"
#         )
#         ax2.set_xlabel("Date")
#         ax2.set_ylabel("kWh")
#         st.pyplot(fig2)

#         # Table: total production per group in GWh
#         summary = df_range.groupby("productiongroup")["quantitykwh"].sum().reset_index()
#         summary["Production (GWh)"] = (summary["quantitykwh"]/1e6).round(2)  # convert to GWh
#         summary = summary.drop(columns=["quantitykwh"])  # drop raw column

#         # Sort by Production (descending), but keep "other" last
#         if "other" in summary["productiongroup"].values:
#             other_row = summary[summary["productiongroup"] == "other"]
#             summary = summary[summary["productiongroup"] != "other"] \
#                 .sort_values(by="Production (GWh)", ascending=False)
#             summary = pd.concat([summary, other_row])
#         else:
#             summary = summary.sort_values(by="Production (GWh)", ascending=False)

#         # Reset index to avoid showing 0,1,2,3
#         summary = summary.reset_index(drop=True)

#         st.write("### Summary for selected range")
#         st.dataframe(summary)

# # ---- Expander with source info ----
# with st.expander("ℹ️ Data Source"):
#     st.markdown("""
#     Data retrieved from the [Elhub API](https://api.elhub.no/energy-data/v0/price-areas),
#     processed with Spark + Cassandra, and stored in MongoDB Atlas for visualization.
#     """)




#part 3




# # -------------------------
# # Weather Data (Open-Meteo API)
# # -------------------------
# from utils import download_weather  # 👈 You’ll create utils.py with this function

# st.subheader("🌦️ Weather Data (Open-Meteo API)")

# # Coordinates for each city
# city_coordinates = {
#     "Oslo": {"lon": 10.75, "lat": 59.91},
#     "Kristiansand": {"lon": 8.00, "lat": 58.15},
#     "Trondheim": {"lon": 10.40, "lat": 63.43},
#     "Tromsø": {"lon": 18.96, "lat": 69.65},
#     "Bergen": {"lon": 5.32, "lat": 60.39}
# }

# # Let the user choose which city to load weather data for
# selected_city = st.selectbox("Select city", list(city_coordinates.keys()))
# coords = city_coordinates[selected_city]

# # Let the user choose year
# year = st.number_input("Select year", 2019, 2024, 2019)

# # Fetch data using your API function
# df_weather = download_weather(coords["lon"], coords["lat"], year)
# st.dataframe(df_weather.head())

# # Save selected city and data for use on other pages
# st.session_state["selected_city"] = selected_city
# st.session_state["df_weather"] = df_weather

