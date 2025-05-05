import pandas as pd
from surprise import Dataset, Reader, KNNBasic
from surprise.model_selection import train_test_split
from surprise import accuracy

# Sample book rating data (in a real system, you'd load this from a database or file)
data = {
    'user_id': ['U1', 'U1', 'U1', 'U2', 'U2', 'U3', 'U3', 'U4', 'U4', 'U5'],
    'book_id': ['B1', 'B2', 'B3', 'B1', 'B4', 'B2', 'B5', 'B3', 'B4', 'B5'],
    'rating': [5, 4, 3, 4, 5, 2, 4, 3, 4, 5]
}

# Book metadata (title, author, etc.)
books = {
    'book_id': ['B1', 'B2', 'B3', 'B4', 'B5'],
    'title': ['The Great Gatsby', 'To Kill a Mockingbird', '1984', 
              'Pride and Prejudice', 'The Hobbit'],
    'author': ['F. Scott Fitzgerald', 'Harper Lee', 'George Orwell', 
               'Jane Austen', 'J.R.R. Tolkien']
}

# Convert to DataFrames
ratings_df = pd.DataFrame(data)
books_df = pd.DataFrame(books)

# Define the rating scale
reader = Reader(rating_scale=(1, 5))

# Load the data into Surprise's Dataset format
data = Dataset.load_from_df(ratings_df[['user_id', 'book_id', 'rating']], reader)

# Split the data into train and test sets
trainset, testset = train_test_split(data, test_size=0.25, random_state=42)

# Use the KNNBasic algorithm (user-based collaborative filtering)
sim_options = {
    'name': 'cosine',
    'user_based': True  # compute similarities between users
}

algo = KNNBasic(sim_options=sim_options)

# Train the algorithm on the trainset
algo.fit(trainset)

# Test the algorithm on the testset
predictions = algo.test(testset)

# Calculate RMSE
accuracy.rmse(predictions)

# Function to get top N recommendations for a user
def get_recommendations(user_id, n=3):
    # Get list of all book ids
    all_book_ids = books_df['book_id'].unique()
    
    # Get list of book ids that user has already rated
    rated_books = ratings_df[ratings_df['user_id'] == user_id]['book_id'].unique()
    
    # Get list of book ids not rated by user
    books_to_predict = [book for book in all_book_ids if book not in rated_books]
    
    # Predict ratings for all unrated books
    testset = [[user_id, book, 4.] for book in books_to_predict]  # 4. is a dummy rating
    predictions = algo.test(testset)
    
    # Get the top N highest predicted rating books
    top_n = sorted(predictions, key=lambda x: x.est, reverse=True)[:n]
    
    # Get book details for the top N
    recommended_books = []
    for pred in top_n:
        book_id = pred.iid
        book_details = books_df[books_df['book_id'] == book_id].iloc[0]
        recommended_books.append({
            'book_id': book_id,
            'title': book_details['title'],
            'author': book_details['author'],
            'estimated_rating': pred.est
        })
    
    return recommended_books

# Example: Get recommendations for user U1
user_id = 'U1'
recommendations = get_recommendations(user_id)

print(f"\nTop recommendations for user {user_id}:")
for i, book in enumerate(recommendations, 1):
    print(f"{i}. {book['title']} by {book['author']} (estimated rating: {book['estimated_rating']:.1f})")
