# 🎯 Article 16 WENSLO-ARTASI Transport Decision Maker

Research-based implementation of advanced Multi-Criteria Decision Making (MCDM) methods for public transport evaluation.

## 📚 Scientific Foundation

This application implements the cutting-edge algorithms described in **Article 16**:

- **WENSLO**: Weights by ENvelope and SLOpe (Pamucar et al., 2023)
- **ARTASI**: Alternative Ranking Technique based on Adaptive Standardized Intervals (Pamucar et al., 2024)

## 🔬 Methodology

### WENSLO Weight Calculation
1. **Linear Normalization**: z_ij = x_ij / Σ(x_ij)
2. **Delta Calculation**: Δz_j = (max z_ij - min z_ij) / (1 + 3.322 × log10(m))
3. **Slope Calculation**: tan φ_j = Σz_ij / ((m-1) × Δz_j)
4. **Envelope Calculation**: E_j = Σ√((z_{i+1,j} - z_{i,j})² + Δz_j²)
5. **Weight Derivation**: w_j = q_j / Σq_j where q_j = E_j / tan φ_j

### ARTASI Scoring System
1. **Standardization**: φ_ij = (x_ij - min_j) / (max_j - min_j)
2. **Ideal Usefulness**: ϑ⁺_ij = (φ_ij / max_i φ_ij) × w_j
3. **Anti-ideal Usefulness**: ϑ⁻_ij = ((max_i φ_ij - φ_ij) / max_i φ_ij) × w_j
4. **Ultimate Utility**: Ω_i = (I⁺_i + I⁻_i) × ((α × f(I⁺_i)^φ + (1-α) × f(I⁻_i)^φ))^(1/φ)

## 🚀 Features

- ✅ **Objective Weight Calculation**: No subjective bias in criteria weighting
- ✅ **Excel Data Integration**: Direct import from Article 16 dataset
- ✅ **Dual Analysis**: Compare objective WENSLO-ARTASI vs. personal preferences
- ✅ **Real-time Calculations**: Interactive sliders for preference setting
- ✅ **Scientific Validation**: Based on peer-reviewed research
- ✅ **Comprehensive Visualization**: Multiple result views and comparisons

## 📊 Transport Criteria

The system evaluates transport modes based on 14 scientific criteria:

### Environmental Impact
- **CO2 Emission** (lower is better)
- **Air Pollution** (lower is better)  
- **Noise Pollution** (lower is better)

### Efficiency & Performance
- **Occupancy Rate** (higher is better)
- **Transport Cost** (lower is better)
- **Travel Time** (lower is better)
- **Capacity** (higher is better)

### Service Quality
- **Availability** (higher is better)
- **Intermodality** (higher is better)
- **Waiting Time** (lower is better)
- **Accessibility** (higher is better)
- **Safety** (higher is better)
- **Flexibility** (higher is better)
- **Comfort** (higher is better)

## 🚌 Transport Modes

- 🚗 Car
- 🚕 Taxi/Martı
- 🚌 Bus
- 🚐 Minibuses
- 🚎 Metrobus
- 🚇 Metro/Marmaray
- ⛴️ Ferry

## ⚡ Quick Start

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run Application**:
   ```bash
   python app_article.py
   ```

3. **Access Interface**:
   - Open browser to `http://localhost:5002`
   - Set your preferences using interactive sliders
   - Click "Calculate with WENSLO-ARTASI Method"
   - Compare objective vs. subjective results

## 📁 File Structure

```
decision making/
├── app_article.py              # Main Flask application (Article 16 implementation)
├── article 16 group 32.xlsx    # Research dataset
├── article_16.pdf              # Research paper reference
├── requirements.txt            # Python dependencies
├── README_article.md           # This documentation
└── templates/
    └── index_article.html      # Web interface
```

## 🔧 Technical Specifications

- **Backend**: Flask + NumPy + Pandas
- **Frontend**: Responsive HTML5 + CSS3 + JavaScript
- **Data Source**: Excel (article 16 group 32.xlsx)
- **Algorithms**: WENSLO + ARTASI (Article 16 formulas)
- **Port**: 5002 (to avoid conflicts)

## 📈 Analysis Results

The application provides three analysis views:

1. **🎯 WENSLO-ARTASI**: Objective scientific method
2. **👤 Your Preferences**: Personal preference-based results
3. **📊 Comparison**: Side-by-side method comparison

## 🎯 Key Advantages

- **Eliminates Bias**: WENSLO calculates weights objectively
- **Research-Based**: Implements latest MCDM algorithms
- **Comprehensive**: Considers all transport aspects
- **Interactive**: Real-time calculations and visualizations
- **Validated**: Based on peer-reviewed scientific methods

## 📝 Citation

If you use this implementation in research, please cite:

```
Pamucar, D. et al. (2023). WENSLO: Weights by ENvelope and SLOpe
Pamucar, D. et al. (2024). ARTASI: Alternative Ranking Technique based on Adaptive Standardized Intervals
```

## 🔄 Differences from Basic Implementation

| Feature | Basic App | Article 16 App |
|---------|-----------|---------------|
| Weight Calculation | User/Static | WENSLO Algorithm |
| Scoring Method | Simple Weighted Sum | ARTASI Method |
| Data Source | JSON | Excel (Research Data) |
| Scientific Validation | Limited | Full Article 16 |
| Objectivity | Subjective | Objective + Subjective |

---

🎯 **Experience the future of transport decision making with scientifically validated algorithms!** 