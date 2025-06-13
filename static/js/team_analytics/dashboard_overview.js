const summary = JSON.parse(document.getElementById('summary').textContent); 

document.addEventListener('DOMContentLoaded', function () {
    // 走力チャート
    const ctx = document.getElementById('speedChart').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['50m走', 'ベースランニング'],
            datasets: [{
                label: '秒',
                data: [summary.avg_sprint_50m, summary.avg_base_running],
                backgroundColor: 'rgba(75, 192, 192, 0.5)',
            }]
        }
    });

    // 肩力チャート
    const throwingCtx = document.getElementById('throwingChart').getContext('2d');
    new Chart(throwingCtx, {
        type: 'bar',
        data: {
            labels: ['遠投', 'ストレート球速'],
            datasets: [{
                label: 'm',
                data: [summary.avg_long_throw, summary.avg_straight_ball_speed],
                backgroundColor: 'rgba(144, 238, 144, 0.5)',
            }]
        }
    });

    // 打撃チャート
    const battingCtx = document.getElementById('battingChart').getContext('2d');
    new Chart(battingCtx, {
        type: 'bar',
        data: {
            labels: ['打球速度', 'スイング速度'],
            datasets: [{
                label: 'km/h',
                data: [summary.avg_hit_ball_speed, summary.avg_swing_speed],
                backgroundColor: 'rgba(255, 159, 64, 0.5)',
            }]
        }
    });

    // 筋力チャート
    const strengthCtx = document.getElementById('strengthChart').getContext('2d');
    new Chart(strengthCtx, {
        type: 'bar',
        data: {
            labels: ['ベンチプレス', 'スクワット'],
            datasets: [{
                label: 'kg',
                data: [summary.avg_bench_press, summary.avg_squat],
                backgroundColor: 'rgba(153, 102, 255, 0.5)',
            }]
        }
    });
});