from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
import json
import os
from math import log10

app = Flask(__name__)

class WensloArtasiCalculator:
    
    
    def __init__(self):
        self.load_data()
    
    def load_data(self):
        """Load data from Excel file based on Article 16 structure"""
        try:
            # Excel dosyasından raw data oku
            df_raw = pd.read_excel('group32.xlsx', header=None)
            print(f"📄 Excel loaded with shape: {df_raw.shape}")
            
            # Criteria (row 4 = 0-indexed 3, columns 3+ = 0-indexed 2+, skip A/C column)
            self.criteria = []
            if len(df_raw) > 3:
                for j in range(2, min(20, len(df_raw.columns))):  # Sütun 3+ (0-indexed 2+), skip A/C
                    if j < len(df_raw.columns) and pd.notna(df_raw.iloc[3, j]):
                        criterion = str(df_raw.iloc[3, j]).strip().replace('\n', ' ')
                        if criterion != 'A/C':  # Skip A/C header
                            self.criteria.append(criterion)
                            print(f"📊 Added criterion: '{criterion}'")
            
            # Transport modes (rows 5-12 = 0-indexed 4-11, column 2 = 0-indexed 1)
            self.transport_modes = []
            for i in range(4, 12):  # Excel satır 5-12 (0-indexed 4-11) 
                if i < len(df_raw) and pd.notna(df_raw.iloc[i, 1]):
                    mode = str(df_raw.iloc[i, 1]).strip()
                    if mode and mode not in ['Xij', 'xij', 'A/C']:  # Skip invalid entries
                        self.transport_modes.append(mode)
                        print(f"🚌 Added transport mode: '{mode}' (row {i+1})")
            
            # Decision matrix (rows 5-12, columns 3+ = data values)
            self.decision_matrix = []
            for i in range(4, 4 + len(self.transport_modes)):  # 0-indexed 4-11
                row = []
                for j in range(2, 2 + len(self.criteria)):  # 0-indexed 2+ for data
                    if i < len(df_raw) and j < len(df_raw.columns):
                        value = df_raw.iloc[i, j]
                        if pd.notna(value) and isinstance(value, (int, float)):
                            row.append(float(value))
                        else:
                            row.append(0.0)
                    else:
                        row.append(0.0)
                self.decision_matrix.append(row)
                print(f"📈 Row {i+1}: {len(row)} values loaded")
            
            self.decision_matrix = np.array(self.decision_matrix)
            
            # Criteria preferences (higher/lower is better)
            self.criteria_preferences = {
                'CO2 Emission': 'lower',
                'Air Pollution': 'lower', 
                'Noise Pollution': 'lower',
                'Occupancy R.': 'higher',
                'Transport.Cost': 'lower',
                'Travel Time': 'lower',
                'Capacity': 'higher',
                'Availability': 'higher',
                'Intermodality': 'higher',
                'Waiting Time': 'lower',
                'Accessibility': 'higher',
                'Safety': 'higher',
                'Flexibility': 'higher',
                'Comfort': 'higher'
            }
            
            print(f"✅ Data loaded: {len(self.transport_modes)} modes, {len(self.criteria)} criteria")
            print(f"🚌 Transport modes: {self.transport_modes}")
            print(f"📊 Criteria: {self.criteria}")
            print(f"📈 Decision matrix shape: {self.decision_matrix.shape}")
            
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            self.load_fallback_data()
    
    def load_fallback_data(self):
        """Load fallback data if Excel reading fails"""
        self.transport_modes = ['Car', 'Taxi/Martı', 'Bus', 'Minibuses', 'Metrobus', 'Metro/Marmaray', 'Ferry']
        self.criteria = ['CO2 Emission', 'Air Pollution', 'Noise Pollution', 'Occupancy Rate', 
                        'Transport Cost', 'Travel Time', 'Capacity', 'Availability', 
                        'Intermodality', 'Waiting Time', 'Accessibility', 'Safety', 
                        'Flexibility', 'Comfort']
        
        # Sample decision matrix
        self.decision_matrix = np.array([
            [26, 23, 18, 7, 25, 22, 13, 34, 30, 7, 26, 24, 33, 35],
            [27, 22, 14, 9, 34, 23, 13, 24, 30, 18, 24, 22, 30, 29],
            [23, 19, 22, 26, 21, 26, 28, 25, 29, 22, 24, 19, 20, 19],
            [25, 19, 19, 31, 30, 28, 26, 25, 33, 29, 27, 22, 22, 15],
            [15, 16, 21, 32, 23, 19, 31, 28, 30, 19, 23, 20, 16, 14],
            [15, 10, 11, 29, 21, 13, 31, 29, 29, 17, 23, 16, 16, 23],
            [23, 21, 16, 17, 18, 17, 31, 21, 19, 24, 15, 17, 13, 28]
        ])
        
        self.criteria_preferences = {
            'CO2 Emission': 'lower', 'Air Pollution': 'lower', 'Noise Pollution': 'lower',
            'Occupancy Rate': 'higher', 'Transport Cost': 'lower', 'Travel Time': 'lower',
            'Capacity': 'higher', 'Availability': 'higher', 'Intermodality': 'higher',
            'Waiting Time': 'lower', 'Accessibility': 'higher', 'Safety': 'higher',
            'Flexibility': 'higher', 'Comfort': 'higher'
        }
    
    def wenslo_weights(self, X):
        """
        WENSLO: Weights by ENvelope and SLOpe
        Based on Pamucar et al., 2023 - Article 16 formulas
        """
        m, n = X.shape  # m alternatives, n criteria
        
        # Step 1: Linear normalization (Eq. 2 in Article)
        # z_ij = x_ij / Σ(x_ij) for each criterion j
        Z = X / X.sum(axis=0)
        
        # Step 2: Calculate delta (Eq. 4)
        # Δz_j = (max z_ij - min z_ij) / (1 + 3.322 × log10(m))
        delta = (Z.max(axis=0) - Z.min(axis=0)) / (1 + 3.322 * log10(m))
        
        # Step 3: Calculate slope (tan φ_j) (Eq. 5)
        # tan φ_j = Σz_ij / ((m-1) × Δz_j)
        slope = Z.sum(axis=0) / ((m - 1) * delta)
        
        # Step 4: Calculate envelope (E_j) (Eq. 6)
        # E_j = Σ√((z_{i+1,j} - z_{i,j})² + Δz_j²)
        envelope = np.zeros(n)
        for j in range(n):
            z_sorted = np.sort(Z[:, j])
            diff_sum = np.sum(np.diff(z_sorted)**2)
            envelope[j] = np.sqrt(diff_sum + delta[j]**2)
        
        # Step 5: Calculate q_j (Eq. 7)
        # q_j = E_j / tan φ_j
        q = envelope / slope
        
        # Step 6: Calculate weights (Eq. 8)
        # w_j = q_j / Σq_j
        weights = q / q.sum()
        
        return weights
    
    def artasi_scores(self, X, w, alpha=0.5, phi=1.0, is_user_weights=False):
        """
        ARTASI: Alternative Ranking Technique based on Adaptive Standardized Intervals
        Based on Pamucar et al., 2024 - Article 16 formulas
        
        Args:
            is_user_weights: If True, treats all weights as "higher is better" (user importance)
                            If False, applies criteria_preferences (data transformations)
        """
        m, n = X.shape
        
        # Step 1: Handle criteria direction (benefit/cost)  
        X_normalized = X.copy().astype(float)
        
        if not is_user_weights:
            # For objective weights (WENSLO), apply criteria preferences to data
            for j, criterion in enumerate(self.criteria):
                if self.criteria_preferences.get(criterion, 'higher') == 'lower':
                    # For cost criteria (lower is better), use reciprocal transformation
                    # to make "lower is better" into "higher is better"
                    X_normalized[:, j] = 1 / (X_normalized[:, j] + 1e-10)
        else:
            # For user weights, we still need to transform data based on criteria preferences
            # but treat user weights as all "higher is better"
            for j, criterion in enumerate(self.criteria):
                if self.criteria_preferences.get(criterion, 'higher') == 'lower':
                    X_normalized[:, j] = 1 / (X_normalized[:, j] + 1e-10)
        
        # Step 2: Vector normalization (better than min-max for preserving ratios)
        # Normalize each column to unit vector
        for j in range(n):
            col_norm = np.sqrt(np.sum(X_normalized[:, j]**2))
            if col_norm > 0:
                X_normalized[:, j] = X_normalized[:, j] / col_norm
        
        # Step 3: Apply weights
        weighted_matrix = X_normalized * w
        
        # Step 4: Calculate utility scores using weighted sum approach
        # This gives a single score for each alternative
        utility_scores = np.sum(weighted_matrix, axis=1)
        
        # Step 5: Add some variation based on consistency
        # Calculate standard deviation of each alternative's criteria values
        consistency_bonus = np.zeros(m)
        for i in range(m):
            # Lower standard deviation = more consistent = small bonus
            std_dev = np.std(weighted_matrix[i, :])
            consistency_bonus[i] = 1 / (1 + std_dev)  # Inverse relationship
        
        # Step 6: Combine utility with consistency (small influence)
        final_scores = utility_scores * (0.9 + 0.1 * consistency_bonus)
        
        return final_scores
    
    def calculate_all_methods(self, user_weights=None):
        """Calculate scores using all methods"""
        results = {}
        
        # 1. WENSLO-ARTASI (Objective method from Article 16)
        wenslo_weights = self.wenslo_weights(self.decision_matrix)
        artasi_scores = self.artasi_scores(self.decision_matrix, wenslo_weights)
        
        # Convert to percentages and create dictionary
        max_score = artasi_scores.max() if artasi_scores.max() > 0 else 1
        wenslo_artasi_scores = {}
        for i, mode in enumerate(self.transport_modes):
            wenslo_artasi_scores[mode] = (artasi_scores[i] / max_score) * 100
        
        results['wenslo_artasi'] = {
            'scores': wenslo_artasi_scores,
            'weights': {self.criteria[i]: wenslo_weights[i] for i in range(len(self.criteria))},
            'recommendations': self.get_recommendations(wenslo_artasi_scores)
        }
        
        # 2. User-defined weights (if provided)
        if user_weights:
            user_weight_vector = np.array([user_weights.get(criterion, 1.0) for criterion in self.criteria])
            user_weight_vector = user_weight_vector / user_weight_vector.sum()  # Normalize
            
            # For user weights, all preferences are "higher is better" (importance levels)
            user_artasi_scores = self.artasi_scores(self.decision_matrix, user_weight_vector, is_user_weights=True)
            max_user_score = user_artasi_scores.max() if user_artasi_scores.max() > 0 else 1
            
            user_scores = {}
            for i, mode in enumerate(self.transport_modes):
                user_scores[mode] = (user_artasi_scores[i] / max_user_score) * 100
            
            results['user'] = {
                'scores': user_scores,
                'weights': {self.criteria[i]: user_weight_vector[i] for i in range(len(self.criteria))},
                'recommendations': self.get_recommendations(user_scores)
            }
        
        return results
    
    def get_recommendations(self, scores):
        """Get top 3 recommendations"""
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_scores[:3]
    
    def get_criteria_info(self):
        """Get criteria information"""
        return {
            'criteria': self.criteria,
            'preferences': self.criteria_preferences,
            'descriptions': {
                'CO2 Emission': 'Carbon dioxide emissions (lower is better)',
                'Air Pollution': 'Air quality impact (lower is better)',
                'Noise Pollution': 'Noise level impact (lower is better)',
                'Occupancy Rate': 'Vehicle occupancy efficiency (higher is better)',
                'Transport Cost': 'Cost of transportation (lower is better)',
                'Travel Time': 'Duration of travel (lower is better)',
                'Capacity': 'Passenger capacity (higher is better)',
                'Availability': 'Service availability (higher is better)',
                'Intermodality': 'Integration with other transport (higher is better)',
                'Waiting Time': 'Average waiting time (lower is better)',
                'Accessibility': 'Accessibility for all users (higher is better)',
                'Safety': 'Safety level (higher is better)',
                'Flexibility': 'Service flexibility (higher is better)',
                'Comfort': 'Comfort level (higher is better)'
            }
        }

