import requests
import time
import json
from datetime import datetime
import mysql.connector
import pytz
from tkinter import *
from tkinter import ttk, messagebox


db = mysql.connector.connect(
    host = "localhost",
    user = "root",
    password = "Meesam_rizvi69"   
)
cur = db.cursor()
cur.execute("create database if not exists weather_coverage")
cur.execute("use weather_coverage")
cur.execute("create table if not exists data(ID INT AUTO_INCREMENT PRIMARY KEY, date varchar(30), time varchar(30), city varchar(30) ,temp varchar(30) ,sky varchar(30) ,humidity varchar(30) ,wind_speed varchar(30) ,wind_dir varchar(30),sunrise varchar(30),sunset varchar(30))")
time.sleep(0.5)

def sendmessage(mes , no):
    try:
        api_url = "https://api.callmebot.com/whatsapp.php"
        payload ={
            "phone": no,
            "text": mes,
            "apikey": "1635564" 
        }
        response = requests.post(api_url, params=payload)

        if response.status_code == 200:
            print("Message sent successfully!")
        else:
            print("Failed to send message. Error:", response.text)
    except Exception as e:
        messagebox.showerror("Failed to send message, Try again!", str(e))
   
time.sleep(0.5)   

def database(date, tim, city, temp, sky, humid, windspeed, winddeg,sunrise_local ,sunset_local ):
    try:
        cur.execute("insert into data(date, time, city, temp, sky, humidity, wind_speed, wind_dir,sunrise ,sunset) values('{}','{}','{}','{}','{}','{}','{}','{}','{}','{}')".format(date, tim, city, temp, sky, humid, windspeed, winddeg,sunrise_local,sunset_local))
        db.commit()
        print("Data Successfully Added")
    except Exception as e:
        messagebox.showerror("Failed to add data to MySQL, Try again!", str(e))

          

def KelvintoCelcius(K):
    C = K-273.15
    return "{:.2f}".format(C)


def degtocardinal(deg):
    if deg >= 337.5 or deg < 22.5:
        return "North"
    elif 22.5 <= deg < 67.5:
        return "North-East"
    elif 67.5 <= deg < 112.5:
        return "East"
    elif 112.5 <= deg < 157.5:
        return "South-East"
    elif 157.5 <= deg < 202.5:
        return "South"
    elif 202.5 <= deg < 247.5:
        return "South-West"
    elif 247.5 <= deg < 292.5:
        return "West"
    elif 292.5 <= deg < 337.5:
        return "North-West"
    else:
        return "Invalid wind direction"    

def get_info():
    try:
        selected_city = selected_timezone.get().split('/')[-1].replace('_', ' ')
        selected_city_value = selected_city
        selected_timezone_value = selected_timezone.get()
        selected_no = str(entry_box.get())
        fetch_and_store_weather(selected_city_value,selected_timezone_value,selected_no)
        mess = "Notification Sent Successfully!"
        messagebox.showinfo("Weather Information", mess)

    except Exception as e:
        messagebox.showerror("Failed to get weather, Try again!", str(e))
    
 
 
def fetch_and_store_weather(selected_city_value,selected_timezone_value,selected_no):
    try:
        key = '3ff4b1100fef4f3f06b00e78af27b533'
        url = f"https://api.openweathermap.org/data/2.5/weather?appid={key}&q={selected_city_value}"   

        response = requests.get(url).json()

        temp = KelvintoCelcius(response["main"]["temp"]) 
        sky = response["weather"][0]["description"]   
        winddeg = degtocardinal(response["wind"]["deg"])
        windspeed = response["wind"]["speed"]
        humid = response["main"]["humidity"]
        
        
        timezone = pytz.timezone(selected_timezone_value)  
        sunrise_utc = datetime.utcfromtimestamp(response["sys"]["sunrise"])
        sunset_utc = datetime.utcfromtimestamp(response["sys"]["sunset"])
        sunrise_local = sunrise_utc.replace(tzinfo=pytz.utc).astimezone(timezone).strftime('%I:%M %p')
        sunset_local = sunset_utc.replace(tzinfo=pytz.utc).astimezone(timezone).strftime('%I:%M %p')
        
        now = datetime.now(timezone)
        tim = now.strftime("%H:%M:%S")
        date = now.strftime("%d-%m-%Y")


        database(date, tim, selected_city_value , temp, sky, humid, windspeed, winddeg,sunrise_local,sunset_local)


        message = f"""Today's Weather Forecast
    City Name: {selected_city_value}.
    Humidity: {humid}%.
    Temperature: {temp} C.
    Cloud Coverage: {sky}.
    Wind speed: {windspeed} m/s.
    Wind direction: {winddeg}.
    Sunrise: {sunrise_local}.
    Sunset: {sunset_local}.
    """
        sendmessage(message, selected_no) 
    except Exception as e:
        messagebox.showerror("Failed to get weather, Try again!", str(e))

def get_exit():
    app.destroy()
    
    
all_timezones = pytz.all_timezones

app = Tk()
app.geometry('727x404+330+185')
app.resizable(0, 0)


background_image = PhotoImage(file="bg.png")
background_label = Label(app, image=background_image)
background_label.place(x=0, y=0, relwidth=1, relheight=1)


main_label = Label(app,
                   text="ClimBot",
                   font=('Times New Roman', 40, 'bold'),
                   fg='#FFFFFF',  
                   bg='#b3d5ee',  
                   pady=10)
main_label.pack()


label = Label(app, text="Please select your region:",
              font=('Times New Roman', 12),
              fg='black')  
label.pack(padx=5, pady=5)

selected_timezone = StringVar()
timezones = ttk.Combobox(app, textvariable=selected_timezone)
timezones['values'] = all_timezones
timezones['state'] = 'readonly'
timezones.pack(padx=5, pady=5)

        

no_label = Label(app,
                text="Please enter your Number:",
                font=('Times New Roman', 12),
                fg='black').pack(padx=5, pady=5)

entry_box = Entry(app,
                bg="white",
                font=('Times New Roman', 11))
entry_box.pack()


get_weather_button = Button(app,
                            text="Get Weather",
                            font=('Times New Roman', 12),
                            padx=5, pady=5,
                            fg='black',
                           command=get_info)
get_weather_button.pack(padx=10, pady=10)

exit_button = Button(app,
                    text="Exit",
                    font=('Times New Roman', 10),
                    padx=10, pady=5,
                    fg='black',
                    command=get_exit).pack()
    
if __name__ == "__main__":
    app.title("Weather Forecast")
    app.mainloop()
