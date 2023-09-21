from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from pymongo import MongoClient
from datetime import datetime

cluster = MongoClient(
    "mongodb+srv://ashwin:GMQXC0meFRZqI1z2@cluster0.hrudxfx.mongodb.net/?retryWrites=true&w=majority&appName=AtlasApp")
db = cluster["Bakery"]
users = db["Users"]
orders = db["Orders"]
app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def reply():
    text = request.form.get("Body")
    number = request.form.get("From")
    number = number.replace("whatsapp:", "")
    res = MessagingResponse()
    user = users.find_one({"number": number})
    if bool(user) == False:  # first time user
        res.message("Hi, thanks for contacting *The Red Velvet*.\nYou can choose from one of the options below: "
                    "\n\n*Type*\n\n 1️⃣ To *contact* us \n 2️⃣ To *order* snacks \n 3️⃣ To know our *working hours* \n 4️⃣ "
                    "To get our *address*")
        users.insert_one({"number": number, "status": "main", "messages": []})
    elif user["status"] == "main":
        try:
            option = int(text)
        except:
            res.message("Please enter a valid response")
            return str(res)

        if option == 1:
            res.message(
                "You can contact us through phone or e-mail.\n\n*Phone*: 991234 56789 \n*E-mail* : contact@theredvelvet.io")
        elif option == 2:
            res.message("You have entered *ordering mode*.")
            users.update_one({"number": number}, {"$set": {"status": "ordering"}})
            res.message(
                "You can select one of the following cakes to order: \n\n1️⃣ Red Velvet  \n2️⃣ Black Forest \n3️⃣ Ice Cream Cake"
                "\n4️⃣ Plum Cake \n5️⃣ Sponge Cake \n6️⃣ Carrot Cake \n0️⃣ Go Back")
        elif option == 3:
            res.message("We work from *9 a.m. to 5 p.m*.")
        elif option == 4:
            res.message(
                "We have multiple stores across the city. Our main center is at *4/54, New Delhi*")
        else:
            res.message("Please enter a valid response")
    elif user["status"] == "ordering":
        try:
            option = int(text)
        except:
            res.message("Please enter a valid response")
            return str(res)
        if option == 0:
            users.update_one({"number": number}, {"$set": {"status": "main"}})
            res.message("You can choose from one of the options below: "
                        "\n\n*Type*\n\n 1️⃣ To *contact* us \n 2️⃣ To *order* snacks \n 3️⃣ To know our *working hours* \n 4️⃣ "
                        "To get our *address*")
        elif 1 <= option <= 6:
            cakes = [
                {
                    "name": "Red Velvet Cake",
                    "image_url": "https://images.unsplash.com/photo-1586788680434-30d324b2d46f?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2151&q=80"
                },
                {
                    "name": "Black Forest Cake",
                    "image_url": "https://images.unsplash.com/photo-1620492129802-2955e00f161e?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1974&q=80"
                },
                {
                    "name": "Ice Cream Cake",
                    "image_url": "https://images.unsplash.com/photo-1562634185-94581bf444ae?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1951&q=80"
                },
                {
                    "name": "Plum Cake",
                    "image_url": "https://images.unsplash.com/photo-1628471036342-adf99e82f1ac?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1931&q=80"
                },
                {
                    "name": "Sponge Cake",
                    "image_url": "https://images.unsplash.com/photo-1586780669486-6f4caec8da3a?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1974&q=80"
                },
                {
                    "name": "Carrot Cake",
                    "image_url": "https://images.unsplash.com/photo-1622926421334-6829deee4b4b?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1996&q=80"
                }
            ]
            selected_cake = cakes[option - 1]
            cake_name = selected_cake["name"]
            cake_image_url = selected_cake["image_url"]

            # Update user status and selected item
            users.update_one({"number": number}, {"$set": {"status": "address"}})
            users.update_one({"number": number}, {"$set": {"item": cake_name}})

            # Create a response message with the cake name and image
            message = (
                f"Excellent choice!\nYou've selected {cake_name} 😊\n"
                f"Please enter your address to confirm the order."
            )

            # Create a Twilio MessagingResponse and send the message with media (image)
            res.message(message).media(cake_image_url)

        else:
            res.message("Please enter a valid response")
    elif user["status"] == "address":
        selected = user["item"]
        res.message("Thanks for shopping with us!")
        res.message(f"Your order for *{selected}* has been received and will be delivered within an hour")
        orders.insert_one({"number": number, "item": selected, "address": text, "order_time": datetime.now()})
        users.update_one({"number": number}, {"$set": {"status": "ordered"}})

    elif user["status"] == "ordered":
        res.message("Hi, thanks for contacting again.\nYou can choose from one of the options below: "
                    "\n\n*Type*\n\n 1️⃣ To *contact* us \n 2️⃣ To *order* snacks \n 3️⃣ To know our *working hours* \n 4️⃣ "
                    "To get our *address*")
        users.update_one(
            {"number": number}, {"$set": {"status": "main"}})
    users.update_one({"number": number}, {"$push": {"messages": {"text": text, "date": datetime.now()}}})
    return str(res)


if __name__ == "__main__":
    app.run()
