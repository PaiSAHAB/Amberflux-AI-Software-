from flask import Flask, render_template, request, session, redirect, url_for
import openai
from bardapi import Bard
import os
import secrets

app = Flask(__name__)
#app.secret_key = '12345678'  # Set a secret key for session security


# Generate a random secret key
secret_key = secrets.token_hex(32)

# Set the secret key for the Flask app
app.secret_key = secret_key


# OpenAI API key

os.environ["Open_API_KEY"] = openai.api_key

# Bard API key

os.environ["_BARD_API_KEY"] = bard_api_key

# Google Bard instance
bard = Bard(bard_api_key)

# Response from ChatGPT
def get_chatgpt_response(query, profession):
    prompt = f"As a {profession}, {query}"
    response = openai.Completion.create(
        engine='text-davinci-003',
        prompt=prompt,
        max_tokens=2048,
        n=1,
        stop=None,
        temperature=0.4
    )
    return response.choices[0].text.strip()

# Response from Bard
def get_bard_response(query, profession):
    response = bard.get_answer(f"As a {profession}: {query}")['content']
    return response.strip()


# Function to store user ratings for ChatGPT and Bard
def store_chatgpt_rating(query, rating):
    with open("chatgpt_ratings.txt", "a") as file:
        file.write(f"Query: {query}\n")
        file.write(f"ChatGPT Rating: {rating}\n\n")

def store_bard_rating(query, rating):
    with open("bard_ratings.txt", "a") as file:
        file.write(f"Query: {query}\n")
        file.write(f"Bard Rating: {rating}\n\n")

def calculate_average_rating(file_path):
    total_ratings = 0
    num_ratings = 0

    with open(file_path, "r") as file:
        lines = file.readlines()
        for i in range(0, len(lines), 3):  # Assumes each entry is in 3 lines (query, rating, empty line)
            rating = int(lines[i + 1].split(": ")[1].strip())
            total_ratings += rating
            num_ratings += 1

    if num_ratings == 0:
        return 0  # Avoid division by zero if no ratings yet

    average_rating = total_ratings / num_ratings
    return round(average_rating, 2)

def get_num_reviews(file_path):
    num_reviews = 0

    with open(file_path, "r") as file:
        lines = file.readlines()
        num_reviews = len(lines) // 3  # Each review is in 3 lines (query, rating, empty line)

    return num_reviews

@app.route('/')
def home():
    return redirect(url_for('registration'))

@app.route('/registration', methods=['GET'])
def registration():
    return render_template('registration.html')

@app.route('/register', methods=['POST'])
def register():
    profession = request.form['profession']

    # Store the profession in the session
    session['profession'] = profession

    # You can process the registration data and store it in the database if needed

    # After processing, redirect the user to the main page
    return redirect(url_for('index'))


@app.route('/index')
def index():
    chatgpt_average_rating = calculate_average_rating("chatgpt_ratings.txt")
    bard_average_rating = calculate_average_rating("bard_ratings.txt")

    chatgpt_num_reviews = get_num_reviews("chatgpt_ratings.txt")
    bard_num_reviews = get_num_reviews("bard_ratings.txt")

    return render_template('index.html', chatgpt_average_rating=chatgpt_average_rating, bard_average_rating=bard_average_rating,
                           chatgpt_num_reviews=chatgpt_num_reviews, bard_num_reviews=bard_num_reviews)

@app.route('/submit', methods=['POST'])
def submit():
    # User query
    query = request.form['query']

    # Retrieve the user's profession from the session
    profession = session.get('profession')

    # Answer from ChatGPT
    chatgpt_response = get_chatgpt_response(query, profession).replace("\n", "<br>")

    # Answer from Bard
    bard_response = get_bard_response(query, profession).replace("\n", "<br>")

    # Pass the responses to the index.html
    return render_template('index.html', query=query, chatgpt_response=chatgpt_response, bard_response=bard_response)



def update_average_ratings(file_path):
    total_ratings = 0
    num_ratings = 0

    with open(file_path, "r") as file:
        lines = file.readlines()
        for i in range(0, len(lines), 3):  # Assumes each entry is in 3 lines (query, rating, empty line)
            rating = int(lines[i + 1].split(": ")[1].strip())
            total_ratings += rating
            num_ratings += 1

    if num_ratings == 0:
        return 0, 0  # Avoid division by zero if no ratings yet

    average_rating = total_ratings / num_ratings
    return round(average_rating, 2), num_ratings


@app.route('/submit_chatgpt_rating', methods=['POST'])
def submit_chatgpt_rating():
    # User rating for ChatGPT
    rating = request.form['chatgpt_rating']

    # Get the original query from the hidden form field
    query = request.form['hidden_chatgpt_query']

    # Store ChatGPT rating
    store_chatgpt_rating(query, rating)

    # Recalculate average ratings and number of reviews
    chatgpt_average_rating, chatgpt_num_reviews = update_average_ratings("chatgpt_ratings.txt")
    bard_average_rating, bard_num_reviews = update_average_ratings("bard_ratings.txt")

    # Redirect back to the index page with updated ratings and number of reviews
    return render_template('index.html', query=query, chatgpt_response=get_chatgpt_response(query).replace("\n", "<br>"),
                           bard_response=get_bard_response(query).replace("\n", "<br>"),
                           chatgpt_average_rating=chatgpt_average_rating, bard_average_rating=bard_average_rating,
                           chatgpt_num_reviews=chatgpt_num_reviews, bard_num_reviews=bard_num_reviews)

@app.route('/submit_bard_rating', methods=['POST'])
def submit_bard_rating():
    # User rating for Bard
    rating = request.form['bard_rating']

    # Get the original query from the hidden form field
    query = request.form['hidden_bard_query']

    # Store Bard rating
    store_bard_rating(query, rating)

    # Recalculate average ratings and number of reviews
    chatgpt_average_rating, chatgpt_num_reviews = update_average_ratings("chatgpt_ratings.txt")
    bard_average_rating, bard_num_reviews = update_average_ratings("bard_ratings.txt")

    # Redirect back to the index page with updated ratings and number of reviews
    return render_template('index.html', query=query, chatgpt_response=get_chatgpt_response(query).replace("\n", "<br>"),
                           bard_response=get_bard_response(query).replace("\n", "<br>"),
                           chatgpt_average_rating=chatgpt_average_rating, bard_average_rating=bard_average_rating,
                           chatgpt_num_reviews=chatgpt_num_reviews, bard_num_reviews=bard_num_reviews)


if __name__ == '__main__':
    app.run()





# async def stage1_openAI(prompt, user_profession):
#     prompt = prompt + " What could be the issue and how do I fix it?"
#     if user_profession.lower() not in prompt.lower():
#         return "Sorry, I can only answer questions related to your profession: " + user_profession + "."
#     else:
#         # Perform further processing here when the user's profession is present in the prompt
#         # For example, you can call the OpenAI API or perform some other operations
#         # and return the results.

#         # Sample return statement:
#         response = "I understand you have a question related to your profession: " + user_profession + ". Here's a response."
#         return response
    
# # async function to get the response from stage1_openAI
# async def get_stage1_response(query, user_profession):
#     response = await stage1_openAI(query, user_profession)
#     return response