
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
