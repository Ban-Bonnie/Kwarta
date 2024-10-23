from flask import Flask, redirect, render_template, request, url_for,flash
from flask_mysqldb import MySQL
from datetime import datetime
import string, random, os, math

class Kwarta:
    def __init__(self, name):
        self.app = Flask(name)

        self.account = ()
        self.historyTuple = ()
        

        self.app.config['MYSQL_HOST'] = "localhost"
        self.app.config['MYSQL_USER'] = "root"
        self.app.config['MYSQL_PASSWORD'] = ""
        self.app.config['MYSQL_DB'] = "kwarta"
        self.app.secret_key = os.urandom(24)
        
        self.mysql = MySQL(self.app)

    def refreshAccounts(self):
        cursor = self.mysql.connection.cursor()
        cursor.execute("SELECT * FROM accounts WHERE userId = %s", (self.account[0],))
        self.account = cursor.fetchone()


        cursor.execute('SELECT * FROM tbl_transactions WHERE userId = %s', (self.account[0],))
        self.historyTuple = cursor.fetchall()
        

        cursor.close()

    def fetchMonthlyCount(self,type):
        cursor = self.mysql.connection.cursor()
        months = [f"{i:02}" for i in range(1, 13)]
        count = []

        if type=="admin_revenue_growth":
            for month in months:
                cursor.execute("SELECT SUM(fee) FROM tbl_transactions WHERE date LIKE %s;",(f'2024-{month}-%', ))
                x = (cursor.fetchone()[0])
                if x:
                    count.append(x)
                else: count.append(0)
        
        elif type=="admin_transaction_volume":
            for month in months:
                cursor.execute("SELECT COUNT(*) FROM tbl_transactions WHERE date LIKE %s AND type <> %s;",(f'2024-{month}-%','Receive' ))
                x = (cursor.fetchone()[0])
                if x:
                    count.append(x)
                else: count.append(0)
        
        elif type=="admin_user_growth":
            for month in months:
                cursor.execute("SELECT COUNT(*) FROM accounts WHERE date_joined LIKE %s;",(f'2024-{month}-%', ))
                x = (cursor.fetchone()[0])
                if x:
                    count.append(x)
                else: count.append(0)
        
        elif type=="admin_monthly_transaction_amount":
            for month in months:
                cursor.execute("SELECT SUM(total_amount) FROM tbl_transactions WHERE date LIKE %s",(f'2024-{month}-%', ))
                x = (cursor.fetchone()[0])
                if x:
                    count.append(x)
                else: count.append(0)
        
        
        else:
            for month in months:
                cursor.execute("SELECT SUM(fee) FROM tbl_transactions WHERE type = %s AND date LIKE %s;",(type,f'2024-{month}-%', ))
                x = (cursor.fetchone()[0])
                if x:
                    count.append(x)
                else: count.append(0)

        return(count)

    def generate_unique_id(self):
        current_date = datetime.now()
        date_str = current_date.strftime("%Y%m%d")
        random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        txn_id = f"TXN{date_str}{random_str}"
        return txn_id

    def amountVerifier(self, amount):
        if(float(amount)<=0):
            print("Amount cannot be less than 1")
            return False
        else: return(True)

    def feeCalculator(self,amount):
        amount = float(amount)
        fee = float(amount * 0.02)
        fee = math.ceil(fee)
        return fee if fee >= 5 else 5

    def fetchDate(self):
        date = datetime.now().strftime('%Y-%m-%d')
        return date
    
    def increment_total_transaction(self,userId):
        cursor = self.mysql.connection.cursor()
        try:    
            cursor.execute("UPDATE accounts SET total_transactions = total_transactions + 1 WHERE userId = %s;",
                           (userId,))
        except: print("Something went wrong")
        self.mysql.connection.commit()
        cursor.close()

    def recordTransaction(self, type, sender, merchant, merchantID, purchase, rawAmount, fee):
        txn = self.generate_unique_id()            # Generate transaction ID
        date = self.fetchDate()                    # Fetch Current Date
        userId = self.account[0]
        rawAmount = float(rawAmount)
        total_amount = rawAmount + fee

        cursor = self.mysql.connection.cursor()
        
        try:
            if type == "Bank Transfer":
                cursor.execute(
                    "INSERT INTO tbl_transactions (userid, txn, type, payee, merchant, purchase, amount, fee, total_amount, date) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    (userId, txn, type, sender, merchant, purchase, rawAmount, fee, total_amount, date))
                self.increment_total_transaction(userId)
                self.recordFees(type, fee)

            elif type == "Game Topup":
                cursor.execute(
                    "INSERT INTO tbl_transactions (userid, txn, type, payee, merchant, purchase, amount, fee, total_amount, date) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    (userId, txn, type, sender, merchant, purchase, rawAmount, fee, total_amount, date))
                self.increment_total_transaction(userId)
                self.recordFees(type, fee)

            elif type == "Load":
                cursor.execute(
                    "INSERT INTO tbl_transactions (userid, txn, type, payee, merchant, purchase, amount, fee, total_amount, date) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    (userId, txn, type, sender, merchant, purchase, rawAmount, fee, total_amount, date))
                self.increment_total_transaction(userId)
                self.recordFees(type, fee)

            elif type == "Donate":
                cursor.execute(
                    "INSERT INTO tbl_transactions (userid, txn, type, payee, merchant, purchase, amount, fee, total_amount, date) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    (userId, txn, type, sender, merchant, purchase, rawAmount, fee, total_amount, date))
                self.increment_total_transaction(userId)
                self.recordFees(type, rawAmount)  # Use rawAmount for donations

            elif type == "Bills Payment":
                cursor.execute(
                    "INSERT INTO tbl_transactions (userid, txn, type, payee, merchant, purchase, amount, fee, total_amount, date) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    (userId, txn, type, sender, merchant, purchase, rawAmount, fee, total_amount, date))
                self.increment_total_transaction(userId)

                self.recordFees(type, fee)

            elif type == "Send":
                total_amount = fee + rawAmount
                cursor.execute(
                    "INSERT INTO tbl_transactions (userid, txn, type, payee, merchant, purchase, amount, fee, total_amount, date) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    (userId, txn, "Send", sender, merchant, purchase, rawAmount, fee, total_amount, date))
                
                cursor.execute(
                    "INSERT INTO tbl_transactions (userid, txn, type, payee, merchant, purchase, amount, fee, total_amount, date) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    (merchantID, txn, "Receive", sender, merchant, purchase, rawAmount, 0, rawAmount, date))

                self.increment_total_transaction(userId)
                self.recordFees(type, fee)

            elif type == "Recharge":
                cursor.execute(
                    "INSERT INTO tbl_transactions (userid, txn, type, payee, merchant, purchase, amount, fee, total_amount, date) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    (merchantID, txn, type, sender, merchant, purchase, rawAmount, fee, rawAmount, date))
                
                self.increment_total_transaction(userId)
                self.recordFees(type, fee)

            else:
                print("Transaction Type is not valid")
                return  # Exit the method if the transaction type is invalid

            self.recordTransactionCount(type,merchant,purchase)

            self.refreshAccounts()

            self.mysql.connection.commit()

        except Exception as e:
            self.mysql.connection.rollback()  # Rollback on error
            print(f"An error occurred while recording the transaction: {e}")
        

        finally:
            cursor.close()  # Ensure cursor is closed regardless of success or error

    def recordFees(self, type, amount):
        cursor = self.mysql.connection.cursor()
        if type == "Donate":
            try:
                #add fee revenue to record
                cursor.execute("UPDATE admin_dashboard SET amount = amount + %s WHERE id = %s;",(amount,2))
                #add transaction count for this type of transaction
                cursor.execute("UPDATE service_revenue SET total_transactions = total_transactions + 1 WHERE name = %s",
                               (type,))
                
                self.mysql.connection.commit()
            except Exception as e:
                print(f"An error in type Donate  occurred: {e}")

        else:
            print(f"attempt to update revenues for {type}")
            try:
                #add fee revenue to record of this type
                cursor.execute("UPDATE service_revenue SET total_revenue = total_revenue + %s WHERE name = %s", (amount, type))
                #add fee revenue to overall record 
                cursor.execute("UPDATE admin_dashboard SET amount = amount + %s WHERE id = %s",(amount,1))
                #add transaction count for this type of transaction 
                cursor.execute("UPDATE service_revenue SET total_transactions = total_transactions + 1 WHERE name = %s",
                               (type,))
                self.mysql.connection.commit()
            except Exception as e:
                
                print(f"An error occurred in incurring fees for {type}: {e}")
        cursor.close()

    def recordTransactionCount(self, type, merchant, purchase):
        cursor = self.mysql.connection.cursor()
        if type == 'Bills Payment':
            try:
                print(f"the name is {purchase}")
                cursor.execute("UPDATE transaction_count SET transactions = transactions + 1 WHERE name = %s",
                                (purchase,))
                self.mysql.connection.commit()

            except Exception as e:
                print(f"Error recording count for Bills: {e}")
        
        elif type == "Game Topup":
            try:
                print(f"the name is {merchant}")
                cursor.execute("UPDATE transaction_count SET transactions = transactions + 1 WHERE name = %s",
                                (merchant,))
                self.mysql.connection.commit()

            except Exception as e:
                print(f"Error recording count for Game: {e}")
        
        elif type == "Load":
            try:
                print(f"the name is {merchant}")
                cursor.execute("UPDATE transaction_count SET transactions = transactions + 1 WHERE name = %s",
                                (merchant,))
                self.mysql.connection.commit()

            except Exception as e:
                print(f"Error recording count for Load: {e}")

        elif type == "Donate":
            try:
                print(f"the name is {merchant}")
                cursor.execute("UPDATE transaction_count SET transactions = transactions + 1 WHERE name = %s",
                                (merchant,))
                self.mysql.connection.commit()

            except Exception as e:
                print(f"Error recording count for Donate: {e}")

        else:
            print("Else Block reached for Record Transaction Count")

    def deposit(self, price, user):
        price = float(price)

        cursor = self.mysql.connection.cursor()    
        cursor.execute("UPDATE accounts SET balance = balance+%s WHERE userId=%s",
                        (price,user[0]))
        self.mysql.connection.commit()
        cursor.close()
        return True
    
    def withdraw(self,price,user):
        price = float(price)

        cursor = self.mysql.connection.cursor()
        if(user[4]<price):
            flash('Insufficient Funds.', 'danger')#alert
            print("Insufficient balance")
            return False
        else:
            flash('Purchased from:', 'success')
            cursor.execute("UPDATE accounts SET balance = balance-%s WHERE userId=%s",
                            (price,user[0]))
            self.mysql.connection.commit()
            cursor.close()
            return True

    def createAgingAccountData(self,userid):
        cursor = self.mysql.connection.cursor()
        try:
            cursor.execute("INSERT INTO aging_accounts (userid,last_login_date, days_offline) VALUES(%s,%s,0)",(userid,self.fetchDate))
            self.mysql.connection.commit()
            print("Successfully created aging account data for user")
        except Exception as e:
            print(f"Error creating data for userid {userid} : {e}")
        cursor.close()

    def record_user_login(self, userid):
        date = self.fetchDate()
        cursor = self.mysql.connection.cursor()
        cursor.execute("UPDATE aging_accounts SET last_login_date = %s WHERE userid = %s",(date,userid))
        self.mysql.connection.commit()
        cursor.close()

    def updateAgingAccounts(self,userid):
        dateNow = self.fetchDate()
        print(f"date now is {dateNow}")
        cursor = self.mysql.connection.cursor()
        cursor.execute("SELECT * FROM aging_accounts")
        accountsTuple =  cursor.fetchall()
        print(accountsTuple)

        for i in accountsTuple:
            tupleUserId = i[0]
            tupleUserLastLoginDate= i[1]
            

            if tupleUserId == userid:
                cursor.execute("UPDATE aging_accounts SET days_offline = 0 WHERE userid = %s",(userid,))
                self.mysql.connection.commit()

            else:
                try:
                    #Get Difference of Date now from last login fate
                    cursor.execute("SELECT DATEDIFF(%s, last_login_date) AS days_offline FROM aging_accounts WHERE userid = %s;",(dateNow,tupleUserId))
                    daysOffline = cursor.fetchone()
                    
                    cursor.execute("UPDATE aging_accounts SET days_offline = %s WHERE userid = %s;",
                                    (daysOffline,tupleUserId))
                    self.mysql.connection.commit()
                except Exception as e:
                    print(f"Error setting days offline for user {tupleUserId}")

    def run(self):
        self.app.run(debug=True)
        

    def setup_route(self):
        @self.app.route("/")
        def home():
            return render_template("homepage.html")

        @self.app.route("/dashboard")
        def dashboard():
            return render_template("dashboard.html", account=self.account, history=self.historyTuple)
        
        @self.app.route("/transaction")
        def transaction():
            self.refreshAccounts()
            return render_template("Transac.html", history=self.historyTuple)
        
        @self.app.route("/TopUp")
        def topup():

            return render_template("TopUp.html")
        
        @self.app.route("/Bills")
        def Bills():
            return render_template("Bills.html")
        
        @self.app.route("/Load")
        def Load():
            return render_template("Load.html")
        
        @self.app.route("/Donate")
        def Donate():
            return render_template("Donate.html")

        @self.app.route("/Profile")
        def Profile():
            return render_template("Profile.html", account=self.account, history=self.historyTuple)
        
        @self.app.route("/Admin")
        def admin():

            #Data for revenue, donations, total users
            adminData = []
            cursor = self.mysql.connection.cursor()
            cursor.execute("SELECT * FROM admin_dashboard")
            admin_dashboard = cursor.fetchall()
            for i in admin_dashboard:
                adminData.append(i[-1])
            
            cursor.execute("SELECT COUNT(*) FROM accounts")
            adminData.append(cursor.fetchone()[0])

            #Data for Top users
            cursor.execute("SELECT name, total_transactions FROM accounts ORDER BY total_transactions DESC LIMIT 5;")
            topUsers = cursor.fetchall()
            
            #Data for Active/Inactive users
            userActiveStatus = []
            cursor.execute("SELECT COUNT(*) FROM aging_accounts WHERE days_offline < 5")
            userActiveStatus.append(cursor.fetchone()[0])

            cursor.execute("SELECT COUNT(*) FROM aging_accounts WHERE days_offline > 4")
            userActiveStatus.append(cursor.fetchone()[0])

            #Data for Transaction Volume Over Time
            transactionVolume = self.fetchMonthlyCount("admin_transaction_volume")
            
            #Data for revenue growth
            revenueGrowth = self.fetchMonthlyCount("admin_revenue_growth")
            
            #Data for User growth
            userGrowth = self.fetchMonthlyCount("admin_user_growth")

            #Data for  monthly transaction amount
            transactionAmount = self.fetchMonthlyCount("admin_monthly_transaction_amount")

            cursor.close()
            return render_template("/Admin.html",adminData=adminData, topUsers=topUsers,
                                    users=userActiveStatus, transactionVolume = transactionVolume,
                                    revenueGrowth = revenueGrowth, userGrowth=userGrowth,
                                    transactionAmount=transactionAmount)
        
        @self.app.route("/AdminBills")
        def adminBills():
            cursor = self.mysql.connection.cursor()
            #fetch revenue
            cursor.execute("SELECT * FROM service_revenue WHERE name = %s",("Bills Payment",))
            revenue = cursor.fetchone()
            
            #fetch game data
            cursor.execute("SELECT * FROM transaction_count WHERE type = %s",("Bills",))
            billsData = cursor.fetchall()

            #data for revenue graph
            monthlyRevenues = self.fetchMonthlyCount("Bills Payment")
            cursor.close()

            return render_template("/AdminBills.html",billsData = billsData, revenue=revenue, monthlyRevenue=monthlyRevenues)
        
        @self.app.route("/AdminDonations")
        def adminDonations():
            cursor = self.mysql.connection.cursor()
            donations = []
            cursor.execute("SELECT total_transactions FROM service_revenue WHERE name = %s",("Donate",))
            Donors = cursor.fetchone()
            donations.append(Donors[0])

            cursor.execute("SELECT amount FROM admin_dashboard WHERE name = %s",("Donations",))
            totalDonations = cursor.fetchone()
            donations.append(totalDonations[0])
            
            cursor.execute("SELECT * FROM transaction_count WHERE type = %s",("Donate",))
            donateData = cursor.fetchall()
            print(donateData)
            print(donations)


            cursor.close()
            return render_template("/AdminDonations.html", donations = donations,donateData = donateData )
        
        @self.app.route("/AdminLoad")
        def adminLoad():
            cursor = self.mysql.connection.cursor()
            #fetch revenue
            cursor.execute("SELECT * FROM service_revenue WHERE name = %s",("Load",))
            revenue = cursor.fetchone()
            
            #fetch game data
            cursor.execute("SELECT * FROM transaction_count WHERE type = %s",("load",))
            loadData = cursor.fetchall()
            
            #Data for revenue graph
            monthlyRevenues = self.fetchMonthlyCount("load")

            cursor.close()

            return render_template("/AdminLoad.html",revenue = revenue, loadData=loadData, monthlyRevenue=monthlyRevenues)
        
        @self.app.route("/AdminTopUp")
        def adminTopup():
            cursor = self.mysql.connection.cursor()
            #fetch revenue
            cursor.execute("SELECT * FROM service_revenue WHERE name = %s",("Game Topup",))
            revenue = cursor.fetchone()
            
            #fetch game data
            cursor.execute("SELECT * FROM transaction_count WHERE type = %s",("Game Topup",))
            gameData = cursor.fetchall()

            #Data for revenue graph
            monthlyRevenues = self.fetchMonthlyCount("Game Topup")


            cursor.close()
            return render_template("/AdminTopUp.html", revenue=revenue,gameData=gameData,monthlyRevenue = monthlyRevenues)



        #Processes 
        @self.app.route("/login_process", methods=['POST', 'GET'])
        def login_process():
            if request.method == 'POST':
                userBox = request.form["username"]
                passBox = request.form["password"]

                cursor = self.mysql.connection.cursor()

                # Fetch the account based on username and password
                cursor.execute("SELECT * FROM accounts WHERE username = %s AND password = %s", (userBox, passBox))
                account = cursor.fetchone()
     
                if account is None:
                    #try admin login
                    cursor.execute("SELECT * FROM admin_accounts WHERE username = %s AND password = %s",(userBox, passBox))
                    isAdmin = cursor.fetchone()

                    if isAdmin:
                        return redirect(url_for("admin"))

                    cursor.execute("SELECT * FROM accounts WHERE username = %s ",(userBox,))
                    user = cursor.fetchone()

                    if user:
                        flash("Incorrect password")
                        cursor.close()
                        return redirect(url_for("home") + "#LoginForm")  
                    else:
                        flash("User does not exist")
                        cursor.close()
                        return redirect(url_for("home") + "#LoginForm")  
                else:
                    #Saving user data in backend
                    self.account = account

                    #Saving user transactions in backend
                    cursor.execute('SELECT * FROM tbl_transactions WHERE userid = %s', (self.account[0],))
                    self.historyTuple = cursor.fetchall()
                    cursor.close()

                    #add user login record to db
                    self.record_user_login(self.account[0])

                    #update aging accounts here
                    self.updateAgingAccounts(self.account[0])
                    
                    return render_template("dashboard.html", account=self.account, history=self.historyTuple)

        @self.app.route("/registration_process", methods=['POST', 'GET'])
        def registration_process():
            if request.method == 'POST':
                name = request.form["name"]
                username = request.form["username"]
                phone = request.form["phone"]
                password = request.form["password"]
                confirmPassword = request.form["confirmPassword"]

                #flags to check if account credential validity
                cursor = self.mysql.connection.cursor()
                cursor.execute('SELECT username FROM accounts WHERE username = %s', (username,))
                userExists = cursor.fetchone()
                if userExists:
                    print('Username already taken')
                    return redirect("/")
                
                if password != confirmPassword:
                    print('Password does not match')
                    return redirect("/")
                
                #registering account to accounts table
                date = self.fetchDate()
                cursor.execute("INSERT INTO accounts(username, password, name, balance, phone, date_joined) VALUES (%s, %s, %s, 0, %s,%s)",
                               (username, password, name, phone, date))
                self.mysql.connection.commit()
                
                #Fetching user's id            
                cursor.execute("SELECT userid FROM accounts WHERE username = %s",(username,))
                userId = cursor.fetchone()
                print(f"newly registered account's user ID is {userId}")
                self.createAgingAccountData(userId)

                print(f"Successfully registered user {username}")
                cursor.close()
                return redirect("/")

        @self.app.route('/send_process', methods=['POST', 'GET'])
        def send():
            if request.method == 'POST':
                receiver = request.form['receiver']                 
                amount = request.form['amount']                
                password = request.form['password']
                
                amount = float(amount)

                fee = self.feeCalculator(amount)
                print(f"total fee for send is {fee}")
            

                #amount should not be negative or equal to 0
                if self.amountVerifier(amount) == False:
                    flash('Please enter a valid deposit amount.', 'danger')#alert
                    return redirect(url_for("dashboard"))

                #send amount cannot be more than your balance
                if self.account[4] < float(amount):
                    flash('Insufficient Funds.', 'danger')#alert
                    print("Insufficient Funds.")
                    return redirect(url_for('dashboard'))

                #check if password matches and fetch receiver's row from db
                if password == self.account[2]: 
                    cursor = self.mysql.connection.cursor()
                    cursor.execute('SELECT * FROM accounts WHERE username = %s or phone = %s', (receiver,receiver))
                    receiver1 = cursor.fetchone()

                    #Prevents user from sending to self
                    if receiver1 == self.account:
                        flash('Cannot send to self!', 'danger')
                        print("Cannot send to self")
                        return redirect(url_for("dashboard"))

                    if receiver and receiver1:
                        #add balance to receiver
                        cursor.execute('UPDATE accounts SET balance = balance + %s WHERE username = %s ', (amount, receiver))
                        #deduct balance from sender
                        cursor.execute('UPDATE accounts SET balance = balance - %s WHERE userid = %s', (amount+fee, self.account[0]))
                        self.mysql.connection.commit()

                        #record the transaction
                        self.recordTransaction("Send", self.account[3], receiver1[3], receiver1[0], "Send Balance", amount,fee)
                        
                        flash('Successfully sent!', 'success')#alert
                        return redirect(url_for('dashboard'))
                    else:
                        flash('User does not exist!', 'danger')
                        print("User does not exist")
                        return redirect(url_for('dashboard'))
                else: 
                    flash('Incorrect password!', 'danger', )
                    print("Incorrect password")    
                return redirect(url_for('dashboard'))

        @self.app.route("/recharge_process", methods=["POST", "GET"])
        def recharge_process():
            if request.method=="POST":
                amount = float(request.form["amount"])
                name = request.form["name"]
                fee = self.feeCalculator(amount)

                #disable negative and 0 amounts
                if float(amount)<=0:
                    flash('Please enter a valid deposit amount.', 'danger')#alert
                    print("amount cannot be less than 1")
                    return redirect(url_for("dashboard"))

                cursor = self.mysql.connection.cursor()
                cursor.execute("UPDATE accounts SET balance = balance+%s WHERE userid=%s", (amount,self.account[0]))
                self.mysql.connection.commit()
                cursor.close()

                self.recordTransaction("Recharge", name, self.account[3] , self.account[0], "Bank Recharge", amount, fee)

                
                flash('Successfully recharged!', 'success')#alert
                return redirect(url_for("dashboard"))

        @self.app.route("/bankTransfer_process", methods=["POST", "GET"])
        def bankTransfer_process():
            if request.method=="POST":
                bank= request.form["bank"]
                accountName = request.form["accountName"]
                amount= float(request.form["amount"])
                password = request.form["password"]

                fee = self.feeCalculator(amount)

                if self.amountVerifier(amount) == False:
                    flash('Please enter a valid deposit amount.', 'danger')#alert
                    return redirect(url_for("dashboard"))

                if (self.account[4] < amount+fee):
                    flash('Insufficient Funds.', 'danger')
                    print("not enough balance")
                    return redirect(url_for('dashboard'))

                if password == self.account[2]:
                    cursor = self.mysql.connection.cursor()
                    cursor.execute("UPDATE accounts SET balance = balance - %s WHERE userid = %s",(amount+fee,self.account[0]))
                    self.mysql.connection.commit()
                    cursor.close()

                    self.recordTransaction("Bank Transfer", self.account[3], accountName ,self.account[0], "Bank Transfer", amount, fee)
                    
                    flash('Successfully sent!', 'success')#alert
                    return redirect("/dashboard")

                else:
                    flash('Incorrect password!', 'danger', )
                    print("Password does not match")
                return redirect("/dashboard")
            
        @self.app.route("/gameTopup_process", methods=["POST", "GET"])
        def gameTopup_process():
            if request.method=="POST":
                game = request.form["game"]
                success = True 
                

                if game == "minecraft":
                    email = request.form["email"]
                    package = request.form["package"]
                   
                    price, Minecoins = package.split("|")
                    fee = self.feeCalculator(price)

                    #data type conversions
                    price = float(price)
                    total = price+fee

                    self.amountVerifier(price)

                    #Deduct Price
                    if(self.withdraw(total, self.account)):

                        print(f"Successfully withdrawn {total}")
                        self.recordTransaction("Game Topup", self.account[3], "Minecraft", self.account[0], f"{Minecoins} Minecoins", price, fee)
                        
                        print(email,price, Minecoins)

                    else: 
                        print(f"Failed to withdraw {price}")

                
                elif game == "genshin":
                    
                    uid = request.form["uid"]
                    server = request.form["server"]
                    package = request.form["genshinOptions"]
                    
                    price, package = package.split("|")
                    price = float(price)

                    if price != 280:
                        package = f"{package} Diamonds"

                    fee = self.feeCalculator(price)
                    total = fee+price
                    if(self.withdraw(total, self.account)):
                        print(f"Successfully withdrawn {price}")
                        print(uid,server,price, package)
                        self.recordTransaction("Game Topup", self.account[3], "Genshin Impact", self.account[0], package, price, fee)
                    else:
                        print(f"Failed to withdraw {price}")


                elif game == "league of legends":
                    riotId = request.form["riotId"]
                    price = request.form["lolOptions"]
                    
                    price, rp = price.split("|")  
                    price = float(price)

                    fee = self.feeCalculator(price)
                    total = fee+price
                    if(self.withdraw(total, self.account)):
                        print(f"Successfully withdrawn {total}")
                        self.recordTransaction("Game Topup", self.account[3], "League of Legends", self.account[0], f"{rp} RP", price, fee)
                        
                        print(riotId,price)
                    else:
                        print(f"Failed to withdraw {total}")
                    
                               
                elif game == "CODM":
                    playerID = request.form["playerId"]
                    price = request.form["codmOptions"]

                    price = float(price)

                    fee = self.feeCalculator(price)
                    total = fee+price

                    if(self.withdraw(total, self.account)):
                        print(f"Successfully withdrawn {total}")
                        self.recordTransaction("Game Topup", self.account[3], "Call of Duty Mobile", self.account[0], f"{int(price)} Garena Shellls", price, fee)
                        print(playerID,price)

                    else:
                        print(f"Failed to withdraw {total}")
                    
             
                elif game == "valorant":
                    playerID = request.form["riotId"]
                    package = request.form["valorantOptions"]

                    price, currency = package.split("|")

                    price = float(price)
                    fee = self.feeCalculator(price)
                    total = fee+price

                    if(self.withdraw(total, self.account)):
                        print(f"Successfully withdrawn {total}")
                        self.recordTransaction("Game Topup", self.account[3], "Valorant", self.account[0], f"{currency} VP", price, fee)
                        
                        print(playerID,price,currency)

                    else: print(f"Failed to withdraw {total}")

                
                return redirect(url_for("dashboard"))
                
                
        
        @self.app.route("/load_process", methods=["POST", "GET"])
        def load_process():
            if request.method == "POST":
                provider = request.form.get('provider')
                phoneNumber = request.form.get('phoneNumber')
                predefined_amount = request.form.get('predefinedAmount')
                custom_amount = request.form.get('customAmount')

                if predefined_amount:
                    amount = predefined_amount
                elif custom_amount:
                    amount = custom_amount
                else:
                    return redirect(url_for('load_process'))

                fee = 5
                total = float(amount)+fee 

                print(phoneNumber, provider, amount)

                if self.withdraw(total,self.account):
                    self.recordTransaction("Load", self.account[3], provider, 0, f"{provider} {amount}", amount, fee)
                    print("Successful")
                else: print("Failed")

                

            return redirect(url_for("dashboard"))

        @self.app.route("/donate_process", methods=["POST", "GET"])
        def donate_process():
            if request.method == "POST":
                name = request.form["name"]
                amount = request.form["amount"]
                email = request.form["email"]
                message = request.form["message"]
                receiver = request.form["receiver"]
                fee = 0 
                amount = float(amount)

                if(self.withdraw(amount,self.account)):
                    self.recordTransaction("Donate",self.account[3], receiver, 0,"Donation", amount, fee )

                else:
                    print("You do not have enough balance")
                
            return redirect(url_for("dashboard"))

        @self.app.route("/pay_bills_process", methods = ["POST","GET"])
        def pay_bills_process():
            if request.method=="POST":
                merchant = request.form["merchant"]
                amount = float(request.form["amount"])
                fee = self.feeCalculator(amount)
                sender = self.account[3]
                userid = self.account[0]
                total = fee+amount

                if merchant == "Electric Utility": 
                    accountNumber = request.form["accountNumber"]
                    provider = request.form["provider"]
                    

                    if self.withdraw(total, self.account):
                        self.recordTransaction("Bills Payment",sender,provider, userid,"Electric Bill",amount,fee)
                        print(f"successful {merchant} payment")
                    else: print("Error with user balance")
 
                elif merchant == "Healthcare":
                    hospital = request.form["hospital"]
                    patientID = request.form["patientID"]
                    
                    
                    if self.withdraw(total, self.account):
                        self.recordTransaction("Bills Payment",sender,hospital, userid,"Healthcare Bill",amount,fee)
                        print(f"successful {merchant} payment")
                    else: print("Error with user balance")
   
                elif merchant == "Telecom":
                    accountNumber = request.form["accountNumber"]
                    provider = request.form["provider"]
                    
                    
                    if self.withdraw(total, self.account):
                        self.recordTransaction("Bills Payment",sender,provider, userid,f"{merchant} Bill",amount,fee)
                        print(f"successful {merchant} payment")
                    else: print("Error with user balance")

                elif merchant == "Credit Card":
                        name = request.form["name"]
                        cardNumber = request.form["cardNumber"]
                        expiryDate = request.form["expiryDate"]
                        cvv = request.form["cvv"]
                        
                        
                        if self.withdraw(total, self.account):
                            self.recordTransaction("Bills Payment",sender,cardNumber, userid,f"{merchant} Payment",amount,fee)
                            print(f"successful {merchant} payment")
                        else: print("Error with user balance")

                elif merchant == "Water":
                        name = request.form["name"]
                        accountNumber = request.form["accountNumber"]
               
                        if self.withdraw(total, self.account):
                            self.recordTransaction("Bills Payment",sender,name, userid,f"{merchant} Bill",amount,fee)
                            print(f"successful {merchant} payment")
                        else: print("Error with user balance")

                elif merchant == "Internet":
                        number = request.form["number"]
                        name =request.form["name"]
                        provider = request.form["provider"]
                        
                        if self.withdraw(total, self.account):
                            self.recordTransaction("Bills Payment",sender,provider, userid,f"{merchant} Bill",amount,fee)
                            print(f"successful {merchant} payment")
                        else: print("Error with user balance")

                elif merchant == "Loan":
                    loanAccountNumber = request.form["loanAccountNumber"]
                    name = request.form["name"]
                    provider = request.form["provider"]

                    if self.withdraw(total,self.account):
                        self.recordTransaction("Bills Payment",sender,provider, userid,f"{merchant} Payment",amount,fee)
                        print(f"successful {merchant} payment")
                    else: print("Error with user balance")
                
                elif merchant == "Insurance":
                    policyNumber = request.form["policyNumber"]
                    name = request.form["name"]
                    provider = request.form["provider"]

                    if self.withdraw(total,self.account):
                        self.recordTransaction("Bills Payment",sender,provider, userid,f"{merchant} Payment",amount,fee)
                        print(f"successful {merchant} payment")
                    else: print("Error with user balance")

            return redirect(url_for('dashboard'))

        @self.app.route("/update_profile_process", methods=["POST"])
        def update_profile_process():
            if request.method == 'POST':
                update = request.form["update"]
                userid = self.account[0]
                user_pass = self.account[2]

                cursor = self.mysql.connection.cursor()

                if update == "changeName":
                    newName= request.form["new_name"]
                    password= request.form["password"]
                    
                    if password == user_pass:
                        cursor.execute(("UPDATE accounts SET name = %s WHERE userId = %s;"),(newName, userid))
                        cursor.execute(("UPDATE tbl_transactions SET payee = %s WHERE userId = %s AND payee = %s;"),(newName, userid,self.account[3]))
                        self.mysql.connection.commit()
                        print(f"Successfully changed name to {newName}")
                    else: print("Incorrect password")
                    
                elif update == "changeNumber":
                    new_phone_number= request.form["new_phone_number"]
                    password= request.form["password"]
                    
                    if password == user_pass:
                        cursor.execute(("UPDATE accounts SET phone = %s WHERE userId = %s;"),(new_phone_number, userid))
                        self.mysql.connection.commit()
                        print(f"Successfully changed phone number to {new_phone_number}")

                    else: print("Password does not match")
                
                elif update == "changePassword":
                    current_password= request.form["current_password"]
                    new_password= request.form["new_password"]
                    confirm_new_password= request.form["confirm_new_password"]
 
                    if (user_pass == current_password) and (new_password == confirm_new_password):
                        
                        cursor.execute(("UPDATE accounts SET password = %s WHERE userId = %s;"),(new_password, userid))
                        
                        self.mysql.connection.commit()
                        print(f"Successfully changed password to {new_password}")
                cursor.close()
                self.refreshAccounts()
                return redirect(url_for("Profile"))

        @self.app.route("/delete_account_process", methods=["GET", "POST"])
        def delete_account_process():
            if request.method == "POST":
                password = request.form["password"]

                if password == self.account[2]:
                    cursor = self.mysql.connection.cursor()
                    cursor.execute("DELETE FROM aging_accounts WHERE userid = %s",(self.account[0],))
                    cursor.execute("DELETE FROM accounts WHERE userid = %s",(self.account[0],))
                    self.mysql.connection.commit()
                    print(f"Goodbye {self.account[3]}")
                    return redirect(url_for("home"))
                else:
                    print("Incorrect Password")
                    return redirect(url_for("Profile"))

# Object
x = Kwarta(__name__) 
x.setup_route()
x.run()


# make Load now button #009d63(main color)
# modals for success transactions (Game topup, Load, etc.)
# also add confirmation modals ("you are sending __ amount to user ___, click to confirm")
