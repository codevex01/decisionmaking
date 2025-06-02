from flask import Flask, render_template, request, jsonify
import json
import math

app = Flask(__name__)

# Load transport data
with open('transport_data.json', 'r') as f:
    transport_data = json.load(f)

def calculate_weighted_scores(user_weights, mode="user"):
    """Calculate weighted scores with different modes."""
    scores = {}
    
    # Choose weights based on mode
    if mode == "scientific":
        weights = transport_data['scientific_weights']
    else:
        weights = user_weights
    
    # Find min and max values for each criterion to normalize
    criteria_ranges = {}
    for criterion in transport_data['criteria']:
        values = [transport_data['data'][mode][criterion] for mode in transport_data['transport_modes']]
        criteria_ranges[criterion] = {'min': min(values), 'max': max(values)}
    
    for transport_mode in transport_data['transport_modes']:
        total_score = 0
        max_possible_score = 0
        
        for criterion in transport_data['criteria']:
            if mode == "scientific":
                weight = weights.get(criterion, 0.071)  # Average weight if missing
            else:
                weight = weights.get(criterion, 1)
            
            raw_value = transport_data['data'][transport_mode][criterion]
            
            # Normalize the value to 0-10 scale
            min_val = criteria_ranges[criterion]['min']
            max_val = criteria_ranges[criterion]['max']
            
            if max_val == min_val:
                normalized_value = 5  # If all values are the same, use middle value
            else:
                # Normalize to 0-10 range based on preference
                if transport_data['weight_preferences'][criterion] == "Lower is better":
                    # For "lower is better" criteria, invert the normalization
                    normalized_value = 10 * (max_val - raw_value) / (max_val - min_val)
                else:
                    # For "higher is better" criteria, use direct normalization
                    normalized_value = 10 * (raw_value - min_val) / (max_val - min_val)
            
            total_score += normalized_value * weight
            
            if mode == "scientific":
                max_possible_score += 10 * weight
            else:
                max_possible_score += 10 * weight
        
        # Calculate percentage score
        if max_possible_score > 0:
            scores[transport_mode] = (total_score / max_possible_score) * 100
        else:
            scores[transport_mode] = 0
    
    return scores

def get_recommendation(scores):
    """Get the top 3 recommendations based on scores."""
    sorted_modes = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return sorted_modes[:3]

def get_artasi_comparison():
    """Return ARTASI expert rankings for comparison."""
    artasi = transport_data['artasi_rankings']
    return [(artasi[str(i)], f"Expert Rank #{i}") for i in range(1, len(artasi)+1)]

@app.route('/')
def index():
    return render_template('index_enhanced.html', 
                         criteria=transport_data['criteria'],
                         descriptions=transport_data['criteria_descriptions'],
                         scientific_weights=transport_data['scientific_weights'],
                         artasi_rankings=transport_data['artasi_rankings'])

@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.json
    user_weights = data.get('weights', {})
    calculation_mode = data.get('mode', 'user')
    
    # Calculate scores based on mode
    user_scores = calculate_weighted_scores(user_weights, "user")
    scientific_scores = calculate_weighted_scores(user_weights, "scientific")
    
    user_recommendations = get_recommendation(user_scores)
    scientific_recommendations = get_recommendation(scientific_scores)
    artasi_comparison = get_artasi_comparison()
    
    return jsonify({
        'user_scores': user_scores,
        'user_recommendations': user_recommendations,
        'scientific_scores': scientific_scores,
        'scientific_recommendations': scientific_recommendations,
        'artasi_comparison': artasi_comparison,
        'scientific_weights': transport_data['scientific_weights'],
        'transport_data': transport_data['data']
    })

@app.route('/data')
def get_data():
    return jsonify(transport_data)

@app.route('/scientific-weights')
def get_scientific_weights():
    return jsonify({
        'weights': transport_data['scientific_weights'],
        'top_criteria': sorted(transport_data['scientific_weights'].items(), 
                              key=lambda x: x[1], reverse=True)[:5]
    })

@app.route('/artasi')
def get_artasi():
    return jsonify({
        'rankings': transport_data['artasi_rankings'],
        'comparison': get_artasi_comparison()
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)  # Different port to avoid conflict 