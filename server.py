from flask import Flask, render_template, session, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_mysqldb import MySQL
#from flask_ngrok import run_with_ngrok
import pandas as pd
from werkzeug.security import check_password_hash, generate_password_hash
import re

app = Flask(__name__)
#run_with_ngrok(app)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

app.config["MYSQL_HOST"] = '127.0.0.1'
app.config["MYSQL_USER"] = 'root'
app.config["MYSQL_PASSWORD"] = ''
app.config["MYSQL_DB"] = 'crime_tracker'

mysql = MySQL(app)
app.secret_key = "SQLSquirrels" 


# Assume Officer & Common users Roles are aready created and stored in the database
def runstatement(statement, parameters=None):
    cursor = mysql.connection.cursor()
    if parameters:
        cursor.execute(statement, parameters)
    else:
        cursor.execute(statement)
    results = cursor.fetchall()
    df = ""
    if (cursor.description):
        column_names = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(results, columns=column_names)
    mysql.connection.commit()
    cursor.close()
    return df


@app.route("/")
def index():
    if 'user' not in session and 'officer' not in session:
        return redirect(url_for('login'))
    else:
        if 'officer' in session:
            return redirect(url_for('home'))
        else:
            return redirect(url_for('userhome')) 


@app.route("/home")
def home():
    if 'officer' not in session:
        return redirect(url_for('login'))
    else:
        criminals_df = runstatement("SELECT * FROM Criminals;")
        crimes_df = runstatement("SELECT * FROM Crimes;")
        user_df = runstatement("SELECT * FROM OfficerUsers WHERE Username = %s;", (session['officer'],))
        return render_template("home.html", rows=criminals_df.to_dict('records'), columns=criminals_df.columns, crime_rows=crimes_df.to_dict('records'), crime_columns=crimes_df.columns, name=user_df.iloc[0]['Last'], badge=user_df.iloc[0]['Badge'])


@app.route("/userhome")
def userhome():
    if 'user' not in session:
        return redirect(url_for('login'))
    criminals_df = runstatement("SELECT * FROM Criminals;")
    crimes_df = runstatement("SELECT * FROM Crimes;")
    user_df = runstatement("SELECT * FROM CommonUsers WHERE Username = %s;", (session['user'],))
    return render_template("userhome.html", rows=criminals_df.to_dict('records'), columns=criminals_df.columns, crime_rows=crimes_df.to_dict('records'), crime_columns=crimes_df.columns, name=user_df.iloc[0]['First'])



@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first = request.form.get("first")
        last = request.form.get("last")
        username = request.form.get("username")
        password = request.form.get("password")
        badgeNumber = request.form.get("badge_number")
        register_type = request.form.get('register_type')
       
        hashedPassword = generate_password_hash(password)
        
        if register_type == 'common_user':
            try:
                runstatement("INSERT INTO CommonUsers (Username, Password, First, Last) VALUES (%s, %s, %s, %s);", (username, hashedPassword, first, last))
                runstatement("CREATE USER %s@'localhost' IDENTIFIED BY %s;",(username, hashedPassword))
                runstatement('GRANT Common_user TO %s IDENTIFIED BY %s;',(username, hashedPassword))
                return redirect("/login")
            except Exception as e:
                return render_template('error.html', error_message=str(e))
        elif register_type == 'officer_user':
            try:
                if (checkBadge(badgeNumber)):
                    runstatement("INSERT INTO OfficerUsers (Username, Password, First, Last, Badge) VALUES (%s, %s, %s, %s, %s);", (username, hashedPassword, first, last, badgeNumber))
                    runstatement("CREATE USER %s@'localhost' IDENTIFIED BY %s;",(username, hashedPassword))
                    runstatement('GRANT Officer_user TO %s IDENTIFIED BY %s;',(username, hashedPassword))
                    return redirect("/login")
                else:
                    return render_template('error.html', error_message='Invalid badge number!')
            except Exception as e:
                return render_template('error.html', error_message=str(e))
        else:
            return render_template("register.html", message="Please select a register type.")
    else:
        return render_template("register.html")
    
