'use strict';

$(function () {
    fetch('/api/measures')
        .then(resp => resp.json())
        .then(data => {
            console.log(data);
            Highcharts.chart('canvas', {
                chart: {
                    type: 'line',
                },
                credits: {
                    enabled: false,
                },
                series: data,
                title: {
                    text: 'Measures',
                },
                xAxis: {
                    type: 'datetime'
                },
                yAxis: [
                    {
                        min: 0,
                    },
                    {
                        opposite: true,
                        title: {
                            text: 'Percent',
                        },
                        min: 0,
                        max: 1,
                    }
                ],
            });
        });
    console.log('hello');
});
