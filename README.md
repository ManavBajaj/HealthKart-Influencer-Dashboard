# HealthKart Influencer Marketing ROI Dashboard

## 1. Objective

This project is an open-source tool built to help HealthKart track and visualize the performance and Return on Investment (ROI) of its influencer marketing campaigns. The dashboard provides insights into campaign effectiveness, influencer performance, and financial metrics like Return on Ad Spend (ROAS), with a key focus on calculating **Incremental ROAS**.

The tool allows marketing and data teams to move beyond vanity metrics and understand the true financial impact of their influencer collaborations across various brands (MuscleBlaze, HKVitals, Gritzo) and platforms (Instagram, YouTube, Twitter).

## 2. Features

* **Interactive Dashboard:** A clean, fast, and visually appealing single-page application.
* **Data Ingestion:** Supports dynamic analysis by allowing users to upload their own campaign data via CSV files. It also includes a pre-loaded sample dataset for immediate demonstration.
* **KPI Tracking:** At-a-glance cards for key metrics like Total Revenue, Total Spend, Overall ROAS, Incremental ROAS, and Total Orders.
* **Dynamic Filtering:** Filter the entire dashboard by Brand, Influencer Category, Platform, or search for a specific influencer by name.
* **Visual Insights:**
    * A doughnut chart showing the revenue contribution by each social media platform.
    * A horizontal bar chart highlighting the top 5 performing influencers by the revenue they've generated.
* **Detailed Performance Table:** A comprehensive table listing all influencers, their stats, and their individual ROAS, with color-coding to easily spot high and low performers.
* **Data Export:** Export the currently filtered view of the influencer performance table to a CSV file for offline analysis or reporting.

## 3. Tech Stack

The dashboard is built with a simple and robust Python-based web stack:

* **Backend:** **Flask** (a lightweight Python web framework)
    * Handles data processing, calculations, and serving the application.
* **Data Manipulation:** **Pandas**
    * Used for reading and processing the uploaded CSV files.
* **Frontend:** **HTML, CSS, and vanilla JavaScript**
    * The structure and styling of the dashboard. JavaScript is used to handle user interactions (filtering, etc.) and make the dashboard dynamic without page reloads.
* **Visualizations:** **Chart.js**
    * A powerful and easy-to-use JavaScript library for creating responsive charts.
* **Icons:** **Lucide Icons**
    * For a clean and modern set of icons throughout the interface.

## 4. Setup and Installation

To run this dashboard on your local machine, follow these steps:

**Prerequisites:**
* Python 3.x installed
* `pip` (Python package installer)

**Folder Structure:**
For the application to work correctly, your files must be organized in the following structure. The `static` and `templates` folders are essential for Flask to find the CSS, JavaScript, and HTML files.


/your-project-folder/
├── app.py
│
├── static/
│   ├── style.css
│   └── script.js
│
└── templates/
└── index.html


**Instructions:**

1.  **Organize your files** into the structure shown above.

2.  **Navigate to the project directory** in your terminal:
    ```bash
    cd /path/to/your-project-folder/
    ```

3.  **Create a virtual environment** (recommended):
    ```bash
    # For Mac/Linux
    python3 -m venv venv
    source venv/bin/activate

    # For Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```

4.  **Install the required Python packages:**
    ```bash
    pip install Flask pandas
    ```

5.  **Run the Flask application:**
    ```bash
    python app.py
    ```

6.  **Open your web browser** and go to the following address:
    [http://127.0.0.1:5000](http://127.0.0.1:5000)

The dashboard should now be running with the sample data.

## 5. Data Modeling & Assumptions

### Data Schema

The dashboard requires three separate CSV files for data ingestion. The files must have the following columns:

1.  `influencers.csv`
    * `id`: Unique identifier for the influencer.
    * `name`: Full name of the influencer.
    * `category`: Niche (e.g., Fitness, Wellness, Nutrition).
    * `gender`: Gender of the influencer.
    * `followers`: Follower count.
    * `platform`: Social media platform (e.g., Instagram, YouTube).

2.  `tracking_data.csv`
    * `source`: The origin of the revenue (must be either `influencer` or `organic`).
    * `campaign`: The name of the campaign.
    * `influencer_id`: The ID of the influencer who drove the sale (matches `influencers.csv`). Can be empty for organic sales.
    * `product`: The brand associated with the sale (e.g., MuscleBlaze, HKVitals).
    * `date`: Date of the transaction.
    * `orders`: Number of orders.
    * `revenue`: Revenue generated from the orders.

3.  `payouts.csv`
    * `influencer_id`: The ID of the influencer being paid.
    * `basis`: The payment model (`post` or `order`).
    * `rate`: The rate per post or per order.
    * `orders`: The number of orders to calculate the payout (if basis is `order`).
    * `total_payout`: The final amount paid to the influencer for the campaign.

### Key Analytical Assumption: Incremental ROAS

The calculation for **Incremental ROAS** is one of the most important features of this dashboard. It aims to measure the *true* return by isolating the revenue generated *above and beyond* what would have been earned organically.

**Formula:**
`Incremental ROAS = (Influencer-Driven Revenue - Baseline Organic Revenue) / Total Influencer Spend`

**The core assumption is that the `tracking_data.csv` file contains entries where `source` is marked as `organic`.** This organic data represents the baseline sales performance for a given period *without* any influencer activity. The dashboard subtracts this baseline from the influencer-driven revenue to find the "incremental lift" before calculating the final ROAS. This provides a much more accurate picture of an influencer's impact than a simple ROAS calculation.

## 6. How to Use the Dashboard

1.  **View Sample Data:** The dashboard loads with a pre-configured sample dataset. You can immediately start using the filters to see how the KPIs and charts react.
2.  **Upload Your Data:**
    * Prepare your three CSV files (`influencers.csv`, `tracking_data.csv`, `payouts.csv`) according to the schema defined above.
    * Use the upload section at the top of the dashboard to select all three files.
    * Click "Upload & Analyze". The dashboard will reload and display the analysis for your data.
3.  **Filter and Analyze:** Use the dropdowns and search bar to drill down into specific segments of your campaign.
4.  **Export:** Click the "Export Performance" button to download a CSV of the data currently displayed in the main table.
