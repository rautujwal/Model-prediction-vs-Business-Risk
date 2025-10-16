from flask import Flask, request, render_template_string
import joblib
import pandas as pd

app = Flask(__name__)

# Load model and columns
pipeline = joblib.load("Premium model.pkl")
columns = joblib.load("premimum model columns.pkl")

numeric_cols = columns["numeric_columns"]
ordinal_cols = columns["ordinal_columns"]
nominal_cols = columns["nominal_columns"]

# Front-end template as a string
template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Insurance Premium Predictor</title>
    <style>
        body { font-family: Arial, sans-serif; background: #f4f4f9; padding: 20px; }
        .container { max-width: 600px; margin: auto; background: #fff; padding: 20px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
        h2 { text-align: center; margin-bottom: 20px; }
        label { display: block; margin-top: 10px; font-weight: bold; }
        input { width: 100%; padding: 8px; margin-top: 5px; border-radius: 5px; border: 1px solid #ccc; }
        button { margin-top: 20px; padding: 10px; width: 100%; background: #007BFF; color: white; border: none; border-radius: 5px; cursor: pointer; }
        button:hover { background: #0056b3; }
        .result { margin-top: 20px; padding: 10px; background: #e8f5e9; border: 1px solid #c8e6c9; border-radius: 5px; text-align: center; font-size: 1.2em; }
    </style>
</head>
<body>
<div class="container">
    <h2>Insurance Premium Predictor</h2>

    <form method="post">
        {% for col in numeric_columns %}
            <label>{{ col }}</label>
            <input type="number" name="{{ col }}" step="any" required value="{{ form_data.get(col, '') }}">
        {% endfor %}

        {% for col in ordinal_columns %}
            <label>{{ col }}</label>
            <input type="text" name="{{ col }}" required value="{{ form_data.get(col, '') }}">
        {% endfor %}

        {% for col in nominal_columns %}
            <label>{{ col }}</label>
            <input type="text" name="{{ col }}" required value="{{ form_data.get(col, '') }}">
        {% endfor %}

        <button type="submit">Predict Premium</button>
    </form>

    {% if prediction_text %}
        <div class="result">{{ prediction_text }}</div>
    {% endif %}
</div>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def home():
    prediction_text = None
    form_data = {}
    if request.method == 'POST':
        form_data = request.form.to_dict()
        try:
            df = pd.DataFrame([form_data])
            
            # Ensure all columns exist
            expected_cols = numeric_cols + ordinal_cols + nominal_cols
            df = df[expected_cols]
            
            # Convert numeric columns to float
            for col in numeric_cols:
                df[col] = df[col].astype(float)
            
            # Predict
            prediction = pipeline.predict(df)[0]
            prediction_text = f"Predicted Premium: {prediction:.2f}"
        except Exception as e:
            prediction_text = f"Error: {e}"
    
    return render_template_string(template,
                                  numeric_columns=numeric_cols,
                                  ordinal_columns=ordinal_cols,
                                  nominal_columns=nominal_cols,
                                  prediction_text=prediction_text,
                                  form_data=form_data)

if __name__ == '__main__':
    app.run(debug=True)

