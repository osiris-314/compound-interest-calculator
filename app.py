from flask import Flask, render_template, request

app = Flask(__name__)

# Custom Jinja filter to format numbers with commas and 2 decimal places (used only for display, not input values)
@app.template_filter('format_number')
def format_number(value):
    try:
        return "{:,.2f}".format(float(value))
    except (ValueError, TypeError):
        return value

def calculate_compound_interest(initial, rate, years, compound, deposits, withdrawals, inflation_rate=0):
    balance = round(float(initial), 2)
    annual_rate = round(float(rate) / 100, 4)
    inflation_rate = round(float(inflation_rate) / 100, 4)
    total_months = int(years) * 12
    compound_per_year = int(compound)
    monthly_rate = round(annual_rate / compound_per_year, 6)
    monthly_inflation = round(inflation_rate / 12, 6)
    total_deposits = 0
    total_withdrawals = 0
    total_interest = 0
    total_contributions = 0
    adjusted_balance = balance

    effective_rate = round(((1 + annual_rate / compound_per_year) ** compound_per_year - 1) * 100, 2)

    yearly_data = {i: {'starting_balance': 0, 'ending_balance': 0, 'deposits': 0, 'withdrawals': 0, 'interest': 0, 'months': []} for i in range(1, years + 1)}
    chart_data = {'months': [], 'contributions': [], 'balances': []}

    for month in range(1, total_months + 1):
        year = (month - 1) // 12 + 1
        starting_balance = round(balance, 2)
        monthly_interest = round(balance * monthly_rate, 2)
        balance = round(balance + monthly_interest, 2)
        total_interest = round(total_interest + monthly_interest, 2)

        deposit_amount = 0
        for dep in deposits:
            start = dep['start_month']
            end = dep['end_month']
            if start <= month <= end:
                deposit_amount = round(deposit_amount + float(dep['amount']), 2)
                balance = round(balance + float(dep['amount']), 2)
                total_deposits = round(total_deposits + float(dep['amount']), 2)
                total_contributions = round(total_contributions + float(dep['amount']), 2)

        withdrawal_amount = 0
        for wth in withdrawals:
            start = wth['start_month']
            end = wth['end_month']
            if start <= month <= end:
                withdrawal_amount = round(withdrawal_amount + float(wth['amount']), 2)
                if balance >= float(wth['amount']):
                    balance = round(balance - float(wth['amount']), 2)
                    total_withdrawals = round(total_withdrawals + float(wth['amount']), 2)
                    total_contributions = round(total_contributions - float(wth['amount']), 2)
                else:
                    total_withdrawals = round(total_withdrawals + balance, 2)
                    total_contributions = round(total_contributions - balance, 2)
                    balance = 0

        adjusted_balance = round(balance / (1 + monthly_inflation) ** month, 2)

        month_data = {
            'month': month,
            'year': year,
            'starting_balance': starting_balance,
            'ending_balance': balance,
            'interest_this_month': monthly_interest,
            'deposit_this_month': deposit_amount,
            'withdrawal_this_month': withdrawal_amount
        }
        yearly_data[year]['months'].append(month_data)

        if month % 12 == 1:
            yearly_data[year]['starting_balance'] = starting_balance
        yearly_data[year]['ending_balance'] = balance
        yearly_data[year]['deposits'] = round(yearly_data[year]['deposits'] + deposit_amount, 2)
        yearly_data[year]['withdrawals'] = round(yearly_data[year]['withdrawals'] + withdrawal_amount, 2)
        yearly_data[year]['interest'] = round(yearly_data[year]['interest'] + monthly_interest, 2)

        chart_data['months'].append(month)
        chart_data['contributions'].append(round(total_contributions, 2))
        chart_data['balances'].append(round(balance, 2))

    totals = {
        'final_balance': balance,
        'total_deposits': total_deposits,
        'total_withdrawals': total_withdrawals,
        'total_interest': total_interest,
        'adjusted_final_balance': adjusted_balance,
        'effective_rate': effective_rate
    }

    return totals, yearly_data, chart_data

