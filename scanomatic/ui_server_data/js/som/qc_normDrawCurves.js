import { getBaseLog } from './qc_normHelper';

const d3 = require('d3/d3.js');

if (!d3.scanomatic) {
  d3.scanomatic = {};
}

function normalizeCurveData(value) {
  const src = value || {};
  const raw = Array.isArray(src.raw_data) ? src.raw_data : [];
  const smooth = Array.isArray(src.smooth_data) ? src.smooth_data : [];
  const time = Array.isArray(src.time_data) ? src.time_data : [];
  return {
    raw_data: raw,
    smooth_data: smooth,
    time_data: time,
  };
}

function isFiniteNumber(value) {
  return typeof value === 'number' && Number.isFinite(value);
}

function toFiniteSeries(time, values) {
  if (!Array.isArray(time) || !Array.isArray(values)) {
    return [];
  }

  const n = Math.min(time.length, values.length);
  const out = [];
  for (let i = 0; i < n; i += 1) {
    const t = time[i];
    const v = values[i];
    if (isFiniteNumber(t) && isFiniteNumber(v) && v > 0) {
      out.push({ time: t, value: v });
    }
  }
  return out;
}

export default function DrawCurves(container, data, gt, gtWhen, yld) {
  // GrowthChart
  const chartMarginAll = 30;
  const chartMargin = {
    top: chartMarginAll, right: chartMarginAll, bottom: chartMarginAll, left: chartMarginAll,
  };
  const chartwidth = 350;
  const chartheight = 294;

  const chart = d3.select(container)
    .append('svg')
    .attr({
      width: chartwidth,
      height: chartheight,
      class: 'growthChart',
      margin: 3,
    });

  const defs = chart.append('defs');

  defs.append('marker')
    .attr({
      id: 'arrow',
      viewBox: '0 -5 10 10',
      refX: 5,
      refY: 0,
      markerWidth: 4,
      markerHeight: 4,
      orient: 'auto',
    })
    .append('path')
    .attr('d', 'M0,-5L10,0L0,5')
    .attr('class', 'arrowHead');

  defs.append('marker')
    .attr({
      id: 'arrow2',
      viewBox: '0 -5 10 10',
      refX: 5,
      refY: 0,
      markerWidth: 4,
      markerHeight: 4,
      orient: 'auto-start-reverse',
    })
    .append('path')
    .attr('d', 'M0,-5L10,0L0,5')
    .attr('class', 'arrowHead');

  // chart
  const gChart = d3.scanomatic.growthChart();
  gChart.data(data);
  gChart.width(chartwidth);
  gChart.height(chartheight);
  gChart.margin(chartMargin);
  gChart.generationTimeWhen(gtWhen);
  gChart.generationTime(gt);
  gChart.growthYield(yld);
  gChart(chart);
}

