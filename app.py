import json
import pandas as pd
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import os

# ==============================================================================
# FLASK APP INITIALIZATION
# ==============================================================================
app = Flask(__name__)
# A secret key is required for session management to store uploaded data
app.secret_key = os.urandom(24)

# ==============================================================================
# DATA SIMULATION (FALLBACK/SAMPLE DATA)
# ==============================================================================
SIMULATED_DATA = {
    "influencers": [
        { "id": 1, "name": 'Aisha Sharma', "category": 'Fitness', "gender": 'Female', "followers": 2500000, "platform": 'Instagram' },
        { "id": 2, "name": 'Rohan Verma', "category": 'Wellness', "gender": 'Male', "followers": 800000, "platform": 'YouTube' },
        { "id": 3, "name": 'Priya Patel', "category": 'Nutrition', "gender": 'Female', "followers": 500000, "platform": 'Instagram' },
        { "id": 4, "name": 'Vikram Singh', "category": 'Fitness', "gender": 'Male', "followers": 5000000, "platform": 'YouTube' },
        { "id": 5, "name": 'Sneha Gupta', "category": 'Wellness', "gender": 'Female', "followers": 150000, "platform": 'Twitter' },
        { "id": 6, "name": 'Arjun Reddy', "category": 'Grit/Motivation', "gender": 'Male', "followers": 1200000, "platform": 'Instagram' },
    ],
    "tracking_data": [
        { "source": 'influencer', "campaign": 'MB_SummerFit', "influencer_id": 1, "product": 'MuscleBlaze', "date": '2024-06-01', "orders": 150, "revenue": 45000 },
        { "source": 'influencer', "campaign": 'MB_SummerFit', "influencer_id": 1, "product": 'MuscleBlaze', "date": '2024-06-15', "orders": 120, "revenue": 38000 },
        { "source": 'influencer', "campaign": 'MB_SummerFit', "influencer_id": 6, "product": 'MuscleBlaze', "date": '2024-06-20', "orders": 200, "revenue": 65000 },
        { "source": 'influencer', "campaign": 'HKV_Wellness', "influencer_id": 2, "product": 'HKVitals', "date": '2024-06-05', "orders": 80, "revenue": 24000 },
        { "source": 'influencer', "campaign": 'HKV_Wellness', "influencer_id": 2, "product": 'HKVitals', "date": '2024-06-25', "orders": 95, "revenue": 29000 },
        { "source": 'influencer', "campaign": 'HKV_Wellness', "influencer_id": 3, "product": 'HKVitals', "date": '2024-06-10', "orders": 50, "revenue": 15000 },
        { "source": 'influencer', "campaign": 'Gritzo_Power', "influencer_id": 4, "product": 'Gritzo', "date": '2024-06-12', "orders": 300, "revenue": 120000 },
        { "source": 'influencer', "campaign": 'Gritzo_Power', "influencer_id": 5, "product": 'Gritzo', "date": '2024-06-18', "orders": 20, "revenue": 5000 },
        { "source": 'organic', "campaign": 'Organic', "influencer_id": None, "product": 'MuscleBlaze', "date": '2024-06-01', "orders": 500, "revenue": 150000 },
        { "source": 'organic', "campaign": 'Organic', "influencer_id": None, "product": 'HKVitals', "date": '2024-06-01', "orders": 300, "revenue": 90000 },
        { "source": 'organic', "campaign": 'Organic', "influencer_id": None, "product": 'Gritzo', "date": '2024-06-01', "orders": 150, "revenue": 60000 },
    ],
    "payouts": [
        { "influencer_id": 1, "basis": 'post', "rate": 40000, "orders": 0, "total_payout": 80000 },
        { "influencer_id": 2, "basis": 'post', "rate": 50000, "orders": 0, "total_payout": 100000 },
        { "influencer_id": 3, "basis": 'order', "rate": 100, "orders": 50, "total_payout": 5000 },
        { "influencer_id": 4, "basis": 'post', "rate": 150000, "orders": 0, "total_payout": 150000 },
        { "influencer_id": 5, "basis": 'order', "rate": 80, "orders": 20, "total_payout": 1600 },
        { "influencer_id": 6, "basis": 'post', "rate": 60000, "orders": 0, "total_payout": 60000 },
    ]
}

