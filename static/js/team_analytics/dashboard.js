const sprint_labels = JSON.parse(document.getElementById('sprint-labels').textContent);
const sprint_values = JSON.parse(document.getElementById('sprint-values').textContent);

document.addEventListener('DOMContentLoaded', function () {
    const ctx = document.getElementById('sprintChart').getContext('2d');
    const sprintChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: sprint_labels,
            datasets: [{
                label: '50m走平均タイム（秒）',
                data: sprint_values,
                borderColor: 'rgba(75, 192, 192, 1)',
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                fill: true,
                tension: 0.3,
                pointRadius: 5,
                pointHoverRadius: 7,
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: false,
                    title: {
                        display: true,
                        text: '秒'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: '年月'
                    }
                }
            },
            responsive: true,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                }
            }
        }
    });
});