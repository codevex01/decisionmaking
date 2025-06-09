from flask import Flask, render_template, request, jsonify
import json
import math
import pandas as pd
import os

app = Flask(__name__)

def load_excel_data():
    """Excel dosyasından transport verilerini yükle"""
    try:
        excel_file = 'article 16 group 32.xlsx'
        
        if not os.path.exists(excel_file):
            print(f"❌ Excel dosyası bulunamadı: {excel_file}")
            return load_json_fallback()
        
        print("📊 Excel dosyasından veri yükleniyor...")
        
        # Excel'i doğru header ile oku (3. satır header)
        df = pd.read_excel(excel_file, sheet_name=0, header=3)
        
        # Gereksiz sütunları temizle
        df = df.dropna(how='all', axis=1)  # Tamamen boş sütunları sil
        df = df.dropna(how='all', axis=0)  # Tamamen boş satırları sil
        
        print(f"✅ Excel verisi yüklendi: {df.shape}")
        print(f"📋 Sütunlar: {df.columns.tolist()}")
        
        # Excel verisini JSON formatına dönüştür
        transport_data = convert_excel_to_transport_data(df)
        print("✅ Excel verisi JSON formatına dönüştürüldü")
        
        return transport_data
        
    except Exception as e:
        print(f"❌ Excel okuma hatası: {e}")
        print("🔄 JSON dosyasından yükleniyor...")
        return load_json_fallback()

def convert_excel_to_transport_data(df):
    """Excel DataFrame'ini transport_data JSON formatına dönüştür"""
    transport_data = {}
    
    # Transport modlarını al (A/C sütunundan) - sadece gerçek transport modları
    all_modes = df['A/C'].dropna().tolist()
    
    # Gerçek transport modlarını filtrele
    valid_transport_modes = [
        'Car', 'Taxi/Martı', 'Bus', 'Minibuses', 'Metrobus', 
        'Metro/Marmaray', 'Ferry', 'Sea taxi'
    ]
    
    transport_modes = []
    for mode in all_modes:
        if mode in valid_transport_modes:
            transport_modes.append(mode)
        elif mode == 'Taxi/Mart\u0131':  # Unicode karakteri düzelt
            transport_modes.append('Taxi/Martı')
    
    # Tekrarları kaldır
    transport_modes = list(dict.fromkeys(transport_modes))
    transport_data['transport_modes'] = transport_modes
    print(f"🚌 Filtrelenmiş Transport modları: {transport_modes}")
    
    # Kriterleri al (CO2 Emission'dan Comfort'a kadar olan sütunlar)
    criteria_columns = [
        'CO2 Emission', 'Air Pollution', 'Noise Pollution', 'Occupancy R.',
        'Transport.Cost', 'Travel Time', 'Capacity', 'Availability', 
        'Intermodality', 'Waiting Time', 'Accessibility', 'Safety', 
        'Flexibility', 'Comfort'
    ]
    
    # Sütun isimlerini standartlaştır
    column_mapping = {
        'Occupancy R.': 'Occupancy Rate',
        'Transport.Cost': 'Transport Cost'
    }
    
    criteria = []
    for col in criteria_columns:
        if col in df.columns:
            standard_name = column_mapping.get(col, col)
            criteria.append(standard_name)
    
    transport_data['criteria'] = criteria
    print(f"📊 Kriterler: {criteria}")
    
    # Her transport modu için veri oluştur - sadece geçerli modlar için
    data = {}
    for mode in transport_modes:
        # Excel'de bu modun olduğu satırı bul
        mode_rows = df[df['A/C'] == mode]
        if not mode_rows.empty:
            row_data = mode_rows.iloc[0]  # İlk eşleşen satırı al
            data[mode] = {}
            
            for col in criteria_columns:
                if col in df.columns:
                    standard_name = column_mapping.get(col, col)
                    value = row_data[col]
                    if pd.notna(value) and isinstance(value, (int, float)):
                        data[mode][standard_name] = int(value)
                    else:
                        data[mode][standard_name] = 0
        else:
            print(f"⚠️ {mode} için veri bulunamadı")
    
    transport_data['data'] = data
    print(f"✅ {len(data)} transport modu verisi işlendi")
    
    # Mevcut JSON'dan diğer gerekli verileri al
    try:
        fallback_data = load_json_fallback()
        transport_data['criteria_descriptions'] = fallback_data.get('criteria_descriptions', {})
        transport_data['weight_preferences'] = fallback_data.get('weight_preferences', {})
        transport_data['scientific_weights'] = fallback_data.get('scientific_weights', {})
        transport_data['artasi_rankings'] = fallback_data.get('artasi_rankings', {})
        print("✅ Ek veriler JSON'dan alındı")
    except:
        print("⚠️ JSON'dan ek veri alınamadı, varsayılan değerler kullanılacak")
        transport_data['criteria_descriptions'] = {}
        transport_data['weight_preferences'] = {}
        transport_data['scientific_weights'] = {}
        transport_data['artasi_rankings'] = {}
    
    return transport_data

def load_json_fallback():
    """JSON dosyasından veri yükle (fallback)"""
    with open('transport_data.json', 'r', encoding='utf-8') as f:
        return json.load(f)

# Load transport data from Excel or JSON
transport_data = load_excel_data()

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

@app.route('/debug')
def debug_data():
    """Debug için veri kaynağı ve yapısını göster"""
    excel_file = 'article 16 group 32.xlsx'
    source = "Excel" if os.path.exists(excel_file) else "JSON"
    
    return jsonify({
        'data_source': source,
        'transport_modes': transport_data.get('transport_modes', []),
        'criteria_count': len(transport_data.get('criteria', [])),
        'criteria': transport_data.get('criteria', []),
        'sample_data': {
            mode: data for mode, data in list(transport_data.get('data', {}).items())[:2]
        }
    })

@app.route('/reload-data')
def reload_data():
    """Veriyi yeniden yükle"""
    global transport_data
    transport_data = load_excel_data()
    return jsonify({
        'status': 'success',
        'message': 'Data reloaded successfully',
        'transport_modes': transport_data.get('transport_modes', [])
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)  # Different port to avoid conflict 