# 🚌 Public Transport Decision Maker

A modern web application that helps users decide which public transport option to use based on their personal preferences and priorities. The application uses multi-criteria decision analysis to provide personalized recommendations.

## 📊 Features

- **Interactive Interface**: Modern, responsive web design with intuitive sliders
- **Multi-Criteria Analysis**: Evaluates transport options based on 7 key criteria:
  - Cost
  - Travel Time
  - CO2 Emission
  - Comfort
  - Availability
  - Accessibility
  - Safety

- **Personalized Recommendations**: Calculates weighted scores based on user preferences
- **Visual Results**: Beautiful cards showing top 3 recommendations with scores
- **Comprehensive Overview**: Shows scores for all transport options

## 🚇 Transport Options Analyzed

- Car 🚗
- Taxi/Martı 🚕
- Bus 🚌
- Minibuses 🚐
- Metrobus 🚎
- Metro/Marmaray 🚇
- Ferry ⛴️

## 🛠️ Installation

1. Make sure you have Python installed on your system
2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

## 🚀 Running the Application

1. Open a terminal in the project directory
2. Run the Flask application:
   ```bash
   python app.py
   ```
3. Open your web browser and navigate to:
   ```
   http://localhost:5000
   ```

## 💡 How to Use

1. **Set Your Preferences**: Use the sliders to indicate how important each criterion is to you (1 = Not Important, 5 = Very Important)

2. **Calculate Recommendations**: Click the "Calculate Best Transport Options" button

3. **View Results**: 
   - Top 3 recommendations are displayed as highlighted cards with match scores
   - All transport options are shown with their calculated scores
   - Higher scores indicate better matches for your preferences

## 📈 Scoring Algorithm

The application uses a weighted scoring system:
- Each criterion has a value for each transport mode
- User preferences (1-5) are used as weights
- Some criteria are inverted (e.g., CO2 emission - lower is better)
- Final scores are calculated as percentages for easy comparison

## 📁 File Structure

```
decision making/
├── app.py                      # Flask web application
├── transport_data.json         # Transport data and criteria
├── requirements.txt           # Python dependencies
├── README.md                  # This file
├── article 16 group 32.xlsx   # Original data source
└── templates/
    └── index.html            # Web interface
```

## 🎨 Interface Features

- **Gradient Background**: Modern purple-blue gradient design
- **Interactive Sliders**: Smooth, responsive preference sliders
- **Animated Elements**: Hover effects and smooth transitions
- **Mobile Responsive**: Works on desktop, tablet, and mobile devices
- **Emoji Icons**: Fun transport mode icons for better UX

## 🔧 Customization

You can modify the transport data by editing `transport_data.json`:
- Add new transport modes
- Adjust scoring values
- Add new criteria
- Update descriptions

## 📊 Data Source

The application is based on data from `article 16 group 32.xlsx`, which contains decision matrix data for public transport analysis.

## 🌐 Browser Compatibility

Works with all modern browsers:
- Chrome
- Firefox
- Safari
- Edge

---

Enjoy making informed transport decisions! 🚌✨ 