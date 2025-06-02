from flask import Flask, render_template, request, jsonify
import json
import math

app = Flask(__name__)

# Load transport data
with open('transport_data.json', 'r') as f:
    transport_data = json.load(f)

def calculate_weighted_scores(user_weights):
    """Calculate weighted scores for each transport mode based on user preferences."""
    scores = {}
    
    # Find min and max values for each criterion to normalize
    criteria_ranges = {}
    for criterion in transport_data['criteria']:
        values = [transport_data['data'][mode][criterion] for mode in transport_data['transport_modes']]
        criteria_ranges[criterion] = {'min': min(values), 'max': max(values)}
    
    for mode in transport_data['transport_modes']:
        total_score = 0
        max_possible_score = 0
        
        for criterion in transport_data['criteria']:
            weight = user_weights.get(criterion, 1)
            raw_value = transport_data['data'][mode][criterion]
            
            # Normalize the value to 0-10 scale
            min_val = criteria_ranges[criterion]['min']
            max_val = criteria_ranges[criterion]['max']
            
            if max_val == min_val:
                normalized_value = 5  # If all values are the same, use middle value
            else:
                # Normalize to 0-10 range
                if transport_data['weight_preferences'][criterion] == "Lower is better":
                    # For "lower is better" criteria, invert the normalization
                    normalized_value = 10 * (max_val - raw_value) / (max_val - min_val)
                else:
                    # For "higher is better" criteria, use direct normalization
                    normalized_value = 10 * (raw_value - min_val) / (max_val - min_val)
            
            total_score += normalized_value * weight
            max_possible_score += 10 * weight
        
        # Calculate percentage score
        if max_possible_score > 0:
            scores[mode] = (total_score / max_possible_score) * 100
        else:
            scores[mode] = 0
    
    return scores

def get_recommendation(scores):
    """Get the top 3 recommendations based on scores."""
    sorted_modes = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return sorted_modes[:3]

@app.route('/')
def index():
    return render_template('index.html', 
                         criteria=transport_data['criteria'],
                         descriptions=transport_data['criteria_descriptions'])

@app.route('/calculate', methods=['POST'])
def calculate():
    user_weights = request.json
    scores = calculate_weighted_scores(user_weights)
    recommendations = get_recommendation(scores)
    
    return jsonify({
        'scores': scores,
        'recommendations': recommendations,
        'transport_data': transport_data['data']
    })

@app.route('/data')
def get_data():
    return jsonify(transport_data)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 