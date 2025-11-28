# NutrifyKE 🇰🇪

**NutrifyKE** is an AI-powered calorie tracking application designed specifically for Kenyan foods. It combines cutting-edge computer vision technology with a comprehensive database of local Kenyan dishes to make nutrition tracking effortless and accurate.

## 🌟 What is NutrifyKE?

NutrifyKE revolutionizes how Kenyans track their nutrition by understanding local foods like Ugali, Chapati, Sukuma Wiki, and more. Simply snap a photo of your meal, and our AI instantly identifies the food and logs the nutritional information - no manual searching required!

## ✨ Key Features

### 🤖 AI-Powered Multi-Food Detection
- **Smart Food Recognition**: Uses Google Gemini 2.5 Flash AI to identify multiple foods in a single image
- **Automatic Logging**: Detected foods are instantly added to your daily log
- **Kenyan Food Database**: Specialized database with accurate nutritional data for local dishes
- **Fuzzy Matching**: Intelligent matching ensures AI-detected foods link correctly to the database

### 📊 Daily Dashboard
- **Calorie Goal Tracking**: Set your daily calorie target (default: 2500 kcal)
- **Visual Progress Bar**: Animated progress bar shows your daily calorie consumption
- **Calories Remaining**: Real-time display of remaining calories (turns red when over limit!)
- **Macro Breakdown**: Track Protein, Carbs, and Fats with color-coded cards
  - 💙 **Protein** - Indigo theme
  - 🧡 **Carbs** - Amber theme
  - ❤️ **Fats** - Rose theme

### 📱 User-Friendly Interface
- **Floating Camera Button**: Always-accessible scan button in the bottom-right corner
- **Responsive Design**: Works seamlessly on mobile and desktop
- **Modern UI**: Clean, intuitive interface built with Tailwind CSS
- **Smooth Animations**: Polished transitions and hover effects

### 📝 Meal Logging
- **Timestamp Tracking**: Each meal shows exact time logged (AM/PM format)
- **Manual Entry**: Option to manually select food and quantity
- **Serving Sizes**: Flexible quantity input (supports decimals)
- **Detailed Nutrition**: View calories and macros for each logged meal

### 🗑️ Meal Management
- **Delete Individual Meals**: Remove mistakes with a single click
- **Instant Recalculation**: Totals update immediately after deletion
- **Reset Day**: Clear all meals and start fresh with one button
- **Confirmation Dialogs**: Prevents accidental deletions

### 💾 Data Persistence
- **LocalStorage Integration**: All data saved automatically to your browser
- **Survives Refreshes**: Your log persists even after closing the browser
- **Auto-Save**: Every action is immediately saved
- **Restore on Load**: Previous meals and settings restored on page load

### 🎯 Smart Quantification
- **Hybrid System**: Supports both piece-based (e.g., "2 chapatis") and weight-based (e.g., "250g rice") foods
- **Portion Sizes**: Pre-defined portions (Small, Medium, Large) for common foods
- **Automatic Conversion**: Intelligent conversion between servings and grams

## 🏗️ Technical Architecture

### Backend (Python/Flask)
- **Framework**: Flask web server
- **AI Integration**: Google Gemini API for image analysis
- **Business Logic**: Custom calculation engine in `utils.py`
- **Food Database**: JSON-based food data with nutritional information

### Frontend (HTML/JavaScript)
- **Styling**: Tailwind CSS for modern, responsive design
- **State Management**: JavaScript with localStorage persistence
- **API Communication**: Fetch API for backend integration
- **File Handling**: Native file input with camera capture support

### Key Files
```
NutrifyKE/
├── main.py              # Flask backend with AI integration
├── utils.py             # Nutrition calculation logic
├── food_data.json       # Kenyan food nutritional database
├── templates/
│   └── index.html       # Frontend UI and JavaScript
├── .env                 # Environment variables (API key)
└── requirements.txt     # Python dependencies
```

## 🚀 Getting Started

### Prerequisites
- Python 3.7+
- Google Gemini API key
- Modern web browser

### Installation

1. **Clone or download the project**
   ```bash
   cd NutrifyKE
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   Create a `.env` file in the project root:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```

4. **Run the application**
   ```bash
   python main.py
   ```

5. **Open in browser**
   Navigate to `http://localhost:5000`

## 📖 How to Use

### Scanning Food (Recommended)
1. Click the **floating camera button** (bottom-right corner) or "Scan Food" button
2. Take a photo or select an image of your meal
3. Wait for AI analysis (shows "Scanning..." animation)
4. Foods are automatically detected and logged!

### Manual Entry
1. Select a food from the dropdown menu
2. Enter the quantity (servings)
3. Click "Log Meal"

### Managing Your Log
- **View Details**: Each entry shows food name, time logged, calories, and macros
- **Delete Meal**: Click the red trash icon on any entry
- **Reset Day**: Click "Reset Day" button to clear all meals

### Tracking Progress
- Monitor your **progress bar** to see how close you are to your goal
- Check **calories remaining** (green) or **over limit** warning (red)
- Review **macro totals** in the dashboard cards

## 🍽️ Supported Kenyan Foods

NutrifyKE includes nutritional data for popular Kenyan dishes:
- Ugali (White & Brown)
- Chapati
- Rice (White & Brown)
- Sukuma Wiki
- Beef Stew
- Chicken Stew
- Githeri
- Mukimo
- Mandazi
- And many more!

## 🔒 Privacy & Data

- **Local Storage**: All data is stored locally in your browser
- **No Account Required**: No sign-up or personal information needed
- **Image Processing**: Images are sent to Google Gemini API for analysis only
- **No Data Collection**: We don't store or collect your meal data

## 🛠️ Technology Stack

- **Backend**: Python, Flask
- **AI**: Google Gemini 2.5 Flash
- **Frontend**: HTML5, JavaScript (ES6+), Tailwind CSS
- **Storage**: Browser localStorage
- **Image Processing**: PIL (Pillow)

## 🎨 Design Philosophy

NutrifyKE is built with three core principles:

1. **Simplicity**: One-tap food logging with minimal user input
2. **Accuracy**: Specialized database for Kenyan foods ensures precise tracking
3. **Accessibility**: Works on any device, no installation required

## 🔮 Future Enhancements

Potential features for future versions:
- Macro goal tracking (not just calories)
- Weekly/monthly statistics and trends
- Export data to CSV
- Meal favorites and quick-add
- Barcode scanning for packaged foods
- Multi-language support (Swahili)

## 📄 License

This project is open-source and available for personal and educational use.

## 🙏 Acknowledgments

- Google Gemini API for AI-powered food recognition
- Tailwind CSS for beautiful, responsive design
- The Kenyan nutrition community for food data validation

---

**Made with ❤️ for Kenya** 🇰🇪

*Track your nutrition, the Kenyan way!*
