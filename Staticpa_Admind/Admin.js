var el = document.getElementById("wrapper");
        var toggleButton = document.getElementById("menu-toggle");

        toggleButton.onclick = function () {
            el.classList.toggle("toggled");
        };

        // Load Google Charts
        google.charts.load('current', { 'packages': ['corechart'] });
        google.charts.setOnLoadCallback(drawCharts);

        function drawCharts() {
            // Get the previous month name
            var monthNames = ["January", "February", "March", "April", "May", "June",
                "July", "August", "September", "October", "November", "December"];
            var currentMonth = new Date().getMonth();
            var previousMonth = (currentMonth === 0) ? 11 : currentMonth - 1;
            var monthTitle = monthNames[previousMonth];

            // Revenue Growth
            var revenueData = google.visualization.arrayToDataTable([
                ['Month', 'Volume'],
                ['Jan', 1000], ['Feb', 2000], ['Mar', 30000], ['Apr', 1000], ['May', 2000], ['Jun', 40000],
                ['Jul', 5000], ['Aug', 1000], ['Sep', 20000], ['Oct', 3000], ['Nov', 40000], ['Dec', 1000]
            ]);

            var revenueOptions = {
                title: 'Revenue Growth',
                curveType: 'function',
                legend: { position: 'bottom' }
            };

            var transactionChart = new google.visualization.LineChart(document.getElementById('revenueGrowthChart'));
            transactionChart.draw(revenueData, revenueOptions);

            // Transaction Volume Over Time
            var transactionData = google.visualization.arrayToDataTable([
                ['Month', 'Volume'],
                ['Jan', 100], ['Feb', 50], ['Mar', 100], ['Apr', 50],
                ['May', 500], ['Jun', 100], ['Jul', 500], ['Aug', 100],
                ['Sep', 500], ['Oct', 200], ['Nov', 500], ['Dec', 500]
            ]);

            var transactionOptions = {
                title: 'Transaction Volume Over Time',
                curveType: 'function',
                legend: { position: 'bottom' }
            };

            var transactionChart = new google.visualization.LineChart(document.getElementById('transactionVolumeChart'));
            transactionChart.draw(transactionData, transactionOptions);

            // Top Users
            var topUsersData = google.visualization.arrayToDataTable([
                ['User', 'Transaction Volume'],
                ['User A', 120], ['User B', 90], ['User C', 80],
                ['User D', 70], ['User E', 60]
            ]);

            var topUsersOptions = {
                title: 'Top Users',
                legend: { position: 'none' }
            };

            var topUsersChart = new google.visualization.BarChart(document.getElementById('topUsersChart'));
            topUsersChart.draw(topUsersData, topUsersOptions);

            // User Growth
            var userGrowthData = google.visualization.arrayToDataTable([
                ['Month', 'Users'],
                ['Jan', 1182], ['Feb', 1568], ['Mar', 1930], ['Apr', 2294],
                ['May', 2856], ['Jun', 3105], ['Jul', 3610], ['Aug', 3960],
                ['Sep', 5000], ['Oct', 6000], ['Nov', 6050], ['Dec', 6845]
            ]);

            var userGrowthOptions = {
                title: 'User Growth',
                curveType: 'function',
                legend: { position: 'bottom' }
            };

            var userGrowthChart = new google.visualization.LineChart(document.getElementById('userGrowthChart'));
            userGrowthChart.draw(userGrowthData, userGrowthOptions);

            // Monthly Transaction Amount
            var monthlyTransactionData = google.visualization.arrayToDataTable([
                ['Month', 'Amount'],
                ['Jan', 12000], ['Feb', 19000], ['Mar', 3000], ['Apr', 5000],
                ['May', 2000], ['Jun', 3000], ['Jul', 15000], ['Aug', 21000],
                ['Sep', 18000], ['Oct', 9000], ['Nov', 11000], ['Dec', 25000]
            ]);

            var monthlyTransactionOptions = {
                title: 'Monthly Transaction Amount',
                legend: { position: 'none' }
            };

            var monthlyTransactionChart = new google.visualization.ColumnChart(document.getElementById('monthlyTransactionChart'));
            monthlyTransactionChart.draw(monthlyTransactionData, monthlyTransactionOptions);

            // User Active Status for the past month (Pie Chart)
            var activeStatusData = google.visualization.arrayToDataTable([
                ['User Status', 'Percentage'],
                ['Active Users', 75], // Replace with real data
                ['Inactive Users', 25] // Replace with real data
            ]);
            
            var activeStatusOptions = {
                title: 'User Active Status for ' + monthTitle,
                pieHole: 0.4, // Donut-style pie chart
                colors: ['#4caf50', '#f44336'] // Customize colors
            };

            var activeStatusChart = new google.visualization.PieChart(document.getElementById('userActiveStatusChart'));
            activeStatusChart.draw(activeStatusData, activeStatusOptions);
        }

        // Redraw charts on window resize
        window.addEventListener('resize', drawCharts);