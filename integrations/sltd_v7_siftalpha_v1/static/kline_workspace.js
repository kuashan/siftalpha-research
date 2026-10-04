(() => {
  'use strict';

  const VERSION = 'KLineChart 10.0.3';
  const STATE_COLORS = {
    BLUE: '#5b8cff',
    GRAY: '#8d99aa',
    GREEN: '#52d49a',
    OTHER: '#344055',
  };

  function num(v) {
    const n = Number(v);
    return Number.isFinite(n) ? n : null;
  }

  function ts(value) {
    const n = Date.parse(String(value || ''));
    return Number.isFinite(n) ? n : null;
  }

  function clamp(v, lo, hi) {
    return Math.max(lo, Math.min(hi, v));
  }

  class Workspace {
    constructor(opts) {
      this.host = document.getElementById(opts.hostId);
      this.overlay = document.getElementById(opts.overlayId);
      this.stateCanvas = document.getElementById(opts.stateId);
      this.positionCanvas = document.getElementById(opts.positionId);
      this.onCrosshair = typeof opts.onCrosshair === 'function' ? opts.onCrosshair : () => {};
      this.chart = null;
      this.volumePaneId = null;
      this.current = null;
      this.dataKey = '';
      this.bars = [];
      this.barByTs = new Map();
      this.raf = 0;
      this.resizeObserver = null;
      this._bound = false;
    }

    ensureChart() {
      if (this.chart) return this.chart;
      if (!window.klinecharts || !window.klinecharts.init) {
        throw new Error('KLineChart v10.0.3 未加载');
      }

      const chart = window.klinecharts.init(this.host);
      if (!chart) throw new Error('KLineChart 初始化失败');
      this.chart = chart;

      chart.setStyles({
        grid: {
          horizontal: { show: true, color: '#1a2638', size: 1, style: 'solid' },
          vertical: { show: false, color: '#1a2638', size: 1, style: 'solid' },
        },
        candle: {
          type: 'candle_solid',
          bar: {
            upColor: '#52d49a',
            downColor: '#ff7b82',
            noChangeColor: '#8d99aa',
            upBorderColor: '#52d49a',
            downBorderColor: '#ff7b82',
            noChangeBorderColor: '#8d99aa',
            upWickColor: '#52d49a',
            downWickColor: '#ff7b82',
            noChangeWickColor: '#8d99aa',
          },
          tooltip: {
            showRule: 'follow_cross',
            showType: 'standard',
          },
          priceMark: {
            high: { show: true, color: '#8fa0ba' },
            low: { show: true, color: '#8fa0ba' },
            last: {
              show: true,
              upColor: '#52d49a',
              downColor: '#ff7b82',
              noChangeColor: '#8d99aa',
              line: { show: true, style: 'dashed', size: 1 },
            },
          },
        },
        indicator: {
          tooltip: { showRule: 'follow_cross', showType: 'standard' },
          bars: [{
            upColor: 'rgba(82,212,154,.60)',
            downColor: 'rgba(255,123,130,.60)',
            noChangeColor: 'rgba(141,153,170,.55)',
          }],
        },
        xAxis: {
          axisLine: { show: true, color: '#243047', size: 1 },
          tickText: { color: '#8292aa', size: 10, family: 'system-ui' },
          tickLine: { show: false, color: '#243047', size: 1, length: 3 },
        },
        yAxis: {
          position: 'right',
          type: 'normal',
          inside: false,
          reverse: false,
          axisLine: { show: false, color: '#243047', size: 1 },
          tickText: { color: '#8292aa', size: 10, family: 'system-ui' },
          tickLine: { show: false, color: '#243047', size: 1, length: 3 },
        },
        crosshair: {
          show: true,
          horizontal: {
            show: true,
            line: { show: true, style: 'dashed', size: 1, color: '#9eacc0' },
            text: { show: true, color: '#f3f6fb', backgroundColor: '#26344d' },
          },
          vertical: {
            show: true,
            line: { show: true, style: 'dashed', size: 1, color: '#9eacc0' },
            text: { show: true, color: '#f3f6fb', backgroundColor: '#26344d' },
          },
        },
        separator: { size: 1, color: '#243047', fill: true, activeBackgroundColor: '#1b2638' },
      });

      chart.setZoomEnabled(true);
      chart.setScrollEnabled(true);
      chart.setOffsetRightDistance(18);
      chart.setMaxOffsetRightDistance(160);
      chart.setMaxOffsetLeftDistance(80);

      try {
        this.volumePaneId = chart.createIndicator('VOL');
        if (this.volumePaneId) {
          chart.setPaneOptions({
            id: this.volumePaneId,
            height: 72,
            minHeight: 58,
            dragEnabled: false,
            order: 1,
          });
        }
      } catch (_) {}

      const redraw = () => this.scheduleRedraw();
      for (const action of ['onZoom', 'onScroll', 'onVisibleRangeChange', 'onPaneDrag']) {
        try { chart.subscribeAction(action, redraw); } catch (_) {}
      }
      try {
        chart.subscribeAction('onCrosshairChange', data => {
          if (data && data.kLineData) {
            const row = this.barByTs.get(Number(data.kLineData.timestamp));
            this.onCrosshair(row || null, data);
          }
        });
      } catch (_) {}

      if (!this._bound) {
        this._bound = true;
        this.resizeObserver = new ResizeObserver(() => {
          try { this.chart && this.chart.resize(); } catch (_) {}
          this.scheduleRedraw();
        });
        this.resizeObserver.observe(this.host);
      }

      return chart;
    }

    makeBars(candles) {
      return (candles || []).map(c => {
        const timestamp = ts(c.date);
        return {
          timestamp,
          open: Number(c.open),
          high: Number(c.high),
          low: Number(c.low),
          close: Number(c.close),
          volume: Number(c.volume || 0),
          turnover: Number(c.turnover || 0),
          __source: c,
        };
      }).filter(x => Number.isFinite(x.timestamp));
    }

    periodOf(tf) {
      const value = String(tf || '1d').toLowerCase();
      const match = value.match(/^(\d+)(m|h|d)$/);
      if (!match) return { span: 1, type: 'day' };
      const span = Number(match[1]);
      const unit = match[2];
      return {
        span,
        type: unit === 'm' ? 'minute' : unit === 'h' ? 'hour' : 'day',
      };
    }

    setData(config) {
      const chart = this.ensureChart();
      const bars = this.makeBars(config.candles);
      const key = [
        config.symbol || '',
        config.timeframe || '',
        bars.length,
        bars[0]?.timestamp || '',
        bars[bars.length - 1]?.timestamp || '',
      ].join('|');

      this.bars = bars;
      this.barByTs = new Map(bars.map(x => [Number(x.timestamp), x.__source]));

      if (this.dataKey !== key) {
        this.dataKey = key;
        chart.setSymbol({
          ticker: String(config.symbol || '—'),
          pricePrecision: 4,
          volumePrecision: 0,
        });
        chart.setPeriod(this.periodOf(config.timeframe));
        chart.setDataLoader({
          getBars: ({ callback }) => {
            callback(bars.map(({ __source, ...x }) => x), false);
            requestAnimationFrame(() => {
              this.fitMobileBarSpace();
              this.scheduleRedraw();
            });
          },
        });
        try { chart.resetData(); } catch (_) {}
      } else {
        this.scheduleRedraw();
      }
    }

    fitMobileBarSpace() {
      if (!this.chart || !this.host) return;
      const width = Math.max(280, this.host.clientWidth || 360);
      const mobile = width < 640;
      const targetBars = mobile ? 52 : 90;
      const space = clamp((width - 58) / targetBars, 4.2, mobile ? 8.2 : 10);
      try { this.chart.setBarSpace(space); } catch (_) {}
      try { this.chart.scrollToRealTime(); } catch (_) {}
    }

    render(config) {
      this.current = config;
      this.setData(config);
      this.scheduleRedraw();
    }

    resetView() {
      this.fitMobileBarSpace();
      try { this.chart && this.chart.scrollToRealTime(); } catch (_) {}
      this.scheduleRedraw();
    }

    scheduleRedraw() {
      if (this.raf) cancelAnimationFrame(this.raf);
      this.raf = requestAnimationFrame(() => {
        this.raf = 0;
        this.redraw();
      });
    }

    sizeCanvas(canvas, cssHeight) {
      const width = Math.max(1, this.host.clientWidth || 1);
      const dpr = Math.max(1, window.devicePixelRatio || 1);
      canvas.style.width = width + 'px';
      canvas.style.height = cssHeight + 'px';
      canvas.width = Math.floor(width * dpr);
      canvas.height = Math.floor(cssHeight * dpr);
      const ctx = canvas.getContext('2d');
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      ctx.clearRect(0, 0, width, cssHeight);
      return { ctx, width, height: cssHeight };
    }

    px(timestamp, value) {
      if (!this.chart) return null;
      try {
        const p = this.chart.convertToPixel(
          { timestamp: Number(timestamp), value: Number(value) },
          { paneId: 'candle_pane', absolute: true },
        );
        if (!p || !Number.isFinite(p.x) || !Number.isFinite(p.y)) return null;
        return p;
      } catch (_) {
        return null;
      }
    }

    x(timestamp) {
      if (!this.chart) return null;
      try {
        const p = this.chart.convertToPixel(
          { timestamp: Number(timestamp) },
          { paneId: 'candle_pane', absolute: true },
        );
        return p && Number.isFinite(p.x) ? p.x : null;
      } catch (_) {
        return null;
      }
    }

    drawPolyline(ctx, rows, key, color, dash, width) {
      ctx.save();
      ctx.strokeStyle = color;
      ctx.lineWidth = width || 1;
      ctx.setLineDash(dash || []);
      ctx.beginPath();
      let started = false;
      for (const row of rows || []) {
        const value = row[key];
        const timestamp = ts(row.date);
        if (value == null || value === '' || timestamp == null) {
          started = false;
          continue;
        }
        const p = this.px(timestamp, value);
        if (!p) {
          started = false;
          continue;
        }
        if (!started) {
          ctx.moveTo(p.x, p.y);
          started = true;
        } else {
          ctx.lineTo(p.x, p.y);
        }
      }
      ctx.stroke();
      ctx.restore();
    }

    drawSegment(ctx, seg, color, width) {
      const p1 = this.px(ts(seg.start_date), seg.start_price);
      const p2 = this.px(ts(seg.end_date), seg.end_price);
      if (!p1 || !p2) return;
      ctx.save();
      ctx.strokeStyle = color;
      ctx.lineWidth = width || 1;
      if (seg.pending) ctx.setLineDash([5, 3]);
      ctx.beginPath();
      ctx.moveTo(p1.x, p1.y);
      ctx.lineTo(p2.x, p2.y);
      ctx.stroke();
      ctx.restore();
    }

    drawArrow(ctx, x, y, buy, color, label, slot) {
      const dy = slot * 15;
      const yy = y + (buy ? dy : -dy);
      ctx.save();
      ctx.fillStyle = color;
      ctx.strokeStyle = '#081018';
      ctx.lineWidth = 1;
      ctx.beginPath();
      if (buy) {
        ctx.moveTo(x, yy - 7);
        ctx.lineTo(x - 5, yy + 4);
        ctx.lineTo(x + 5, yy + 4);
      } else {
        ctx.moveTo(x, yy + 7);
        ctx.lineTo(x - 5, yy - 4);
        ctx.lineTo(x + 5, yy - 4);
      }
      ctx.closePath();
      ctx.fill();
      ctx.stroke();
      ctx.font = 'bold 8px system-ui';
      ctx.textAlign = 'center';
      ctx.fillStyle = color;
      ctx.fillText(label, x, yy + (buy ? 15 : -10));
      ctx.restore();
    }

    redrawOverlay() {
      const cfg = this.current;
      if (!cfg || !this.chart) return;
      const hostHeight = Math.max(1, this.host.clientHeight || 400);
      const { ctx, width } = this.sizeCanvas(this.overlay, hostHeight);
      const payloads = cfg.payloads;
      const selected = cfg.selected;
      const rows = cfg.candles || [];

      const get = id => payloads.get(id) || null;
      const structure = selected.has('v7') ? get('v7') : selected.has('e') ? get('e') : null;
      if (structure) {
        for (const [key, color, dash, w] of [
          ['GZB3', '#728096', [], 1],
          ['GZB4', '#9ba6b7', [], 1],
          ['ZD1', '#65c5d8', [4, 3], 1],
          ['ZK1', '#c28bd8', [4, 3], 1],
          ['BS', '#eab464', [2, 3], 1],
          ['BD', '#eab464', [2, 3], 1],
        ]) {
          this.drawPolyline(ctx, structure.chart || [], key, color, dash, w);
        }
      }

      if (selected.has('support_resistance')) {
        const sr = get('support_resistance');
        for (const [key, color, dash, w] of [
          ['sr_short_pressure', '#52d49a', [5, 4], 1],
          ['sr_short_support', '#ff7b82', [5, 4], 1],
          ['sr_long_pressure', '#52d49a', [], 1],
          ['sr_long_support', '#ff7b82', [], 1],
        ]) {
          this.drawPolyline(ctx, sr?.chart || [], key, color, dash, w);
        }
      }

      if (selected.has('chan')) {
        const ch = get('chan')?.chan || {};
        for (const z of ch.zhongshus || []) {
          const a = this.px(ts(z.start_date), z.ZG);
          const b = this.px(ts(z.end_date), z.ZD);
          if (!a || !b) continue;
          const x = Math.min(a.x, b.x);
          const y = Math.min(a.y, b.y);
          const rw = Math.abs(a.x - b.x);
          const rh = Math.abs(a.y - b.y);
          if (rw < 1 || rh < 1 || x > width || x + rw < 0) continue;
          ctx.save();
          ctx.fillStyle = 'rgba(234,180,100,.08)';
          ctx.strokeStyle = 'rgba(234,180,100,.55)';
          if (z.pending) ctx.setLineDash([5, 3]);
          ctx.fillRect(x, y, rw, rh);
          ctx.strokeRect(x, y, rw, rh);
          ctx.restore();
        }
        (ch.bis || []).forEach(s => this.drawSegment(ctx, s, 'rgba(120,170,255,.55)', 1));
        (ch.segments || []).forEach(s => this.drawSegment(ctx, s, 'rgba(235,195,98,.88)', 1.4));
      }

      const barMap = new Map(rows.map(r => [String(r.date), r]));
      const stacks = new Map();
      const nextSlot = (date, buy) => {
        const k = String(date) + '|' + (buy ? 'B' : 'S');
        const n = stacks.get(k) || 0;
        stacks.set(k, n + 1);
        return n;
      };

      const markerSeries = [
        ['v7', 'SL', '#71e0b0'],
        ['e', 'E', '#dba6ff'],
        ['5s_stocks', '5S', '#6ea1ff'],
      ];
      for (const [id, label, color] of markerSeries) {
        if (!selected.has(id)) continue;
        const p = get(id);
        for (const m of p?.markers || []) {
          const date = String(m.signal_date || m.execution_date || '');
          const bar = barMap.get(date);
          if (!bar) continue;
          const buy = m.side === 'B';
          const price = buy ? bar.low : bar.high;
          const point = this.px(ts(date), price);
          if (!point) continue;
          this.drawArrow(
            ctx,
            point.x,
            point.y + (buy ? 17 : -17),
            buy,
            color,
            label + (m.side === 'X' ? '清' : buy ? '买' : '卖'),
            nextSlot(date, buy),
          );
        }
      }

      const chanSignals = selected.has('chan')
        ? (get('chan')?.chan?.signals || [])
        : [];
      for (const s of chanSignals) {
        const date = String(s.anchor_date || '');
        const bar = barMap.get(date);
        if (!bar) continue;
        const buy = String(s.kind || '').startsWith('B');
        const price = num(s.price) ?? (buy ? num(bar.low) : num(bar.high));
        const point = this.px(ts(date), price);
        if (!point) continue;
        this.drawArrow(
          ctx,
          point.x,
          point.y + (buy ? 16 : -16),
          buy,
          buy ? '#52d49a' : '#ff7b82',
          '缠' + String(s.kind || ''),
          nextSlot(date, buy),
        );
      }
    }

    redrawState() {
      const cfg = this.current;
      if (!cfg) return;
      const { ctx, width, height } = this.sizeCanvas(this.stateCanvas, 26);
      ctx.fillStyle = '#080d17';
      ctx.fillRect(0, 0, width, height);
      if (!cfg.selected.has('v7')) {
        ctx.fillStyle = '#71819a';
        ctx.font = '9px system-ui';
        ctx.fillText('SLTD 三色状态（选择 SLTD 后显示）', 8, 17);
        return;
      }
      const v7 = cfg.payloads.get('v7');
      const map = new Map((v7?.chart || []).map(r => [String(r.date), r]));
      const xs = [];
      for (const row of cfg.candles || []) {
        const x = this.x(ts(row.date));
        if (x == null) continue;
        xs.push({ x, row });
      }
      for (let i = 0; i < xs.length; i++) {
        const { x, row } = xs[i];
        if (x < -20 || x > width + 20) continue;
        const prev = xs[i - 1]?.x;
        const next = xs[i + 1]?.x;
        const half = Math.max(1, Math.min(10, Math.abs((next ?? x + 6) - (prev ?? x - 6)) / 4));
        const state = map.get(String(row.date))?.state || 'OTHER';
        ctx.fillStyle = STATE_COLORS[state] || STATE_COLORS.OTHER;
        ctx.fillRect(x - half, 3, half * 2, height - 6);
      }
      ctx.fillStyle = 'rgba(8,13,23,.82)';
      ctx.fillRect(4, 4, 76, 15);
      ctx.fillStyle = '#cbd5e4';
      ctx.font = '8px system-ui';
      ctx.fillText('SLTD 三色状态', 8, 15);
    }

    redrawPosition() {
      const cfg = this.current;
      if (!cfg) return;
      const { ctx, width, height } = this.sizeCanvas(this.positionCanvas, 62);
      ctx.fillStyle = '#080d17';
      ctx.fillRect(0, 0, width, height);

      const top = 7;
      const bottom = 52;
      ctx.strokeStyle = '#1f2c41';
      ctx.lineWidth = 1;
      ctx.fillStyle = '#71819a';
      ctx.font = '8px system-ui';
      for (const f of [0, .5, 1]) {
        const y = bottom - f * (bottom - top);
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(width, y);
        ctx.stroke();
        ctx.fillText(Math.round(f * 100) + '%', width - 28, y - 2);
      }

      const defs = [
        ['v7', 'SLTD', '#5b8cff'],
        ['e', 'E', '#dba6ff'],
        ['5s_stocks', '5s', '#65c5d8'],
      ];
      let labelRow = 0;
      for (const [id, label, color] of defs) {
        if (!cfg.selected.has(id)) continue;
        const p = cfg.payloads.get(id);
        if (!p) continue;
        const byDate = new Map((p.chart || []).map(r => [String(r.date), r]));
        ctx.save();
        ctx.strokeStyle = color;
        ctx.lineWidth = 1.5;
        ctx.beginPath();
        let started = false;
        let last = null;
        for (const row of cfg.candles || []) {
          const x = this.x(ts(row.date));
          const value = num(byDate.get(String(row.date))?.position);
          if (x == null || value == null) continue;
          const y = bottom - clamp(value, 0, 1) * (bottom - top);
          if (x < -30 || x > width + 30) continue;
          if (!started) {
            ctx.moveTo(x, y);
            started = true;
          } else {
            ctx.lineTo(x, y);
          }
          last = value;
        }
        if (started) ctx.stroke();
        if (last != null) {
          ctx.fillStyle = color;
          ctx.font = 'bold 8px system-ui';
          ctx.textAlign = 'left';
          ctx.fillText(label + ' ' + Math.round(last * 100) + '%', 6 + labelRow * 62, 10);
          labelRow++;
        }
        ctx.restore();
      }
      if (labelRow === 0) {
        ctx.fillStyle = '#71819a';
        ctx.font = '9px system-ui';
        ctx.fillText('当前选择的策略没有仓位轨迹', 8, 15);
      }
    }

    redraw() {
      if (!this.chart || !this.current) return;
      this.redrawOverlay();
      this.redrawState();
      this.redrawPosition();
    }

    dispose() {
      if (this.resizeObserver) this.resizeObserver.disconnect();
      try {
        if (this.chart && window.klinecharts?.dispose) {
          window.klinecharts.dispose(this.host);
        }
      } catch (_) {}
      this.chart = null;
    }
  }

  window.SiftAlphaKLineWorkspace = {
    VERSION,
    create(opts) { return new Workspace(opts); },
  };
})();