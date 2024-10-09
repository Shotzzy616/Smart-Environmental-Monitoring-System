let myChart; // Declare the chart variable globally

        function fetchWeatherData() {
            $.ajax({
                url: '/latest_data',
                method: 'GET',
                success: function(data) {
                    // Update predictions
                    $('#svm-prediction').text(data.svm === 1 ? 'Normal' : 'Anomaly');
                    $('#lof-prediction').text(data.lof === 1 ? 'Normal' : 'Anomaly');
                    $('#isof-prediction').text(data.isof === 1 ? 'Normal' : 'Anomaly');
                    $('#elliptic-prediction').text(data.elliptic === 1 ? 'Normal' : 'Anomaly');
                },
                error: function() {
                    $('#weather-data').html('<strong>Error fetching data.</strong>');
                }
            });
        }

        $(document).ready(function() {
            fetchWeatherData(); // Initial fetch
            setInterval(fetchWeatherData, 5000);  // Fetch data every 5 seconds

            // Event listener for list-group-item clicks (whole box clickable)
            $('.list-group-item').click(function () {
                const modelName = $(this).find('.model-prediction').data('model');
                displayParams(modelName);
                $(this).find('.model-params').toggle(); // Show/hide parameters
            });

            // Model parameters handling
            const model_parameters = {
                "OneClassSVM": {
                    "nu": {"type": "float", "min": 0.01, "max": 1.0},
                    "gamma": {"type": "float", "min": 0.01, "max": 1.0},
                    "kernel": {"type": "text", "options": ["linear", "poly", "rbf", "sigmoid"]},
                    "degree": {"type": "int", "min": 1, "max": 5},
                    "cache_size": {"type": "int", "min": 50, "max": 1000},
                },
                "LocalOutlierFactor": {
                    "n_neighbors": {"type": "int", "min": 1, "max": 50},
                    "contamination": {"type": "float", "min": 0.01, "max": 0.5},
                    "novelty": {"type": "bool", "options": [true, false]},
                    "algorithm": {"type": "text", "options": ["auto", "ball_tree", "kd_tree", "brute"]},
                    "p": {"type": "int", "options": [1, 2]},  // Dropdown for p
                },
                "IsolationForest": {
                    "n_estimators": {"type": "int", "min": 50, "max": 300},
                    "bootstrap": {"type": "bool", "options": [true, false]},
                    "warm_start": {"type": "bool", "options": [true, false]},
                },
                "EllipticEnvelope": {
                    "contamination": {"type": "float", "min": 0.01, "max": 0.5},
                    "support_fraction": {"type": "float", "min": 0.1, "max": 1.0},
                    "assume_centered": {"type": "bool", "options": [true, false]},
                    "random_state": {"type": "int", "min": 0},
                },
            };

            // Handle parameter UI rendering
            function displayParams(modelName) {
                const params = model_parameters[modelName];
                const paramsContainer = $(`#${modelName.toLowerCase()}-params`);
                paramsContainer.empty();

                for (let param in params) {
                    const config = params[param];
                    let inputField = '';

                    switch (config.type) {
                        case 'float':
                            inputField = `
                                <div class="form-group">
                                    <label for="${param}">${param} (${config.type}):</label>
                                    <div class="input-group">
                                        <input type="number" step="0.01" min="${config.min}" max="${config.max}" class="form-control" id="${param}" name="${param}" value="${config.min}">
                                        <div class="input-group-append">
                                            <button class="btn btn-outline-secondary increment-btn" type="button" data-param="${param}" data-step="0.01">+</button>
                                            <button class="btn btn-outline-secondary decrement-btn" type="button" data-param="${param}" data-step="0.01">-</button>
                                        </div>
                                    </div>
                                </div>`;
                            break;
                        case 'int':
                            if (param === 'p') {
                                inputField = `
                                    <div class="form-group">
                                        <label for="${param}">${param} (${config.type}):</label>
                                        <select class="form-control" id="${param}" name="${param}">
                                            ${config.options.map(option => `<option value="${option}">${option}</option>`).join('')}
                                        </select>
                                    </div>`;
                            } else {
                                inputField = `
                                    <div class="form-group">
                                        <label for="${param}">${param} (${config.type}):</label>
                                        <div class="input-group">
                                            <input type="number" step="1" min="${config.min}" max="${config.max}" class="form-control" id="${param}" name="${param}" value="${config.min}">
                                            <div class="input-group-append">
                                                <button class="btn btn-outline-secondary increment-btn" type="button" data-param="${param}" data-step="1">+</button>
                                                <button class="btn btn-outline-secondary decrement-btn" type="button" data-param="${param}" data-step="1">-</button>
                                            </div>
                                        </div>
                                    </div>`;
                            }
                            break;
                        case 'bool':
                            inputField = `
                                <div class="form-group">
                                    <label for="${param}">${param} (${config.type}):</label>
                                    <select class="form-control" id="${param}" name="${param}">
                                        ${config.options.map(option => `<option value="${option}">${option}</option>`).join('')}
                                    </select>
                                </div>`;
                            break;
                        case 'text':
                            if (config.options) {
                                inputField = `
                                    <div class="form-group">
                                        <label for="${param}">${param}:</label>
                                        <select class="form-control" id="${param}" name="${param}">
                                            ${config.options.map(option => `<option value="${option}">${option}</option>`).join('')}
                                        </select>
                                    </div>`;
                            }
                            break;
                    }
                    paramsContainer.append(inputField);
                }

                // Show the model parameters section and set the model name
                $('#model-name').text(modelName);
                $('#model-params').show();
            }

            // Increment/decrement functionality for parameter inputs
            $(document).on('click', '.increment-btn', function() {
                const param = $(this).data('param');
                const input = $(`#${param}`);
                let newValue = parseFloat(input.val()) + parseFloat($(this).data('step'));
                if (newValue <= parseFloat(input.attr('max'))) {
                    input.val(newValue.toFixed(2)); // Set to two decimal places for float
                }
            });

            $(document).on('click', '.decrement-btn', function() {
                const param = $(this).data('param');
                const input = $(`#${param}`);
                let newValue = parseFloat(input.val()) - parseFloat($(this).data('step'));
                if (newValue >= parseFloat(input.attr('min'))) {
                    input.val(newValue.toFixed(2)); // Set to two decimal places for float
                }
            });
        });