/* msca provisioner admin desktop javascript */

/*jslint browser: true, plusplus: true, regexp: true */
/*global $, jQuery, Handlebars, Highcharts, moment, alert, confirm, startSubscriptionMonitoring, stopSubscriptionMonitoring */


"use strict";


$(document).ready(function () {
    var hash = window.location.hash;

    if (hash) {
        $('ul.nav a[href="' + hash + '"]').tab('show');
    }

    // prep for api post/put
    $.ajaxSetup({
        headers: { "X-CSRFToken": $('input[name="csrfmiddlewaretoken"]').val() }
    });

    // init Highcharts
    Highcharts.setOptions({
        global: {
            useUTC: false
        }
    });

    function format_date(dt) {
        return (dt !== null) ? moment(dt).format("MM/DD/YYYY h:mm a") : '';
    }

    function format_long_date(dt) {
        return (dt !== null) ? moment(dt).format("MMM Do YYYY, h:mm a") : '';
    }

    function format_relative_date(dt) {
        return (dt !== null) ? moment(dt).fromNow() : '';
    }

    function format_hms_date(dt) {
        return moment(dt).format("h:mm:ss a");
    }

    function subscriptionMonitor() {
        var state = window.provisioner;

        updateProvisioningStatus();
        if (state.hasOwnProperty('subscriptionCountdownId') && state.subscriptionCountdownId) {
            clearInterval(state.subscriptionCountdownId);
        }

        state.subscriptionCountdown = window.provisioner.subscription_update_frequency;
        state.subscriptionCountdownId = setInterval(function () {
            state.subscriptionCountdown -= 1;
            if (state.subscriptionCountdown >= 0) {
                $('.subscription-update > span + a + span').html(state.subscriptionCountdown);
            }
        }, 1000);
    }

    function startSubscriptionMonitoring() {
        var state = window.provisioner;

        subscriptionMonitor();
        state.subscriptionTimerId = setInterval(subscriptionMonitor,
                                                state.subscription_update_frequency * 1000);
    }

    function stopSubscriptionMonitoring() {
        var state = window.provisioner;

        if (state.hasOwnProperty('subscriptionTimerId') && state.subscriptionTimerId) {
            clearInterval(state.subscriptionTimerId);
        }
    }

    function toggleJob() {
	    var input = $(this);
        $.ajax({
            url: 'api/v1/job/' + encodeURIComponent(input.attr('data-job-id')),
            contentType: 'application/json',
            type: 'PUT',
            processData: false,
            data: '{"job": {"is_active": ' + $(this).is(':checked') + '}}',
            success: function (data) {
		        if (data.hasOwnProperty('job')) {
		            input.closest('td')
                        .prev()
                        .html(data.job.changed_by)
                        .prev()
                        .html(format_date(data.job.changed_date));
		        }
            },
            error: function (xhr) {
                var json;
                try {
                    json = $.parseJSON(xhr.responseText);
                    console.log('Event service error:' + json.error);
                } catch (e) {
                    console.log('Unknown job service error');
                }
            }
        });
    }

    function deleteJob() {
        var btn = $(this),
	        msg = 'Permanently delete this job?';
        if (confirm(msg)) {
            $.ajax({
                url: 'api/v1/job/' + encodeURIComponent(btn.attr('data-job-id')),
                contentType: 'application/json',
                type: 'DELETE',
                success: function () {
                    btn.closest('tr').remove();
                },
                error: function (xhr) {
                    var json;
                    try {
                        json = $.parseJSON(xhr.responseText);
                        console.log('Event service error:' + json.error);
                    } catch (e) {
                        console.log('Unknown job service error');
                    }
                }
            });
        }
    }

    function loadJobs() {
        $.ajax({
            url: 'api/v1/jobs',
            dataType: 'json',
            success: function (data) {
                var tpl = Handlebars.compile($('#job-table-row').html()),
                    context = {jobs: []};
                if (data.hasOwnProperty('jobs')) {
                    $.each(data.jobs, function (i) {
                        var job = data.jobs[i];
                        context.jobs.push({
                            job_id: job.job_id,
                            name: job.name,
                            title: job.title,
                            is_active: job.is_active ? true : false,
                            changed_by: job.changed_by,
                            changed_date: job.changed_date ? format_date(job.changed_date) : null,
                            last_run_date: job.last_run_date ? format_date(job.last_run_date) : null,
                            last_run_relative: job.last_run_date ? format_relative_date(job.last_run_date) : null,
                            read_only: job.read_only
                        });
                    });
                    $('#jobs-table tbody').html(tpl(context));
                    $('#jobs-table tbody input.toggle-job').each(function () {
                        $(this).bootstrapToggle().change(toggleJob);
                    });
                    $('#jobs-table tbody button.delete-job').click(deleteJob);
                    $('#jobs-table').dataTable({
                        'aaSorting': [[ 0, 'asc' ]],
                        'bPaginate': false,
                        'searching': false,
			            'bScrollCollapse': true
                    });
                }
            },
            error: function (xhr) {
                var json;
                try {
                    json = $.parseJSON(xhr.responseText);
                    console.log('admin service error:' + json.error);
                } catch (e) {
                    console.log('Unknown admin service error');
                }
            }
        });
    }

    function initProvisioningStatus() {
        $('#subscription-table').dataTable({
            'aaSorting': [[ 0, 'asc' ]],
            'bPaginate': false,
            'bInfo': false,
            'searching': false,
			'bScrollCollapse': true
        });
    }

    function updateProvisioningStatus() {
        var table_api = $('#subscription-table').dataTable().api();

        table_api.clear().draw();
        $('.dataTables_empty').addClass('waiting');
        $.ajax({
            url: '/provisioner/api/v1/subscriptions',
            dataType: 'json',
            success: function (data) {
                var tpl = Handlebars.compile($('#subscription-table-row').html()),
                    context = {
                        user_count: (data.hasOwnProperty('subscriptions')) ? data.subscriptions.length : 0,
                        subscriptions: []
                    };

                if (context.user_count > 0) {
                    $.each(data.subscriptions, function (i) {
                        var sub = this,
                            html = tpl({
                                'subscription_id': sub.subscription_id,
                                'net_id': sub.net_id,
                                'subscription': sub.subscription,
                                'subscription_name': sub.subscription_name,
                                'state': sub.state,
                                'modified_date': format_date(sub.modified_date),
                                'modified_date_relative': format_relative_date(sub.modified_date),
                                'in_process': sub.in_process
                            });

                        table_api.row.add($(html));
                    });

                    table_api.draw();

                    $('#user-count').show();
                    $('#user-count').html(context.user_count);
                } else {
                    $('#user-count').hide();
                }


                $('.provisioner-list').parent().removeClass('waiting');
                $('.provisioner-list').html(tpl(context));

                $('.subscription-update > span:first').html(format_hms_date());
                $('.subscription-update > span + a + span').html(window.provisioner.subscription_update_frequency);
            },
            error: function (xhr) {
                var json, msg;
                try {
                    json = $.parseJSON(xhr.responseText);
                    msg = 'Subscription service error: ' + json.error;
                } catch (e) {
                    msg = 'Problem getting subscription list from server';
                }

                $('.dataTables_empty')
                    .removeClass('waiting')
                    .addClass('')
                    .html(msg);
            }
        });
    }

    // event frequency chart
    function initializeStripAndGauge(event_type) {
        var url_base = '/events/api/v1/events?type=' + event_type + '&',
            gauge = new Highcharts.Chart({
                chart: {
                    renderTo: 'event-gauge',
                    type: 'gauge',
                    plotBorderWidth: 1,
                    plotBackgroundColor: {
                        linearGradient: { x1: 0, y1: 0, x2: 0, y2: 1 },
                        stops: [
                            [0, '#FFF4C6'],
                            [0.3, '#FFFFFF'],
                            [1, '#FFF4C6']
                        ]
                    },
                    plotBackgroundImage: null,
                    height: 200,
                    width: 420
                },
                title: {
                    text: null
                },
                tooltip: {
                    shared: true
                },
                credits: {
                    enabled: false
                },
                pane: [{
                    startAngle: -45,
                    endAngle: 45,
                    background: null,
                    center: ['50%', '150%'],
                    size: 400
                }],
                yAxis: [{
                    type: 'logarithmic',
                    min: 1,
                    max: 10000,
                    minorTickPosition: 'outside',
                    tickPosition: 'outside',
                    minorTickInterval: 0.1,
                    labels: {
                        rotation: 'auto',
                        distance: 20
                    },
                    plotBands: [{
                        from: 4000,
                        to: 7000,
                        color: '#FFFF00',
                        innerRadius: '100%',
                        outerRadius: '105%'
                    }, {
                        from: 7000,
                        to: 10000,
                        color: '#C02316',
                        innerRadius: '100%',
                        outerRadius: '105%'
                    }],
                    pane: 0,
                    title: {
                        text: 'events / hour',
                        y: -40
                    }
                }, {
                    type: 'logarithmic',
                    pane: 0
                }],

                plotOptions: {
                    gauge: {
                        dataLabels: {
                            enabled: false
                        },
                        dial: {
                            radius: '100%'
                        },
                        tooltip: {
                            followPointer: true
                        }
                    }
                },
                series: [{
                    name: 'per hour',
                    data: [1],
                    yAxis: 0,
                    dial: {
                        backgroundColor: '#000000'
                    }
                }, {
                    name: 'per hour (over 6 hours)',
                    data: [1],
                    yAxis: 0,
                    dial: {
                        backgroundColor: '#00CC00'
                    }
                }]
            }),
            updateGauge = function (data) {
                var last_hour = 0,
                    avg_hours = 0,
                    hours_to_avg = 6,
                    n,
                    i;

                n = data.length - 60;
                if (n > 0) {
                    for (i = n; i < data.length; i += 1) {
                        last_hour += data[i].y;
                    }

                    i = (n - (60 * (hours_to_avg - 1)));
                    if (i >= 0) {
                        avg_hours = last_hour;
                        while (i < n) {
                            avg_hours += data[i].y;
                            i += 1;
                        }
                    }
                }

                gauge.series[0].setData([(last_hour) ? last_hour : 1], true);
                gauge.series[1].setData((avg_hours) ? [Math.ceil(avg_hours / hours_to_avg)] : 1, true);
                gauge.redraw();
            },
            chart = new Highcharts.Chart({
                chart: {
                    renderTo: 'event-graph',
                    zoomType: 'x',
                    spacingRight: 8,
                    events: {
                        load: function () {
                            setInterval(function () {
                                var now = new Date();

                                now.setSeconds(0); // normalize for resolution
                                now.setMilliseconds(0);

                                $.ajax({
                                    url: url_base + 'on=' + moment.utc(now).toISOString(),
                                    dataType: 'json',
                                    success: function (data) {
                                        if (chart.series[0].data.length) {
                                            var last = chart.series[0].data[chart.series[0].data.length - 1],
                                                point = data.points[0],
                                                max = 0,
                                                delta,
                                                sum = 0;

                                            $.each(chart.series[0].data, function (i) {
                                                sum = sum + this.y;
                                                chart.series[1].data[i].y = sum;

                                                if (this.y > max) {
                                                    max = this.y;
                                                }
                                            });

                                            if (last.x === now.getTime()) {
                                                delta = point - last.y;
                                                last.y = point;
                                            } else {
                                                delta = point;
                                                sum = sum + delta;
                                                chart.series[0].addPoint([now.getTime(), point], true, true);
                                                chart.series[1].addPoint([now.getTime(), sum], true, true);
                                            }

                                            if (point > max) {  // rescale
                                                chart.yAxis[0].setExtremes(0, point);
                                                chart.yAxis[1].setExtremes(0, sum);
                                            }

                                            $('#event-count').html(sum);
                                            updateGauge(chart.series[0].data);
                                        }
                                    },
                                    error: function (xhr) {
                                        var json;

                                        try {
                                            json = $.parseJSON(xhr.responseText);
                                            console.log('Event service error:' + json.error);
                                        } catch (e) {
                                            console.log('Unknown event service error');
                                        }
                                    }
                                });
                            }, window.provisioner.event_update_frequency * 1000);
                        }
                    },
                    resetZoomButton: {
                        position: {
                            align: 'left',
                            // verticalAlign: 'top', // by default
                            x: 0,
                            y: -6
                        }
                    }
                },
                title: {
                    text: null
                },
                xAxis: [{
                    type: 'datetime',
                    maxZoom: 5 * 60 * 1000, // five minutes
                    title: {
                        text: null
                    },
                    events: {
                        setExtremes: function (event) {
                            var data = chart.series[0].data,
                                min = event.min ? Math.floor(event.min) : this.dataMin,
                                max = event.max ? Math.ceil(event.max) : this.dataMax,
                                l = data.length,
                                sum = 0,
                                i;

                            for (i = 0; i < l && data[i].x <= max; i += 1) {
                                if (data[i].x >= min) {
                                    sum = sum + data[i].y;
                                }

                                chart.series[1].data[i].y = sum;
                            }

                            chart.yAxis[1].setExtremes(0, sum);
                            $('#event-count').html(sum);
                        }
                    }
                }],
                yAxis: [{
                    title: {
                        text: 'per minute'
                    },
                    min: 0,
                    minRange: 1,
                    allowDecimals: false,
                    startOnTick: false,
                    showFirstLabel: false,
                    minPadding: 0.2
                }, {
                    title: {
                        text: 'cumulative'
                    },
                    min: 0,
                    minRange: 100,
                    allowDecimals: false,
                    startOnTick: false,
                    showFirstLabel: false,
                    minPadding: 0.2,
                    opposite: true
                }],
                tooltip: {
                    shared: true
                },
                legend: {
                    enabled: false
                },
                credits: {
                    enabled: false
                },
                plotOptions: {
                    area: {
                        fillColor: {
                            linearGradient: { x1: 0, y1: 0, x2: 0, y2: 1},
                            stops: [
                                [0, Highcharts.getOptions().colors[0]],
                                [1, 'rgba(2,0,0,0)']
                            ]
                        },
                        lineWidth: 1,
                        marker: {
                            enabled: false,
                            states: {
                                hover: {
                                    enabled: true,
                                    radius: 5
                                }
                            }
                        },
                        shadow: false,
                        states: {
                            hover: {
                                lineWidth: 1
                            }
                        }
                    }
                },

                series: [{
                    type: 'column',
                    name: 'Events',
                    data: []
                }, {
                    type: 'spline',
                    name: 'Event Sum',
                    yAxis: 1,
                    data: []
                }]
            }),
            pointStart = new Date();

        pointStart.setDate(pointStart.getDate() - 2);
        pointStart.setSeconds(0);
        pointStart.setMilliseconds(0);

        $.ajax({
            url: url_base + 'begin=' +  moment.utc(pointStart).toISOString(),
            dataType: 'json',
            success: function (data) {
                var series = [[], []],
                    t = pointStart.getTime(),
                    sum = 0;

                $.each(data.points, function (i) {
                    sum = sum + this;
                    series[0].push([t + (i * 60 * 1000), data.points[i]]);
                    series[1].push([t + (i * 60 * 1000), sum]);
                });

                $('#event-count').html(sum);
                chart.series[0].setData(series[0], true);
                chart.series[1].setData(series[1], true);
                updateGauge(chart.series[0].data);
            },
            error: function (xhr) {
                var json;
                try {
                    json = $.parseJSON(xhr.responseText);
                    console.log('Event service error:' + json.error);
                } catch (e) {
                    console.log('Unknown event service error');
                }
            }
        });

        $('.subscription-update > span + a').on('click', function () {
            stopSubscriptionMonitoring();
            startSubscriptionMonitoring();
        });
    }

    if ($('.event-freq').length) {
        initializeStripAndGauge('subscription');
        initProvisioningStatus();
        startSubscriptionMonitoring();
    } else if ($('#jobs-table').length) {
        loadJobs();
    }

});
