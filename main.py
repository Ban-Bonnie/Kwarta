from flask import Flask, flash, redirect, render_template, request, url_for
from flask_mysqldb import MySQL
from datetime import datetime
import string, random

class Kwarta:
    def __init__(self, name):
        self.app = Flask(name)

        self.account = ()
        self.historyTuple = ()
        

        self.app.config['MYSQL_HOST'] = "localhost"
        self.app.config['MYSQL_USER'] = "root"
        self.app.config['MYSQL_PASSWORD'] = ""
        self.app.config['MYSQL_DB'] = "kwarta"
        
        self.mysql = MySQL(self.app)

    def refreshAccounts(self):
        cursor = self.mysql.connection.cursor()
        cursor.execute("SELECT * FROM accounts WHERE userId = %s", (self.account[0],))
        self.account = cursor.fetchone()


        cursor.execute('SELECT * FROM transactions WHERE userId = %s', (self.account[0],))
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
            print("Amount cannot be Zero or Negative.")
            return False
        else: return(True)


    def recordTransaction(self, senderName, recipientName, amount, transaction_type, senderId, recipientId):
        txn = self.generate_unique_id()
        date = datetime.now().strftime('%Y-%m-%d')

        cursor = self.mysql.connection.cursor()

        if transaction_type == "Sent":
            cursor.execute(
                "INSERT INTO transactions (date, name, amount, type, transactionid, userid) VALUES (%s, %s, %s, %s, %s, %s)",
                (date, recipientName, amount, "Sent", txn, senderId)
            )

            cursor.execute(
                "INSERT INTO transactions (date, name, amount, type, transactionid, userid) VALUES (%s, %s, %s, %s, %s, %s)",
                (date, senderName, amount, "Received", txn, recipientId)
            )
            self.mysql.connection.commit()

        elif transaction_type == "Recharge":
            cursor.execute("INSERT INTO transactions VALUES(%s,%s,%s,%s,%s,%s)",
                           (date,senderName,amount,"Recharge",txn,recipientId))
            self.mysql.connection.commit()
        
        elif transaction_type == "Bank Transfer":
            cursor.execute("INSERT INTO transactions VALUES(%s,%s,%s,%s,%s,%s)",
                           (date, senderName,amount, "Bank Transfer", txn, recipientId))
            self.mysql.connection.commit()
        
        elif transaction_type =="Game Topup":
            cursor.execute("INSERT INTO transactions VALUES(%s,%s,%s,%s,%s,%s)",
                           (date,senderName, amount, "Game Topup",txn,recipientId))
            self.mysql.connection.commit()
        
        elif transaction_type == "Load":
            cursor.execute("INSERT INTO transactions VALUES(%s,%s,%s,%s,%s,%s)",
                           (date, senderName, amount, "Load", txn, recipientId))
            self.mysql.connection.commit()

        elif transaction_type == "Donated":
            cursor.execute("INSERT INTO transactions VALUES(%s,%s,%s,%s,%s,%s)",
                           (date, recipientName, amount, "Donated", txn, recipientId))
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
            print("Insufficient balance")
            return False
        else:
            
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
                    print("Invalid username or password")
                    cursor.close()
                    return redirect(url_for("home"))

                # Debugging print statements (after checking account is not None)
                print(account[1])
                print(account[2])

                
                if account[1] != userBox or account[2] != passBox: 
                    cursor.close()
                    return redirect(url_for("home"))
                
                self.account = account

                cursor.execute('SELECT * FROM transactions WHERE userid = %s', (self.account[0],))
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
                
                cursor.execute("INSERT INTO accounts(username, password, name, balance, phone) VALUES (%s, %s, %s, 0, %s)",
                               (username, password, name, phone))
                self.mysql.connection.commit()
                cursor.close()
                print(f"Successfully registered user {username}")
                return redirect("/")
        


        @self.app.route("/update_profile", methods=["POST"])
        def update_profile():
            if request.method == 'POST':
                name = request.form.get("name")
                username = request.form.get("username")
                phone = request.form.get("phone")
                current_password = request.form.get("current_password")
                new_password = request.form.get("new_password")
                confirm_password = request.form.get("confirm_password")

                cursor = self.mysql.connection.cursor()


                if current_password:
                    cursor.execute("SELECT password FROM accounts WHERE userId = %s", (self.account[0],))
                    db_password = cursor.fetchone()

                    if db_password is None or db_password[0] != current_password:
                        print("Current password is incorrect.", "error")
                        cursor.close()
                        return redirect(url_for("Profile"))


                cursor.execute("""
                    UPDATE accounts 
                    SET name = %s, username = %s, phone = %s 
                    WHERE userId = %s """, (name, username, phone, self.account[0]))


                if new_password and new_password == confirm_password:
                    cursor.execute("UPDATE accounts SET password = %s WHERE userId = %s", (new_password, self.account[0]))

                self.mysql.connection.commit()
                cursor.close()

                print("Profile updated successfully!", "success")
                self.refreshAccounts()
                return redirect(url_for("Profile"))





        @self.app.route('/send_process', methods=['POST', 'GET'])
        def send():
            if request.method == 'POST':
                receiver = request.form['receiver']                 
                amount = request.form['amount']                
                password = request.form['password']
            

                #amount should not be negative or equal to 0
                if self.amountVerifier(amount) == False:
                    return redirect(url_for("dashboard"))

                #send amount cannot be more than your balance
                if self.account[4] < float(amount):
                    print("Insufficient Funds.")
                    return redirect(url_for('dashboard'))

                #check if password matches
                if password == self.account[2]: 
                    cursor = self.mysql.connection.cursor()
                    cursor.execute('SELECT * FROM accounts WHERE username = %s or phone = %s', (receiver,receiver))
                    receiver1 = cursor.fetchone()

                    #Prevents user from sending to self 
                    if receiver1 == self.account:
                        print("Cannot send to self")
                        return redirect(url_for("dashboard"))

                    if receiver and receiver1:
                        cursor.execute('UPDATE accounts SET balance = balance + %s WHERE username = %s ', (amount, receiver))
                        cursor.execute('UPDATE accounts SET balance = balance - %s WHERE username = %s', (amount, self.account[1]))
                        self.mysql.connection.commit()
                        self.recordTransaction(self.account[3], receiver1[3], amount, "Sent", self.account[0], receiver1[0])
                        self.refreshAccounts()
                        return redirect(url_for('dashboard'))
                    else:
                        print("User does not exist")
                        return redirect(url_for('dashboard'))
                else: 
                    print("Incorrect password")    
                return redirect(url_for('dashboard'))



        @self.app.route("/recharge_process", methods=["POST", "GET"])
        def recharge_process():
            if request.method=="POST":
                amount = request.form["amount"]
                name = request.form["name"]

                #disable negative and 0 amounts
                if self.amountVerifier(amount) == False:
                    return redirect(url_for("dashboard"))

                cursor = self.mysql.connection.cursor()
                cursor.execute("UPDATE accounts SET balance = balance+%s WHERE userid=%s", (amount,self.account[0]))
                self.mysql.connection.commit()
                cursor.close()

                self.recordTransaction(name,self.account[3],amount,"Recharge",self.account[0],self.account[0])

                self.refreshAccounts()

                return redirect(url_for("dashboard"))
            



        @self.app.route("/bankTransfer_process", methods=["POST", "GET"])
        def bankTransfer_process():
            if request.method=="POST":
                bank= request.form["bank"]
                amount= float(request.form["amount"])
                password = request.form["password"]

                if password == self.account[2]:
                    cursor = self.mysql.connection.cursor()
                    cursor.execute("UPDATE accounts SET balance = balance - %s WHERE userid = %s",(amount,self.account[0]))
                    self.mysql.connection.commit()
                    cursor.close()

                    self.recordTransaction(bank,self.account[3],int(amount),"Bank Transfer", 0, self.account[0])
                    self.refreshAccounts()
                else: print("Password does not match")
                
                return redirect("/dashboard")
            

        @self.app.route("/gameTopup_process", methods=["POST", "GET"])
        def gameTopup_process():
            if request.method=="POST":
                game = request.form["game"]

                if game == "minecraft":
                    email = request.form["email"]
                    package = request.form["package"]

                    price, Minecoins = package.split("|")
                    #data type conversions
                    price = float(price)
                    currency = f"Minecraft {Minecoins} Minecoins"

                    #Deduct Price
                    if(self.withdraw(price, self.account)):
                        print(f"Successfully withdrawn {price}")
                        self.recordTransaction(currency,self.account[3],price,"Game Topup",0,self.account[0])
                        self.refreshAccounts()
                        print(email,price,currency)

                    else: print(f"Failed to withdraw {price}")

                
                elif game == "genshin":
                    
                    uid = request.form["uid"]
                    server = request.form["server"]
                    package = request.form["genshinOptions"]
                    
                    price, package = package.split("|")
                    price = float(price)
                    
                    if price == 280: currency= "Genshin Impact Welkin Moon"
                    else: currency = f"Genshin Impact {package} Diamonds"

                    if(self.withdraw(price, self.account)):
                        print(f"Successfully withdrawn {price}")
                        print(uid,server,price,currency)
                        self.recordTransaction(currency,self.account[3],price,"Game Topup",0,self.account[0])
                        self.refreshAccounts()
                    else: print(f"Failed to withdraw {price}")


                elif game == "league of legends":
                    riotId = request.form["riotId"]
                    price = request.form["lolOptions"]
                    
                    price, rp = price.split("|")  
                    price = float(price)
                    
                    currency = f"League of Legends {rp}RP"
                    

                    if(self.withdraw(price, self.account)):
                        print(f"Successfully withdrawn {price}")
                        self.recordTransaction(currency,self.account[3],price,"Game Topup",0,self.account[0])
                        self.refreshAccounts()
                        print(riotId,price,currency)
                    else: print(f"Failed to withdraw {price}")
                    
                               
                elif game == "CODM":
                    playerID = request.form["playerId"]
                    price = request.form["codmOptions"]
                    

                    currency = f"CODM {price} Garena Shells"
                    price = float(price)


                    if(self.withdraw(price, self.account)):
                        print(f"Successfully withdrawn {price}")
                        self.recordTransaction(currency,self.account[3],price,"Game Topup",0,self.account[0])
                        self.refreshAccounts()
                        print(playerID,price,currency)

                    else: print(f"Failed to withdraw {price}")
                    
             
                elif game == "valorant":
                    playerID = request.form["riotId"]
                    package = request.form["valorantOptions"]

                    price, currency = package.split("|")

                    price = float(price)
                    currency = f"Valorant {currency}VP"

                    if(self.withdraw(price, self.account)):
                        print(f"Successfully withdrawn {price}")
                        self.recordTransaction(currency,self.account[3],price,"Game Topup",0,self.account[0])
                        self.refreshAccounts()
                        print(playerID,price,currency)

                    else: print(f"Failed to withdraw {price}")
                    
                    
                return redirect(url_for("topup"))
        
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

                    
                print(phoneNumber, provider, amount)

                if self.withdraw(amount,self.account):
                    #self.recordTransaction("")
                    print("Successful")
                else: print("Failed")

                self.recordTransaction(provider,phoneNumber,amount,"Load",0,self.account[0])

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

                if(self.withdraw(amount,self.account)):
                    self.recordTransaction(name,receiver,amount,"Donated",0,self.account[0])
                else:
                    print("You do not have enough balance")
                
            return redirect(url_for("dashboard"))



# Object
x = Kwarta(__name__) 
x.setup_route()
x.run()


#send username or number inputs
#send more than balance
#recent should be at top