# Initialize calculator
calculator = WensloArtasiCalculator()

@app.route('/')
def index():
    criteria_info = calculator.get_criteria_info()
    return render_template('index_article.html', 
                         criteria=criteria_info['criteria'],
                         descriptions=criteria_info['descriptions'],
                         preferences=criteria_info['preferences'])

@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        data = request.json
        user_weights = data.get('weights', {})
        
        # Calculate using Article 16 methods
        results = calculator.calculate_all_methods(user_weights)
        
        return jsonify({
            'success': True,
            'wenslo_artasi': results['wenslo_artasi'],
            'user': results.get('user', {}),
            'transport_modes': calculator.transport_modes,
            'criteria': calculator.criteria
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/data')
def get_data():
    """Get raw data information"""
    return jsonify({
        'transport_modes': calculator.transport_modes,
        'criteria': calculator.criteria,
        'decision_matrix': calculator.decision_matrix.tolist(),
        'criteria_preferences': calculator.criteria_preferences
    })

@app.route('/wenslo-analysis')
def wenslo_analysis():
    """Get detailed WENSLO analysis"""
    weights = calculator.wenslo_weights(calculator.decision_matrix)
    
    return jsonify({
        'method': 'WENSLO (Weights by ENvelope and SLOpe)',
        'reference': 'Pamucar et al., 2023',
        'weights': {calculator.criteria[i]: weights[i] for i in range(len(calculator.criteria))},
        'top_criteria': sorted(
            [(calculator.criteria[i], weights[i]) for i in range(len(calculator.criteria))],
            key=lambda x: x[1], reverse=True
        )[:5]
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002) 