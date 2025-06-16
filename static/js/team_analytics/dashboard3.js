const labels = JSON.parse(document.getElementById('labels').textContent);
const sprint_values = JSON.parse(document.getElementById('sprint-values').textContent);
const base_running_values = JSON.parse(document.getElementById('base-running-values').textContent);
const long_throw_values = JSON.parse(document.getElementById('long-throw-values').textContent);

// グラフ生成関数
function createLineChart(canvasId, label, data, borderColor, backgroundColor, yAxisTitle) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: label,
                data: data,
                borderColor: borderColor,
                backgroundColor: backgroundColor,
                fill: true,
                tension: 0,
                pointRadius: 5,
                pointHoverRadius: 7,
            }],
        },
        options: {
            scales: {
                y: {
                    beginAtZero: false,
                    title: {
                        display: true,
                        text: yAxisTitle,
                    },
                },
                x: {
                    title: {
                        display: true,
                        text: '年月',
                    },
                },
            },
            responsive: true,
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                },
            },
        },
    });
}

document.addEventListener('DOMContentLoaded', function () {
    createLineChart(
        'sprintChart',
        '50m走平均タイム（秒）',
        sprint_values,
        'rgba(75, 192, 192, 1)',
        'rgba(75, 192, 192, 0.2)',
        '秒'
    );

    createLineChart(
        'baseRunningChart',
        'ベースランニング平均タイム（秒）',
        base_running_values,
        'rgba(255, 99, 132, 1)',
        'rgba(255, 99, 132, 0.2)',
        '秒'
    );

    createLineChart(
        'longThrowChart',
        '遠投平均距離（m）',
        long_throw_values,
        'rgba(54, 162, 235, 1)',
        'rgba(54, 162, 235, 0.2)',
        'メートル'
    );
});