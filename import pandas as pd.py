import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

# Create a simple dataset
data = {
    "Hours_Studied": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    "Marks": [35, 40, 45, 50, 55, 60, 65, 70, 80, 90]
}

df = pd.DataFrame(data)

# Input (X) and Output (y)
X = df[["Hours_Studied"]]
y = df["Marks"]

# Split data into training and testing data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Create the model
model = LinearRegression()

# Train the model
model.fit(X_train, y_train)

# Make predictions
predictions = model.predict(X_test)

# Display predictions
print("Actual Marks:")
print(y_test.values)

print("\nPredicted Marks:")
print(predictions)

# Evaluate the model
mse = mean_squared_error(y_test, predictions)
r2 = r2_score(y_test, predictions)

print("\nMean Squared Error:", mse)
print("R2 Score:", r2)

# Predict marks for a new student
hours = [[7.5]]
predicted_marks = model.predict(hours)

print("\nPredicted marks for 7.5 hours of study:",
      predicted_marks[0])