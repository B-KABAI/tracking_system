from flask import Flask, render_template, request, redirect, url_for

import mysql.connector

import pandas as pd

import matplotlib

import matplotlib.pyplot as plt
import os

matplotlib.use('Agg')



app = Flask(__name__)

app.secret_key = 'secret'

url = "Apple_data.csv"

db =mysql.connector.connect(host = "127.0.0.1", user = "root", passwd = "root", database = "developmentDatabase")





@app.route("/", methods=['GET', 'POST'])

def index():

    if request.method == 'POST':

     email = request.form.get('email')

     password = request.form.get('password')



     cursor = db.cursor()

     cursor.execute ("SELECT * FROM users WHERE email=%s AND password=%s",(email,password))

     user = cursor.fetchone()

     cursor.close()



     if user:

         return redirect('dashboard')

     else:

         return "LOGIN FAILED ,TRY AGAIN"

    return render_template('index.html')



    



@app.route("/signup", methods=['GET', 'POST'])

def signup():

    if request.method == 'POST':

        email = request.form.get('email')

        first_name = request.form.get('first_name')

        surname = request.form.get('surname')

        password = request.form.get('password')



        try:

            cursor = db.cursor()

            cursor.execute("INSERT INTO users (email, first_name, surname, password) VALUES (%s, %s, %s, %s)",

                         (email, first_name, surname, password))

            db.commit()

            cursor.close()

            

        except mysql.connector.IntegrityError:

            return "YOUR NEW ACCOUNT HAS BEEN CREATED GO BACK TO  <a href = '/' >  sign in</a>"



    return render_template('signup.html')



@app.route("/dashboard")

def dashboard():

    df = pd.read_csv(url)


    



    # Ensure static folder exists
    os.makedirs("static", exist_ok=True)

    
    kwh_cols = ['Year1_kWh', 'Year2_kWh', 'Year3_kWh', 'Year4_kWh', 'Year5_kWh']

    df_kwh = df.melt(
        id_vars=['Product'],
        value_vars=kwh_cols,
        var_name='Year',
        value_name='kWh'
    )


    df_kwh['Year'] = df_kwh['Year'].str.extract('(\d+)').astype(int)

    plt.figure(figsize=(10, 6))

    for product, group in df_kwh.groupby('Product'):
        group = group.sort_values('Year')
        plt.plot(group['Year'], group['kWh'], marker='o', label=product)

    plt.xlabel('Year')
    plt.ylabel('Electricity Consumption (kWh)')
    plt.title('Electricity Usage Trend (5 Years)')
    plt.legend()
    plt.grid(True)

    plt.savefig('static/graph1.png')
    plt.close()


    co2_cols = ['Year1_CO2e', 'Year2_CO2e', 'Year3_CO2e', 'Year4_CO2e', 'Year5_CO2e']


    df_grouped = df.groupby('Product', as_index=False).sum()

    df_grouped['TkWh'] = df_grouped[kwh_cols].sum(axis=1)
    df_grouped['TCO2e'] = df_grouped[co2_cols].sum(axis=1)

    plt.figure(figsize=(8, 6))

    
    for _, row in df_grouped.iterrows():
        plt.scatter(row['TkWh'], row['TCO2e'], label=row['Product'])

    plt.xlabel('Total Electricity Consumption (kWh over 5 Years)')
    plt.ylabel('Total CO2 Emissions (CO2e over 5 Years)')
    plt.title('Electricity vs CO2 Emissions')

    plt.legend()   # shows each product ONCE
    plt.grid(True)

    plt.savefig('static/graph2.png')
    plt.close()

    return render_template("dashboard.html")

if __name__ == '__main__':

 app.run(debug=True)