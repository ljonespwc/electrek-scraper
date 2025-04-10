document.addEventListener('DOMContentLoaded', function() {
  // Tab switching functionality
  const tabs = document.querySelectorAll('.tab');
  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      // Remove active class from all tabs
      tabs.forEach(t => t.classList.remove('active'));
      // Add active class to clicked tab
      tab.classList.add('active');
      
      // Here you would normally show/hide content based on the selected tab
      const tabName = tab.dataset.tab;
      console.log(`Selected tab: ${tabName}`);
      // This would be replaced with actual content switching logic
    });
  });
  
  // Date range button functionality
  const dateButtons = document.querySelectorAll('.date-btn');
  dateButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      // Remove active class from all buttons
      dateButtons.forEach(b => b.classList.remove('active'));
      // Add active class to clicked button
      btn.classList.add('active');
      
      // In a real implementation, this would trigger a data refresh
      // For now, just log the selection
      console.log(`Selected date range: ${btn.textContent.trim()}`);
      
      // Update the chart with dummy data
      updateChart();
    });
  });
  
  // Initialize trends chart with dummy data
  const ctx = document.getElementById('trendsChart').getContext('2d');
  let trendsChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: ['Jan 2025', 'Feb 2025', 'Mar 2025', 'Apr 2025'],
      datasets: [
        {
          label: 'Average Comments',
          data: [120, 70, 85, 95],
          borderColor: 'rgb(59, 130, 246)',
          backgroundColor: 'rgba(59, 130, 246, 0.1)',
          tension: 0.3,
          yAxisID: 'y'
        },
        {
          label: 'Articles Published',
          data: [20, 33, 35, 15],
          borderColor: 'rgb(34, 197, 94)',
          backgroundColor: 'rgba(34, 197, 94, 0.1)',
          tension: 0.3,
          yAxisID: 'y1'
        }
      ]
    },
    options: {
      responsive: true,
      interaction: {
        mode: 'index',
        intersect: false,
      },
      stacked: false,
      scales: {
        y: {
          type: 'linear',
          display: true,
          position: 'left',
          title: {
            display: true,
            text: 'Average Comments'
          },
          min: 0
        },
        y1: {
          type: 'linear',
          display: true,
          position: 'right',
          title: {
            display: true,
            text: 'Articles Published'
          },
          min: 0,
          grid: {
            drawOnChartArea: false
          }
        },
        x: {
          title: {
            display: true,
            text: 'Month'
          }
        }
      },
      plugins: {
        legend: {
          position: 'bottom',
        }
      }
    }
  });
  
  // Function to update chart with different data based on selected date range
  function updateChart() {
    const activeButton = document.querySelector('.date-btn.active');
    let data1, data2;
    
    // Generate different dummy data based on the selected date range
    switch(activeButton.textContent.trim()) {
      case '3 Months':
        data1 = [95, 110, 85];
        data2 = [25, 30, 18];
        trendsChart.data.labels = ['Feb 2025', 'Mar 2025', 'Apr 2025'];
        break;
      case '6 Months':
        data1 = [120, 70, 85, 95, 110, 90];
        data2 = [20, 33, 35, 15, 28, 22];
        trendsChart.data.labels = ['Nov 2024', 'Dec 2024', 'Jan 2025', 'Feb 2025', 'Mar 2025', 'Apr 2025'];
        break;
      case '1 Year':
        data1 = [80, 90, 110, 95, 85, 100, 115, 70, 95, 105, 120, 90];
        data2 = [15, 18, 25, 30, 28, 20, 22, 35, 30, 25, 18, 20];
        trendsChart.data.labels = ['May 2024', 'Jun 2024', 'Jul 2024', 'Aug 2024', 'Sep 2024', 'Oct 2024', 
                                  'Nov 2024', 'Dec 2024', 'Jan 2025', 'Feb 2025', 'Mar 2025', 'Apr 2025'];
        break;
      case '2 Years':
        data1 = [70, 80, 95, 105, 90, 75, 85, 100, 110, 80, 90, 105, 
                115, 85, 95, 75, 80, 90, 100, 105, 115, 95, 85, 90];
        data2 = [10, 15, 20, 25, 30, 25, 20, 15, 20, 25, 30, 35, 
                30, 25, 20, 15, 20, 25, 30, 25, 20, 15, 25, 20];
        trendsChart.data.labels = Array.from({length: 24}, (_, i) => {
          const date = new Date(2023, 4 + i, 1);
          return date.toLocaleDateString('en-US', { month: 'short', year: 'numeric' });
        });
        break;
    }
    
    trendsChart.data.datasets[0].data = data1;
    trendsChart.data.datasets[1].data = data2;
    trendsChart.update();
  }
});