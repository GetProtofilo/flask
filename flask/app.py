from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)
app.secret_key = "securekey"

# HTML Template with Sleek UI
HTML_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Credit Card Validator</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(to bottom, #eef2f3, #8e9eab);
            color: #333;
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }
        .container {
            background: #fff;
            border-radius: 8px;
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
            padding: 20px;
            width: 100%;
            max-width: 400px;
        }
        h1 {
            color: #4a90e2;
            text-align: center;
        }
        form {
            margin-top: 20px;
        }
        input[type="text"] {
            width: calc(100% - 20px);
            padding: 10px;
            margin-bottom: 20px;
            border: 1px solid #ccc;
            border-radius: 4px;
            font-size: 16px;
        }
        button {
            background: #4a90e2;
            color: #fff;
            border: none;
            padding: 10px 20px;
            font-size: 16px;
            cursor: pointer;
            border-radius: 4px;
            width: 100%;
        }
        button:hover {
            background: #357abd;
        }
        .result {
            margin-top: 20px;
            padding: 10px;
            border-radius: 4px;
            display: none;
        }
        .valid {
            background: #d4edda;
            color: #155724;
        }
        .invalid {
            background: #f8d7da;
            color: #721c24;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Credit Card Validator</h1>
        <form id="cardForm">
            <input type="text" id="cardNumber" name="card_number" placeholder="Enter your card number" required>
            <button type="submit">Validate</button>
        </form>
        <div id="result" class="result"></div>
    </div>

    <script>
        document.getElementById("cardForm").addEventListener("submit", function (e) {
            e.preventDefault();
            const cardNumber = document.getElementById("cardNumber").value;
            fetch("/validate", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ card_number: cardNumber })
            })
            .then(response => response.json())
            .then(data => {
                const resultDiv = document.getElementById("result");
                resultDiv.style.display = "block";
                if (data.valid) {
                    resultDiv.className = "result valid";
                    resultDiv.textContent = "Card is valid! (" + data.message + ")";
                } else {
                    resultDiv.className = "result invalid";
                    resultDiv.textContent = "Card is invalid! (" + data.message + ")";
                }
            });
        });
    </script>
</body>
</html>
"""

def luhn_algorithm(card_number):
    """Validate the card number using the Luhn algorithm."""
    digits = [int(d) for d in str(card_number)]
    checksum = 0

    # Double every second digit from the right
    for i, digit in enumerate(reversed(digits)):
        if i % 2 == 1:
            digit *= 2
            if digit > 9:
                digit -= 9
        checksum += digit

    return checksum % 10 == 0

def get_card_type(card_number):
    """Identify the card type based on prefixes."""
    if card_number.startswith("4"):
        return "Visa"
    elif card_number.startswith(("51", "52", "53", "54", "55")):
        return "Mastercard"
    elif card_number.startswith("34") or card_number.startswith("37"):
        return "American Express"
    else:
        return "Unknown"

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route("/validate", methods=["POST"])
def validate():
    data = request.get_json()
    card_number = data.get("card_number", "").replace(" ", "")
    
    if not card_number.isdigit():
        return jsonify(valid=False, message="Card number must contain only digits.")
    
    if len(card_number) < 13 or len(card_number) > 19:
        return jsonify(valid=False, message="Card number must be between 13 and 19 digits.")

    card_type = get_card_type(card_number)
    if card_type == "Unknown":
        return jsonify(valid=False, message="Card type not recognized.")

    if luhn_algorithm(card_number):
        return jsonify(valid=True, message=f"Valid {card_type} card.")
    else:
        return jsonify(valid=False, message="Failed Luhn check.")

if __name__ == "__main__":
    app.run(debug=True)
