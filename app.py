from flask import Flask, render_template, request, url_for, flash, redirect #for webforms
from datetime import date, datetime #for conversion of date read from html into iso format
import mysql.connector #for storing data collected in sql db
import main #importing functions from other python file(s)

app = Flask(__name__)

#sql connection
app.config['MYSQL_USER'] = 'user_name' #set to 'root' if using default
app.config['MYSQL_HOST'] = 'host_name' #set to 'localhost' if using default
app.config['MYSQL_DB'] = 'database_name' #create a db using MySQL and change it to db's name
app.config['MYSQL_PASSWORD'] = 'your_password' #the password to user in MySQL

db_config = {
    "host": app.config['MYSQL_HOST'],
    "user": app.config['MYSQL_USER'],
    "password": app.config['MYSQL_PASSWORD'],
    "database": app.config['MYSQL_DB'],
}

try:
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor() #establishing a connection


except mysql.connector.Error as err:
    print(f"Error: {err}")


#for showing flash() message
app.config['SECRET_KEY'] = 'type_secret_key_here'  #generated using os.urandom(24).hex() - generates reandom string encoded in hexadecimal, of length 24


#to render index.html - show all templates belonging to user
@app.route('/')
def index():
    try:
    
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        query = "SELECT * FROM templates"
        cursor.execute(query)
        result_set = cursor.fetchall()
        templates = {row[0]: row[1] for row in result_set}

        return render_template('index.html', messages=templates)

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return render_template('index.html', messages={})
    
    finally:
        cursor.close()
        conn.close()


#to render template.html - show events in specified template

@app.route('/<template_id>/', methods=('GET', 'POST'))
def events(template_id):

    try: 
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        #print(cursor.execute('SHOW TABLES'))

        query2 = f"SELECT * FROM {template_id}" 
        cursor.execute(query2)

        result_set = cursor.fetchall()
        query_count = len(result_set)
        
        event_name = list(row[0] for row in result_set)
        event_desc = list(row[1] for row in result_set)
        event_colour = list(row[2] for row in result_set)
        event_time = list(row[3] for row in result_set)
        email = list(row[4] for row in result_set)

        event = {}
        for i in range(query_count):
            event["event_names"] = event_name[i]
            event["event_description"] = event_desc[i]
            event["event_colours"] = event_colour[i]
            event["event_timings"] = event_time[i]
            event["event_email"] = email[i]

        return render_template('template.html', event=event)
    
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return render_template('template.html', event={})

    finally:
        cursor.close()
        conn.close()


#to render create_template.html - form to add template as table to database
@app.route('/create_template/', methods=["GET", "POST"])
def create_template():

    if request.method == 'POST':
        template_title = request.form['templateTitle']
        template_desc = request.form['templateDescription']

        if not template_title:
            flash("Title is required!")
        elif not template_desc:
            flash("Description is required!")

        else:
            try:
                conn = mysql.connector.connect(**db_config)
                cursor = conn.cursor()
                query2 = f"INSERT INTO templates (template_name, template_desc) VALUES ('{template_title}', '{template_desc}')"
                cursor.execute(query2)
                query_to_create_table = "CREATE TABLE " + template_title +  " (Name varchar(255), Description varchar(255), startDate datetime, endDate datetime, Email varchar(255), Colour int)"
                cursor.execute(query_to_create_table)

                conn.commit()
                return redirect(url_for('index'))
            
            except mysql.connector.Error as err:
                print(f"Error: {err}")

            finally:
                cursor.close()
                conn.close()

    return render_template('create_template.html')


#to render create.html - form to add event to specified template
@app.route('/<template_id>/create10', methods=('GET', 'POST'))
def create9(template_id):

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        startdate = request.form['startdate']
        enddate = request.form['enddate']
        colour = request.form['colour']
        email = request.form['email']

        if not title:
            flash('Title is required!')
        elif not content:
            flash('Content is required!')
        elif not colour:
            flash('Colour is required!')
        elif not startdate:
            flash('Start Time is required!')
        elif not enddate:
            flash('End Time is required!')
        elif not email:
            flash('Email is required!')
        else: #if all data has been entered
            #events.append({'title': title, 'content': content, 'colour': colour, 'time': time, 'email': email})
            try:

                conn = mysql.connector.connect(**db_config)
                cursor = conn.cursor()

                '''create10 = ""
                print(create10)'''
                #cursor.execute(f"SELECT * FROM {template_id}")

                #create query to add data into sql table template
                query1 = f"INSERT INTO " + template_id + " (Name, Description, startDate, endDate, Email, Colour) values (%s, %s, %s, %s, %s, %s)"
                values = (title, content, startdate, enddate, email, colour)
                cursor.execute(query1, values) 
                conn.commit()

                return render_template('create.html')
                #return redirect(url_for('create9', template_id=template_id))

                #return render_template('create.html')

            except mysql.connector.Error as err:
                print(f"Error: {err}")

            finally:
                cursor.close()
                conn.close()


    return render_template('create.html')

#logging.basicConfig(filename='app.log', level=logging.DEBUG)


@app.route('/<template_id>/added')
def added(template_id):
    try:
        #print(template_id)
        #format = "%Y-%m-%d"
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        query = f"SELECT * FROM {template_id}"
        cursor.execute(query)
        #conn.commit()

        #cursor.execute("convert(varchar, startDate, 23)")
        #cursor.execute("convert(varchar, endDate, 23)")

        events = []

        rows = cursor.fetchall()
        #print(rows)
        for row in rows:
            event = {}
            event['summary'] = row[0]
            event['description'] = row[1]
            event['end'] = {}
            event['end']['dateTime'] = datetime.strptime(str(row[3]), "%Y-%m-%d %H:%M:%S").isoformat() + "+05:30"
            event['start'] = {}
            event['start']['dateTime'] = datetime.strptime(str(row[2]), "%Y-%m-%d %H:%M:%S").isoformat() + "+05:30"
            event['attendees'] = row[4]
            event['colorId'] = row[5]

            events.append(event)
            #sprint(event)

            main.get_event(events)
            main.add(events)

        return render_template("added.html", events=events)

    except mysql.connector.Error as err:
        print(f"Error: {err}    ")
        #return render_template("error.html")

    finally:
        cursor.close()
        conn.close()

    

cursor.close()
conn.close()
                
if __name__ == '__main__':
    app.run(debug=True)