# ==============================================================================
# DATA PROCESSING LOGIC
# ==============================================================================
def process_data(data_source, filters):
    influencers = data_source['influencers']
    tracking_data = data_source['tracking_data']
    payouts = data_source['payouts']

    filtered_influencers = [
        inf for inf in influencers
        if (filters['platform'] == 'All' or inf['platform'] == filters['platform']) and
           (filters['category'] == 'All' or inf['category'] == filters['category']) and
           (filters['search_term'] == '' or filters['search_term'].lower() in inf['name'].lower())
    ]
    filtered_influencer_ids = {inf['id'] for inf in filtered_influencers}

    filtered_tracking_data = [
        t for t in tracking_data
        if (filters['brand'] == 'All' or t['product'] == filters['brand']) and
           (t.get('influencer_id') is None or t.get('influencer_id') in filtered_influencer_ids)
    ]

    influencer_details = []
    for inf in filtered_influencers:
        inf_payout = next((p for p in payouts if p['influencer_id'] == inf['id']), {'total_payout': 0})
        inf_tracking = [t for t in filtered_tracking_data if t.get('influencer_id') == inf['id']]
        
        total_revenue = sum(item['revenue'] for item in inf_tracking)
        total_orders = sum(item['orders'] for item in inf_tracking)
        total_cost = inf_payout['total_payout']
        roas = total_revenue / total_cost if total_cost > 0 else 0

        details = inf.copy()
        details.update({'total_revenue': total_revenue, 'total_orders': total_orders, 'total_cost': total_cost, 'roas': roas})
        influencer_details.append(details)

    campaign_revenue = sum(t['revenue'] for t in filtered_tracking_data if t['source'] == 'influencer')
    campaign_cost = sum(p['total_payout'] for p in payouts if p['influencer_id'] in filtered_influencer_ids)
    campaign_roas = campaign_revenue / campaign_cost if campaign_cost > 0 else 0

    organic_revenue = sum(
        t['revenue'] for t in data_source['tracking_data']
        if t['source'] == 'organic' and (filters['brand'] == 'All' or t['product'] == filters['brand'])
    )
    
    incremental_revenue = campaign_revenue - organic_revenue
    incremental_roas = incremental_revenue / campaign_cost if campaign_cost > 0 else 0

    revenue_by_platform = {}
    for inf in influencer_details:
        if inf['total_revenue'] > 0:
            platform = inf['platform']
            revenue_by_platform[platform] = revenue_by_platform.get(platform, 0) + inf['total_revenue']
    
    chart_data_platform = [{'name': k, 'revenue': v} for k, v in revenue_by_platform.items()]
    top_influencers_by_revenue = sorted(influencer_details, key=lambda x: x['total_revenue'], reverse=True)[:5]
    total_orders = sum(inf['total_orders'] for inf in influencer_details)

    return {
        'influencer_details': influencer_details, 'campaign_revenue': campaign_revenue, 'campaign_cost': campaign_cost,
        'campaign_roas': campaign_roas, 'incremental_roas': incremental_roas, 'chart_data_platform': chart_data_platform,
        'top_influencers_by_revenue': top_influencers_by_revenue, 'total_orders': total_orders, 'overall_campaign_roas': campaign_roas
    }

# ==============================================================================
# FLASK ROUTES
# ==============================================================================
@app.route('/')
def index():
    data_source = session.get('user_data', SIMULATED_DATA)
    active_file = session.get('active_file', 'Sample Data')

    initial_filters = {'brand': 'All', 'platform': 'All', 'category': 'All', 'search_term': ''}
    
    all_influencers = data_source.get('influencers', [])
    all_tracking_data = data_source.get('tracking_data', [])

    brands = ['All'] + sorted(list(set(t['product'] for t in all_tracking_data if t.get('product'))))
    platforms = ['All'] + sorted(list(set(i['platform'] for i in all_influencers if i.get('platform'))))
    categories = ['All'] + sorted(list(set(i['category'] for i in all_influencers if i.get('category'))))
    
    context = {
        'brands': brands, 'platforms': platforms, 'categories': categories,
        'data': process_data(data_source, initial_filters),
        'active_file': active_file
    }
    return render_template('index.html', **context)

@app.route('/update_data', methods=['POST'])
def update_data():
    data_source = session.get('user_data', SIMULATED_DATA)
    filters = request.get_json()
    filters['search_term'] = filters.get('search_term', '').strip()
    updated_data = process_data(data_source, filters)
    return jsonify(updated_data)

@app.route('/upload', methods=['POST'])
def upload_files():
    try:
        influencers_file = request.files.get('influencers_file')
        tracking_file = request.files.get('tracking_data_file')
        payouts_file = request.files.get('payouts_file')

        user_data = {}
        if influencers_file and tracking_file and payouts_file:
            user_data['influencers'] = pd.read_csv(influencers_file).to_dict(orient='records')
            user_data['tracking_data'] = pd.read_csv(tracking_file).to_dict(orient='records')
            user_data['payouts'] = pd.read_csv(payouts_file).to_dict(orient='records')
            
            session['user_data'] = user_data
            session['active_file'] = 'Uploaded CSVs'
    except Exception as e:
        print(f"Error processing uploaded files: {e}")
    return redirect(url_for('index'))

@app.route('/reset')
def reset_to_sample():
    session.pop('user_data', None)
    session.pop('active_file', None)
    return redirect(url_for('index'))

# ==============================================================================
# MAIN EXECUTION
# ==============================================================================
if __name__ == '__main__':
    app.run(debug=True)
