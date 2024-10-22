from flask import Flask, redirect, render_template, request, url_for,flash
from flask_mysqldb import MySQL
from datetime import datetime
import string, random, os

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
        fee = float(amount * 0.02 if amount < 5000 else 100)
        return fee

    def fetchDate (self):
        date = datetime.now().strftime('%Y-%m-%d')
        return date
    
    def recordTransaction(self, type, sender, merchant, merchantID, purchase, rawAmount,fee):
        txn = self.generate_unique_id()            #Generate transaction ID
        date = self.fetchDate() #Fetch Current Date
        userId = self.account[0]
        rawAmount = float(rawAmount)
        total_amount = rawAmount + fee

        cursor = self.mysql.connection.cursor()
        
        standardType = ["Bank Transfer", "Game Topup", "Load","Donate", "Bills Payment"]
        
        if type in standardType:
            print(type)
            cursor.execute(
                "INSERT INTO tbl_transactions (userid, transaction_id, type, payee, merchant, purchase,amount,fee, total_amount,date)"
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (userId, txn, type, sender, merchant, purchase, rawAmount, fee, total_amount, date))
            self.mysql.connection.commit()
            
        elif type == "Send":
            total_amount = fee+ rawAmount
            cursor.execute(
                "INSERT INTO tbl_transactions (userid, transaction_id, type, payee, merchant, purchase,amount,fee, total_amount,date)"
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (userId, txn, "Sent", sender, merchant, purchase, rawAmount, fee, total_amount, date))

            cursor.execute(
                "INSERT INTO tbl_transactions (userid, transaction_id, type, payee, merchant, purchase,amount,fee, total_amount,date)"
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (merchantID, txn, "Received", sender, merchant, purchase, rawAmount, 0, rawAmount, date))
            self.mysql.connection.commit()

        elif type == "Recharge":
            cursor.execute(
                "INSERT INTO tbl_transactions (userid, transaction_id, type, payee, merchant, purchase,amount,fee, total_amount,date)"
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (merchantID, txn, type, sender, merchant, purchase, rawAmount, fee, rawAmount, date))
            self.mysql.connection.commit()

        

        else:
            print("Transaction Type is not valid")

        self.refreshAccounts()
        cursor.close()

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

                self.account = account

                cursor.execute('SELECT * FROM tbl_transactions WHERE userid = %s', (self.account[0],))
                self.historyTuple = cursor.fetchall()
                cursor.close()

                return render_template("dashboard.html", account=self.account, history=self.historyTuple)

        @self.app.route("/registration_process", methods=['POST', 'GET'])
        def registration_process():
            if request.method == 'POST':
                name = request.form["name"]
                username = request.form["username"]
                phone = request.form["phone"]
                password = request.form["password"]
                confirmPassword = request.form["confirmPassword"]

                cursor = self.mysql.connection.cursor()
                cursor.execute('SELECT username FROM accounts WHERE username = %s', (username,))
                userExists = cursor.fetchone()
                if userExists:
                    print('Username already taken')
                    return redirect("/")
                
                if password != confirmPassword:
                    print('Password does not match')
                    return redirect("/")
                
                date = self.fetchDate()

                cursor.execute("INSERT INTO accounts(username, password, name, balance, phone, date_joined) VALUES (%s, %s, %s, 0, %s,%s)",
                               (username, password, name, phone, date))
                self.mysql.connection.commit()
                cursor.close()
                print(f"Successfully registered user {username}")
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
                        self.recordTransaction("Game Topup", self.account[3], "Call of Duty Mobile", self.account[0], f"{float(price)} Garena Shellls", price, fee)
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
                    self.recordTransaction("Load", self.account[3], phoneNumber, 0, f"{provider} {amount}", amount, fee)
                    print("Successful")
                else: print("Failed")

                

            return redirect(url_for("dashboard"))

        @self.app.route("/donate_process", methods=["POST", "GET"])
        def donate_process():
            print("Donatee")
            if request.method == "POST":
                name = request.form["name"]
                amount = request.form["amount"]
                email = request.form["email"]
                message = request.form["message"]
                receiver = request.form["receiver"]
                fee = 0 
                amount = float(amount)

                if(self.withdraw(amount,self.account)):
                    self.recordTransaction("Donate",self.account[3], receiver, 0,f"{receiver} Donation", amount, fee )

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
                    cursor.execute("DELETE FROM accounts WHERE userid = %s",(self.account[0],))
                    cursor.execute("DELETE FROM tbl_transactions WHERE userid = %s",(self.account[0],))
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
# make tables for transactions more pleasant
# modals for success transactions (Game topup, Load, etc.)
# also add confirmation modals ("you are sending __ amount to user ___, click to confirm")
