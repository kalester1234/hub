// Admin Dashboard Charts
document.addEventListener('DOMContentLoaded', function() {
    // Load Chart.js if not already loaded
    if (typeof Chart === 'undefined') {
        const script = document.createElement('script');
        script.src = '{% static "js/chart.js" %}';
        script.onload = initializeCharts;
        document.head.appendChild(script);
    } else {
        initializeCharts();
    }

    function initializeCharts() {
        // Appointment Trends Chart
        const ctx = document.getElementById('appointmentChart');
        if (ctx) {
            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                    datasets: [{
                        label: 'Appointments',
                        data: [12, 19, 3, 5, 2, 3],
                        borderColor: '#00897B',
                        backgroundColor: 'rgba(0, 137, 123, 0.1)',
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        }

        // Status Distribution Chart
        const statusCtx = document.getElementById('statusChart');
        if (statusCtx) {
            new Chart(statusCtx, {
                type: 'doughnut',
                data: {
                    labels: ['Completed', 'Pending', 'Confirmed', 'Cancelled'],
                    datasets: [{
                        data: [{{ appointment_overview.completed }}, {{ appointment_counts.pending }}, {{ appointment_counts.upcoming }}, {{ appointment_counts.total|add:appointment_counts.pending|add:appointment_counts.upcoming|add:appointment_counts.completed|sub:appointment_counts.total }}],
                        backgroundColor: ['#00897B', '#FFC107', '#2196F3', '#F44336'],
                        borderWidth: 0
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            position: 'bottom'
                        }
                    }
                }
            });
        }
    }
});