# check if a badge number is valid
def checkBadge(badge_num):
    df = runstatement("SELECT badge FROM Officers")
    badge_list = df['badge'].tolist()
    return (badge_num in badge_list)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        badgeNumber = request.form.get("badge_number")
        login_type = request.form.get('login_type')
        

        if login_type == 'common_user':
            # common user login
            user_df = runstatement("SELECT * FROM CommonUsers WHERE Username = %s;", (username,))
            officerBadge = None
        elif login_type == 'officer_user':
            # officer user login, verify the badge number is valid. 
            #print("check badge", checkBadge(badgeNumber))        
            if (checkBadge(badgeNumber)):
                user_df = runstatement("SELECT * FROM OfficerUsers WHERE Username = %s;", (username,))
                if user_df.empty:
                    return render_template("login.html", message="Username not found in the OfficerUsers Table")
                officerBadge = runstatement("SELECT Badge FROM OfficerUsers WHERE Username = %s;", (username,)).iloc[0]['Badge']
                # Can not login user others' badge number                
                if badgeNumber != officerBadge:
                    return render_template("login.html", message="Invalid badge number.")
            else:
                return render_template("register.html", message="Invalid badge number.")
        else:
            return render_template("register.html", message="Please select a register type.")

        # verified as an officer user
        if (not user_df.empty and check_password_hash(user_df.iloc[0]['Password'], password) and officerBadge):
            session.clear() 
            session['officer'] = user_df.iloc[0]['Username']
            return redirect(url_for('home'))
        # verified as a common user
        if (not user_df.empty and check_password_hash(user_df.iloc[0]['Password'], password)):
            session.clear()
            session['user'] = user_df.iloc[0]['Username']
            return redirect(url_for('userhome'))
        else:
            error = "Invalid username or password."
            return render_template("login.html", message=error)
    else:
        return render_template("login.html")
    
