from flask import Flask, render_template, request, jsonify
import math
import json

app = Flask(__name__)

def calculate_investment(initial, rate, years, compound, inflation_rate, tax_rate, deposits, withdrawals, slider_unit):
    total_months = years * 12
    balance = initial
    total_deposits = 0
    total_withdrawals = 0
    total_interest = 0
    total_tax = 0
    monthly_rate = rate / compound
    monthly_inflation = inflation_rate / 12

    yearly_data = {}
    chart_data = {
        'months': [],
        'years': [],
        'balances': [],
        'contributions': [],
        'withdrawals': [],
        'deposits': [],
        'interest': [],
        'withdrawals_this_month': []
    }

    for month in range(1, total_months + 1):
        year = math.ceil(month / 12)
        if year not in yearly_data:
            yearly_data[year] = {
                'starting_balance': balance,
                'deposits': 0,
                'total_deposits': total_deposits,
                'withdrawals': 0,
                'total_withdrawals': total_withdrawals,
                'interest': 0,
                'total_interest': total_interest,
                'taxes': 0,
                'total_taxes': total_tax,
                'ending_balance': 0,
                'months': []
            }

        # Deposits this month
        deposit_this_month = 0
        for dep in deposits:
            period_start = dep['start'] if slider_unit == 'months' else dep['start'] * 12
            period_end = dep['end'] if slider_unit == 'months' else dep['end'] * 12
            if period_start <= month <= period_end:
                deposit_this_month += dep['amount']
        balance += deposit_this_month
        total_deposits += deposit_this_month
        yearly_data[year]['deposits'] += deposit_this_month
        yearly_data[year]['total_deposits'] = total_deposits

        # Interest this month
        interest_this_month = balance * monthly_rate
        tax_this_month = interest_this_month * tax_rate
        net_interest = interest_this_month - tax_this_month
        balance += net_interest
        total_interest += interest_this_month
        total_tax += tax_this_month
        yearly_data[year]['interest'] += interest_this_month
        yearly_data[year]['total_interest'] = total_interest
        yearly_data[year]['taxes'] += tax_this_month
        yearly_data[year]['total_taxes'] = total_tax

        # Withdrawals this month
        withdrawal_this_month = 0
        for wth in withdrawals:
            period_start = wth['start'] if slider_unit == 'months' else wth['start'] * 12
            period_end = wth['end'] if slider_unit == 'months' else wth['end'] * 12
            if period_start <= month <= period_end:
                withdrawal_this_month += wth['amount']
        balance -= withdrawal_this_month
        total_withdrawals += withdrawal_this_month
        yearly_data[year]['withdrawals'] += withdrawal_this_month
        yearly_data[year]['total_withdrawals'] = total_withdrawals

        # Record monthly data with absolute month
        yearly_data[year]['months'].append({
            'month': month,  # Changed to absolute month number
            'starting_balance': balance - net_interest + withdrawal_this_month - deposit_this_month,
            'deposit_this_month': deposit_this_month,
            'total_deposits': total_deposits,
            'withdrawal_this_month': withdrawal_this_month,
            'total_withdrawals': total_withdrawals,
            'interest_this_month': interest_this_month,
            'total_interest': total_interest,
            'taxes': tax_this_month,
            'total_taxes': total_tax,
            'ending_balance': balance
        })
        yearly_data[year]['ending_balance'] = balance

        # Chart data with absolute month
        chart_data['months'].append(month)  # Changed to absolute month number
        chart_data['years'].append(year)
        chart_data['balances'].append(balance)
        chart_data['contributions'].append(total_deposits + initial)
        chart_data['withdrawals'].append(total_withdrawals)
        chart_data['deposits'].append(deposit_this_month)
        chart_data['interest'].append(interest_this_month)
        chart_data['withdrawals_this_month'].append(withdrawal_this_month)

    # Calculate totals
    final_balance = balance
    adjusted_final_balance = final_balance / ((1 + monthly_inflation) ** total_months)
    effective_rate = ((final_balance / initial) ** (1 / years) - 1) * 100 if initial > 0 else 0

    totals = {
        'final_balance': round(final_balance, 2),
        'adjusted_final_balance': round(adjusted_final_balance, 2),
        'total_deposits': round(total_deposits, 2),
        'total_withdrawals': round(total_withdrawals, 2),
        'total_interest': round(total_interest, 2),
        'total_tax': round(total_tax, 2),
        'effective_rate': round(effective_rate, 2)
    }

    return totals, yearly_data, chart_data

@app.route('/', methods=['GET', 'POST'])
def index():
    # Default values
    defaults = {
        'initial': 1000.00,
        'rate': 5.0,
        'years': 30,
        'compound': 12,
        'inflation_rate': 2.0,
        'tax_rate': 15.0,
        'slider_unit': 'months',
        'deposits': [],
        'withdrawals': []
    }

    if request.method == 'GET':
        # Calculate initial data for GET request
        totals, yearly_data, chart_data = calculate_investment(
            defaults['initial'],
            defaults['rate'] / 100,
            defaults['years'],
            defaults['compound'],
            defaults['inflation_rate'] / 100,
            defaults['tax_rate'] / 100,
            defaults['deposits'],
            defaults['withdrawals'],
            defaults['slider_unit']
        )
        # Pass chart_data as JSON string
        chart_data_json = json.dumps(chart_data)
        return render_template('index.html', **defaults, totals=totals, yearly_data=yearly_data, chart_data_json=chart_data_json)

    elif request.method == 'POST':
        # Parse form data
        initial = float(request.form.get('initial', 0))
        rate = float(request.form.get('rate', 0)) / 100
        years = int(request.form.get('years', 1))
        compound = int(request.form.get('compound', 12))
        inflation_rate = float(request.form.get('inflation_rate', 0)) / 100
        tax_rate = float(request.form.get('tax_rate', 0)) / 100
        slider_unit = request.form.get('slider_unit', 'months')

        # Parse deposits
        deposit_count = int(request.form.get('deposit_count', 0))
        deposits = []
        for i in range(deposit_count):
            start = int(request.form.get(f'deposit_start_{i}', 1))
            end = int(request.form.get(f'deposit_end_{i}', 1))
            amount = float(request.form.get(f'deposit_amount_{i}', 0))
            deposits.append({'start': start, 'end': end, 'amount': amount})

        # Parse withdrawals
        withdrawal_count = int(request.form.get('withdrawal_count', 0))
        withdrawals = []
        for i in range(withdrawal_count):
            start = int(request.form.get(f'withdrawal_start_{i}', 1))
            end = int(request.form.get(f'withdrawal_end_{i}', 1))
            amount = float(request.form.get(f'withdrawal_amount_{i}', 0))
            withdrawals.append({'start': start, 'end': end, 'amount': amount})

        # Calculate data
        totals, yearly_data, chart_data = calculate_investment(
            initial, rate, years, compound, inflation_rate, tax_rate, deposits, withdrawals, slider_unit
        )

        # Return JSON for AJAX
        return jsonify({
            'totals': totals,
            'yearly_data': yearly_data,
            'chart_data': chart_data
        })

# Custom filter for number formatting
@app.template_filter('format_number')
def format_number(value):
    return "{:,.2f}".format(value)

if __name__ == '__main__':
    app.run(debug=True)
