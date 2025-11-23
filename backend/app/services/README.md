# AI-Powered Data Analytics Platform

## Abschlussprojekt - 9 Day Development Plan

### Project Overview
An AI-powered data analytics platform that helps businesses turn raw data into clear insights and visual dashboards — without needing a full data team.

### Target Customers
Small and medium-sized businesses, startups, and non-technical teams that want to make data-driven decisions easily.

### Problem Statement
Many organizations collect large amounts of data but struggle to analyze it effectively. Our tool simplifies data exploration and reporting through automation and intuitive visualization.

---

## MVP Features

1. ✅ Upload CSV/Excel files
2. ✅ Automatic data cleaning and validation
3. ✅ AI-powered data summary and insights
4. ✅ Auto-generate visualizations (bar, line, pie, scatter)
5. ✅ Interactive dashboard view
6. ✅ Export insights as reports

---

## Tech Stack

- **Backend**: Python + FastAPI
- **Database**: SQLite
- **Data Processing**: Pandas, NumPy
- **AI**: Claude API (Anthropic)
- **Visualization**: Plotly (planned)
- **Frontend**: React + Vite (planned)

---

## Project Structure
```
ai-data-analytics/
├── backend/
│   ├── app/
│   │   ├── routes/          # API endpoints
│   │   ├── services/        # Business logic
│   │   ├── __init__.py
│   │   ├── main.py          # FastAPI application
│   │   ├── models.py        # Database models
│   │   └── database.py      # Database connection
│   └── uploads/             # Uploaded data files
├── venv/                    # Virtual environment
├── .env                     # Environment variables
├── .gitignore
└── README.md
```

---

## Setup Instructions

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Installation Steps

1. **Clone or download the project**
```cmd
   cd Desktop\ai-data-analytics
```

2. **Create virtual environment**
```cmd
   python -m venv venv
```

3. **Activate virtual environment**
   - Windows: `venv\Scripts\activate.bat`
   - Mac/Linux: `source venv/bin/activate`

4. **Install dependencies**
```cmd
   pip install -r requirements.txt
```

5. **Configure environment variables**
   - Edit `.env` file
   - Add your Anthropic API key

6. **Run the server**
```cmd
   cd backend
   uvicorn app.main:app --reload
```

7. **Access the API**
   - API: http://localhost:8000
   - Documentation: http://localhost:8000/docs

---

## Project Timeline

### Day 1: Setup & Architecture ✓
- [x] Define tech stack
- [x] Set up development environment
- [x] Create project structure
- [x] Design database schema
- [x] Create basic FastAPI server

### Day 2: Data Upload & Processing
- [ ] Build file upload endpoint
- [ ] Implement CSV/Excel parsing
- [ ] Data validation and cleaning
- [ ] Store dataset metadata

### Day 3: AI Integration
- [ ] Connect to Claude API
- [ ] Create analysis prompts
- [ ] Test with sample datasets
- [ ] Handle API errors

### Day 4: Insights Generation
- [ ] Automated trend analysis
- [ ] Statistical summaries
- [ ] Key metrics extraction
- [ ] Natural language insights

### Day 5: Visualization Engine
- [ ] Integrate charting library
- [ ] Auto-generate chart types
- [ ] Interactive visualizations
- [ ] Chart customization

### Day 6: Dashboard Builder
- [ ] Dashboard layout system
- [ ] Save/load dashboards
- [ ] Export functionality
- [ ] Multiple dataset support

### Day 7: UI Polish
- [ ] Improve user interface
- [ ] Add loading states
- [ ] Error handling
- [ ] User feedback

### Day 8: Testing
- [ ] End-to-end testing
- [ ] Bug fixes
- [ ] Performance optimization
- [ ] Real-world data testing

### Day 9: Documentation & Demo
- [ ] User guide
- [ ] API documentation
- [ ] Demo preparation
- [ ] Final presentation

---

## API Endpoints

### Current Endpoints

- **GET /** - Welcome message
- **GET /api/health** - Health check

### Planned Endpoints

- **POST /api/upload** - Upload dataset
- **GET /api/datasets** - List all datasets
- **GET /api/datasets/{id}** - Get dataset details
- **POST /api/analyze/{id}** - Generate AI insights
- **GET /api/visualize/{id}** - Get visualizations
- **POST /api/dashboard** - Create dashboard

---

## Development Notes

### Current Status
Day 1 Complete! ✓
- Project structure created
- Database models defined
- FastAPI server running
- Service classes ready

### Next Steps
- Implement file upload functionality
- Add data processing logic
- Test with sample CSV files

---

## Author
**Student Name**: [Your Name]  
**Project**: Abschlussprojekt  
**Duration**: 9 days  
**Institution**: [Your School]

---

## License
This project is created for educational purposes.
```

2. **Click inside the empty `README.md` file**

3. **Paste the text:**
   - Press **Ctrl + V**

4. **Save the file:**
   - Press **Ctrl + S**

---

### **Step 3: Verify the file was created**

Your **left sidebar** should now show:
```
AI-DATA-ANALYTICS
├── backend
├── venv
├── .env
├── .gitignore
└── README.md              ← NEW! ✓