@app.route('/', methods=['GET', 'POST'])
def index():
    totals = None
    yearly_data = None
    chart_data = None
    initial = 1000
    rate = 5
    years = 10
    compound = 12
    inflation_rate = 0
    slider_unit = 'months'
    deposits = []  # Start with empty list
    withdrawals = []

    if request.method == 'POST':
        initial = float(request.form.get('initial', 1000))
        rate = float(request.form.get('rate', 5))
        years = int(request.form.get('years', 10))
        compound = int(request.form.get('compound', 12))
        inflation_rate = float(request.form.get('inflation_rate', 0))
        slider_unit = request.form.get('slider_unit', 'months')

        # Process deposits from form data
        deposits = []
        deposit_count = int(request.form.get('deposit_count', 0))
        for i in range(deposit_count):
            start = request.form.get(f'deposit_start_{i}')
            end = request.form.get(f'deposit_end_{i}')
            amount = request.form.get(f'deposit_amount_{i}', '')
            print(f"Deposit {i}: start={start}, end={end}, amount={amount}")  # Debugging
            if start and end:
                try:
                    start = int(start)
                    end = int(end)
                    amount = float(amount) if amount else 0
                    if slider_unit == 'years':
                        start = (start - 1) * 12 + 1
                        end = end * 12
                    deposits.append({
                        'start_month': start,
                        'end_month': end,
                        'amount': round(amount, 2)
                    })
                except ValueError as e:
                    print(f"Deposit {i} parsing error: {e}, using amount=0")
                    if slider_unit == 'years':
                        start = (int(start) - 1) * 12 + 1 if start else 1
                        end = int(end) * 12 if end else 12
                    deposits.append({
                        'start_month': start,
                        'end_month': end,
                        'amount': 0
                    })

        # Process withdrawals from form data
        withdrawals = []
        withdrawal_count = int(request.form.get('withdrawal_count', 0))
        for i in range(withdrawal_count):
            start = request.form.get(f'withdrawal_start_{i}')
            end = request.form.get(f'withdrawal_end_{i}')
            amount = request.form.get(f'withdrawal_amount_{i}', '')
            print(f"Withdrawal {i}: start={start}, end={end}, amount={amount}")  # Debugging
            if start and end:
                try:
                    start = int(start)
                    end = int(end)
                    amount = float(amount) if amount else 0
                    if slider_unit == 'years':
                        start = (start - 1) * 12 + 1
                        end = end * 12
                    withdrawals.append({
                        'start_month': start,
                        'end_month': end,
                        'amount': round(amount, 2)
                    })
                except ValueError as e:
                    print(f"Withdrawal {i} parsing error: {e}, using amount=0")
                    if slider_unit == 'years':
                        start = (int(start) - 1) * 12 + 1 if start else 1
                        end = int(end) * 12 if end else 12
                    withdrawals.append({
                        'start_month': start,
                        'end_month': end,
                        'amount': 0
                    })

        totals, yearly_data, chart_data = calculate_compound_interest(
            initial, rate, years, compound, deposits, withdrawals, inflation_rate
        )
    else:
        # For GET request (initial load), provide a default deposit
        deposits = [{'start_month': 1, 'end_month': 60, 'amount': 100}]

    # Prepare deposits for template rendering
    slider_deposits = []
    for dep in deposits:
        if slider_unit == 'years':
            start = (dep['start_month'] - 1) // 12 + 1
            end = dep['end_month'] // 12
            if dep['end_month'] % 12 != 0:
                end += 1
        else:
            start = dep['start_month']
            end = dep['end_month']
        slider_deposits.append({'start': start, 'end': end, 'amount': dep['amount']})

    # Prepare withdrawals for template rendering
    slider_withdrawals = []
    for wth in withdrawals:
        if slider_unit == 'years':
            start = (wth['start_month'] - 1) // 12 + 1
            end = wth['end_month'] // 12
            if wth['end_month'] % 12 != 0:
                end += 1
        else:
            start = wth['start_month']
            end = wth['end_month']
        slider_withdrawals.append({'start': start, 'end': end, 'amount': wth['amount']})

    print(f"Slider Deposits: {slider_deposits}")  # Debugging
    print(f"Slider Withdrawals: {slider_withdrawals}")  # Debugging

    return render_template('index.html', totals=totals, yearly_data=yearly_data, chart_data=chart_data,
                           initial=initial, rate=rate, years=years, compound=compound,
                           inflation_rate=inflation_rate, slider_unit=slider_unit, 
                           deposits=slider_deposits, withdrawals=slider_withdrawals)

if __name__ == '__main__':
    app.run(debug=True)