# check if a badge number is valid
def checkBadge(badge_num):
    df = runstatement("SELECT badge FROM Officers")
    badge_list = df['badge'].tolist()
    return (badge_num in badge_list)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route("/add", methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        # Extract form data
        crime_id = request.form.get('Crime_ID', '').strip()
        criminal_id = request.form.get('criminalID', '').strip()
        classification = request.form.get('classification', '').strip()
        date_charged = request.form.get('Date_Charged', '').strip()
        status = request.form.get('Status', '').strip()
        hearing_date = request.form.get('Hearing_Date', '').strip()
        appeal_cutoff_date = request.form.get('Appeal_Cutoff_Date', '').strip()
        cr_ID = request.form.get('cr_ID', '').strip()  # Additional criminal ID 
        new_last = request.form.get('new_Last', '').strip()
        new_first = request.form.get('new_First', '').strip()
        new_street = request.form.get('new_Street', '').strip()
        new_city = request.form.get('new_City', '').strip()
        new_state = request.form.get('new_State', '').strip()
        new_zip = request.form.get('new_Zip', '').strip()
        new_phone = request.form.get('new_Phone', '').strip()
        new_v_status = request.form.get('new_V_status', '').strip()
        new_p_status = request.form.get('new_P_status', '').strip()

        # server-side validation
        if not validate_server_side(crime_id, criminal_id, classification, date_charged, status, hearing_date, 
                                    appeal_cutoff_date, cr_ID, new_last, new_first, new_street, new_city, 
                                    new_state, new_zip, new_phone, new_v_status, new_p_status):
            # If validation fails, re-render form with error message and existing inputs
            return render_template("error.html", error_message = 'Not Added, Inputs are Wrong!')

        cursor = mysql.connection.cursor()
        try:
            cursor.callproc('addCrime', (crime_id, criminal_id, classification, date_charged, status, hearing_date, appeal_cutoff_date))
            mysql.connection.commit()
            
            cr_check = runstatement("SELECT * FROM Criminals WHERE Criminal_ID = %s;", (criminal_id,))
            if cr_check.empty:
                cursor.callproc('addCriminal', (cr_ID, new_last, new_first, new_street, new_city, new_state, new_zip, new_phone, new_v_status, new_p_status))
                mysql.connection.commit()

            return render_template('action_success.html', message = 'The Crime was added to the database!')
        except Exception as e:
            mysql.connection.rollback()
            return render_template('error.html', error_message=str(e))
        finally:
            cursor.close()
            return render_template('action_success.html', message='The Crime was added to the database!')
    else:
        return render_template("add.html")

def validate_server_side(*args): #server side checking inputs
    regex_date = re.compile(r'^\d{4}-\d{2}-\d{2}$')
    if len(args[2]) > 1:  # classification
        return False
    if not regex_date.match(args[3]) or not regex_date.match(args[5]) or not regex_date.match(args[6]):  # date fields
        return False
    if len(args[4]) > 2:  # status
        return False
    if args[1] != args[7]:  # criminal_id vs cr_ID
        return False
    if len(args[8]) > 15 or len(args[9]) > 10:  # last and first name
        return False
    if len(args[10]) > 30 or len(args[11]) > 20:  # street and city
        return False
    if len(args[12]) > 2:  # state
        return False
    if len(args[13]) != 5:  # zip
        return False
    if len(args[14]) != 10:  # phone
        return False
    if len(args[15]) > 1 or len(args[16]) > 1:  # v_status, p_status
        return False
    return True

@app.route('/update', methods=['GET', 'POST'])
def update():

    if 'officer' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        selected_instance = request.form.get('selected_instance')
        
        # Split the value_string into individual values
        if selected_instance:
            Crime_ID, Criminal_ID, classification, date_charged, status, hearing_date, appeal_cut_date = selected_instance.split(',')
            return render_template('update.html', id=Criminal_ID, classification= classification, date_charged = date_charged, status=status, hearing_date=hearing_date, appeal_cut_date=appeal_cut_date )
        else:
            return render_template('error.html', error_message="No instance selected")
    else:
        return render_template('error.html', error_message= "Unsupported Request Method")


@app.route('/updated', methods=['POST'])
def updated():
    if request.method == 'POST':
        # Get inputs from the user
        new_class = request.form['new_classification']
        criminal_id = request.form['criminal_id']
        new_date_charged = request.form['new_date_charged']
        new_status = request.form['new_status']
        new_hearing_date = request.form['new_hearing_date']
        new_appeal_cut_date = request.form['new_appeal_cut_date']

        # Update the database
        cur = mysql.connection.cursor()
        try:
            cur.callproc('updateClassfication', (new_class, criminal_id))
            mysql.connection.commit()
            cur.callproc('updateDateCH', (new_date_charged, new_hearing_date, criminal_id))
            mysql.connection.commit()
            cur.callproc('updateStatus', (new_status, criminal_id))
            mysql.connection.commit()
           
            cur.callproc('updateAppealCutDate',(new_appeal_cut_date, criminal_id))
            mysql.connection.commit()
            
        except Exception as e:
            error_message = str(e)
            return render_template('error.html', error_message=error_message)
          
        finally:
            cur.close()
            return render_template('action_success.html',message="The record has been updated in the database!")

@app.route('/search')
def search():
    if 'user' in session:
        return render_template('user_search.html')
    elif 'officer' in session:
        return render_template('search.html')
    else:
        return redirect(url_for('login'))

@app.route('/searchresult', methods=['GET'])
def searchresult():
    query = request.args.get('query')
    search_type = request.args.get('search_type')
    cur = mysql.connection.cursor()
    try:
        if search_type == 'criminal':
            # Search by criminal
            cur.callproc('searchCriminal',(query,))
            results = cur.fetchall()
            df = "" 
            if (cur.description):
                column_names = [desc[0] for desc in cur.description]
                df = pd.DataFrame(results, columns=column_names)
            cur.close()

            if 'officer' in session:
                return render_template('criminal_search_results.html', search_results=df.to_dict('records'))
            elif 'user' in session:
                return render_template("user_criminal_search_results.html", search_results=df.to_dict('records'))
            else:
                return redirect(url_for('login'))

        elif search_type == 'officer':
            # Search by officer
            cur.callproc('searchProbationOfficer',(query,))
            results = cur.fetchall()
            df = "" 
            if (cur.description):
                column_names = [desc[0] for desc in cur.description]
                df = pd.DataFrame(results, columns=column_names)
            cur.close()
            if ('officer' in session):
                return render_template('officer_search_results.html', search_results=df.to_dict('records'))
            elif ('user' in session):
                return render_template('user_officer_search_results.html', search_results=df.to_dict('records'))
            else:
                return redirect(url_for('login'))
            
        elif search_type == 'badge_num':
            # search by officers name to get badge number, one officer at a time
            if 'officer' in session:
                #print("OFFICER IN SESSION!")
                cur.execute("SELECT searchCrimeOfficer(%s)", (query,))
                badge = cur.fetchall()[0][0]
                #print("RESULT:", badge)
                cur.close()

                return render_template('badge_search_results.html', badge =badge)
            else:
                return redirect(url_for('login'))
        else:
            if 'user' in session:
                return render_template('user_error.html', error_message='Invalid search type')
            else:
                return render_template('error.html', error_message='Invalid search type')
               
        
    except Exception as e:
        if 'user' in session:
            return render_template('user_error.html', error_message= "Invalid Search. Try another search.")
        elif 'officer' in session:
            return render_template('error.html', error_message="Invalid Search. Try another search.")

@app.route('/delete', methods=['GET', 'POST'])
def delete():
    if 'officer' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        selected_instance = request.form.get('selected_instance')
    
    if selected_instance:
        crime_id = selected_instance.split(',')[0] 
        #print(crime_id)
    cursor = mysql.connection.cursor()
    try:
        cursor.callproc('deleteCrime', (crime_id,))
        mysql.connection.commit()
        cursor.close()
        return render_template('action_success.html', message="Selected row was successfully deleted!")
    except Exception as e:
        mysql.connection.rollback()
        return render_template('error.html', error_message="Selected row could not be deleted.") #make a separate error page for this

if __name__ == '__main__':
    #app.run(debug=True)
    app.run(port=5002)
