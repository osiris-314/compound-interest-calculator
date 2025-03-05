function updateDualSlider(type, index) {
    const startInput = document.querySelector(`input[name="${type}_start_${index}"]`);
    const endInput = document.querySelector(`input[name="${type}_end_${index}"]`);
    const startVal = document.getElementById(`${type}_start_val_${index}`);
    const endVal = document.getElementById(`${type}_end_val_${index}`);
    const slider = startInput.parentElement;

    let start = parseInt(startInput.value);
    let end = parseInt(endInput.value);
    const min = parseInt(startInput.min);
    const max = parseInt(startInput.max);

    if (start > end) {
        if (startInput === document.activeElement) {
            endInput.value = start;
            end = start;
        } else {
            startInput.value = end;
            start = end;
        }
    }

    startVal.textContent = start;
    endVal.textContent = end;

    const range = max - min;
    const leftPercent = ((start - min) / range) * 100;
    const rightPercent = ((end - min) / range) * 100;
    slider.style.setProperty('--left', `${leftPercent}%`);
    slider.style.setProperty('--right', `${100 - rightPercent}%`);
}

function addDeposit(years) {
    const container = document.getElementById('deposits');
    const count = container.children.length;
    const unit = document.getElementById('slider_unit').value;
    const total = (unit === 'years') ? years : years * 12;
    const defaultEnd = (unit === 'years') ? 5 : 60;
    const div = document.createElement('div');
    div.className = 'deposit-entry';
    div.innerHTML = `
        <label>Period: <span class="slider-value" id="deposit_start_val_${count}">1</span> - <span class="slider-value" id="deposit_end_val_${count}">${defaultEnd}</span></label>
        <div class="dual-slider" data-min="1" data-max="${total}" data-start="1" data-end="${defaultEnd}">
            <input type="range" name="deposit_start_${count}" class="range-start" min="1" max="${total}" value="1" oninput="updateDualSlider('deposit', ${count})">
            <input type="range" name="deposit_end_${count}" class="range-end" min="1" max="${total}" value="${defaultEnd}" oninput="updateDualSlider('deposit', ${count})">
        </div>
        <div class="amount-row">
            <label>Amount ($):</label>
            <input type="number" name="deposit_amount_${count}" value="100" min="0" step="0.01" required>
            <button type="button" onclick="this.parentElement.parentElement.remove(); updateDepositCount()">Remove</button>
        </div>
    `;
    container.appendChild(div);
    updateDepositCount();
    updateDualSlider('deposit', count);
}

function addWithdrawal(years) {
    const container = document.getElementById('withdrawals');
    const count = container.children.length;
    const unit = document.getElementById('slider_unit').value;
    const total = (unit === 'years') ? years : years * 12;
    const defaultEnd = (unit === 'years') ? 5 : 60;
    const div = document.createElement('div');
    div.className = 'withdrawal-entry';
    div.innerHTML = `
        <label>Period: <span class="slider-value" id="withdrawal_start_val_${count}">1</span> - <span class="slider-value" id="withdrawal_end_val_${count}">${defaultEnd}</span></label>
        <div class="dual-slider" data-min="1" data-max="${total}" data-start="1" data-end="${defaultEnd}">
            <input type="range" name="withdrawal_start_${count}" class="range-start" min="1" max="${total}" value="1" oninput="updateDualSlider('withdrawal', ${count})">
            <input type="range" name="withdrawal_end_${count}" class="range-end" min="1" max="${total}" value="${defaultEnd}" oninput="updateDualSlider('withdrawal', ${count})">
        </div>
        <div class="amount-row">
            <label>Amount ($):</label>
            <input type="number" name="withdrawal_amount_${count}" value="0" min="0" step="0.01" required>
            <button type="button" onclick="this.parentElement.parentElement.remove(); updateWithdrawalCount()">Remove</button>
        </div>
    `;
    container.appendChild(div);
    updateWithdrawalCount();
    updateDualSlider('withdrawal', count);
}

function updateDepositCount() {
    document.getElementById('deposit_count').value = document.getElementById('deposits').children.length;
}

function updateWithdrawalCount() {
    document.getElementById('withdrawal_count').value = document.getElementById('withdrawals').children.length;
}

function updateSliders() {
    const years = parseInt(document.getElementById('years').value);
    const unit = document.getElementById('slider_unit').value;
    const total = (unit === 'years') ? years : years * 12;
    document.querySelectorAll('.dual-slider input[type="range"]').forEach(slider => {
        const currentMax = parseInt(slider.max);
        slider.max = total;
        let value = parseInt(slider.value);
        if (value > total) slider.value = total;
        const type = slider.name.includes('deposit') ? 'deposit' : 'withdrawal';
        const index = slider.name.match(/\d+$/)[0];
        updateDualSlider(type, index);
    });
}

window.onload = function() {
    updateDepositCount();
    updateWithdrawalCount();
    document.querySelectorAll('.dual-slider').forEach(slider => {
        const type = slider.querySelector('input').name.includes('deposit') ? 'deposit' : 'withdrawal';
        const index = slider.querySelector('input').name.match(/\d+$/)[0];
        updateDualSlider(type, index);
    });
};
