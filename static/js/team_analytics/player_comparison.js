const labels = JSON.parse(document.getElementById('labels').textContent);
const team_values = JSON.parse(document.getElementById('team-values').textContent);
const player_values = JSON.parse(document.getElementById('player-values').textContent);

// グラフ生成関数
function createLineChart(canvasId, title, playerData, teamData, yAxisTitle) {
  const ctx = document.getElementById(canvasId).getContext('2d');
  return new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [
        {
          label: '個人',
          data: playerData,
          borderColor: 'rgba(75, 192, 192, 1)',
          backgroundColor: 'rgba(75, 192, 192, 0.2)',
          fill: false,
          tension: 0,
          pointRadius: 5,
          pointHoverRadius: 7,
          pointStyle: 'circle',
        },
        {
          label: 'チーム平均',
          data: teamData,
          borderColor: 'rgba(255, 99, 132, 1)',
          backgroundColor: 'rgba(255, 99, 132, 0.2)',
          fill: false,
          tension: 0,
          borderWidth: 3,
          pointRadius: 6,
          pointHoverRadius: 8,
          pointStyle: 'triangle',
          borderDash: [5, 5],
        }
      ]

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
        title: {
          display: true,
          text: title,
        },
      },
    },
  });
}

document.addEventListener('DOMContentLoaded', function () {
  createLineChart(
    'sprintChart',
    '50m走平均タイム（秒）',
    player_values["50m走"],
    team_values["50m走"],
    '秒'
  );

  createLineChart(
    'baseRunningChart',
    'ベースランニング平均タイム（秒）',
    player_values["ベースラン"],
    team_values["ベースラン"],
    '秒'
  );

  createLineChart(
    'longThrowChart',
    '遠投平均距離（m）',
    player_values["遠投"],
    team_values["遠投"],
    'm'
  );
  createLineChart(
    'straightBallSpeedChart',
    'ストレート平均球速（km/h）',
    player_values["ストレート球速"],
    team_values["ストレート球速"],
    'km/h'
  );
  createLineChart(
    'hitBallSpeedChart',
    '打球平均速度（km/h）',
    player_values["打球速度"],
    team_values["打球速度"],
    'km/h'
  );
  createLineChart(
    'swingSpeedChart',
    'スイング平均速度（km/h）',
    player_values["スイング速度"],
    team_values["スイング速度"],
    'km/h'
  );
  createLineChart(
    'benchPressChart',
    'ベンチプレス平均重量（kg）',
    player_values["ベンチプレス"],
    team_values["ベンチプレス"],
    'kg'
  );
  createLineChart(
    'squatChart',
    'スクワット平均重量（kg）',
    player_values["スクワット"],
    team_values["スクワット"],
    'kg'
  );
});