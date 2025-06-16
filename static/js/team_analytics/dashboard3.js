const sprint_labels = JSON.parse(document.getElementById('sprint-labels').textContent);
const sprint_values = JSON.parse(document.getElementById('sprint-values').textContent);
const base_running_labels = JSON.parse(document.getElementById('base-running-labels').textContent);
const base_running_values = JSON.parse(document.getElementById('base-running-values').textContent);

document.addEventListener('DOMContentLoaded', function () {
    const sprintCtx = document.getElementById('sprintChart').getContext('2d');
    const sprintChart = new Chart(sprintCtx, {
        type: 'line',
        data: {
            labels: sprint_labels,
            datasets: [{
                label: '50m走平均タイム（秒）',
                data: sprint_values,
                borderColor: 'rgba(75, 192, 192, 1)',
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
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
    const baseRunningCtx = document.getElementById('baseRunningChart').getContext('2d');
    const baseRunningChart = new Chart(baseRunningCtx, {
        type: 'line',
        data: {
            labels: base_running_labels,
            datasets: [{
                label: 'ベースランニング平均タイム（秒）',
                data: base_running_values,
                borderColor: 'rgba(255, 99, 132, 1)',
                backgroundColor: 'rgba(255, 99, 132, 0.2)',
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