d3.scanomatic.growthChart = () => {
  // properties
  let data;
  let margin;
  let height;
  let width;
  let generationTimeWhen;
  let generationTime;
  let growthYield;

  // local variables
  let g;

  function addAxis(xScale, yScale, chartHeight) {
    const xAxis = d3.svg.axis()
      .scale(xScale)
      .orient('bottom');

    const yAxis = d3.svg.axis()
      .scale(yScale)
      .orient('left')
      .tickFormat(d3.format('.0e'));

    g.append('g')
      .attr('class', 'x axis')
      .attr('transform', `translate(0,${chartHeight})`)
      .call(xAxis);

    g.append('g')
      .attr('class', 'y axis')
      .call(yAxis)
      .append('text')
      .attr('transform', 'rotate(-90)')
      .attr('y', 6)
      .attr('dy', '.5em')
      .style('text-anchor', 'end')
      .style('font-size', '11')
      .text('Population size [cells]');
  }

  function addSeries(rawData, smoothData, xScale, yScale) {
    const lineFun = d3.svg.line()
      .x(d => xScale(d.time))
      .y(d => yScale(d.value))
      .interpolate('linear');

    g.append('g')
      .classed('series', true)
      .append('path')
      .attr({
        class: 'raw',
        d: lineFun(rawData),
      });

    g.append('g')
      .classed('series', true)
      .append('path')
      .attr({
        class: 'smooth',
        d: lineFun(smoothData),
      });
  }

  function getYOffset(y, offset) {
    return (y > 100) ? y - offset : y + offset;
  }

  function addMetaGt(smoothData, xScale, yScale) {
    if (generationTime == null || generationTimeWhen == null) return;

    const lineStartOffset = 50;
    const lineEndOffset = 10;

    const smoothGtTime = generationTimeWhen;
    let smoothGtValue = 0;
    for (let i = 0; i < smoothData.length; i += 1) {
      const approx = d3.round(smoothData[i].time, 2);
      if (approx === d3.round(smoothGtTime, 2)) { smoothGtValue = smoothData[i].value; }
    }

    const gtX = xScale(smoothGtTime);
    const gtY = yScale(smoothGtValue);

    const gMetaGt = g.append('g')
      .classed('meta gt', true);

    gMetaGt.append('circle')
      .attr({
        cx: gtX,
        cy: gtY,
        r: 4,
        fill: 'red',
      });

    gMetaGt.append('line')
      .attr({
        class: 'arrow',
        'marker-end': 'url(#arrow)',
        x1: gtX,
        y1: getYOffset(gtY, lineStartOffset),
        x2: gtX,
        y2: getYOffset(gtY, lineEndOffset),
        stroke: 'black',
        'stroke-width': 1.5,
      });

    gMetaGt.append('text')
      .attr({
        x: gtX - 10,
        y: getYOffset(gtY, 55),
      })
      .text('GT');
    // Py=m (Px-x) + Py
    console.log(`GT:${generationTime}`);
    console.log(`GTTimeWhen:${generationTimeWhen}`);
    console.log(`GTTimeWhenValue:${smoothGtValue}`);
    const windowSize = 4;
    const gtSlope = 1 / generationTime;
    const l = parseFloat(smoothGtTime) - windowSize;
    const leftXLimit = xScale(l);
    const logPy = getBaseLog(2, smoothGtValue);
    const yLeftLogged = logPy - (windowSize * gtSlope);
    const yLeft = 2 ** yLeftLogged;
    const leftYLimit = yScale(yLeft);

    gMetaGt.append('line')
      .attr({
        x1: gtX,
        y1: gtY,
        x2: leftXLimit,
        y2: leftYLimit,
        stroke: 'blue',
        'stroke-width': 3,
      });

    const r = parseFloat(smoothGtTime) + windowSize;
    const rightXlimit = xScale(r);
    const yRightLogged = (windowSize * gtSlope) + logPy;
    const yRight = 2 ** yRightLogged;
    const rightYLimit = yScale(yRight);

    gMetaGt.append('line')
      .attr({
        x1: gtX,
        y1: gtY,
        x2: rightXlimit,
        y2: rightYLimit,
        stroke: 'blue',
        'stroke-width': 3,
      });
  }

  function addMetaYield(smoothData, xScale, yScale) {
    if (growthYield == null) return;

    const smoothYieldValue = growthYield;
    let smoothYieldTime = 0;
    for (let i = 0; i < smoothData.length; i += 1) {
      if (smoothData[i].value >= smoothYieldValue) {
        smoothYieldTime = smoothData[i].time;
        break;
      }
    }

    const gtX = xScale(smoothYieldTime);
    const gtY = yScale(smoothYieldValue);
    const baseX = gtX;
    const baseY = yScale(smoothData[0].value);
    console.log(`Yield time:${smoothYieldTime}`);
    console.log(`Yield value:${smoothYieldValue}`);

    const gMetaYeild = g.append('g')
      .classed('meta yield', true);

    gMetaYeild.append('line')
      .attr({
        class: 'arrow',
        'marker-end': 'url(#arrow)',
        'marker-start': 'url(#arrow2)',
        x1: gtX,
        y1: gtY + 5,
        x2: baseX,
        y2: baseY - 5,
        stroke: 'black',
        'stroke-width': 1.5,
      });

    const middle = (baseY - gtY) / 2;
    gMetaYeild.append('text')
      .attr({
        x: gtX + 3,
        y: gtY + middle,
      })
      .text('Yield');
  }

  function update() {
    // data
    const serRaw = data.raw_data;
    const serSmooth = data.smooth_data;
    const time = data.time_data;
    // chart
    const w = width - margin.left - margin.right;
    const h = height - margin.top - margin.bottom;

    if (serRaw.length === 0 || serSmooth.length === 0 || time.length === 0) {
      throw Error('GrowthData is empty');
    }

    if (serRaw.length !== time.length || serSmooth.length !== time.length) {
      throw Error('GrowthData lengths do not match!!!');
    }

    const rawData = toFiniteSeries(time, serRaw);
    const smoothData = toFiniteSeries(time, serSmooth);

    if (rawData.length === 0 && smoothData.length === 0) {
      throw Error('GrowthData has no finite values');
    }

    const allPoints = rawData.concat(smoothData);
    const xDomain = d3.extent(allPoints, (d) => d.time);
    const yDomain = d3.extent(allPoints, (d) => d.value);

    if (
      !isFiniteNumber(xDomain[0])
      || !isFiniteNumber(xDomain[1])
      || !isFiniteNumber(yDomain[0])
      || !isFiniteNumber(yDomain[1])
      || yDomain[0] <= 0
    ) {
      throw Error('GrowthData has invalid plotting domain');
    }

    const xScale = d3.scale.linear()
      .domain(xDomain)
      .range([0, w]);

    const yScale = d3.scale.log()
      .base(2)
      .domain(yDomain)
      .range([h, 0]);

    addAxis(xScale, yScale, h);

    addSeries(rawData, smoothData, xScale, yScale);

    addMetaGt(smoothData, xScale, yScale);

    addMetaYield(smoothData, xScale, yScale);
  }

  function chart(container) {
    g = container.append('g')
      .attr({
        transform: `translate(${margin.left},${margin.top})`,
        class: 'PlotArea',
      });
    update();
  }

  chart.update = update;

  chart.data = (value) => {
    if (typeof value === 'undefined') return data;
    data = normalizeCurveData(value);
    return chart;
  };

  chart.margin = (value) => {
    if (typeof value === 'undefined') return margin;
    margin = value;
    return chart;
  };

  chart.width = (value) => {
    if (typeof value === 'undefined') return width;
    width = value;
    return chart;
  };

  chart.height = (value) => {
    if (typeof value === 'undefined') return height;
    height = value;
    return chart;
  };

  chart.generationTimeWhen = (value) => {
    if (typeof value === 'undefined') return generationTimeWhen;
    generationTimeWhen = value;
    return chart;
  };

  chart.generationTime = (value) => {
    if (typeof value === 'undefined') return generationTime;
    generationTime = value;
    return chart;
  };

  chart.growthYield = (value) => {
    if (typeof value === 'undefined') return growthYield;
    growthYield = value;
    return chart;
  };

  return chart;
};
